# Generated manually to increase Lesson slug max_length

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='slug',
            field=models.SlugField(max_length=200),
        ),
    ]

