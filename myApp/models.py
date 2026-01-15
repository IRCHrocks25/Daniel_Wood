from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
import re


# Course Model
class Course(models.Model):
    COURSE_TYPE_CHOICES = [
        ('sprint', 'Sprint'),
        ('speaking', 'Speaking'),
        ('consultancy', 'Consultancy'),
        ('special', 'Special'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('locked', 'Locked'),
        ('coming_soon', 'Coming Soon'),
    ]
    
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('members_only', 'Members Only'),
        ('hidden', 'Hidden'),
        ('private', 'Private'),
    ]
    
    ENROLLMENT_METHOD_CHOICES = [
        ('open', 'Open Enrollment'),
        ('purchase', 'Purchase Required'),
        ('invite_only', 'Invite Only'),
        ('cohort_only', 'Cohort Only'),
        ('subscription_only', 'Subscription Only'),
    ]
    
    ACCESS_DURATION_TYPE_CHOICES = [
        ('lifetime', 'Lifetime'),
        ('fixed_days', 'Fixed Days'),
        ('until_date', 'Until Date'),
        ('drip', 'Drip Content'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    course_type = models.CharField(max_length=20, choices=COURSE_TYPE_CHOICES, default='sprint')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', blank=True, null=True)
    
    # Course Features
    coach_name = models.CharField(max_length=100, blank=True)
    is_subscribers_only = models.BooleanField(default=False)
    is_accredible_certified = models.BooleanField(default=False)
    has_asset_templates = models.BooleanField(default=False)
    exam_unlock_days = models.IntegerField(default=0, help_text="Days after enrollment before exam unlocks")
    special_tag = models.CharField(max_length=100, blank=True, help_text="e.g., 'Black Friday 2025'")
    
    # Access Control
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public')
    enrollment_method = models.CharField(max_length=20, choices=ENROLLMENT_METHOD_CHOICES, default='open')
    access_duration_type = models.CharField(max_length=20, choices=ACCESS_DURATION_TYPE_CHOICES, default='lifetime')
    access_duration_days = models.IntegerField(null=True, blank=True, help_text="Duration in days if fixed_days")
    access_until_date = models.DateTimeField(null=True, blank=True, help_text="Expiration date if until_date")
    prerequisite_courses = models.ManyToManyField('self', symmetrical=False, blank=True)
    required_quiz_score = models.IntegerField(default=0, help_text="Required quiz score to unlock (0-100)")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('course_detail', kwargs={'course_slug': self.slug})
    
    def get_lesson_count(self):
        return self.lesson_set.count()
    
    def get_user_progress(self, user):
        """Calculate course progress as percentage of completed lessons"""
        if not user.is_authenticated:
            return 0
        lessons = self.lesson_set.all()
        if not lessons.exists():
            return 0
        total_lessons = lessons.count()
        completed_lessons = UserProgress.objects.filter(
            lesson__course=self,
            user=user,
            completed=True
        ).count()
        return int((completed_lessons / total_lessons * 100)) if total_lessons > 0 else 0


# Module Model
class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.course.name} - {self.name}"


# Lesson Model
class Lesson(models.Model):
    LESSON_TYPE_CHOICES = [
        ('video', 'Video'),
        ('live', 'Live'),
        ('replay', 'Replay'),
    ]
    
    TRANSCRIPTION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    AI_GENERATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generated', 'Generated'),
        ('approved', 'Approved'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField(blank=True)
    
    # Rich Content (Editor.js blocks)
    content = models.JSONField(default=dict, blank=True, help_text="Rich content blocks from Editor.js")
    
    # Video Information
    video_url = models.URLField(blank=True, help_text="Generic video URL")
    video_duration = models.IntegerField(default=0, help_text="Duration in minutes")
    order = models.IntegerField(default=0)
    workbook_url = models.URLField(blank=True)
    resources_url = models.URLField(blank=True)
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPE_CHOICES, default='video')
    
    # Vimeo Integration
    vimeo_url = models.URLField(blank=True)
    vimeo_id = models.CharField(max_length=100, blank=True)
    vimeo_thumbnail = models.URLField(blank=True)
    vimeo_duration_seconds = models.IntegerField(null=True, blank=True)
    
    # Google Drive Integration
    google_drive_url = models.URLField(blank=True)
    google_drive_id = models.CharField(max_length=200, blank=True)
    
    # AI Generation Fields
    working_title = models.CharField(max_length=200, blank=True)
    rough_notes = models.TextField(blank=True)
    transcription = models.TextField(blank=True)
    transcription_status = models.CharField(max_length=20, choices=TRANSCRIPTION_STATUS_CHOICES, default='pending')
    transcription_error = models.TextField(blank=True)
    ai_generation_status = models.CharField(max_length=20, choices=AI_GENERATION_STATUS_CHOICES, default='pending')
    ai_clean_title = models.CharField(max_length=200, blank=True)
    ai_short_summary = models.TextField(blank=True)
    ai_full_description = models.TextField(blank=True)
    ai_outcomes = models.JSONField(default=list, blank=True)
    ai_coach_actions = models.JSONField(default=list, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'id']
        unique_together = ['course', 'slug']
    
    def __str__(self):
        return f"{self.course.name} - {self.title}"
    
    def get_absolute_url(self):
        return reverse('lesson_detail', kwargs={'course_slug': self.course.slug, 'lesson_slug': self.slug})
    
    def get_vimeo_embed_url(self):
        if self.vimeo_id:
            return f"https://player.vimeo.com/video/{self.vimeo_id}"
        return None
    
    def get_formatted_duration(self):
        if self.vimeo_duration_seconds:
            minutes = self.vimeo_duration_seconds // 60
            seconds = self.vimeo_duration_seconds % 60
            return f"{minutes:02d}:{seconds:02d}"
        elif self.video_duration:
            return f"{self.video_duration} min"
        return "N/A"
    
    def get_outcomes_list(self):
        if isinstance(self.ai_outcomes, list):
            return self.ai_outcomes
        return []
    
    def get_coach_actions_list(self):
        if isinstance(self.ai_coach_actions, list):
            return self.ai_coach_actions
        return []
    
    def get_google_drive_embed_url(self):
        """Convert Google Drive sharing URL to embed/preview URL for iframe embedding"""
        # First try to use the stored google_drive_id
        if self.google_drive_id:
            return f"https://drive.google.com/file/d/{self.google_drive_id}/preview"
        
        # If no ID stored, extract it from the URL (won't save, but will work for display)
        if self.google_drive_url:
            drive_match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', self.google_drive_url)
            if drive_match:
                file_id = drive_match.group(1)
                return f"https://drive.google.com/file/d/{file_id}/preview"
        
        return None
    
    def has_content(self):
        """Check if lesson has rich content blocks"""
        if not self.content:
            return False
        if isinstance(self.content, dict):
            blocks = self.content.get('blocks', [])
            return len(blocks) > 0
        return False
    
    def save(self, *args, **kwargs):
        # Extract Vimeo ID from URL
        if self.vimeo_url and not self.vimeo_id:
            vimeo_match = re.search(r'vimeo\.com/(?:video/)?(\d+)', self.vimeo_url)
            if vimeo_match:
                self.vimeo_id = vimeo_match.group(1)
        
        # Extract Google Drive ID from URL
        if self.google_drive_url and not self.google_drive_id:
            drive_match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', self.google_drive_url)
            if drive_match:
                self.google_drive_id = drive_match.group(1)
        
        super().save(*args, **kwargs)


# Lesson Quiz Model
class LessonQuiz(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_required = models.BooleanField(default=False, help_text="Required to complete lesson")
    passing_score = models.IntegerField(default=70, help_text="Passing score (0-100%)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.lesson.title} - Quiz"
    
    def get_question_count(self):
        return self.questions.count()


# Lesson Quiz Question Model
class LessonQuizQuestion(models.Model):
    CORRECT_OPTION_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ]
    
    quiz = models.ForeignKey(LessonQuiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500, blank=True)
    option_d = models.CharField(max_length=500, blank=True)
    correct_option = models.CharField(max_length=1, choices=CORRECT_OPTION_CHOICES)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.quiz.lesson.title} - Q{self.order + 1}"


# Lesson Quiz Attempt Model
class LessonQuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(LessonQuiz, on_delete=models.CASCADE)
    score = models.FloatField(help_text="Score percentage (0-100)")
    passed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now_add=True)
    answers = models.JSONField(default=dict, help_text="User's answers as {question_id: 'A'/'B'/'C'/'D'}")
    
    class Meta:
        ordering = ['-completed_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.lesson.title} - {self.score}%"


# User Progress Model
class UserProgress(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percentage = models.IntegerField(default=0, help_text="Overall progress (0-100)")
    
    # Video Watch Progress
    video_watch_percentage = models.FloatField(default=0.0, help_text="Percentage of video watched (0-100)")
    last_watched_timestamp = models.FloatField(default=0.0, help_text="Last position in video (seconds)")
    video_completion_threshold = models.FloatField(default=90.0, help_text="Required watch % to complete")
    last_accessed = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'lesson']
        ordering = ['-last_accessed']
    
    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} - {self.status}"
    
    def update_status(self):
        """Automatically update status based on video watch percentage"""
        if self.video_watch_percentage >= self.video_completion_threshold:
            self.status = 'completed'
            self.completed = True
            if not self.completed_at:
                self.completed_at = timezone.now()
        elif self.video_watch_percentage > 0:
            self.status = 'in_progress'
            if not self.started_at:
                self.started_at = timezone.now()
        else:
            self.status = 'not_started'
        self.save()


# Course Enrollment Model
class CourseEnrollment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('full', 'Full Payment'),
        ('installment', 'Installment'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='full')
    
    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.name}"


# Favorite Course Model
class FavoriteCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.name}"


# Exam Model
class Exam(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='exam')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    passing_score = models.IntegerField(default=70, help_text="Minimum score to pass (0-100)")
    max_attempts = models.IntegerField(default=0, help_text="0 = unlimited")
    time_limit_minutes = models.IntegerField(null=True, blank=True, help_text="Time limit in minutes (null = no limit)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.course.name} - Exam"
    
    def get_question_count(self):
        return self.questions.count()


# Exam Question Model
class ExamQuestion(models.Model):
    CORRECT_OPTION_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ]
    
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500, blank=True)
    option_d = models.CharField(max_length=500, blank=True)
    correct_option = models.CharField(max_length=1, choices=CORRECT_OPTION_CHOICES)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.exam.course.name} - Q{self.order + 1}"


# Exam Attempt Model
class ExamAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    score = models.FloatField(help_text="Score percentage (0-100)")
    passed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_taken_seconds = models.IntegerField(null=True, blank=True)
    answers = models.JSONField(default=dict)
    is_final = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-completed_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.exam.course.name} - {self.score}%"
    
    def attempt_number(self):
        return ExamAttempt.objects.filter(user=self.user, exam=self.exam, completed_at__lt=self.completed_at).count() + 1


# Certification Model
class Certification(models.Model):
    STATUS_CHOICES = [
        ('not_eligible', 'Not Eligible'),
        ('eligible', 'Eligible'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_eligible')
    accredible_certificate_id = models.CharField(max_length=200, blank=True)
    accredible_certificate_url = models.URLField(blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    passing_exam_attempt = models.ForeignKey(ExamAttempt, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-issued_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.name} - {self.status}"


# Course Access Model - CORE ACCESS CONTROL
class CourseAccess(models.Model):
    ACCESS_TYPE_CHOICES = [
        ('purchase', 'Purchase'),
        ('manual', 'Manual'),
        ('cohort', 'Cohort'),
        ('subscription', 'Subscription'),
        ('bundle', 'Bundle'),
    ]
    
    STATUS_CHOICES = [
        ('unlocked', 'Unlocked'),
        ('locked', 'Locked'),
        ('revoked', 'Revoked'),
        ('expired', 'Expired'),
        ('pending', 'Pending'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unlocked')
    
    # Source Tracking
    bundle_purchase = models.ForeignKey('BundlePurchase', on_delete=models.SET_NULL, null=True, blank=True)
    cohort = models.ForeignKey('Cohort', on_delete=models.SET_NULL, null=True, blank=True)
    purchase_id = models.CharField(max_length=200, blank=True, help_text="External purchase/order ID")
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='granted_accesses')
    granted_at = models.DateTimeField(auto_now_add=True)
    
    # Expiration & Revocation
    expires_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='revoked_accesses')
    revocation_reason = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True, help_text="Audit trail notes")
    
    class Meta:
        unique_together = ['user', 'course', 'access_type', 'purchase_id']
        ordering = ['-granted_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.name} - {self.status}"
    
    def is_active(self):
        """Check if access is currently active"""
        if self.status in ['revoked', 'expired']:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            self.status = 'expired'
            self.save()
            return False
        return self.status == 'unlocked'
    
    def get_source_display(self):
        """Return human-readable source of access"""
        if self.bundle_purchase:
            return f"Bundle: {self.bundle_purchase.bundle.name}"
        elif self.cohort:
            return f"Cohort: {self.cohort.name}"
        elif self.purchase_id:
            return f"Purchase: {self.purchase_id}"
        elif self.granted_by:
            return f"Manual grant by {self.granted_by.username}"
        return self.get_access_type_display()


# Bundle Model
class Bundle(models.Model):
    BUNDLE_TYPE_CHOICES = [
        ('fixed', 'Fixed Bundle'),
        ('pick_your_own', 'Pick Your Own'),
        ('tiered', 'Tiered Bundle'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    bundle_type = models.CharField(max_length=20, choices=BUNDLE_TYPE_CHOICES, default='fixed')
    courses = models.ManyToManyField(Course, blank=True)
    max_course_selections = models.IntegerField(default=0, help_text="For pick-your-own bundles")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


# Bundle Purchase Model
class BundlePurchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE)
    purchase_id = models.CharField(max_length=200, help_text="External purchase/order ID")
    purchase_date = models.DateTimeField(auto_now_add=True)
    selected_courses = models.ManyToManyField(Course, blank=True, help_text="For pick-your-own bundles")
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-purchase_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.bundle.name} - {self.purchase_id}"


# Cohort Model
class Cohort(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def get_member_count(self):
        return self.members.count()


# Cohort Member Model
class CohortMember(models.Model):
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    remove_access_on_leave = models.BooleanField(default=True, help_text="Revoke access when removed from cohort")
    
    class Meta:
        unique_together = ['cohort', 'user']
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.cohort.name} - {self.user.username}"


# Learning Path Model
class LearningPath(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    courses = models.ManyToManyField(Course, through='LearningPathCourse', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


# Learning Path Course Model
class LearningPathCourse(models.Model):
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    is_required = models.BooleanField(default=True, help_text="Must complete to unlock next")
    
    class Meta:
        unique_together = ['learning_path', 'course']
        ordering = ['order']
    
    def __str__(self):
        return f"{self.learning_path.name} - {self.course.name}"
