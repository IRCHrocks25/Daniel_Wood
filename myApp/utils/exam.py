"""
Exam Utility Functions
"""
from django.utils import timezone
from datetime import timedelta
from myApp.models import Course, Exam, ExamAttempt, UserProgress, CourseAccess, CourseEnrollment


def check_exam_eligibility(user, course):
    """
    Check if user is eligible to take the exam for a course.
    
    Returns:
        tuple: (eligible: bool, reason: str, missing_items: list)
    """
    if not user.is_authenticated:
        return False, "User not authenticated", []
    
    # Check if exam exists
    if not hasattr(course, 'exam'):
        return False, "No exam exists for this course", []
    
    exam = course.exam
    
    if not exam.is_active:
        return False, "Exam is not active", []
    
    # Check course access
    from myApp.utils.access import has_course_access
    has_access, _, _ = has_course_access(user, course)
    if not has_access:
        return False, "No access to this course", []
    
    # Check if all lessons are completed
    lessons = course.lesson_set.all()
    if lessons.exists():
        completed_lessons = UserProgress.objects.filter(
            user=user,
            lesson__course=course,
            completed=True
        ).count()
        if completed_lessons < lessons.count():
            missing = lessons.count() - completed_lessons
            return False, f"{missing} lesson(s) not completed", []
    
    # Check exam_unlock_days
    if course.exam_unlock_days > 0:
        # Get enrollment date
        enrollment = CourseEnrollment.objects.filter(user=user, course=course).first()
        if not enrollment:
            # Check CourseAccess
            access = CourseAccess.objects.filter(user=user, course=course, status='unlocked').first()
            if access:
                enrollment_date = access.granted_at
            else:
                return False, "No enrollment found", []
        else:
            enrollment_date = enrollment.enrolled_at
        
        days_since_enrollment = (timezone.now() - enrollment_date).days
        if days_since_enrollment < course.exam_unlock_days:
            days_remaining = course.exam_unlock_days - days_since_enrollment
            return False, f"Exam unlocks in {days_remaining} day(s)", []
    
    # Check max attempts
    if exam.max_attempts > 0:
        attempt_count = ExamAttempt.objects.filter(user=user, exam=exam).count()
        if attempt_count >= exam.max_attempts:
            return False, f"Maximum attempts ({exam.max_attempts}) reached", []
    
    return True, "Eligible", []


def calculate_exam_score(exam, answers):
    """
    Calculate exam score based on answers.
    
    Args:
        exam: Exam object
        answers: dict of {question_id: 'A'/'B'/'C'/'D'}
    
    Returns:
        tuple: (score: float, correct_count: int, total_count: int)
    """
    questions = exam.questions.all().order_by('order')
    total = questions.count()
    correct = 0
    
    for question in questions:
        user_answer = answers.get(str(question.id))
        if user_answer == question.correct_option:
            correct += 1
    
    score = (correct / total * 100) if total > 0 else 0
    return score, correct, total

