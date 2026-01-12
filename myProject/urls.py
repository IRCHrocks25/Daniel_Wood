from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from myApp import views, student_views, dashboard_views, api_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Public Views
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('courses/', views.courses, name='courses'),
    path('courses/<slug:course_slug>/', views.course_detail, name='course_detail'),
    path('courses/<slug:course_slug>/<slug:lesson_slug>/', views.lesson_detail, name='lesson_detail'),
    path('courses/<slug:course_slug>/<slug:lesson_slug>/quiz/', views.lesson_quiz_view, name='lesson_quiz'),
    
    # Student Dashboard
    path('my-dashboard/', student_views.student_dashboard, name='student_dashboard'),
    path('my-dashboard/course/<slug:course_slug>/', student_views.student_course_progress, name='student_course_progress'),
    path('my-certifications/', student_views.student_certifications, name='student_certifications'),
    
    # Student Exam
    path('my-dashboard/course/<slug:course_slug>/exam/', student_views.take_exam, name='take_exam'),
    path('my-dashboard/course/<slug:course_slug>/exam/submit/', student_views.submit_exam, name='submit_exam'),
    path('my-dashboard/course/<slug:course_slug>/exam-results/', student_views.student_exam_results, name='student_exam_results'),
    
    # Admin Dashboard
    path('dashboard/', dashboard_views.dashboard_home, name='dashboard_home'),
    path('dashboard/analytics/', dashboard_views.dashboard_analytics, name='dashboard_analytics'),
    path('dashboard/courses/', dashboard_views.dashboard_courses, name='dashboard_courses'),
    path('dashboard/courses/add/', dashboard_views.dashboard_add_course, name='dashboard_add_course'),
    path('dashboard/courses/<slug:course_slug>/', dashboard_views.dashboard_course_detail, name='dashboard_course_detail'),
    path('dashboard/courses/<slug:course_slug>/delete/', dashboard_views.dashboard_delete_course, name='dashboard_delete_course'),
    path('dashboard/lessons/', dashboard_views.dashboard_lessons, name='dashboard_lessons'),
    path('dashboard/lessons/add/', dashboard_views.dashboard_add_lesson, name='dashboard_add_lesson'),
    path('dashboard/lessons/<int:lesson_id>/edit/', dashboard_views.dashboard_edit_lesson, name='dashboard_edit_lesson'),
    path('dashboard/lessons/<int:lesson_id>/delete/', dashboard_views.dashboard_delete_lesson, name='dashboard_delete_lesson'),
    
    # Quiz Management
    path('dashboard/lessons/<int:lesson_id>/quiz/add/', dashboard_views.dashboard_add_quiz, name='dashboard_add_quiz'),
    path('dashboard/quizzes/<int:quiz_id>/edit/', dashboard_views.dashboard_edit_quiz, name='dashboard_edit_quiz'),
    path('dashboard/quizzes/<int:quiz_id>/delete/', dashboard_views.dashboard_delete_quiz, name='dashboard_delete_quiz'),
    path('dashboard/quizzes/<int:quiz_id>/questions/add/', dashboard_views.dashboard_add_quiz_question, name='dashboard_add_quiz_question'),
    path('dashboard/quiz-questions/<int:question_id>/edit/', dashboard_views.dashboard_edit_quiz_question, name='dashboard_edit_quiz_question'),
    path('dashboard/quiz-questions/<int:question_id>/delete/', dashboard_views.dashboard_delete_quiz_question, name='dashboard_delete_quiz_question'),
    
    # Exam Management
    path('dashboard/courses/<slug:course_slug>/exam/add/', dashboard_views.dashboard_add_exam, name='dashboard_add_exam'),
    path('dashboard/exams/<int:exam_id>/edit/', dashboard_views.dashboard_edit_exam, name='dashboard_edit_exam'),
    path('dashboard/exams/<int:exam_id>/questions/add/', dashboard_views.dashboard_add_exam_question, name='dashboard_add_exam_question'),
    path('dashboard/exam-questions/<int:question_id>/edit/', dashboard_views.dashboard_edit_exam_question, name='dashboard_edit_exam_question'),
    path('dashboard/exam-questions/<int:question_id>/delete/', dashboard_views.dashboard_delete_exam_question, name='dashboard_delete_exam_question'),
    
    path('dashboard/students/', dashboard_views.dashboard_students, name='dashboard_students'),
    path('dashboard/students/<int:user_id>/', dashboard_views.dashboard_student_detail, name='dashboard_student_detail'),
    path('dashboard/students/<int:user_id>/<slug:course_slug>/', dashboard_views.dashboard_student_detail, name='dashboard_student_detail_course'),
    path('dashboard/students/<int:user_id>/grant-access/', dashboard_views.grant_course_access_view, name='grant_course_access'),
    path('dashboard/students/<int:user_id>/revoke-access/', dashboard_views.revoke_course_access_view, name='revoke_course_access'),
    
    # API Endpoints
    path('api/lessons/<int:lesson_id>/progress/', api_views.update_video_progress, name='update_video_progress'),
    path('api/lessons/<int:lesson_id>/complete/', api_views.complete_lesson, name='complete_lesson'),
    path('api/courses/<int:course_id>/favorite/', api_views.toggle_favorite_course, name='toggle_favorite'),
    path('api/chatbot/', api_views.chatbot_webhook, name='chatbot_webhook'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
