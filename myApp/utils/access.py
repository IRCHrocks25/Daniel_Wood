"""
Access Control Utility Functions

Core principle: "Access is a thing, not a side effect"
Every access is explicitly tracked with full audit trail.
"""
from django.utils import timezone
from django.db.models import Q
from myApp.models import CourseAccess, Course, BundlePurchase, Cohort, CourseEnrollment


def has_course_access(user, course):
    """
    Check if user has active access to a course.
    
    Returns:
        tuple: (has_access: bool, access_record: CourseAccess or None, reason: str)
    """
    if not user.is_authenticated:
        return False, None, "User not authenticated"
    
    # Check for active CourseAccess records
    access_records = CourseAccess.objects.filter(user=user, course=course)
    
    for access in access_records:
        if access.is_active():
            return True, access, f"Access via {access.get_source_display()}"
    
    # Check if course is publicly accessible (no access required)
    if course.visibility == 'public' and course.enrollment_method == 'open':
        return True, None, "Public course"
    
    # Check if user is enrolled (legacy support)
    if CourseEnrollment.objects.filter(user=user, course=course).exists():
        # Create access record if it doesn't exist
        access, created = CourseAccess.objects.get_or_create(
            user=user,
            course=course,
            access_type='manual',
            defaults={
                'status': 'unlocked',
                'notes': 'Auto-created from enrollment'
            }
        )
        if created or access.is_active():
            return True, access, "Access via enrollment"
    
    return False, None, "No active access found"


def grant_course_access(user, course, access_type='manual', granted_by=None, 
                       expires_at=None, bundle_purchase=None, cohort=None, 
                       purchase_id='', notes=''):
    """
    Grant course access to a user.
    
    Args:
        user: User to grant access to
        course: Course to grant access for
        access_type: Type of access ('purchase', 'manual', 'cohort', 'subscription', 'bundle')
        granted_by: Admin user granting access (optional)
        expires_at: Expiration datetime (optional)
        bundle_purchase: BundlePurchase object if access via bundle (optional)
        cohort: Cohort object if access via cohort (optional)
        purchase_id: External purchase ID (optional)
        notes: Additional notes for audit trail
    
    Returns:
        CourseAccess: Created access record
    """
    access = CourseAccess.objects.create(
        user=user,
        course=course,
        access_type=access_type,
        status='unlocked',
        granted_by=granted_by,
        expires_at=expires_at,
        bundle_purchase=bundle_purchase,
        cohort=cohort,
        purchase_id=purchase_id,
        notes=notes
    )
    return access


def revoke_course_access(user, course, revoked_by, reason='', notes=''):
    """
    Revoke course access for a user.
    
    Args:
        user: User to revoke access from
        course: Course to revoke access for
        revoked_by: Admin user revoking access
        reason: Reason for revocation
        notes: Additional notes
    
    Returns:
        CourseAccess: Updated access record (or None if no access found)
    """
    access_records = CourseAccess.objects.filter(
        user=user, 
        course=course, 
        status='unlocked'
    )
    
    updated_records = []
    for access in access_records:
        access.status = 'revoked'
        access.revoked_at = timezone.now()
        access.revoked_by = revoked_by
        access.revocation_reason = reason
        access.notes = f"{access.notes}\nRevoked: {notes}" if access.notes else f"Revoked: {notes}"
        access.save()
        updated_records.append(access)
    
    return updated_records[0] if updated_records else None


def get_user_accessible_courses(user):
    """
    Get all courses that user has active access to.
    Uses the same logic as has_course_access() to ensure consistency.
    
    Returns:
        QuerySet: Courses with active access
    """
    if not user.is_authenticated:
        return Course.objects.none()
    
    accessible_course_ids = set()
    
    # 1. Courses with active CourseAccess records
    active_access = CourseAccess.objects.filter(
        user=user,
        status='unlocked'
    ).exclude(
        expires_at__lt=timezone.now()
    )
    accessible_course_ids.update(active_access.values_list('course_id', flat=True))
    
    # 2. Courses with CourseEnrollment (legacy support)
    enrollments = CourseEnrollment.objects.filter(user=user)
    accessible_course_ids.update(enrollments.values_list('course_id', flat=True))
    
    # 3. Public courses with open enrollment
    public_courses = Course.objects.filter(
        visibility='public',
        enrollment_method='open',
        status='active'
    )
    accessible_course_ids.update(public_courses.values_list('id', flat=True))
    
    # 4. Courses where user has progress (if they can view it, they have access)
    from myApp.models import UserProgress
    progress_courses = UserProgress.objects.filter(
        user=user
    ).values_list('lesson__course_id', flat=True).distinct()
    accessible_course_ids.update(progress_courses)
    
    return Course.objects.filter(id__in=accessible_course_ids)


def get_courses_by_visibility(user):
    """
    Get courses categorized by visibility and access.
    
    Returns:
        dict: {
            'my_courses': QuerySet of courses with access,
            'available_to_unlock': QuerySet of courses available but not accessed,
            'not_available': QuerySet of courses not available
        }
    """
    if not user.is_authenticated:
        return {
            'my_courses': Course.objects.none(),
            'available_to_unlock': Course.objects.filter(visibility='public', status='active'),
            'not_available': Course.objects.exclude(visibility='public').exclude(status='active')
        }
    
    # Get courses with active access
    my_courses = get_user_accessible_courses(user)
    my_course_ids = list(my_courses.values_list('id', flat=True))
    
    # Get all active courses
    all_active = Course.objects.filter(status='active')
    
    # Available to unlock: active courses not in my_courses but visible
    available = all_active.exclude(id__in=my_course_ids).filter(
        visibility__in=['public', 'members_only']
    )
    
    # Not available: hidden/private or locked courses
    not_available = Course.objects.filter(
        Q(visibility__in=['hidden', 'private']) | 
        Q(status__in=['locked', 'coming_soon'])
    ).exclude(id__in=my_course_ids)
    
    return {
        'my_courses': my_courses,
        'available_to_unlock': available,
        'not_available': not_available
    }


def check_course_prerequisites(user, course):
    """
    Check if user has completed prerequisite courses.
    
    Returns:
        tuple: (met: bool, missing_prerequisites: list)
    """
    if not course.prerequisite_courses.exists():
        return True, []
    
    prerequisites = course.prerequisite_courses.all()
    missing = []
    
    for prereq in prerequisites:
        # Check if course is completed
        from myApp.models import UserProgress
        lessons = prereq.lesson_set.all()
        if not lessons.exists():
            continue
        
        completed_lessons = UserProgress.objects.filter(
            user=user,
            lesson__course=prereq,
            completed=True
        ).count()
        
        if completed_lessons < lessons.count():
            missing.append(prereq)
    
    return len(missing) == 0, missing


def grant_bundle_access(user, bundle_purchase):
    """
    Grant access to all courses in a bundle.
    
    Args:
        user: User who purchased bundle
        bundle_purchase: BundlePurchase object
    
    Returns:
        list: Created CourseAccess records
    """
    bundle = bundle_purchase.bundle
    courses = bundle.courses.all()
    
    # If pick-your-own bundle, use selected courses
    if bundle.bundle_type == 'pick_your_own' and bundle_purchase.selected_courses.exists():
        courses = bundle_purchase.selected_courses.all()
    
    access_records = []
    for course in courses:
        access, created = CourseAccess.objects.get_or_create(
            user=user,
            course=course,
            access_type='bundle',
            bundle_purchase=bundle_purchase,
            defaults={
                'status': 'unlocked',
                'purchase_id': bundle_purchase.purchase_id,
                'notes': f'Access via bundle purchase: {bundle.name}'
            }
        )
        if created:
            access_records.append(access)
    
    return access_records

