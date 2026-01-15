"""
Admin Dashboard Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import timedelta
import json

from .models import (
    Course, Lesson, Module, LessonQuiz, LessonQuizQuestion, LessonQuizAttempt, UserProgress,
    CourseEnrollment, FavoriteCourse, Certification, Exam, ExamQuestion, ExamAttempt,
    CourseAccess, Bundle, BundlePurchase, Cohort, CohortMember, User
)
from .utils.access import grant_course_access, revoke_course_access, grant_bundle_access
from .utils.exam import calculate_exam_score


def is_staff(user):
    """Check if user is staff"""
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_staff)
def dashboard_home(request):
    """Admin dashboard overview"""
    # Quick stats
    total_students = User.objects.filter(is_staff=False).count()
    active_students = User.objects.filter(
        is_staff=False,
        userprogress__last_accessed__gte=timezone.now() - timedelta(days=30)
    ).distinct().count()
    
    new_students = User.objects.filter(
        is_staff=False,
        date_joined__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    total_enrollments = CourseEnrollment.objects.count()
    total_accesses = CourseAccess.objects.filter(status='unlocked').count()
    total_progress = UserProgress.objects.count()
    total_certifications = Certification.objects.filter(status='passed').count()
    
    # Recent activity (last 20 items)
    recent_activities = []
    
    # Recent lesson completions
    recent_completions = UserProgress.objects.filter(
        completed_at__isnull=False
    ).order_by('-completed_at')[:10]
    for completion in recent_completions:
        recent_activities.append({
            'type': 'lesson_completion',
            'user': completion.user,
            'content': f"Completed: {completion.lesson.title}",
            'timestamp': completion.completed_at,
            'url': f"/dashboard/students/{completion.user.id}/"
        })
    
    # Recent quiz attempts
    recent_quizzes = LessonQuizAttempt.objects.order_by('-completed_at')[:5]
    for quiz in recent_quizzes:
        recent_activities.append({
            'type': 'quiz_attempt',
            'user': quiz.user,
            'content': f"Quiz: {quiz.quiz.lesson.title} - {quiz.score:.1f}%",
            'timestamp': quiz.completed_at,
            'url': f"/dashboard/students/{quiz.user.id}/"
        })
    
    # Recent certifications
    recent_certs = Certification.objects.filter(
        status='passed',
        issued_at__isnull=False
    ).order_by('-issued_at')[:5]
    for cert in recent_certs:
        recent_activities.append({
            'type': 'certification',
            'user': cert.user,
            'content': f"Certified: {cert.course.name}",
            'timestamp': cert.issued_at,
            'url': f"/dashboard/students/{cert.user.id}/"
        })
    
    # Sort by timestamp
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activities = recent_activities[:20]
    
    context = {
        'total_students': total_students,
        'active_students': active_students,
        'new_students': new_students,
        'total_enrollments': total_enrollments,
        'total_accesses': total_accesses,
        'total_progress': total_progress,
        'total_certifications': total_certifications,
        'recent_activities': recent_activities,
    }
    return render(request, 'dashboard/home.html', context)


@login_required
@user_passes_test(is_staff)
def dashboard_analytics(request):
    """Comprehensive analytics dashboard"""
    # Student Analytics
    total_students = User.objects.filter(is_staff=False).count()
    active_students = User.objects.filter(
        is_staff=False,
        userprogress__last_accessed__gte=timezone.now() - timedelta(days=30)
    ).distinct().count()
    new_students = User.objects.filter(
        is_staff=False,
        date_joined__gte=timezone.now() - timedelta(days=7)
    ).count()
    inactive_students = User.objects.filter(
        is_staff=False,
        userprogress__last_accessed__lt=timezone.now() - timedelta(days=90)
    ).distinct().count()
    
    # Enrollment Analytics
    total_enrollments = CourseEnrollment.objects.count()
    enrollments_30d = CourseEnrollment.objects.filter(
        enrolled_at__gte=timezone.now() - timedelta(days=30)
    ).count()
    enrollments_7d = CourseEnrollment.objects.filter(
        enrolled_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    # Enrollment trends (last 30 days)
    enrollment_dates = []
    enrollment_counts = []
    for i in range(30, -1, -1):
        date = timezone.now() - timedelta(days=i)
        count = CourseEnrollment.objects.filter(
            enrolled_at__date=date.date()
        ).count()
        enrollment_dates.append(date.strftime('%m/%d'))
        enrollment_counts.append(count)
    
    # Access Analytics
    active_access = CourseAccess.objects.filter(status='unlocked').count()
    
    # Progress Analytics
    total_progress_updates = UserProgress.objects.count()
    progress_updates_7d = UserProgress.objects.filter(
        last_accessed__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    # Certification Analytics
    total_certs = Certification.objects.filter(status='passed').count()
    certs_30d = Certification.objects.filter(
        issued_at__gte=timezone.now() - timedelta(days=30),
        status='passed'
    ).count()
    
    # Certification trends (last 30 days)
    cert_dates = []
    cert_counts = []
    for i in range(30, -1, -1):
        date = timezone.now() - timedelta(days=i)
        count = Certification.objects.filter(
            issued_at__date=date.date(),
            status='passed'
        ).count()
        cert_dates.append(date.strftime('%m/%d'))
        cert_counts.append(count)
    
    # Course Performance
    course_performance = Course.objects.annotate(
        enrollment_count=Count('courseenrollment'),
        access_count=Count('courseaccess', filter=Q(courseaccess__status='unlocked')),
        progress_count=Count('lesson__userprogress'),
        completion_count=Count('lesson__userprogress', filter=Q(lesson__userprogress__completed=True)),
    ).order_by('-enrollment_count')
    
    # Calculate completion rates
    for course in course_performance:
        if course.progress_count > 0:
            course.completion_rate = (course.completion_count / course.progress_count) * 100
        else:
            course.completion_rate = 0
    
    # Top 5 courses by enrollment
    top_courses = course_performance[:5]
    
    # Most active students (last 7 days)
    active_students_list = User.objects.filter(
        is_staff=False,
        userprogress__last_accessed__gte=timezone.now() - timedelta(days=7)
    ).annotate(
        progress_count=Count('userprogress', filter=Q(userprogress__last_accessed__gte=timezone.now() - timedelta(days=7)))
    ).order_by('-progress_count')[:10]
    
    # Completion rate
    total_lessons_started = UserProgress.objects.filter(status__in=['in_progress', 'completed']).count()
    total_lessons_completed = UserProgress.objects.filter(completed=True).count()
    completion_rate = (total_lessons_completed / total_lessons_started * 100) if total_lessons_started > 0 else 0
    
    context = {
        # Student Analytics
        'total_students': total_students,
        'active_students': active_students,
        'new_students': new_students,
        'inactive_students': inactive_students,
        
        # Enrollment Analytics
        'total_enrollments': total_enrollments,
        'enrollments_30d': enrollments_30d,
        'enrollments_7d': enrollments_7d,
        'enrollment_dates': json.dumps(enrollment_dates),
        'enrollment_counts': json.dumps(enrollment_counts),
        
        # Access Analytics
        'active_access': active_access,
        
        # Progress Analytics
        'total_progress_updates': total_progress_updates,
        'progress_updates_7d': progress_updates_7d,
        
        # Certification Analytics
        'total_certs': total_certs,
        'certs_30d': certs_30d,
        'cert_dates': json.dumps(cert_dates),
        'cert_counts': json.dumps(cert_counts),
        
        # Course Performance
        'course_performance': course_performance,
        'top_courses': top_courses,
        'active_students_list': active_students_list,
        'completion_rate': round(completion_rate, 2),
    }
    return render(request, 'dashboard/analytics.html', context)


@login_required
@user_passes_test(is_staff)
def dashboard_courses(request):
    """List all courses"""
    courses = Course.objects.all().order_by('-created_at')
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        courses = courses.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(slug__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        courses = courses.filter(status=status_filter)
    
    context = {
        'courses': courses,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'dashboard/courses.html', context)


@login_required
@user_passes_test(is_staff)
def dashboard_add_course(request):
    """Create new course"""
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        course_type = request.POST.get('course_type', 'sprint')
        status = request.POST.get('status', 'active')
        description = request.POST.get('description', '')
        short_description = request.POST.get('short_description', '')
        
        # Create course
        course = Course.objects.create(
            name=name,
            slug=slug,
            course_type=course_type,
            status=status,
            description=description,
            short_description=short_description,
        )
        
        messages.success(request, f'Course "{course.name}" created successfully.')
        return redirect('dashboard_course_detail', course_slug=course.slug)
    
    return render(request, 'dashboard/add_course.html')


@login_required
@user_passes_test(is_staff)
def dashboard_course_detail(request, course_slug):
    """Edit course details"""
    course = get_object_or_404(Course, slug=course_slug)
    
    if request.method == 'POST':
        course.name = request.POST.get('name', course.name)
        course.slug = request.POST.get('slug', course.slug)
        course.course_type = request.POST.get('course_type', course.course_type)
        course.status = request.POST.get('status', course.status)
        course.description = request.POST.get('description', course.description)
        course.short_description = request.POST.get('short_description', course.short_description)
        course.coach_name = request.POST.get('coach_name', course.coach_name)
        course.is_subscribers_only = request.POST.get('is_subscribers_only') == 'on'
        course.is_accredible_certified = request.POST.get('is_accredible_certified') == 'on'
        course.has_asset_templates = request.POST.get('has_asset_templates') == 'on'
        
        # Access control fields
        course.visibility = request.POST.get('visibility', course.visibility)
        course.enrollment_method = request.POST.get('enrollment_method', course.enrollment_method)
        course.access_duration_type = request.POST.get('access_duration_type', course.access_duration_type)
        
        if request.FILES.get('thumbnail'):
            course.thumbnail = request.FILES['thumbnail']
        
        course.save()
        messages.success(request, 'Course updated successfully.')
        return redirect('dashboard_course_detail', course_slug=course.slug)
    
    # Get lessons and modules
    modules = Module.objects.filter(course=course).order_by('order')
    lessons = Lesson.objects.filter(course=course).order_by('order')
    
    context = {
        'course': course,
        'modules': modules,
        'lessons': lessons,
    }
    return render(request, 'dashboard/course_detail.html', context)


@login_required
@user_passes_test(is_staff)
@require_POST
def dashboard_delete_course(request, course_slug):
    """Delete course"""
    course = get_object_or_404(Course, slug=course_slug)
    course_name = course.name
    course.delete()
    messages.success(request, f'Course "{course_name}" deleted successfully.')
    return redirect('dashboard_courses')


@login_required
@user_passes_test(is_staff)
def dashboard_students(request):
    """List all students"""
    students = User.objects.filter(is_staff=False).order_by('-date_joined')
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Pagination (simple version)
    from django.core.paginator import Paginator
    paginator = Paginator(students, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'students': page_obj,
        'search_query': search_query,
    }
    return render(request, 'dashboard/students.html', context)


@login_required
@user_passes_test(is_staff)
def dashboard_student_detail(request, user_id, course_slug=None):
    """Detailed student view"""
    student = get_object_or_404(User, id=user_id, is_staff=False)
    
    # Get all courses
    all_courses = Course.objects.all().order_by('name')
    
    # Get student's course accesses
    accesses = CourseAccess.objects.filter(user=student).order_by('-granted_at')
    
    # Get student's progress
    progress = UserProgress.objects.filter(user=student).order_by('-last_accessed')
    
    # Get enrollments
    enrollments = CourseEnrollment.objects.filter(user=student).order_by('-enrolled_at')
    
    # Get certifications
    certifications = Certification.objects.filter(user=student).order_by('-issued_at')
    
    # Selected course detail
    selected_course = None
    course_progress = None
    if course_slug:
        selected_course = get_object_or_404(Course, slug=course_slug)
        course_progress = UserProgress.objects.filter(
            user=student,
            lesson__course=selected_course
        )
    
    # Cohorts
    cohorts = Cohort.objects.filter(members__user=student)
    all_cohorts = Cohort.objects.all().order_by('name')
    
    context = {
        'student': student,
        'all_courses': all_courses,
        'accesses': accesses,
        'progress': progress[:20],  # Recent 20
        'enrollments': enrollments,
        'certifications': certifications,
        'selected_course': selected_course,
        'course_progress': course_progress,
        'cohorts': cohorts,
        'all_cohorts': all_cohorts,
    }
    return render(request, 'dashboard/student_detail.html', context)


@login_required
@user_passes_test(is_staff)
@require_POST
def grant_course_access_view(request, user_id):
    """Grant manual course access"""
    student = get_object_or_404(User, id=user_id, is_staff=False)
    course_id = request.POST.get('course_id')
    course = get_object_or_404(Course, id=course_id)
    
    access = grant_course_access(
        user=student,
        course=course,
        access_type='manual',
        granted_by=request.user,
        notes=f'Granted via admin dashboard by {request.user.username}'
    )
    
    messages.success(request, f'Access granted to {course.name} for {student.username}.')
    return redirect('dashboard_student_detail', user_id=user_id)


@login_required
@user_passes_test(is_staff)
@require_POST
def revoke_course_access_view(request, user_id):
    """Revoke course access"""
    student = get_object_or_404(User, id=user_id, is_staff=False)
    course_id = request.POST.get('course_id')
    course = get_object_or_404(Course, id=course_id)
    reason = request.POST.get('reason', '')
    
    revoke_course_access(
        user=student,
        course=course,
        revoked_by=request.user,
        reason=reason,
        notes=f'Revoked via admin dashboard by {request.user.username}'
    )
    
    messages.success(request, f'Access revoked for {course.name} for {student.username}.')
    return redirect('dashboard_student_detail', user_id=user_id)


@login_required
@user_passes_test(is_staff)
@login_required
@user_passes_test(is_staff)
def dashboard_lessons(request):
    """List all lessons"""
    lessons = Lesson.objects.select_related('course', 'module').all().order_by('-created_at')
    
    # Filter by course
    course_filter = request.GET.get('course', '')
    if course_filter:
        lessons = lessons.filter(course_id=course_filter)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        lessons = lessons.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(course__name__icontains=search_query)
        )
    
    # Get all courses for filter dropdown
    all_courses = Course.objects.all().order_by('name')
    
    context = {
        'lessons': lessons,
        'search_query': search_query,
        'course_filter': course_filter,
        'all_courses': all_courses,
    }
    return render(request, 'dashboard/lessons.html', context)


@login_required
@user_passes_test(is_staff)
def dashboard_add_lesson(request):
    """Add a new lesson"""
    if request.method == 'POST':
        try:
            course_id = request.POST.get('course')
            course = get_object_or_404(Course, id=course_id)
            
            # Check if slug already exists for this course
            slug = request.POST.get('slug', '').strip()
            if Lesson.objects.filter(course=course, slug=slug).exists():
                messages.error(request, f'A lesson with slug "{slug}" already exists in this course. Please use a different slug.')
                courses = Course.objects.all().order_by('name')
                modules = Module.objects.select_related('course').all().order_by('course__name', 'order')
                import json
                modules_json = json.dumps([{'id': m.id, 'course_id': m.course.id, 'name': m.name} for m in modules])
                return render(request, 'dashboard/add_lesson.html', {
                    'courses': courses,
                    'modules_json': modules_json,
                })
            
            # Parse content blocks JSON from Editor.js
            import json
            content_data = {}
            try:
                content_json = request.POST.get('content', '{}')
                if content_json:
                    content_data = json.loads(content_json)
            except (json.JSONDecodeError, TypeError):
                pass  # Keep empty content if JSON is invalid
            
            # Create lesson
            lesson = Lesson.objects.create(
                course=course,
                title=request.POST.get('title'),
                slug=slug,
                description=request.POST.get('description', ''),
                content=content_data,
                video_url=request.POST.get('video_url', ''),
                video_duration=int(request.POST.get('video_duration', 0) or 0),
                order=int(request.POST.get('order', 0) or 0),
                workbook_url=request.POST.get('workbook_url', ''),
                resources_url=request.POST.get('resources_url', ''),
                lesson_type=request.POST.get('lesson_type', 'video'),
                vimeo_url=request.POST.get('vimeo_url', ''),
                google_drive_url=request.POST.get('google_drive_url', ''),
            )
            
            # Handle module assignment
            module_id = request.POST.get('module')
            if module_id:
                try:
                    module = Module.objects.get(id=module_id, course=course)
                    lesson.module = module
                    lesson.save()
                except Module.DoesNotExist:
                    pass
            
            messages.success(request, f'Lesson "{lesson.title}" created successfully!')
            return redirect('dashboard_lessons')
        except Exception as e:
            messages.error(request, f'Error creating lesson: {str(e)}')
    
    # Get courses and modules for form
    courses = Course.objects.all().order_by('name')
    modules = Module.objects.select_related('course').all().order_by('course__name', 'order')
    
    # Prepare modules data for JavaScript
    import json
    modules_json = json.dumps([{'id': m.id, 'course_id': m.course.id, 'name': m.name} for m in modules])
    
    # Empty content blocks for new lesson
    content_json = "{}"
    
    context = {
        'courses': courses,
        'modules_json': modules_json,
        'content_json': content_json,
    }
    return render(request, 'dashboard/add_lesson.html', context)


@login_required
@user_passes_test(is_staff)
def dashboard_edit_lesson(request, lesson_id):
    """Edit a lesson"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    if request.method == 'POST':
        try:
            # Check if slug already exists for this course (excluding current lesson)
            slug = request.POST.get('slug', '').strip()
            if Lesson.objects.filter(course=lesson.course, slug=slug).exclude(id=lesson.id).exists():
                messages.error(request, f'A lesson with slug "{slug}" already exists in this course. Please use a different slug.')
                modules = Module.objects.filter(course=lesson.course).order_by('order')
                return render(request, 'dashboard/edit_lesson.html', {
                    'lesson': lesson,
                    'modules': modules,
                })
            
            lesson.title = request.POST.get('title')
            lesson.slug = slug
            lesson.description = request.POST.get('description', '')
            
            # Parse content blocks JSON from Editor.js
            import json
            try:
                content_json = request.POST.get('content', '{}')
                if content_json:
                    lesson.content = json.loads(content_json)
            except (json.JSONDecodeError, TypeError):
                pass  # Keep existing content if JSON is invalid
            
            lesson.video_url = request.POST.get('video_url', '')
            lesson.video_duration = int(request.POST.get('video_duration', 0) or 0)
            lesson.order = int(request.POST.get('order', 0) or 0)
            lesson.workbook_url = request.POST.get('workbook_url', '')
            lesson.resources_url = request.POST.get('resources_url', '')
            lesson.lesson_type = request.POST.get('lesson_type', 'video')
            lesson.vimeo_url = request.POST.get('vimeo_url', '')
            lesson.google_drive_url = request.POST.get('google_drive_url', '')
            
            # Handle module assignment
            module_id = request.POST.get('module')
            if module_id:
                try:
                    module = Module.objects.get(id=module_id, course=lesson.course)
                    lesson.module = module
                except Module.DoesNotExist:
                    lesson.module = None
            else:
                lesson.module = None
            
            lesson.save()
            messages.success(request, f'Lesson "{lesson.title}" updated successfully!')
            return redirect('dashboard_lessons')
        except Exception as e:
            messages.error(request, f'Error updating lesson: {str(e)}')
    
    # Get modules for the lesson's course
    modules = Module.objects.filter(course=lesson.course).order_by('order')
    
    # Prepare content blocks JSON for Editor.js
    import json
    content_json = json.dumps(lesson.content) if lesson.content else "{}"
    
    context = {
        'lesson': lesson,
        'modules': modules,
        'content_json': content_json,
    }
    return render(request, 'dashboard/edit_lesson.html', context)


@login_required
@user_passes_test(is_staff)
@require_POST
def dashboard_delete_lesson(request, lesson_id):
    """Delete a lesson"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    lesson_title = lesson.title
    lesson.delete()
    messages.success(request, f'Lesson "{lesson_title}" deleted successfully!')
    return redirect('dashboard_lessons')


# ============================================
# QUIZ MANAGEMENT VIEWS
# ============================================

@login_required
@user_passes_test(is_staff)
def dashboard_add_quiz(request, lesson_id):
    """Create a quiz for a lesson"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    # Check if quiz already exists
    if hasattr(lesson, 'quiz'):
        messages.info(request, f'A quiz already exists for this lesson. You can edit it instead.')
        return redirect('dashboard_edit_quiz', quiz_id=lesson.quiz.id)
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        is_required = request.POST.get('is_required') == 'on'
        passing_score = int(request.POST.get('passing_score', 70) or 70)
        
        if not title:
            messages.error(request, 'Quiz title is required.')
        else:
            quiz = LessonQuiz.objects.create(
                lesson=lesson,
                title=title,
                description=description,
                is_required=is_required,
                passing_score=passing_score
            )
            messages.success(request, f'Quiz "{quiz.title}" created successfully!')
            return redirect('dashboard_edit_quiz', quiz_id=quiz.id)
    
    context = {
        'lesson': lesson,
    }
    return render(request, 'dashboard/add_quiz.html', context)


@login_required
@user_passes_test(is_staff)
def dashboard_edit_quiz(request, quiz_id):
    """Edit quiz details"""
    quiz = get_object_or_404(LessonQuiz, id=quiz_id)
    
    if request.method == 'POST':
        quiz.title = request.POST.get('title', '').strip()
        quiz.description = request.POST.get('description', '').strip()
        quiz.is_required = request.POST.get('is_required') == 'on'
        quiz.passing_score = int(request.POST.get('passing_score', 70) or 70)
        
        if not quiz.title:
            messages.error(request, 'Quiz title is required.')
        else:
            quiz.save()
            messages.success(request, 'Quiz updated successfully!')
            return redirect('dashboard_edit_quiz', quiz_id=quiz.id)
    
    # Get questions ordered by order field
    questions = quiz.questions.all().order_by('order', 'id')
    
    context = {
        'quiz': quiz,
        'lesson': quiz.lesson,
        'questions': questions,
    }
    return render(request, 'dashboard/edit_quiz.html', context)


@login_required
@user_passes_test(is_staff)
@require_POST
def dashboard_delete_quiz(request, quiz_id):
    """Delete a quiz"""
    quiz = get_object_or_404(LessonQuiz, id=quiz_id)
    lesson = quiz.lesson
    quiz_title = quiz.title
    quiz.delete()
    messages.success(request, f'Quiz "{quiz_title}" deleted successfully!')
    return redirect('dashboard_edit_lesson', lesson_id=lesson.id)


@login_required
@user_passes_test(is_staff)
def dashboard_add_quiz_question(request, quiz_id):
    """Add a question to a quiz"""
    quiz = get_object_or_404(LessonQuiz, id=quiz_id)
    
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        option_a = request.POST.get('option_a', '').strip()
        option_b = request.POST.get('option_b', '').strip()
        option_c = request.POST.get('option_c', '').strip()
        option_d = request.POST.get('option_d', '').strip()
        correct_option = request.POST.get('correct_option', 'A')
        order = int(request.POST.get('order', 0) or 0)
        
        if not text or not option_a or not option_b:
            messages.error(request, 'Question text and at least options A and B are required.')
        elif correct_option not in ['A', 'B', 'C', 'D']:
            messages.error(request, 'Invalid correct option selected.')
        else:
            question = LessonQuizQuestion.objects.create(
                quiz=quiz,
                text=text,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_option=correct_option,
                order=order
            )
            messages.success(request, 'Question added successfully!')
            return redirect('dashboard_edit_quiz', quiz_id=quiz.id)
    
    # Get next order number
    last_question = quiz.questions.all().order_by('-order').first()
    next_order = (last_question.order + 1) if last_question else 0
    
    context = {
        'quiz': quiz,
        'lesson': quiz.lesson,
        'next_order': next_order,
    }
    return render(request, 'dashboard/add_quiz_question.html', context)


@login_required
@user_passes_test(is_staff)
def dashboard_edit_quiz_question(request, question_id):
    """Edit a quiz question"""
    question = get_object_or_404(LessonQuizQuestion, id=question_id)
    quiz = question.quiz
    
    if request.method == 'POST':
        question.text = request.POST.get('text', '').strip()
        question.option_a = request.POST.get('option_a', '').strip()
        question.option_b = request.POST.get('option_b', '').strip()
        question.option_c = request.POST.get('option_c', '').strip()
        question.option_d = request.POST.get('option_d', '').strip()
        question.correct_option = request.POST.get('correct_option', 'A')
        question.order = int(request.POST.get('order', 0) or 0)
        
        if not question.text or not question.option_a or not question.option_b:
            messages.error(request, 'Question text and at least options A and B are required.')
        elif question.correct_option not in ['A', 'B', 'C', 'D']:
            messages.error(request, 'Invalid correct option selected.')
        else:
            question.save()
            messages.success(request, 'Question updated successfully!')
            return redirect('dashboard_edit_quiz', quiz_id=quiz.id)
    
    context = {
        'question': question,
        'quiz': quiz,
        'lesson': quiz.lesson,
    }
    return render(request, 'dashboard/edit_quiz_question.html', context)


@login_required
@user_passes_test(is_staff)
@require_POST
def dashboard_delete_quiz_question(request, question_id):
    """Delete a quiz question"""
    question = get_object_or_404(LessonQuizQuestion, id=question_id)
    quiz = question.quiz
    question.delete()
    messages.success(request, 'Question deleted successfully!')
    return redirect('dashboard_edit_quiz', quiz_id=quiz.id)


# ============================================
# EXAM MANAGEMENT VIEWS
# ============================================

@login_required
@user_passes_test(is_staff)
def dashboard_add_exam(request, course_slug):
    """Create an exam for a course"""
    course = get_object_or_404(Course, slug=course_slug)
    
    # Check if exam already exists
    if hasattr(course, 'exam'):
        messages.info(request, 'An exam already exists for this course. You can edit it instead.')
        return redirect('dashboard_edit_exam', exam_id=course.exam.id)
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        passing_score = int(request.POST.get('passing_score', 70) or 70)
        max_attempts = int(request.POST.get('max_attempts', 0) or 0)
        time_limit_minutes = request.POST.get('time_limit_minutes', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        
        if not title:
            messages.error(request, 'Exam title is required.')
        else:
            exam = Exam.objects.create(
                course=course,
                title=title,
                description=description,
                passing_score=passing_score,
                max_attempts=max_attempts if max_attempts > 0 else 0,
                time_limit_minutes=int(time_limit_minutes) if time_limit_minutes else None,
                is_active=is_active
            )
            messages.success(request, f'Exam "{exam.title}" created successfully!')
            return redirect('dashboard_edit_exam', exam_id=exam.id)
    
    context = {
        'course': course,
    }
    return render(request, 'dashboard/add_exam.html', context)


@login_required
@user_passes_test(is_staff)
def dashboard_edit_exam(request, exam_id):
    """Edit exam details"""
    exam = get_object_or_404(Exam, id=exam_id)
    course = exam.course
    
    if request.method == 'POST':
        exam.title = request.POST.get('title', '').strip()
        exam.description = request.POST.get('description', '').strip()
        exam.passing_score = int(request.POST.get('passing_score', 70) or 70)
        exam.max_attempts = int(request.POST.get('max_attempts', 0) or 0)
        time_limit_minutes = request.POST.get('time_limit_minutes', '').strip()
        exam.time_limit_minutes = int(time_limit_minutes) if time_limit_minutes else None
        exam.is_active = request.POST.get('is_active') == 'on'
        
        if not exam.title:
            messages.error(request, 'Exam title is required.')
        else:
            exam.save()
            messages.success(request, 'Exam updated successfully!')
            return redirect('dashboard_edit_exam', exam_id=exam.id)
    
    # Get questions ordered
    questions = exam.questions.all().order_by('order', 'id')
    
    # Get attempt statistics
    total_attempts = ExamAttempt.objects.filter(exam=exam).count()
    passed_attempts = ExamAttempt.objects.filter(exam=exam, passed=True).count()
    avg_score = ExamAttempt.objects.filter(exam=exam).aggregate(Avg('score'))['score__avg'] or 0
    
    context = {
        'exam': exam,
        'course': course,
        'questions': questions,
        'total_attempts': total_attempts,
        'passed_attempts': passed_attempts,
        'avg_score': round(avg_score, 1),
    }
    return render(request, 'dashboard/edit_exam.html', context)


@login_required
@user_passes_test(is_staff)
def dashboard_add_exam_question(request, exam_id):
    """Add a question to an exam"""
    exam = get_object_or_404(Exam, id=exam_id)
    
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        option_a = request.POST.get('option_a', '').strip()
        option_b = request.POST.get('option_b', '').strip()
        option_c = request.POST.get('option_c', '').strip()
        option_d = request.POST.get('option_d', '').strip()
        correct_option = request.POST.get('correct_option', 'A')
        order = int(request.POST.get('order', 0) or 0)
        
        if not text or not option_a or not option_b:
            messages.error(request, 'Question text and at least options A and B are required.')
        elif correct_option not in ['A', 'B', 'C', 'D']:
            messages.error(request, 'Invalid correct option selected.')
        else:
            question = ExamQuestion.objects.create(
                exam=exam,
                text=text,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_option=correct_option,
                order=order
            )
            messages.success(request, 'Question added successfully!')
            return redirect('dashboard_edit_exam', exam_id=exam.id)
    
    # Get next order number
    last_question = exam.questions.all().order_by('-order').first()
    next_order = (last_question.order + 1) if last_question else 0
    
    context = {
        'exam': exam,
        'course': exam.course,
        'next_order': next_order,
    }
    return render(request, 'dashboard/add_exam_question.html', context)


@login_required
@user_passes_test(is_staff)
def dashboard_edit_exam_question(request, question_id):
    """Edit an exam question"""
    question = get_object_or_404(ExamQuestion, id=question_id)
    exam = question.exam
    
    if request.method == 'POST':
        question.text = request.POST.get('text', '').strip()
        question.option_a = request.POST.get('option_a', '').strip()
        question.option_b = request.POST.get('option_b', '').strip()
        question.option_c = request.POST.get('option_c', '').strip()
        question.option_d = request.POST.get('option_d', '').strip()
        question.correct_option = request.POST.get('correct_option', 'A')
        question.order = int(request.POST.get('order', 0) or 0)
        
        if not question.text or not question.option_a or not question.option_b:
            messages.error(request, 'Question text and at least options A and B are required.')
        elif question.correct_option not in ['A', 'B', 'C', 'D']:
            messages.error(request, 'Invalid correct option selected.')
        else:
            question.save()
            messages.success(request, 'Question updated successfully!')
            return redirect('dashboard_edit_exam', exam_id=exam.id)
    
    context = {
        'question': question,
        'exam': exam,
        'course': exam.course,
    }
    return render(request, 'dashboard/edit_exam_question.html', context)


@login_required
@user_passes_test(is_staff)
@require_POST
def dashboard_delete_exam_question(request, question_id):
    """Delete an exam question"""
    question = get_object_or_404(ExamQuestion, id=question_id)
    exam = question.exam
    question.delete()
    messages.success(request, 'Question deleted successfully!')
    return redirect('dashboard_edit_exam', exam_id=exam.id)

