# Manual Test Checklist

## Phase 1: Quiz Management (Admin)

### ✅ Create Quiz
1. **Navigate**: Dashboard → Courses → Select Course → Edit Lesson
2. **Action**: Click "Create Quiz" button
3. **Fill Form**:
   - Title: "Lesson 1 Quiz"
   - Description: "Test your understanding"
   - Passing Score: 70%
   - Check "Required to complete lesson"
4. **Expected**: Quiz created, redirected to quiz edit page
5. **Verify**: Quiz appears in lesson edit page

### ✅ Add Quiz Questions
1. **Navigate**: Quiz edit page
2. **Action**: Click "Add Question"
3. **Fill Form**:
   - Question Text: "What is the main topic?"
   - Option A: "Topic A"
   - Option B: "Topic B"
   - Option C: "Topic C"
   - Option D: "Topic D"
   - Correct Answer: A
   - Order: 0
4. **Expected**: Question added, appears in questions list
5. **Verify**: Question shows with green highlight on correct answer

### ✅ Edit Quiz Question
1. **Navigate**: Quiz edit page → Click "Edit" on a question
2. **Action**: Change correct answer from A to B
3. **Expected**: Question updated, correct answer highlighted in green
4. **Verify**: Changes saved correctly

### ✅ Delete Quiz Question
1. **Navigate**: Quiz edit page
2. **Action**: Click "Delete" on a question → Confirm
3. **Expected**: Question removed from list
4. **Verify**: Question count decreases

### ✅ Edit Quiz Settings
1. **Navigate**: Quiz edit page
2. **Action**: Change passing score to 80%, uncheck "Required"
3. **Expected**: Settings saved
4. **Verify**: Changes reflected in quiz info sidebar

### ✅ Delete Quiz
1. **Navigate**: Quiz edit page
2. **Action**: Click "Delete Quiz" → Confirm
3. **Expected**: Quiz deleted, redirected to lesson edit page
4. **Verify**: "Create Quiz" button appears again

---

## Phase 2: Student Quiz Flow

### ✅ Take Quiz (Student)
1. **Navigate**: As student → Course → Lesson with quiz
2. **Action**: Click "Take Quiz" button
3. **Expected**: Quiz form displays with all questions
4. **Verify**: Radio buttons work, can select answers

### ✅ Submit Quiz
1. **Action**: Answer all questions → Click "Submit Exam"
2. **Expected**: Score calculated, pass/fail message shown
3. **Verify**: 
   - Score displayed correctly
   - Pass/fail status correct based on passing_score
   - Redirected to lesson page

### ✅ Required Quiz Blocks Completion
1. **Setup**: Create lesson with required quiz (passing_score: 70%)
2. **Action**: 
   - Complete lesson without passing quiz
   - Try to mark lesson complete via API/button
3. **Expected**: Error message: "Required quiz must be passed before completing lesson"
4. **Verify**: Lesson cannot be completed until quiz passed

### ✅ Retake Quiz
1. **Action**: After failing quiz, click "Retake Quiz"
2. **Expected**: Can take quiz again
3. **Verify**: New attempt recorded, previous attempts shown

---

## Phase 3: Exam System (Student)

### ✅ Check Exam Eligibility
1. **Setup**: Course with exam, exam_unlock_days: 0, all lessons completed
2. **Navigate**: Student Dashboard → Course Progress
3. **Expected**: "Take Exam" button visible
4. **Verify**: Can access exam page

### ✅ Exam Eligibility - Lessons Not Completed
1. **Setup**: Course with exam, some lessons incomplete
2. **Action**: Try to access exam
3. **Expected**: Warning message: "X lesson(s) not completed"
4. **Verify**: Redirected to course progress, cannot take exam

### ✅ Exam Eligibility - Unlock Days
1. **Setup**: Course with exam_unlock_days: 7, enrolled today
2. **Action**: Try to access exam
3. **Expected**: Warning: "Exam unlocks in 7 day(s)"
4. **Verify**: Cannot take exam yet

### ✅ Exam Eligibility - Max Attempts
1. **Setup**: Exam with max_attempts: 2, already taken 2 times
2. **Action**: Try to access exam
3. **Expected**: Warning: "Maximum attempts (2) reached"
4. **Verify**: Cannot take exam again

### ✅ Take Exam
1. **Navigate**: Course Progress → "Take Exam"
2. **Expected**: 
   - Exam form displays
   - All questions shown
   - Timer visible (if time_limit_minutes set)
   - Previous attempts shown (if any)
3. **Verify**: Can select answers, form validates

### ✅ Submit Exam
1. **Action**: Answer all questions → Click "Submit Exam"
2. **Expected**: 
   - Score calculated
   - Pass/fail determined
   - ExamAttempt created
   - If passed: Certification issued
3. **Verify**: 
   - Score matches correct answers
   - Pass/fail correct based on passing_score
   - Redirected to exam results page

### ✅ Exam Timer
1. **Setup**: Exam with time_limit_minutes: 5
2. **Action**: Start exam, wait for timer
3. **Expected**: 
   - Timer counts down
   - At 0:00, exam auto-submits
   - time_taken_seconds recorded
4. **Verify**: Timer works correctly, submission happens

### ✅ View Exam Results
1. **Navigate**: Course Progress → "View Exam Results"
2. **Expected**: 
   - All attempts listed
   - Scores displayed
   - Pass/fail status shown
   - Certification status if passed
3. **Verify**: All attempt data correct

---

## Phase 4: Exam Management (Admin)

### ✅ Create Exam
1. **Navigate**: Dashboard → Courses → Select Course
2. **Action**: Click "Create Exam" in sidebar
3. **Fill Form**:
   - Title: "Final Exam"
   - Description: "Comprehensive assessment"
   - Passing Score: 75%
   - Max Attempts: 3
   - Time Limit: 60 minutes
   - Check "Active"
4. **Expected**: Exam created, redirected to exam edit page
5. **Verify**: Exam appears in course sidebar

### ✅ Add Exam Questions
1. **Navigate**: Exam edit page
2. **Action**: Click "Add Question"
3. **Fill Form**: Similar to quiz questions
4. **Expected**: Question added to exam
5. **Verify**: Question appears in list, correct answer highlighted

### ✅ Edit Exam
1. **Navigate**: Exam edit page
2. **Action**: Change passing_score to 80%, max_attempts to 5
3. **Expected**: Changes saved
4. **Verify**: Statistics update correctly

### ✅ Edit Exam Question
1. **Navigate**: Exam edit page → Click "Edit" on question
2. **Action**: Change correct answer
3. **Expected**: Question updated
4. **Verify**: Changes saved

### ✅ Delete Exam Question
1. **Navigate**: Exam edit page
2. **Action**: Click "Delete" on question → Confirm
3. **Expected**: Question removed
4. **Verify**: Question count decreases

### ✅ Exam Statistics
1. **Navigate**: Exam edit page
2. **Expected**: Sidebar shows:
   - Total Attempts
   - Passed Attempts
   - Average Score
3. **Verify**: Statistics accurate

---

## Phase 5: Certification Issuance

### ✅ Auto-Issue on Exam Pass
1. **Setup**: Course with exam, is_accredible_certified: False
2. **Action**: Student passes exam (score >= passing_score)
3. **Expected**: 
   - Certification created/updated
   - status = 'passed'
   - issued_at set
   - passing_exam_attempt linked
4. **Verify**: 
   - Certification appears in student certifications page
   - Trophy tier updated if applicable

### ✅ Certification Display
1. **Navigate**: Student Dashboard → My Certifications
2. **Expected**: 
   - All passed certifications listed
   - Trophy tiers displayed
   - Current tier highlighted
   - Next tier progress shown
3. **Verify**: All certifications visible

### ✅ Accredible Integration (Stub)
1. **Setup**: Course with is_accredible_certified: True, ACCREDIBLE_API_KEY set
2. **Action**: Student passes exam
3. **Expected**: 
   - Certification issued
   - accredible_certificate_id generated (stub)
   - accredible_certificate_url generated (stub)
4. **Verify**: Certificate fields populated (even if stub)

---

## Phase 6: Prerequisite Enforcement

### ✅ Prerequisites Not Met - Course Access
1. **Setup**: 
   - Course B has prerequisite Course A
   - Student has not completed Course A
2. **Navigate**: Student → Course B detail page
3. **Expected**: 
   - Yellow warning box displayed
   - Lists missing prerequisites: "Course A"
   - Cannot access lessons
4. **Verify**: Prerequisites clearly shown

### ✅ Prerequisites Not Met - Lesson Access
1. **Setup**: Same as above
2. **Action**: Try to access lesson in Course B (via direct URL)
3. **Expected**: 
   - Warning message: "You must complete the following prerequisite courses: Course A"
   - Redirected to course detail page
4. **Verify**: Lesson access blocked

### ✅ Prerequisites Met
1. **Setup**: 
   - Course B has prerequisite Course A
   - Student completed all lessons in Course A
2. **Navigate**: Student → Course B
3. **Expected**: 
   - No prerequisite warning
   - Can access all lessons
4. **Verify**: Full access granted

---

## Integration Tests

### ✅ End-to-End: Course Completion → Exam → Certification
1. **Setup**: Course with lessons, quiz, exam
2. **Actions**:
   - Complete all lessons
   - Pass all required quizzes
   - Pass final exam
3. **Expected**: 
   - Course shows 100% progress
   - Certification issued
   - Trophy tier updated
4. **Verify**: Complete flow works

### ✅ Access Control + Prerequisites
1. **Setup**: 
   - Course A (public)
   - Course B (requires Course A, purchase required)
2. **Actions**:
   - Student completes Course A
   - Admin grants access to Course B
3. **Expected**: 
   - Prerequisites met
   - Access granted
   - Can view Course B
4. **Verify**: Both checks work together

---

## Edge Cases

### ✅ Empty Quiz/Exam
1. **Action**: Create quiz/exam with no questions
2. **Expected**: 
   - Quiz/exam created
   - Student sees "No questions yet" message
   - Cannot submit empty quiz/exam
3. **Verify**: Handles gracefully

### ✅ All Questions Correct
1. **Action**: Answer all questions correctly
2. **Expected**: Score = 100%, Pass
3. **Verify**: Correct calculation

### ✅ All Questions Wrong
1. **Action**: Answer all questions incorrectly
2. **Expected**: Score = 0%, Fail
3. **Verify**: Correct calculation

### ✅ Time Limit Expired
1. **Setup**: Exam with 1 minute time limit
2. **Action**: Wait for timer to expire
3. **Expected**: Exam auto-submits with current answers
4. **Verify**: Submission happens, time recorded

---

## Notes

- All tests should be performed as both admin and student users
- Use Django admin to verify database records
- Check console for JavaScript errors
- Verify CSRF tokens work correctly
- Test with different user roles (staff vs regular user)

