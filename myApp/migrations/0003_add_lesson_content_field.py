# Generated manually to add content field to Lesson model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0002_increase_lesson_slug_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='content',
            field=models.JSONField(blank=True, default=dict, help_text='Rich content blocks from Editor.js'),
        ),
    ]

