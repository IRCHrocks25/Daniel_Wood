"""
Template filter for rendering Editor.js blocks to HTML
"""
import json
from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape

register = template.Library()


def _render_inline_text(text_data):
    """
    Render Editor.js inline text data (can be string or array with inline formatting).
    Handles: links, bold, italic
    """
    if isinstance(text_data, str):
        # Simple string - escape and return
        return escape(text_data)
    
    if isinstance(text_data, list):
        # Array format with inline formatting
        html_parts = []
        for fragment in text_data:
            if isinstance(fragment, dict):
                text = fragment.get('text', '')
                escaped_text = escape(text)
                
                # Handle links
                link_data = fragment.get('link')
                if link_data:
                    url = link_data if isinstance(link_data, str) else link_data.get('url', '')
                    if url:
                        escaped_text = f'<a href="{escape(url)}" target="_blank" rel="noopener noreferrer" class="text-purple-600 hover:text-purple-700 underline">{escaped_text}</a>'
                
                # Handle bold/italic
                if fragment.get('bold'):
                    escaped_text = f'<strong>{escaped_text}</strong>'
                if fragment.get('italic'):
                    escaped_text = f'<em>{escaped_text}</em>'
                
                html_parts.append(escaped_text)
        return ''.join(html_parts)
    
    return escape(str(text_data))


def _render_block(block):
    """Render a single Editor.js block to HTML"""
    block_type = block.get('type', '')
    block_data = block.get('data', {})
    
    if block_type == 'paragraph':
        text_data = block_data.get('text', '')
        rendered_text = _render_inline_text(text_data)
        return f'<p class="mb-4 text-slate leading-relaxed">{rendered_text}</p>'
    
    elif block_type == 'header':
        level = block_data.get('level', 2)
        text_data = block_data.get('text', '')
        rendered_text = _render_inline_text(text_data)
        
        if level == 1:
            return f'<h1 class="text-4xl font-bold mt-8 mb-4 text-ink">{rendered_text}</h1>'
        elif level == 2:
            return f'<h2 class="text-3xl font-bold mt-8 mb-4 text-ink">{rendered_text}</h2>'
        elif level == 3:
            return f'<h3 class="text-2xl font-semibold mt-6 mb-3 text-ink">{rendered_text}</h3>'
        elif level == 4:
            return f'<h4 class="text-xl font-semibold mt-6 mb-3 text-ink">{rendered_text}</h4>'
        elif level == 5:
            return f'<h5 class="text-lg font-semibold mt-4 mb-2 text-ink">{rendered_text}</h5>'
        else:
            return f'<h6 class="text-base font-semibold mt-4 mb-2 text-ink">{rendered_text}</h6>'
    
    elif block_type == 'list':
        style = block_data.get('style', 'unordered')
        items = block_data.get('items', [])
        items_html = ''.join([f'<li class="mb-2">{_render_inline_text(item)}</li>' for item in items])
        
        if style == 'ordered':
            return f'<ol class="list-decimal pl-6 mb-4 space-y-2">{items_html}</ol>'
        else:
            return f'<ul class="list-disc pl-6 mb-4 space-y-2">{items_html}</ul>'
    
    elif block_type == 'quote':
        text = block_data.get('text', '')
        caption = block_data.get('caption', '')
        rendered_text = _render_inline_text(text)
        caption_html = f'<div class="text-sm text-slate mt-2 italic">{escape(caption)}</div>' if caption else ''
        return f'<blockquote class="border-l-4 border-purple-500 pl-4 italic my-6 text-slate">{rendered_text}{caption_html}</blockquote>'
    
    elif block_type == 'code':
        code = block_data.get('code', '')
        return f'<pre class="bg-slate-900 text-slate-100 rounded-lg p-4 overflow-auto my-4"><code class="text-sm">{escape(code)}</code></pre>'
    
    elif block_type == 'table':
        content = block_data.get('content', [])
        if not content:
            return ''
        
        rows_html = ''
        for row in content:
            cells_html = ''.join([f'<td class="border border-glass px-4 py-2">{_render_inline_text(cell)}</td>' for cell in row])
            rows_html += f'<tr>{cells_html}</tr>'
        
        return f'<div class="overflow-x-auto my-6"><table class="min-w-full border-collapse border border-glass"><tbody>{rows_html}</tbody></table></div>'
    
    elif block_type == 'image':
        file_data = block_data.get('file', {})
        url = file_data.get('url') if file_data else block_data.get('url', '')
        caption = block_data.get('caption', '')
        
        if url:
            caption_html = f'<figcaption class="text-sm text-slate mt-2 text-center">{escape(caption)}</figcaption>' if caption else ''
            return f'<figure class="my-6"><img src="{escape(url)}" alt="{escape(caption)}" class="rounded-xl shadow-lg w-full max-w-4xl mx-auto" loading="lazy"/>{caption_html}</figure>'
        return ''
    
    elif block_type == 'delimiter':
        return '<hr class="my-8 border-glass"/>'
    
    elif block_type == 'raw':
        html = block_data.get('html', '')
        return f'<div class="my-4">{html}</div>'
    
    return ''


@register.filter
def render_editorjs(value):
    """
    Convert Editor.js blocks JSON to HTML.
    
    Usage in template:
    {{ lesson.content|render_editorjs }}
    """
    if not value:
        return ""
    
    try:
        # Handle both dict and JSON string
        if isinstance(value, str):
            data = json.loads(value)
        else:
            data = value
        
        if not isinstance(data, dict):
            return ""
        
        blocks = data.get('blocks', [])
        if not blocks:
            return ""
        
        html = ''.join([_render_block(block) for block in blocks])
        return mark_safe(html)
    
    except (json.JSONDecodeError, TypeError, AttributeError):
        return ""

