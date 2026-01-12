# Standardized Form Field Pattern

## Base Classes (Apply to ALL: input, textarea, select)

```html
class="w-full px-4 py-3 text-sm bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 border border-slate-200 dark:border-slate-700 rounded-xl shadow-sm hover:border-slate-300 dark:hover:border-slate-600 focus:ring-2 focus:ring-violet-500 focus:border-violet-500 focus:outline-none transition-all placeholder:text-slate-400 dark:placeholder:text-slate-500 disabled:opacity-60 disabled:cursor-not-allowed disabled:bg-slate-50 dark:disabled:bg-slate-900 disabled:text-slate-900 dark:disabled:text-slate-100"
```

## For Textarea (add min-height and resize)

Add: `min-h-[100px] resize-y` (or `min-h-[150px]` for larger textareas)

## For Select (add dropdown arrow)

Add: `pr-10 appearance-none bg-[url('data:image/svg+xml;charset=utf-8,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 fill=%27none%27 viewBox=%270 0 20 20%27%3E%3Cpath stroke=%27%236b7280%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27 stroke-width=%271.5%27 d=%27M6 8l4 4 4-4%27/%3E%3C/svg%3E')] bg-[length:1.5em_1.5em] bg-[right_0.75rem_center] bg-no-repeat`

## Label Pattern

```html
<label for="field_id" class="block text-sm font-medium text-slate-900 dark:text-slate-100 mb-2">
    Label Text <span class="text-rose-500">*</span> <!-- if required -->
</label>
```

## Help Text Pattern

```html
<p class="mt-2 text-xs text-slate-600 dark:text-slate-400">Help text here</p>
```

## Error State (add to base classes)

Replace border classes with:
```html
border-rose-400 dark:border-rose-500 focus:ring-rose-300/40 focus:border-rose-400
```

And add error text:
```html
<p class="mt-2 text-xs text-rose-600 dark:text-rose-400">Error message</p>
```

## Checkbox Pattern

```html
<input type="checkbox" name="field_name" id="field_id"
       class="w-4 h-4 text-violet-600 border-slate-200 dark:border-slate-700 rounded focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 cursor-pointer">
```

