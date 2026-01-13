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
        
        # Calculate updated course progress
        total_lessons = lesson.course.lesson_set.count()
        completed_lessons = UserProgress.objects.filter(
            user=request.user,
            lesson__course=lesson.course,
            completed=True
        ).count()
        if total_lessons > 0:
            course_progress = int((completed_lessons / total_lessons) * 100)
            course_progress = max(0, min(100, course_progress))  # Clamp to 0-100
        else:
            course_progress = 0
        
        return JsonResponse({
            'success': True,
            'message': 'Lesson marked as complete',
            'lesson_id': lesson.id,
            'course_progress': course_progress,
            'completed_lessons': completed_lessons,
            'total_lessons': total_lessons,
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


@csrf_exempt
@require_POST
def chatbot_public(request):
    """Public AI chatbot for landing page (no login required)"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        page_context = data.get('page_context', {})
        
        if not message:
            return JsonResponse({'success': False, 'error': 'Message is required'}, status=400)
        
        # Rate limiting check (simple in-memory, in production use Redis/cache)
        # For now, just process the request
        
        # Stub response for now (replace with OpenAI later)
        responses = {
            'what\'s inside the community': 'Swedish Wealth Institute offers a high-trust community with vetted mentors, world-class conversations, and a global network. Members get access to programs across three pillars: Assets Mastery, Financial Literacy, and Time Management. The community is built for action, not just information—with real support and accountability.',
            'how do programs work': 'Our programs are structured around three core pillars: Assets Mastery, Financial Literacy, and Time Management. Each program includes video lessons, practical exercises, and access to our community. You can learn at your own pace, track your progress, and connect with mentors and peers who are on the same journey.',
            'how do i join': 'To join Swedish Wealth Institute, click "Step Into the Room" to create an account. Once you\'re registered, you\'ll have access to browse our programs, join the community, and start your journey toward financial freedom and personal growth.',
            'upcoming experiences': 'We regularly host events, workshops, and live conversations with vetted experts. Check our Events page for the latest schedule. These experiences are designed to provide actionable insights and connect you with mentors who can guide your journey.'
        }
        
        # Simple keyword matching for stub responses
        message_lower = message.lower()
        response_text = None
        for key, value in responses.items():
            if key in message_lower:
                response_text = value
                break
        
        if not response_text:
            # Generic helpful response
            response_text = 'Thank you for your question! Swedish Wealth Institute offers programs in Assets Mastery, Financial Literacy, and Time Management. Our community provides vetted mentors, world-class conversations, and a global network of ambitious individuals. Would you like to know more about our programs, how to join, or upcoming events?'
        
        return JsonResponse({
            'success': True,
            'response': response_text,
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
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

