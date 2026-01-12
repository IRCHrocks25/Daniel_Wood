# Global Form Field Fix - Single Source of Truth

## Problem Identified
Form fields across the application were showing dark backgrounds with unreadable text because:
1. Some templates (like `course_detail.html`, `edit_lesson.html`) were missing explicit background color classes
2. Form fields were inheriting dark backgrounds from parent elements or browser defaults
3. No global styling was enforcing readable contrast

## Solution Applied

### Global CSS in `base.html`
Added comprehensive CSS rules in `<head>` that apply to ALL form fields globally using `!important` to override any conflicting classes:

**Light Mode:**
- Background: `white`
- Text: `slate-900` (rgb(15 23 42))
- Border: `slate-200` (rgb(226 232 240))
- Placeholder: `slate-400` (rgb(148 163 184))

**Dark Mode:**
- Background: `slate-900` (rgb(15 23 42))
- Text: `slate-100` (rgb(241 245 249))
- Border: `slate-700` (rgb(51 65 85))
- Placeholder: `slate-500` (rgb(100 116 139))

### Coverage
The global styles apply to:
- ✅ All input types (text, email, password, number, url, tel, search, date, time, datetime-local)
- ✅ Textareas
- ✅ Selects
- ✅ File inputs
- ✅ Select options
- ✅ Autofill states (prevents browser from applying dark backgrounds)

### Key Features
1. **!important flags** ensure these styles override any template-level classes
2. **Autofill handling** prevents browsers from applying dark backgrounds with dark text
3. **Select options** are styled to remain readable in dropdowns
4. **Dark mode support** via `.dark` class selector

## Files Updated
1. **myApp/templates/base.html** - Added global form field styles
2. **myApp/templates/dashboard/course_detail.html** - Updated to use standardized classes (for consistency, though global styles handle it)

## Testing
To verify the fix:
1. Navigate to any form page (e.g., `/dashboard/courses/<course>/`)
2. Check the "Course Name" input field
3. Type text - it should be high-contrast and readable
4. Toggle dark mode (if available) - text should remain readable
5. Test autofill - should not show dark background with dark text

## Result
All form fields across Admin + Student + Login pages now inherit readable styling from the single source of truth in `base.html`, regardless of individual template classes.

