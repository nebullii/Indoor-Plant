import json
from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape
import re

register = template.Library()

def is_safe_url(url):
    """
    Check if URL is safe (basic validation)
    """
    if not url:
        return False
    
    # Allow data URLs for images (base64)
    if url.startswith('data:image/'):
        return True
    
    # Allow HTTP/HTTPS URLs only
    if not re.match(r'^https?://', url):
        return False
    
    # Block javascript: and other dangerous protocols
    dangerous_protocols = ['javascript:', 'data:text/', 'vbscript:', 'file:', 'ftp:']
    url_lower = url.lower()
    for protocol in dangerous_protocols:
        if protocol in url_lower:
            return False
    
    return True

@register.filter
def quill_to_html(value):
    """
    Convert Quill JSON content to HTML (XSS-safe)
    """
    if not value:
        return ""
    
    try:
        # Try to parse as JSON
        content = json.loads(value)
        if isinstance(content, dict) and 'ops' in content:
            # Extract text from Quill JSON
            text = ""
            for op in content['ops']:
                if 'insert' in op:
                    if isinstance(op['insert'], str):
                        # Escape HTML in text content
                        text += escape(op['insert'])
                    elif isinstance(op['insert'], dict) and 'image' in op['insert']:
                        # SECURITY: Validate and escape image URLs
                        image_url = op['insert'].get('image', '')
                        if is_safe_url(image_url):
                            # Escape the URL to prevent XSS
                            safe_url = escape(image_url)
                            text += f'<img src="{safe_url}" alt="User Image" style="max-width:100%;height:auto;">'
                        else:
                            text += '<span class="text-muted">[Invalid Image]</span>'
            
            # Convert line breaks to <br> tags (text is already escaped)
            text = text.replace('\n', '<br>')
            return mark_safe(text)
        else:
            # If it's not Quill JSON, return as escaped plain text
            return mark_safe(escape(value).replace('\n', '<br>'))
    except (json.JSONDecodeError, TypeError):
        # If it's not valid JSON, return as escaped plain text
        return mark_safe(escape(value).replace('\n', '<br>'))

@register.filter
def quill_to_text(value):
    """
    Convert Quill JSON content to plain text
    """
    if not value:
        return ""
    
    try:
        # Try to parse as JSON
        content = json.loads(value)
        if isinstance(content, dict) and 'ops' in content:
            # Extract text from Quill JSON
            text = ""
            for op in content['ops']:
                if 'insert' in op and isinstance(op['insert'], str):
                    text += op['insert']
            return text
        else:
            # If it's not Quill JSON, return as is
            return value
    except (json.JSONDecodeError, TypeError):
        # If it's not valid JSON, return as is
        return value 