from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.core.files.storage import default_storage
import json

from .models import (
    Course, Lesson, Module, LessonQuiz, LessonQuizQuestion, LessonQuizAttempt,
    UserProgress, CourseEnrollment, FavoriteCourse, Certification, Exam, ExamAttempt,
    CourseAccess, Bundle, BundlePurchase, Cohort, CohortMember
)
from .utils.access import has_course_access, get_courses_by_visibility, get_user_accessible_courses, check_course_prerequisites


@require_POST
@login_required
def editor_image_upload(request):
    """Upload image for Editor.js"""
    f = request.FILES.get("file")
    if not f:
        return HttpResponseBadRequest("No file provided")
    
    try:
        # Save to default storage (Cloudinary if configured, otherwise local)
        name = default_storage.save(f"editor/{f.name}", f)
        secure_url = default_storage.url(name)
        
        # Prefer lightweight delivery variant for web use (if Cloudinary)
        web_url = secure_url
        if "/upload/" in secure_url:
            web_url = secure_url.replace("/upload/", "/upload/f_auto,q_auto/")
        
        return JsonResponse({"url": secure_url, "web_url": web_url})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def home(request):
    """Landing page"""
    return render(request, 'landing.html')


def coming_soon(request):
    """Placeholder page for features coming soon"""
    return render(request, 'coming_soon.html')


def contact(request):
    """Contact page"""
    return render(request, 'contact.html')


def about(request):
    """About page"""
    return render(request, 'about.html')


def testimonials(request):
    """Testimonials page - scrolls to testimonials section on landing page"""
    return redirect('/#testimonials')


def events(request):
    """Events page"""
    return render(request, 'events.html')


def community(request):
    """Community page"""
    return render(request, 'community.html')


def updates(request):
    """Updates/Blog page"""
    return render(request, 'updates.html')


def terms(request):
    """Terms of Service page"""
    return render(request, 'terms.html')


def privacy(request):
    """Privacy Policy page"""
    return render(request, 'privacy.html')


def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('student_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Please provide both username and password.')
            return render(request, 'login.html')
        
        # Check if user exists first
        from django.contrib.auth.models import User
        try:
            user_obj = User.objects.get(username=username)
            if not user_obj.is_active:
                messages.error(request, 'Your account is inactive. Please contact an administrator.')
                return render(request, 'login.html')
        except User.DoesNotExist:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'login.html')
        
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
    """Course catalog page - redirects to dashboard for authenticated users"""
    if request.user.is_authenticated:
        return redirect('student_dashboard')
    
    # Public course catalog (only for non-authenticated users)
    import logging
    logger = logging.getLogger(__name__)
    
    # Check favorites filter
    filter_favorites = request.GET.get('favorites') == 'true'
    
    if False:  # This block will never execute, kept for structure
        # Get accessible courses using the same logic as has_course_access()
        accessible_courses = get_user_accessible_courses(request.user)
        accessible_course_ids = set(accessible_courses.values_list('id', flat=True))
        
        # Also include courses where user has progress (bulletproof check)
        progress_course_ids = set(UserProgress.objects.filter(
            user=request.user
        ).values_list('lesson__course_id', flat=True).distinct())
        
        # Union both sets - if user has progress, they have access
        all_accessible_ids = accessible_course_ids | progress_course_ids
        
        # Get favorites
        favorited_ids = list(FavoriteCourse.objects.filter(user=request.user).values_list('course_id', flat=True))
        
        # Get all active courses
        all_active_courses = Course.objects.filter(status='active')
        
        # My Courses: courses in accessible set
        my_courses_qs = Course.objects.filter(id__in=all_accessible_ids)
        
        # Available Courses: active courses NOT in accessible set
        available_qs = all_active_courses.exclude(id__in=all_accessible_ids).filter(
            visibility__in=['public', 'members_only']
        )
        
        # Pre-calculate progress for ALL courses (my_courses + available)
        all_courses_for_progress = list(my_courses_qs) + list(available_qs)
        course_progress_map = {}
        
        for course in all_courses_for_progress:
            total_lessons = course.lesson_set.count()
            completed_lessons = UserProgress.objects.filter(
                user=request.user,
                lesson__course=course,
                completed=True
            ).count()
            
            # Calculate percentage and clamp between 0 and 100
            if total_lessons > 0:
                course_progress = int((completed_lessons / total_lessons) * 100)
                course_progress = max(0, min(100, course_progress))  # Clamp to 0-100
            else:
                course_progress = 0
            
            course_progress_map[course.id] = {
                'progress': course_progress,
                'completed': course_progress == 100,
                'total_lessons': total_lessons,
                'completed_lessons': completed_lessons,
            }
            
            logger.info(f"[PROGRESS DEBUG] Course: {course.name} (ID: {course.id}), User: {request.user.username} (ID: {request.user.id}), Completed: {completed_lessons}/{total_lessons}, Progress: {course_progress}%")
        
        # Build Continue Learning: My Courses with progress > 0 and < 100%
        continue_learning_ids = [
            course_id for course_id, data in course_progress_map.items()
            if course_id in all_accessible_ids and data['progress'] > 0 and data['progress'] < 100
        ]
        continue_learning_qs = Course.objects.filter(id__in=continue_learning_ids)
        
        # My Courses: ALL accessible courses (including 100% completed)
        # Filter by favorites if requested
        my_courses_filtered = my_courses_qs
        if filter_favorites:
            my_courses_filtered = my_courses_filtered.filter(id__in=favorited_ids)
        
        # Continue Learning: filter by favorites if requested
        continue_learning_filtered = continue_learning_qs
        if filter_favorites:
            continue_learning_filtered = continue_learning_filtered.filter(id__in=favorited_ids)
        
        # Available: filter by favorites if requested
        available_filtered = available_qs
        if filter_favorites:
            available_filtered = available_filtered.filter(id__in=favorited_ids)
        
        # Attach progress data to course objects
        my_courses_list = list(my_courses_filtered)
        continue_learning_list = list(continue_learning_filtered)
        available_list = list(available_filtered)
        
        for course in my_courses_list + continue_learning_list + available_list:
            if course.id in course_progress_map:
                data = course_progress_map[course.id]
                course.user_progress_percent = data['progress']
                course.is_completed = data['completed']
            else:
                course.user_progress_percent = 0
                course.is_completed = False
            course.is_favorited = course.id in favorited_ids
        
        # Debug output
        logger.info(f"[COURSES DEBUG] User: {request.user.username} (ID: {request.user.id})")
        logger.info(f"[COURSES DEBUG] Filter favorites: {filter_favorites}")
        logger.info(f"[COURSES DEBUG] Accessible course IDs (from access): {sorted(accessible_course_ids)}")
        logger.info(f"[COURSES DEBUG] Progress course IDs (from UserProgress): {sorted(progress_course_ids)}")
        logger.info(f"[COURSES DEBUG] All accessible IDs (union): {sorted(all_accessible_ids)}")
        logger.info(f"[COURSES DEBUG] My Courses count: {len(my_courses_list)}, IDs: {[c.id for c in my_courses_list]}")
        logger.info(f"[COURSES DEBUG] Continue Learning count: {len(continue_learning_list)}, IDs: {[c.id for c in continue_learning_list]}")
        logger.info(f"[COURSES DEBUG] Available count: {len(available_list)}, IDs: {[c.id for c in available_list]}")
        logger.info(f"[COURSES DEBUG] Favorited IDs: {favorited_ids}")
        
    else:
        my_courses_list = []
        continue_learning_list = []
        available_qs = Course.objects.filter(visibility='public', status='active')
        if filter_favorites:
            available_qs = available_qs.none()  # Can't favorite when not logged in
        available_list = list(available_qs)
        favorited_ids = []
        
        for course in available_list:
            course.user_progress_percent = 0
            course.is_completed = False
            course.is_favorited = False
    
    context = {
        'my_courses': my_courses_list,
        'available_courses': available_list,
        'continue_learning': continue_learning_list,
        'favorited_ids': favorited_ids,
        'filter_favorites': filter_favorites,
    }
    return render(request, 'student/courses.html', context)


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
    
    # Get user progress if authenticated and check lesson unlock status
    user_progress = {}
    lessons_with_status = []
    course_progress = 0
    if request.user.is_authenticated:
        progress_records = UserProgress.objects.filter(user=request.user, lesson__course=course)
        for progress in progress_records:
            user_progress[progress.lesson_id] = progress
        # Calculate progress based on completed lessons count
        total_lessons = lessons.count()
        completed_lessons = UserProgress.objects.filter(
            user=request.user,
            lesson__course=course,
            completed=True
        ).count()
        course_progress = int((completed_lessons / total_lessons * 100)) if total_lessons > 0 else 0
        
        # Check unlock status for each lesson
        lessons_list = list(lessons)
        for i, lesson in enumerate(lessons_list):
            is_unlocked = True
            is_completed = False
            progress_obj = None
            
            # Check if lesson has progress
            if lesson.id in user_progress:
                progress_obj = user_progress[lesson.id]
                is_completed = progress_obj.completed
            
            # First lesson is always unlocked if user has access
            if i > 0 and has_access:
                # Check if previous lesson is completed
                prev_lesson = lessons_list[i - 1]
                if prev_lesson.id in user_progress:
                    prev_progress = user_progress[prev_lesson.id]
                    is_unlocked = prev_progress.completed
                else:
                    is_unlocked = False
            
            lessons_with_status.append({
                'lesson': lesson,
                'is_unlocked': is_unlocked,
                'is_completed': is_completed,
                'progress_obj': progress_obj,
            })
    else:
        # For non-authenticated users, mark all as locked
        for lesson in lessons:
            lessons_with_status.append({
                'lesson': lesson,
                'is_unlocked': False,
                'is_completed': False,
            })
    
    # Check if favorited
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = FavoriteCourse.objects.filter(user=request.user, course=course).exists()
    
    context = {
        'course': course,
        'modules': modules,
        'lessons': lessons,
        'lessons_with_status': lessons_with_status if request.user.is_authenticated else [],
        'has_access': has_access,
        'access_reason': reason,
        'user_progress': user_progress,
        'course_progress': course_progress,
        'is_favorited': is_favorited,
        'prerequisites_met': prerequisites_met,
        'missing_prerequisites': missing_prerequisites,
    }
    return render(request, 'student/course_detail.html', context)


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
    
    # Get all lessons with progress
    all_lessons = list(Lesson.objects.filter(course=course).order_by('order'))
    current_index = None
    
    # Attach progress to each lesson and check if unlocked
    lessons_with_progress = []
    for i, l in enumerate(all_lessons):
        if l.id == lesson.id:
            current_index = i
        
        # Get progress for this lesson
        try:
            lesson_progress = UserProgress.objects.get(user=request.user, lesson=l)
            is_completed = lesson_progress.completed
        except UserProgress.DoesNotExist:
            lesson_progress = None
            is_completed = False
        
        # Check if lesson is unlocked (first lesson or previous is completed)
        is_unlocked = True
        if i > 0:  # Not the first lesson
            try:
                prev_progress = UserProgress.objects.get(user=request.user, lesson=all_lessons[i-1])
                is_unlocked = prev_progress.completed
            except UserProgress.DoesNotExist:
                is_unlocked = False
        
        lessons_with_progress.append({
            'lesson': l,
            'progress': lesson_progress,
            'is_completed': is_completed,
            'is_unlocked': is_unlocked,
            'is_current': l.id == lesson.id,
        })
    
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
        'all_lessons_with_progress': lessons_with_progress,
        'quiz': quiz,
        'quiz_attempt': quiz_attempt,
    }
    return render(request, 'student/lesson.html', context)


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
    return render(request, 'student/lesson_quiz.html', context)


# API Views will be in a separate file - api_views.py
