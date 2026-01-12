"""
API Endpoints for AJAX requests
"""
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json

from .models import (
    Lesson, UserProgress, FavoriteCourse, LessonQuiz, LessonQuizAttempt, Course
)
from .utils.access import has_course_access


@login_required
@require_POST
def update_video_progress(request, lesson_id):
    """Update video watch progress"""
    try:
        lesson = Lesson.objects.get(id=lesson_id)
        data = json.loads(request.body)
        
        watch_percentage = float(data.get('watch_percentage', 0))
        timestamp = float(data.get('timestamp', 0))
        
        # Check access
        has_access, _, _ = has_course_access(request.user, lesson.course)
        if not has_access:
            return JsonResponse({'success': False, 'error': 'No access to this course'}, status=403)
        
        # Get or create progress
        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={
                'video_watch_percentage': watch_percentage,
                'last_watched_timestamp': timestamp,
                'progress_percentage': int(watch_percentage),
            }
        )
        
        if not created:
            progress.video_watch_percentage = watch_percentage
            progress.last_watched_timestamp = timestamp
            progress.progress_percentage = int(watch_percentage)
        
        # Update status based on watch percentage
        progress.update_status()
        
        return JsonResponse({
            'success': True,
            'watch_percentage': progress.video_watch_percentage,
            'status': progress.status,
            'completed': progress.completed,
        })
    
    except Lesson.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Lesson not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def complete_lesson(request, lesson_id):
    """Mark lesson as complete"""
    try:
        lesson = Lesson.objects.get(id=lesson_id)
        
        # Check access
        has_access, _, _ = has_course_access(request.user, lesson.course)
        if not has_access:
            return JsonResponse({'success': False, 'error': 'No access to this course'}, status=403)
        
        # Check if required quiz is passed
        if hasattr(lesson, 'quiz') and lesson.quiz.is_required:
            quiz_attempt = LessonQuizAttempt.objects.filter(
                user=request.user,
                quiz=lesson.quiz,
                passed=True
            ).exists()
            
            if not quiz_attempt:
                return JsonResponse({
                    'success': False,
                    'error': 'Required quiz must be passed before completing lesson',
                    'quiz_required': True
                }, status=400)
        
        # Get or create progress
        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson
        )
        
        # Mark as complete
        progress.status = 'completed'
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.progress_percentage = 100
        progress.video_watch_percentage = 100.0
        progress.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Lesson marked as complete',
            'lesson_id': lesson.id,
        })
    
    except Lesson.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Lesson not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def toggle_favorite_course(request, course_id):
    """Toggle favorite status for a course"""
    try:
        course = Course.objects.get(id=course_id)
        
        favorite, created = FavoriteCourse.objects.get_or_create(
            user=request.user,
            course=course
        )
        
        if not created:
            favorite.delete()
            is_favorited = False
            message = 'Course removed from favorites'
        else:
            is_favorited = True
            message = 'Course added to favorites'
        
        return JsonResponse({
            'success': True,
            'is_favorited': is_favorited,
            'message': message,
        })
    
    except Course.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Course not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
@csrf_exempt
def chatbot_webhook(request):
    """AI chatbot integration"""
    try:
        data = json.loads(request.body)
        action = data.get('action', 'free_form')
        action_text = data.get('action_text', '')
        user_message = data.get('user_message', '')
        lesson_id = data.get('lesson_id')
        lesson_title = data.get('lesson_title', '')
        course_name = data.get('course_name', '')
        
        # Placeholder for AI integration
        # In production, integrate with OpenAI API
        from django.conf import settings
        import openai
        
        if not settings.OPENAI_API_KEY:
            return JsonResponse({
                'success': False,
                'error': 'AI services not configured',
                'response': 'AI features are not currently available. Please contact support.'
            })
        
        # Build prompt based on action
        if action == 'free_form':
            prompt = f"{action_text}\n\nUser message: {user_message}\n\nLesson: {lesson_title}\nCourse: {course_name}"
        else:
            prompt = f"Action: {action_text}\n\n{user_message}"
        
        # Call OpenAI API
        try:
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful learning assistant for an online course platform."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            return JsonResponse({
                'success': True,
                'response': ai_response,
            })
        except Exception as ai_error:
            return JsonResponse({
                'success': False,
                'error': 'AI service error',
                'response': f'An error occurred: {str(ai_error)}'
            })
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

