from django.contrib import admin
from .models import (
    Course, Module, Lesson, LessonQuiz, LessonQuizQuestion, LessonQuizAttempt,
    UserProgress, CourseEnrollment, FavoriteCourse, Certification, Exam, ExamQuestion, ExamAttempt,
    CourseAccess, Bundle, BundlePurchase, Cohort, CohortMember, LearningPath, LearningPathCourse
)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'course_type', 'status', 'visibility', 'enrollment_method', 'created_at']
    list_filter = ['course_type', 'status', 'visibility', 'enrollment_method', 'created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['prerequisite_courses']


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'order']
    list_filter = ['course']
    search_fields = ['name', 'course__name']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'module', 'order', 'lesson_type', 'video_duration', 'created_at']
    list_filter = ['course', 'module', 'lesson_type', 'created_at']
    search_fields = ['title', 'description', 'course__name']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(LessonQuiz)
class LessonQuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'is_required', 'passing_score', 'created_at']
    list_filter = ['is_required', 'created_at']
    search_fields = ['title', 'lesson__title']


@admin.register(LessonQuizQuestion)
class LessonQuizQuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'quiz', 'correct_option', 'order']
    list_filter = ['quiz', 'correct_option']
    search_fields = ['text', 'quiz__lesson__title']


@admin.register(LessonQuizAttempt)
class LessonQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'score', 'passed', 'completed_at']
    list_filter = ['passed', 'completed_at']
    search_fields = ['user__username', 'quiz__lesson__title']
    readonly_fields = ['completed_at']


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'status', 'completed', 'progress_percentage', 'video_watch_percentage', 'last_accessed']
    list_filter = ['status', 'completed', 'last_accessed']
    search_fields = ['user__username', 'lesson__title']
    readonly_fields = ['last_accessed', 'completed_at', 'started_at']


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'enrolled_at', 'payment_type']
    list_filter = ['payment_type', 'enrolled_at']
    search_fields = ['user__username', 'course__name']
    readonly_fields = ['enrolled_at']


@admin.register(FavoriteCourse)
class FavoriteCourseAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'course__name']
    readonly_fields = ['created_at']


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'status', 'issued_at']
    list_filter = ['status', 'issued_at']
    search_fields = ['user__username', 'course__name']
    readonly_fields = ['issued_at']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['course', 'title', 'passing_score', 'max_attempts', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'course__name']


@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'exam', 'correct_option', 'order']
    list_filter = ['exam', 'correct_option']
    search_fields = ['text', 'exam__course__name']


@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'exam', 'score', 'passed', 'completed_at', 'is_final']
    list_filter = ['passed', 'is_final', 'completed_at']
    search_fields = ['user__username', 'exam__course__name']
    readonly_fields = ['started_at', 'completed_at']


@admin.register(CourseAccess)
class CourseAccessAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'access_type', 'status', 'granted_at', 'expires_at']
    list_filter = ['access_type', 'status', 'granted_at']
    search_fields = ['user__username', 'course__name', 'purchase_id']
    readonly_fields = ['granted_at', 'revoked_at']


@admin.register(Bundle)
class BundleAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'bundle_type', 'price', 'is_active', 'created_at']
    list_filter = ['bundle_type', 'is_active', 'created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['courses']


@admin.register(BundlePurchase)
class BundlePurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'bundle', 'purchase_id', 'purchase_date']
    list_filter = ['purchase_date']
    search_fields = ['user__username', 'bundle__name', 'purchase_id']
    readonly_fields = ['purchase_date']
    filter_horizontal = ['selected_courses']


@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']


@admin.register(CohortMember)
class CohortMemberAdmin(admin.ModelAdmin):
    list_display = ['cohort', 'user', 'joined_at', 'remove_access_on_leave']
    list_filter = ['cohort', 'joined_at', 'remove_access_on_leave']
    search_fields = ['cohort__name', 'user__username']
    readonly_fields = ['joined_at']


@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']


@admin.register(LearningPathCourse)
class LearningPathCourseAdmin(admin.ModelAdmin):
    list_display = ['learning_path', 'course', 'order', 'is_required']
    list_filter = ['learning_path', 'is_required']
    search_fields = ['learning_path__name', 'course__name']
