"""
Management command to seed initial data
Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from myApp.models import Course, Lesson, Module


class Command(BaseCommand):
    help = 'Seed initial data for the learning platform'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')
        
        # Create admin user if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin.username}'))
        else:
            self.stdout.write('Admin user already exists')
        
        # Create a sample course
        course, created = Course.objects.get_or_create(
            slug='virtual-rockstar',
            defaults={
                'name': 'VIRTUAL ROCKSTAR™',
                'course_type': 'sprint',
                'status': 'active',
                'visibility': 'public',
                'enrollment_method': 'open',
                'description': 'Transform your virtual presence and become a rockstar online. This comprehensive course covers everything you need to know about virtual success.',
                'short_description': 'Become a virtual rockstar with this comprehensive course',
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created course: {course.name}'))
        else:
            self.stdout.write(f'Course already exists: {course.name}')
        
        # Create sample lessons
        lessons_data = [
            {'title': 'Session #1: Introduction', 'order': 1, 'description': 'Welcome to Virtual Rockstar. Learn the fundamentals.'},
            {'title': 'Session #2: Building Your Brand', 'order': 2, 'description': 'Discover how to build a powerful personal brand.'},
            {'title': 'Session #3: Content Creation', 'order': 3, 'description': 'Master the art of creating engaging content.'},
        ]
        
        for lesson_data in lessons_data:
            lesson, created = Lesson.objects.get_or_create(
                course=course,
                slug=lesson_data['title'].lower().replace(' ', '-').replace('#', '').replace(':', ''),
                defaults={
                    'title': lesson_data['title'],
                    'order': lesson_data['order'],
                    'description': lesson_data['description'],
                    'video_url': 'https://vimeo.com/example',
                    'video_duration': 30,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Created lesson: {lesson.title}'))
        
        self.stdout.write(self.style.SUCCESS('Seeding completed!'))

