from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q, Count, Avg
import json

from .models import (
    Course, Lesson, Module, LessonQuiz, LessonQuizQuestion, LessonQuizAttempt,
    UserProgress, CourseEnrollment, FavoriteCourse, Certification, Exam, ExamAttempt,
    CourseAccess, Bundle, BundlePurchase, Cohort, CohortMember
)
from .utils.access import has_course_access, get_courses_by_visibility, check_course_prerequisites


def home(request):
    """Landing page"""
    return render(request, 'landing.html')


def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('student_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', 'student_dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')


def logout_view(request):
    """User logout"""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


def courses(request):
    """Course catalog page"""
    if request.user.is_authenticated:
        courses_dict = get_courses_by_visibility(request.user)
        my_courses = courses_dict['my_courses']
        available = courses_dict['available_to_unlock']
    else:
        my_courses = Course.objects.none()
        available = Course.objects.filter(visibility='public', status='active')
    
    # Get favorites if authenticated
    favorited_ids = []
    if request.user.is_authenticated:
        favorited_ids = list(FavoriteCourse.objects.filter(user=request.user).values_list('course_id', flat=True))
    
    # Continue learning - courses with progress
    continue_learning = []
    if request.user.is_authenticated:
        progress_courses = UserProgress.objects.filter(
            user=request.user,
            status__in=['in_progress', 'completed'],
            lesson__course__in=my_courses
        ).values_list('lesson__course_id', flat=True).distinct()
        continue_learning = Course.objects.filter(id__in=progress_courses)
    
    context = {
        'my_courses': my_courses,
        'available_courses': available,
        'continue_learning': continue_learning,
        'favorited_ids': favorited_ids,
    }
    return render(request, 'courses.html', context)


def course_detail(request, course_slug):
    """Course detail page"""
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check prerequisites
    prerequisites_met = True
    missing_prerequisites = []
    if request.user.is_authenticated:
        prerequisites_met, missing_prerequisites = check_course_prerequisites(request.user, course)
    
    # Check access
    has_access, access_record, reason = has_course_access(request.user, course)
    
    # Get lessons grouped by module
    modules = Module.objects.filter(course=course).order_by('order')
    lessons = Lesson.objects.filter(course=course).order_by('order')
    
    # Get user progress if authenticated
    user_progress = {}
    course_progress = 0
    if request.user.is_authenticated:
        progress_records = UserProgress.objects.filter(user=request.user, lesson__course=course)
        for progress in progress_records:
            user_progress[progress.lesson_id] = progress
        lessons_list = list(lessons)
        if lessons_list:
            total_progress = sum(p.progress_percentage for p in progress_records)
            course_progress = int(total_progress / len(lessons_list)) if lessons_list else 0
    
    # Check if favorited
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = FavoriteCourse.objects.filter(user=request.user, course=course).exists()
    
    context = {
        'course': course,
        'modules': modules,
        'lessons': lessons,
        'has_access': has_access,
        'access_reason': reason,
        'user_progress': user_progress,
        'course_progress': course_progress,
        'is_favorited': is_favorited,
        'prerequisites_met': prerequisites_met,
        'missing_prerequisites': missing_prerequisites,
    }
    return render(request, 'course_detail.html', context)


@login_required
def lesson_detail(request, course_slug, lesson_slug):
    """Lesson video player page"""
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, course=course, slug=lesson_slug)
    
    # Check prerequisites
    prerequisites_met, missing_prerequisites = check_course_prerequisites(request.user, course)
    if not prerequisites_met:
        messages.warning(request, f'You must complete the following prerequisite courses: {", ".join([p.name for p in missing_prerequisites])}')
        return redirect('course_detail', course_slug=course_slug)
    
    # Check access
    has_access, access_record, reason = has_course_access(request.user, course)
    if not has_access:
        messages.error(request, 'You do not have access to this course.')
        return redirect('course_detail', course_slug=course_slug)
    
    # Get or create user progress
    progress, created = UserProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson,
        defaults={
            'status': 'not_started',
            'last_accessed': timezone.now()
        }
    )
    
    if not created:
        progress.last_accessed = timezone.now()
        progress.save()
    
    # Get previous and next lessons
    all_lessons = list(Lesson.objects.filter(course=course).order_by('order'))
    current_index = None
    for i, l in enumerate(all_lessons):
        if l.id == lesson.id:
            current_index = i
            break
    
    previous_lesson = all_lessons[current_index - 1] if current_index and current_index > 0 else None
    next_lesson = all_lessons[current_index + 1] if current_index is not None and current_index < len(all_lessons) - 1 else None
    
    # Check if quiz exists
    quiz = None
    quiz_attempt = None
    if hasattr(lesson, 'quiz'):
        quiz = lesson.quiz
        quiz_attempt = LessonQuizAttempt.objects.filter(user=request.user, quiz=quiz).order_by('-completed_at').first()
    
    context = {
        'course': course,
        'lesson': lesson,
        'progress': progress,
        'previous_lesson': previous_lesson,
        'next_lesson': next_lesson,
        'quiz': quiz,
        'quiz_attempt': quiz_attempt,
    }
    return render(request, 'lesson.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def lesson_quiz_view(request, course_slug, lesson_slug):
    """Lesson quiz page"""
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, course=course, slug=lesson_slug)
    
    # Check access
    has_access, _, _ = has_course_access(request.user, course)
    if not has_access:
        messages.error(request, 'You do not have access to this course.')
        return redirect('course_detail', course_slug=course_slug)
    
    # Check if quiz exists
    if not hasattr(lesson, 'quiz'):
        messages.error(request, 'This lesson does not have a quiz.')
        return redirect('lesson_detail', course_slug=course_slug, lesson_slug=lesson_slug)
    
    quiz = lesson.quiz
    
    if request.method == 'POST':
        # Process quiz submission
        answers = {}
        correct_count = 0
        total_questions = quiz.questions.count()
        
        for question in quiz.questions.all():
            answer = request.POST.get(f'question_{question.id}')
            if answer:
                answers[str(question.id)] = answer
                if answer == question.correct_option:
                    correct_count += 1
        
        score = (correct_count / total_questions * 100) if total_questions > 0 else 0
        passed = score >= quiz.passing_score
        
        # Save attempt
        attempt = LessonQuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            score=score,
            passed=passed,
            answers=answers
        )
        
        messages.success(request, f'Quiz completed! Your score: {score:.1f}%. {"Passed!" if passed else f"Required: {quiz.passing_score}%"}.')
        
        # Redirect to lesson or show results
        return redirect('lesson_detail', course_slug=course_slug, lesson_slug=lesson_slug)
    
    # GET request - show quiz
    questions = quiz.questions.all().order_by('order')
    
    context = {
        'course': course,
        'lesson': lesson,
        'quiz': quiz,
        'questions': questions,
    }
    return render(request, 'lesson_quiz.html', context)


# API Views will be in a separate file - api_views.py
