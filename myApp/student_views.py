"""
Student Dashboard Views
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone

from .models import (
    Course, Lesson, UserProgress, FavoriteCourse, Certification, ExamAttempt,
    CourseEnrollment, Exam, ExamQuestion
)
from .utils.access import has_course_access, get_courses_by_visibility
from .utils.exam import check_exam_eligibility, calculate_exam_score


@login_required
def student_dashboard(request):
    """Student personal dashboard - consolidated with courses page"""
    from .utils.access import get_user_accessible_courses
    
    user = request.user
    import logging
    logger = logging.getLogger(__name__)
    
    # Overall stats
    enrolled_courses = CourseEnrollment.objects.filter(user=user).count()
    completed_courses = 0
    
    total_lessons = Lesson.objects.filter(course__courseenrollment__user=user).count()
    completed_lessons = UserProgress.objects.filter(user=user, completed=True).count()
    
    certifications = Certification.objects.filter(user=user, status='passed').count()
    
    # Get accessible courses using the same logic as has_course_access()
    accessible_courses = get_user_accessible_courses(user)
    accessible_course_ids = set(accessible_courses.values_list('id', flat=True))
    
    # Also include courses where user has progress (bulletproof check)
    progress_course_ids = set(UserProgress.objects.filter(
        user=user
    ).values_list('lesson__course_id', flat=True).distinct())
    
    # Union both sets - if user has progress, they have access
    all_accessible_ids = accessible_course_ids | progress_course_ids
    
    # Get favorites
    favorited_ids = list(FavoriteCourse.objects.filter(user=user).values_list('course_id', flat=True))
    
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
        total_lessons_count = course.lesson_set.count()
        completed_lessons_count = UserProgress.objects.filter(
            user=user,
            lesson__course=course,
            completed=True
        ).count()
        
        # Calculate percentage and clamp between 0 and 100
        if total_lessons_count > 0:
            course_progress = int((completed_lessons_count / total_lessons_count) * 100)
            course_progress = max(0, min(100, course_progress))
            # Check if course is completed
            if completed_lessons_count == total_lessons_count:
                completed_courses += 1
        else:
            course_progress = 0
        
        course_progress_map[course.id] = {
            'progress': course_progress,
            'completed': course_progress == 100,
            'total_lessons': total_lessons_count,
            'completed_lessons': completed_lessons_count,
        }
    
    # Build Continue Learning: My Courses with progress > 0 and < 100%
    continue_learning_ids = [
        course_id for course_id, data in course_progress_map.items()
        if course_id in all_accessible_ids and data['progress'] > 0 and data['progress'] < 100
    ]
    continue_learning_qs = Course.objects.filter(id__in=continue_learning_ids)
    
    # Check filters
    filter_favorites = request.GET.get('favorites') == 'true'
    
    # My Courses: ALL accessible courses (including 100% completed)
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
    
    # Sort options
    sort_by = request.GET.get('sort', 'recent')
    if sort_by == 'progress':
        my_courses_list.sort(key=lambda c: c.user_progress_percent, reverse=True)
        continue_learning_list.sort(key=lambda c: c.user_progress_percent, reverse=True)
    elif sort_by == 'name':
        my_courses_list.sort(key=lambda c: c.name)
        continue_learning_list.sort(key=lambda c: c.name)
    else:  # recent
        my_courses_list.sort(key=lambda c: c.created_at, reverse=True)
        continue_learning_list.sort(key=lambda c: c.created_at, reverse=True)
    
    context = {
        'enrolled_courses': enrolled_courses,
        'completed_courses': completed_courses,
        'total_lessons': total_lessons,
        'completed_lessons': completed_lessons,
        'certifications': certifications,
        'my_courses': my_courses_list,
        'continue_learning': continue_learning_list,
        'available_courses': available_list,
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
    
    # Check exam eligibility
    exam_eligible = False
    exam_eligibility_reason = ''
    if hasattr(course, 'exam') and course.exam.is_active:
        eligible, reason, missing = check_exam_eligibility(request.user, course)
        exam_eligible = eligible
        exam_eligibility_reason = reason
    
    context = {
        'course': course,
        'modules': modules,
        'lessons': lessons,
        'progress_records': progress_records,
        'course_progress': course_progress,
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons,
        'quiz_results': quiz_results,
        'exam_eligible': exam_eligible,
        'exam_eligibility_reason': exam_eligibility_reason,
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


@login_required
def take_exam(request, course_slug):
    """Student exam view - start/take exam"""
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check access
    has_access, _, _ = has_course_access(request.user, course)
    if not has_access:
        from django.contrib import messages
        messages.error(request, 'You do not have access to this course.')
        return redirect('student_dashboard')
    
    # Check if exam exists
    if not hasattr(course, 'exam'):
        from django.contrib import messages
        messages.error(request, 'No exam available for this course.')
        return redirect('student_course_progress', course_slug=course_slug)
    
    exam = course.exam
    
    # Check eligibility
    eligible, reason, missing = check_exam_eligibility(request.user, course)
    if not eligible:
        from django.contrib import messages
        messages.warning(request, f'Not eligible to take exam: {reason}')
        return redirect('student_course_progress', course_slug=course_slug)
    
    # Get questions ordered
    questions = exam.questions.all().order_by('order', 'id')
    
    if not questions.exists():
        from django.contrib import messages
        messages.error(request, 'Exam has no questions yet.')
        return redirect('student_course_progress', course_slug=course_slug)
    
    # Get previous attempts
    previous_attempts = ExamAttempt.objects.filter(
        user=request.user,
        exam=exam
    ).order_by('-completed_at')[:5]
    
    context = {
        'course': course,
        'exam': exam,
        'questions': questions,
        'previous_attempts': previous_attempts,
    }
    return render(request, 'student/take_exam.html', context)


@login_required
def submit_exam(request, course_slug):
    """Submit exam answers - optimized for fast response"""
    import logging
    logger = logging.getLogger(__name__)
    
    start_time = timezone.now()
    logger.info(f"[EXAM SUBMIT] Request received at {start_time} for user {request.user.username}, course {course_slug}")
    
    if request.method != 'POST':
        return redirect('take_exam', course_slug=course_slug)
    
    try:
        # Quick validation checks
        logger.info(f"[EXAM SUBMIT] Starting validation for {course_slug}")
        course = get_object_or_404(Course, slug=course_slug)
        
        # Check access
        has_access, _, _ = has_course_access(request.user, course)
        if not has_access:
            logger.warning(f"[EXAM SUBMIT] Access denied for {request.user.username}")
            from django.contrib import messages
            messages.error(request, 'You do not have access to this course.')
            return redirect('student_dashboard')
        
        # Check if exam exists
        if not hasattr(course, 'exam'):
            logger.warning(f"[EXAM SUBMIT] No exam found for course {course_slug}")
            from django.contrib import messages
            messages.error(request, 'No exam available for this course.')
            return redirect('student_course_progress', course_slug=course_slug)
        
        exam = course.exam
        
        # Check eligibility (quick check)
        eligible, reason, missing = check_exam_eligibility(request.user, course)
        if not eligible:
            logger.warning(f"[EXAM SUBMIT] Not eligible: {reason}")
            from django.contrib import messages
            messages.warning(request, f'Not eligible to take exam: {reason}')
            return redirect('student_course_progress', course_slug=course_slug)
        
        logger.info(f"[EXAM SUBMIT] Validation complete, starting answer collection")
        
        # Get questions (optimized query)
        questions = exam.questions.all().order_by('order', 'id').only('id', 'correct_option', 'order')
        
        # Collect answers (fast operation)
        answers = {}
        for question in questions:
            answer = request.POST.get(f'question_{question.id}')
            if answer:
                answers[str(question.id)] = answer
        
        logger.info(f"[EXAM SUBMIT] Collected {len(answers)} answers out of {questions.count()} questions")
        
        # Calculate score (fast operation)
        score, correct_count, total_count = calculate_exam_score(exam, answers)
        passed = score >= exam.passing_score
        
        logger.info(f"[EXAM SUBMIT] Score calculated: {score:.1f}% (passed: {passed})")
        
        # Calculate time taken from client or use default
        time_taken_seconds = None
        client_time = request.POST.get('time_taken_seconds')
        if client_time:
            try:
                time_taken_seconds = int(client_time)
            except (ValueError, TypeError):
                pass
        
        # Get exam start time if available (for server-side calculation)
        exam_start_time = request.POST.get('exam_start_time')
        if exam_start_time:
            try:
                from datetime import datetime
                start_dt = datetime.fromisoformat(exam_start_time.replace('Z', '+00:00'))
                if timezone.is_aware(start_dt):
                    elapsed = (timezone.now() - start_dt).total_seconds()
                    time_taken_seconds = int(elapsed)
                    logger.info(f"[EXAM SUBMIT] Server-calculated time: {time_taken_seconds}s")
            except Exception as e:
                logger.warning(f"[EXAM SUBMIT] Could not parse start time: {e}")
        
        logger.info(f"[EXAM SUBMIT] Starting DB write")
        
        # Create exam attempt (fast DB operation)
        completed_at = timezone.now()
        attempt = ExamAttempt.objects.create(
            user=request.user,
            exam=exam,
            score=score,
            passed=passed,
            answers=answers,
            completed_at=completed_at,
            time_taken_seconds=time_taken_seconds,  # Will be recalculated below if needed
            is_final=passed
        )
        
        # Calculate time_taken_seconds from started_at -> completed_at (server-side truth)
        if attempt.started_at and completed_at:
            server_calculated_time = int((completed_at - attempt.started_at).total_seconds())
            # Use server-calculated time if client time is missing or significantly different
            if not time_taken_seconds or abs(server_calculated_time - time_taken_seconds) > 60:
                attempt.time_taken_seconds = server_calculated_time
                attempt.save(update_fields=['time_taken_seconds'])
                logger.info(f"[EXAM SUBMIT] Server-calculated time: {server_calculated_time}s (client: {time_taken_seconds}s)")
        
        logger.info(f"[EXAM SUBMIT] ExamAttempt created: ID {attempt.id}, time: {attempt.time_taken_seconds}s")
        
        # Issue certification asynchronously if passed (don't block request)
        if passed:
            try:
                from myApp.utils.certification import issue_certification
                logger.info(f"[EXAM SUBMIT] Issuing certification")
                issue_certification(request.user, course, attempt)
                logger.info(f"[EXAM SUBMIT] Certification issued")
                from django.contrib import messages
                messages.success(request, f'Congratulations! You passed the exam with {score:.1f}%. Your certification has been issued.')
            except Exception as e:
                logger.error(f"[EXAM SUBMIT] Certification issuance failed: {e}", exc_info=True)
                # Don't fail the request if certification fails
                from django.contrib import messages
                messages.success(request, f'Congratulations! You passed the exam with {score:.1f}%.')
        else:
            from django.contrib import messages
            messages.warning(request, f'Exam score: {score:.1f}%. Required: {exam.passing_score}%. You can retake the exam.')
        
        total_time = (timezone.now() - start_time).total_seconds()
        logger.info(f"[EXAM SUBMIT] Request completed in {total_time:.2f}s, redirecting to results")
        
        return redirect('student_exam_results', course_slug=course_slug)
        
    except Exception as e:
        logger.error(f"[EXAM SUBMIT] Error processing exam submission: {e}", exc_info=True)
        from django.contrib import messages
        messages.error(request, 'An error occurred while submitting your exam. Please try again or contact support.')
        return redirect('student_course_progress', course_slug=course_slug)


@login_required
def student_exam_results(request, course_slug):
    """Display exam results and history"""
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check access
    has_access, _, _ = has_course_access(request.user, course)
    if not has_access:
        from django.contrib import messages
        messages.error(request, 'You do not have access to this course.')
        return redirect('student_dashboard')
    
    # Check if exam exists
    if not hasattr(course, 'exam'):
        from django.contrib import messages
        messages.error(request, 'No exam available for this course.')
        return redirect('student_course_progress', course_slug=course_slug)
    
    exam = course.exam
    
    # Get all attempts
    attempts = ExamAttempt.objects.filter(
        user=request.user,
        exam=exam
    ).order_by('-completed_at')
    
    # Get certification if exists
    certification = None
    try:
        certification = Certification.objects.get(user=request.user, course=course)
    except Certification.DoesNotExist:
        pass
    
    # Check eligibility for retake
    eligible, reason, missing = check_exam_eligibility(request.user, course)
    
    context = {
        'course': course,
        'exam': exam,
        'attempts': attempts,
        'certification': certification,
        'eligible': eligible,
        'eligibility_reason': reason,
    }
    return render(request, 'student/exam_results.html', context)

