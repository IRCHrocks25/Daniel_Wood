# Dashboard URLs Test Guide

## ✅ Navbar Admin Link
- **Location**: Top navbar (visible when logged in as staff)
- **Link**: Points to `/dashboard/` (dashboard_home)
- **Status**: ✅ Already correct in `base.html` line 66

## Dashboard Entry Points

### 1. Dashboard Home
- **URL**: `http://127.0.0.1:8000/dashboard/`
- **Name**: `dashboard_home`
- **Access**: Staff only
- **What to see**: Stats overview, quick action cards

### 2. Courses List
- **URL**: `http://127.0.0.1:8000/dashboard/courses/`
- **Name**: `dashboard_courses`
- **Access**: Staff only
- **What to see**: All courses with search/filter, edit/delete buttons

### 3. Course Detail (Main Management Page)
- **URL**: `http://127.0.0.1:8000/dashboard/courses/<course_slug>/`
- **Example**: `http://127.0.0.1:8000/dashboard/courses/virtual-rockstar/`
- **Name**: `dashboard_course_detail`
- **Access**: Staff only
- **What to see**:
  - Course edit form (left side)
  - Sidebar with:
    - **Lessons List** (clickable to edit)
    - **Quizzes List** (clickable to manage)
    - **Exam Management** (create/edit exam)
    - Quick stats

## Lesson Management URLs

### 4. All Lessons List
- **URL**: `http://127.0.0.1:8000/dashboard/lessons/`
- **Name**: `dashboard_lessons`
- **Access**: Staff only
- **What to see**: Table of all lessons with edit/delete/view buttons
- **Filter**: Can filter by course using `?course=<course_id>`

### 5. Add Lesson
- **URL**: `http://127.0.0.1:8000/dashboard/lessons/add/`
- **Name**: `dashboard_add_lesson`
- **Access**: Staff only
- **What to see**: Form to create new lesson

### 6. Edit Lesson (Quiz Management Available Here)
- **URL**: `http://127.0.0.1:8000/dashboard/lessons/<lesson_id>/edit/`
- **Example**: `http://127.0.0.1:8000/dashboard/lessons/1/edit/`
- **Name**: `dashboard_edit_lesson`
- **Access**: Staff only
- **What to see**:
  - Lesson edit form
  - **Quiz Management Section** at bottom:
    - If quiz exists: "Manage Quiz" button
    - If no quiz: "Create Quiz" button

### 7. Delete Lesson
- **URL**: `http://127.0.0.1:8000/dashboard/lessons/<lesson_id>/delete/`
- **Name**: `dashboard_delete_lesson`
- **Method**: POST only
- **Access**: Staff only

## Quiz Management URLs

### 8. Add Quiz
- **URL**: `http://127.0.0.1:8000/dashboard/lessons/<lesson_id>/quiz/add/`
- **Example**: `http://127.0.0.1:8000/dashboard/lessons/1/quiz/add/`
- **Name**: `dashboard_add_quiz`
- **Access**: Staff only
- **What to see**: Form to create quiz (title, description, passing score, required checkbox)

### 9. Edit Quiz (Question Management Available Here)
- **URL**: `http://127.0.0.1:8000/dashboard/quizzes/<quiz_id>/edit/`
- **Example**: `http://127.0.0.1:8000/dashboard/quizzes/1/edit/`
- **Name**: `dashboard_edit_quiz`
- **Access**: Staff only
- **What to see**:
  - Quiz settings form (left)
  - Questions list with edit/delete buttons (left)
  - "Add Question" button
  - Quiz info sidebar (right)

### 10. Delete Quiz
- **URL**: `http://127.0.0.1:8000/dashboard/quizzes/<quiz_id>/delete/`
- **Name**: `dashboard_delete_quiz`
- **Method**: POST only
- **Access**: Staff only

### 11. Add Quiz Question
- **URL**: `http://127.0.0.1:8000/dashboard/quizzes/<quiz_id>/questions/add/`
- **Example**: `http://127.0.0.1:8000/dashboard/quizzes/1/questions/add/`
- **Name**: `dashboard_add_quiz_question`
- **Access**: Staff only
- **What to see**: Form with question text, options A/B/C/D, correct answer, order

### 12. Edit Quiz Question
- **URL**: `http://127.0.0.1:8000/dashboard/quiz-questions/<question_id>/edit/`
- **Example**: `http://127.0.0.1:8000/dashboard/quiz-questions/1/edit/`
- **Name**: `dashboard_edit_quiz_question`
- **Access**: Staff only
- **What to see**: Edit form for question

### 13. Delete Quiz Question
- **URL**: `http://127.0.0.1:8000/dashboard/quiz-questions/<question_id>/delete/`
- **Name**: `dashboard_delete_quiz_question`
- **Method**: POST only
- **Access**: Staff only

## Exam Management URLs

### 14. Add Exam
- **URL**: `http://127.0.0.1:8000/dashboard/courses/<course_slug>/exam/add/`
- **Example**: `http://127.0.0.1:8000/dashboard/courses/virtual-rockstar/exam/add/`
- **Name**: `dashboard_add_exam`
- **Access**: Staff only
- **What to see**: Form to create exam

### 15. Edit Exam (Question Management Available Here)
- **URL**: `http://127.0.0.1:8000/dashboard/exams/<exam_id>/edit/`
- **Example**: `http://127.0.0.1:8000/dashboard/exams/1/edit/`
- **Name**: `dashboard_edit_exam`
- **Access**: Staff only
- **What to see**:
  - Exam settings form (left)
  - Questions list with edit/delete buttons (left)
  - "Add Question" button
  - Exam info and statistics sidebar (right)

### 16. Add Exam Question
- **URL**: `http://127.0.0.1:8000/dashboard/exams/<exam_id>/questions/add/`
- **Name**: `dashboard_add_exam_question`
- **Access**: Staff only

### 17. Edit Exam Question
- **URL**: `http://127.0.0.1:8000/dashboard/exam-questions/<question_id>/edit/`
- **Name**: `dashboard_edit_exam_question`
- **Access**: Staff only

### 18. Delete Exam Question
- **URL**: `http://127.0.0.1:8000/dashboard/exam-questions/<question_id>/delete/`
- **Name**: `dashboard_delete_exam_question`
- **Method**: POST only
- **Access**: Staff only

## Complete Test Flow

### Step 1: Login as Admin
1. Go to: `http://127.0.0.1:8000/login/`
2. Username: `admin`
3. Password: `admin123`
4. Click "Admin" in navbar (top right, purple link)

### Step 2: Navigate to Course
1. From dashboard home, click "Manage Courses"
2. Or go directly: `http://127.0.0.1:8000/dashboard/courses/`
3. Click on "VIRTUAL ROCKSTAR™" course
4. URL: `http://127.0.0.1:8000/dashboard/courses/virtual-rockstar/`

### Step 3: Verify Course Detail Page
**Expected UI Elements:**
- ✅ Course edit form (left side)
- ✅ Sidebar (right side) with:
  - **Lessons section**: Shows all lessons with edit links
  - **Quizzes section**: Shows all quizzes with manage links
  - **Exam section**: Create/edit exam button
  - Quick stats

### Step 4: Test Lesson Management
1. **From Course Detail sidebar**: Click lesson title or edit icon
2. **Or go to**: `http://127.0.0.1:8000/dashboard/lessons/1/edit/`
3. **Expected**: Lesson edit form with quiz management section at bottom
4. **Quiz section shows**:
   - If quiz exists: Quiz info + "Manage Quiz" button
   - If no quiz: "Create Quiz" button

### Step 5: Test Quiz Management
1. **From Lesson Edit page**: Click "Create Quiz" or "Manage Quiz"
2. **Or go to**: `http://127.0.0.1:8000/dashboard/quizzes/1/edit/`
3. **Expected**: 
   - Quiz settings form
   - Questions list
   - "Add Question" button
4. **Click "Add Question"**: Form to add question
5. **Click "Edit" on question**: Edit question form
6. **Click "Delete" on question**: Confirms and deletes

### Step 6: Test Exam Management
1. **From Course Detail sidebar**: Click "Create Exam" or "Manage Exam"
2. **Or go to**: `http://127.0.0.1:8000/dashboard/exams/1/edit/`
3. **Expected**: Similar to quiz management with statistics

## Quick Access URLs (After Login)

```
Dashboard Home:        http://127.0.0.1:8000/dashboard/
Courses List:          http://127.0.0.1:8000/dashboard/courses/
Course Detail:         http://127.0.0.1:8000/dashboard/courses/virtual-rockstar/
Lessons List:          http://127.0.0.1:8000/dashboard/lessons/
Add Lesson:            http://127.0.0.1:8000/dashboard/lessons/add/
Edit Lesson:           http://127.0.0.1:8000/dashboard/lessons/1/edit/
Add Quiz:              http://127.0.0.1:8000/dashboard/lessons/1/quiz/add/
Edit Quiz:             http://127.0.0.1:8000/dashboard/quizzes/1/edit/
Add Quiz Question:     http://127.0.0.1:8000/dashboard/quizzes/1/questions/add/
Add Exam:              http://127.0.0.1:8000/dashboard/courses/virtual-rockstar/exam/add/
Edit Exam:             http://127.0.0.1:8000/dashboard/exams/1/edit/
```

## Verification Checklist

- [x] Navbar "Admin" link points to `/dashboard/`
- [x] Dashboard home accessible
- [x] Courses list accessible
- [x] Course detail shows lessons with edit links
- [x] Course detail shows quizzes with manage links
- [x] Course detail shows exam management
- [x] Lesson edit page shows quiz management section
- [x] Quiz edit page shows questions with edit/delete
- [x] All URLs exist in `urls.py`
- [x] All views have `@user_passes_test(is_staff)` decorator
- [x] Templates exist and render correctly

## Staff-Only Access Verification

All dashboard views are protected with:
```python
@login_required
@user_passes_test(is_staff)
```

Non-staff users will be redirected to login or see 403 error.

