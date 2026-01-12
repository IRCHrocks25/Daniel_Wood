"""
Student Dashboard Views
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone

from .models import (
    Course, Lesson, UserProgress, FavoriteCourse, Certification, ExamAttempt,
    CourseEnrollment
)
from .utils.access import has_course_access, get_courses_by_visibility


@login_required
def student_dashboard(request):
    """Student personal dashboard"""
    user = request.user
    
    # Overall stats
    enrolled_courses = CourseEnrollment.objects.filter(user=user).count()
    completed_courses = 0  # Calculate based on all lessons completed
    
    total_lessons = Lesson.objects.filter(course__courseenrollment__user=user).count()
    completed_lessons = UserProgress.objects.filter(user=user, completed=True).count()
    
    certifications = Certification.objects.filter(user=user, status='passed').count()
    
    # Get courses
    courses_dict = get_courses_by_visibility(user)
    my_courses_list = list(courses_dict['my_courses'])
    
    # Calculate course completion
    for course in my_courses_list:
        lessons = Lesson.objects.filter(course=course)
        completed = UserProgress.objects.filter(
            user=user,
            lesson__course=course,
            completed=True
        ).count()
        if lessons.count() > 0 and completed == lessons.count():
            completed_courses += 1
    
    # Get favorites
    favorited_ids = list(FavoriteCourse.objects.filter(user=user).values_list('course_id', flat=True))
    
    # Filter by favorites if requested
    filter_favorites = request.GET.get('favorites') == 'true'
    if filter_favorites:
        my_courses_list = [c for c in my_courses_list if c.id in favorited_ids]
    
    # Sort options
    sort_by = request.GET.get('sort', 'recent')
    if sort_by == 'progress':
        my_courses_list.sort(key=lambda c: c.get_user_progress(user), reverse=True)
    elif sort_by == 'name':
        my_courses_list.sort(key=lambda c: c.name)
    else:  # recent
        my_courses_list.sort(key=lambda c: c.created_at, reverse=True)
    
    context = {
        'enrolled_courses': enrolled_courses,
        'completed_courses': completed_courses,
        'total_lessons': total_lessons,
        'completed_lessons': completed_lessons,
        'certifications': certifications,
        'my_courses': my_courses_list,
        'favorited_ids': favorited_ids,
        'filter_favorites': filter_favorites,
        'sort_by': sort_by,
    }
    return render(request, 'student/dashboard.html', context)


@login_required
def student_course_progress(request, course_slug):
    """Detailed course progress view"""
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check access
    has_access, _, _ = has_course_access(request.user, course)
    if not has_access:
        from django.contrib import messages
        messages.error(request, 'You do not have access to this course.')
        return redirect('student_dashboard')
    
    # Get lessons
    modules = course.module_set.all().order_by('order')
    lessons = course.lesson_set.all().order_by('order')
    
    # Get progress and attach to lessons
    progress_records = {}
    for lesson in lessons:
        try:
            progress = UserProgress.objects.get(user=request.user, lesson=lesson)
            progress_records[lesson.id] = progress
            lesson.user_progress = progress
        except UserProgress.DoesNotExist:
            progress_records[lesson.id] = None
            lesson.user_progress = None
    
    # Calculate overall progress
    total_lessons = lessons.count()
    completed_lessons = UserProgress.objects.filter(
        user=request.user,
        lesson__course=course,
        completed=True
    ).count()
    course_progress = int((completed_lessons / total_lessons * 100)) if total_lessons > 0 else 0
    
    # Check quiz results and attach to lessons
    quiz_results = {}
    for lesson in lessons:
        if hasattr(lesson, 'quiz') and lesson.quiz:
            attempt = lesson.quiz.lessonquizattempt_set.filter(
                user=request.user
            ).order_by('-completed_at').first()
            if attempt:
                quiz_results[lesson.id] = attempt
                lesson.quiz_attempt = attempt
            else:
                lesson.quiz_attempt = None
        else:
            lesson.quiz_attempt = None
    
    context = {
        'course': course,
        'modules': modules,
        'lessons': lessons,
        'progress_records': progress_records,
        'course_progress': course_progress,
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons,
        'quiz_results': quiz_results,
    }
    return render(request, 'student/course_progress.html', context)


@login_required
def student_certifications(request):
    """Display student's certifications"""
    user = request.user
    
    # Get certifications
    certifications = Certification.objects.filter(user=user, status='passed').order_by('-issued_at')
    
    # Calculate trophy tier
    cert_count = certifications.count()
    trophy_tiers = {
        'bronze': {'min': 1, 'max': 1, 'unlocked': cert_count >= 1},
        'silver': {'min': 2, 'max': 2, 'unlocked': cert_count >= 2},
        'gold': {'min': 3, 'max': 4, 'unlocked': cert_count >= 3},
        'platinum': {'min': 5, 'max': 9, 'unlocked': cert_count >= 5},
        'diamond': {'min': 10, 'max': 19, 'unlocked': cert_count >= 10},
        'ultimate': {'min': 20, 'max': 999, 'unlocked': cert_count >= 20},
    }
    
    # Determine current tier
    current_tier = None
    for tier_name, tier_info in trophy_tiers.items():
        if tier_info['unlocked']:
            current_tier = tier_name
    
    # Next tier progress
    next_tier = None
    certs_needed_for_next = None
    if current_tier:
        tier_names = ['bronze', 'silver', 'gold', 'platinum', 'diamond', 'ultimate']
        current_index = tier_names.index(current_tier)
        if current_index < len(tier_names) - 1:
            next_tier = tier_names[current_index + 1]
            next_tier_info = trophy_tiers[next_tier]
            certs_needed_for_next = max(0, next_tier_info['min'] - cert_count)
    
    context = {
        'certifications': certifications,
        'cert_count': cert_count,
        'trophy_tiers': trophy_tiers,
        'current_tier': current_tier,
        'next_tier': next_tier,
        'certs_needed_for_next': certs_needed_for_next,
    }
    return render(request, 'student/certifications.html', context)

