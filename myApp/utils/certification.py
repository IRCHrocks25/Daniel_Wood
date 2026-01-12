"""
Certification Utility Functions
"""
from django.utils import timezone
from django.conf import settings
from myApp.models import Certification, ExamAttempt


def issue_certification(user, course, exam_attempt):
    """
    Issue a certification to a user after passing an exam.
    
    Args:
        user: User who passed the exam
        course: Course for which certification is issued
        exam_attempt: ExamAttempt object (must be passed=True)
    
    Returns:
        Certification: Created or updated certification object
    """
    if not exam_attempt.passed:
        raise ValueError("Cannot issue certification for failed exam attempt")
    
    # Get or create certification
    certification, created = Certification.objects.get_or_create(
        user=user,
        course=course,
        defaults={
            'status': 'passed',
            'passing_exam_attempt': exam_attempt,
            'issued_at': timezone.now(),
        }
    )
    
    # If already exists but not passed, update it
    if not created and certification.status != 'passed':
        certification.status = 'passed'
        certification.passing_exam_attempt = exam_attempt
        certification.issued_at = timezone.now()
        certification.save()
    
    # If Accredible is configured, create certificate there
    if course.is_accredible_certified and settings.ACCREDIBLE_API_KEY:
        try:
            accredible_id, accredible_url = create_accredible_certificate(user, course, exam_attempt)
            certification.accredible_certificate_id = accredible_id
            certification.accredible_certificate_url = accredible_url
            certification.save()
        except Exception as e:
            # Log error but don't fail certification issuance
            print(f"Accredible certificate creation failed: {str(e)}")
    
    return certification


def create_accredible_certificate(user, course, exam_attempt):
    """
    Create a certificate via Accredible API.
    
    Args:
        user: User to issue certificate for
        course: Course name
        exam_attempt: ExamAttempt object
    
    Returns:
        tuple: (certificate_id: str, certificate_url: str)
    
    Note: This is a stub implementation. Replace with actual Accredible API calls.
    """
    # TODO: Implement actual Accredible API integration
    # For now, return placeholder values
    import hashlib
    cert_id = hashlib.md5(f"{user.id}_{course.id}_{exam_attempt.id}".encode()).hexdigest()
    cert_url = f"https://accredible.com/cert/{cert_id}"
    
    return cert_id, cert_url

