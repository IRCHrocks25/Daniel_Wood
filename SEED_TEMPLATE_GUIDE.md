# Course Seeding Template Guide

This guide explains how to use the seed file template to add course lessons with Google Drive video URLs.

## Quick Start

Run the seed command:
```bash
python manage.py seed_data
```

To seed lessons to a specific course:
```bash
python manage.py seed_data --course-slug your-course-slug
```

## Template Structure

The seed file (`myApp/management/commands/seed_data.py`) contains a template section where you can customize:

### 1. Course Information
- **Course Slug**: Unique identifier for the course
- **Course Name**: Display name
- **Course Type**: sprint, speaking, consultancy, or special
- **Status**: active, locked, or coming_soon
- **Description**: Full course description

### 2. Lessons Data Template

Each lesson in the `lessons_data` array contains:
- `title`: Lesson title (e.g., "Lesson 1", "Introduction to X")
- `order`: Sequential order number (1, 2, 3, ...)
- `description`: Brief description of the lesson
- `google_drive_url`: Full Google Drive sharing URL

### Example Customization

```python
lessons_data = [
    {
        'title': 'Introduction to Virtual Presence',
        'order': 1,
        'description': 'Learn the fundamentals of building your virtual presence and online brand.',
        'google_drive_url': 'https://drive.google.com/file/d/1vjh0c7ReJn4YjFsgcBCSJKW4xhJg3JOp/view?usp=sharing',
    },
    {
        'title': 'Building Your Personal Brand',
        'order': 2,
        'description': 'Discover strategies to create a powerful and authentic personal brand.',
        'google_drive_url': 'https://drive.google.com/file/d/15LLxGCE3gzMPpo4j7K5yyzaQmt9sTKHd/view?usp=sharing',
    },
    # ... add more lessons
]
```

## Current Video URLs

The template includes all 13 Google Drive video URLs you provided:

1. `1vjh0c7ReJn4YjFsgcBCSJKW4xhJg3JOp` - Lesson 1
2. `15LLxGCE3gzMPpo4j7K5yyzaQmt9sTKHd` - Lesson 2
3. `1c4DpGIwhRJo5ZrasVnRM4JJZdFLupvaw` - Lesson 3
4. `1ItvLVPWsmdb9yoKDINcyIyOoa1IMCtcT` - Lesson 4
5. `15cB6GJwybTMijjGf6CPU2ixBQ6V8EUI1` - Lesson 5
6. `1z7NwNXfgEtZdLouj8b2wZu-YHHpfl2Nm` - Lesson 6
7. `1Wv06ZSdCzzb4TwdydHM_UF_I9bdhNsk3` - Lesson 7
8. `1paEt7fjQAc3MD_82JWA-oOZzJ7_MD82f` - Lesson 8
9. `1geHiehW3AOx80b2p2_TGSXLAjjcWBryX` - Lesson 9
10. `1-bCMwhgBrAW80en5lWIYURBh-XOWWBrn` - Lesson 10
11. `1tyNbO0k1QgL5thBxAndEWr8fLHyAMNjZ` - Lesson 11
12. `1sxRMfRi70UmEetf4bbSELMehXM8C38K4` - Lesson 12
13. `1rvZR8uldp-dTgwsx7rbPkKmYFeUq2N5x` - Lesson 13

## Features

- **Automatic Slug Generation**: Lesson slugs are automatically generated from titles
- **Google Drive ID Extraction**: The system automatically extracts the Google Drive file ID from the URL
- **Idempotent**: Running the command multiple times won't create duplicates (uses `get_or_create`)
- **Update Existing**: If a lesson exists but is missing the Google Drive URL, it will be updated

## Customization Tips

1. **Update Lesson Titles**: Replace generic "Lesson 1", "Lesson 2" with descriptive titles
2. **Add Descriptions**: Write meaningful descriptions for each lesson
3. **Set Video Duration**: Update `video_duration` if you know the length of each video
4. **Add Modules**: You can organize lessons into modules by creating Module objects and assigning them
5. **Add Workbooks/Resources**: Include `workbook_url` and `resources_url` if available

## Next Steps

1. Customize the lesson titles and descriptions in `seed_data.py`
2. Run the seed command
3. Verify lessons in the Django admin or through the course detail page

