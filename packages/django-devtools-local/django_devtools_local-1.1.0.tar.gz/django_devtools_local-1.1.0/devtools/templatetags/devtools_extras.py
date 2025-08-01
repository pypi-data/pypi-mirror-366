from django import template

register = template.Library()


@register.filter
def lookup(dictionary, key):
    """
    Filter to access dictionary values with dynamic key
    Usage: {{ dict|lookup:key }}
    """
    if hasattr(dictionary, 'get'):
        return dictionary.get(key, '')
    return ''


@register.filter
def multiply(value, arg):
    """
    Multiply two values
    Usage: {{ value|multiply:arg }}
    """
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def percentage(value, total):
    """
    Calculate percentage
    Usage: {{ value|percentage:total }}
    """
    try:
        if total == 0:
            return 0
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.simple_tag
def get_item(dictionary, key):
    """
    Tag to get an item from dictionary
    Usage: {% get_item dict key %}
    """
    return dictionary.get(key, '')


@register.inclusion_tag('devtools/partials/stats_card.html')
def stats_card(title, value, icon, color='primary'):
    """
    Inclusion tag to display statistics card
    Usage: {% stats_card "Title" value "bi-icon" "primary" %}
    """
    return {
        'title': title,
        'value': value,
        'icon': icon,
        'color': color
    }


@register.filter
def truncate_sql(value, length=100):
    """
    Intelligently truncate SQL query
    """
    if len(value) <= length:
        return value
    
    # Try to cut at SQL keyword
    sql_keywords = ['SELECT', 'FROM', 'WHERE', 'ORDER BY', 'GROUP BY', 'HAVING']
    
    truncated = value[:length]
    for keyword in sql_keywords:
        pos = truncated.rfind(keyword)
        if pos > length // 2:  # If keyword found in second half
            return value[:pos] + '...'
    
    return truncated + '...'


@register.filter
def format_bytes(value):
    """
    Format byte size in readable format
    Usage: {{ size_in_bytes|format_bytes }}
    """
    try:
        value = float(value)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if value < 1024.0:
                return f"{value:.1f} {unit}"
            value /= 1024.0
        return f"{value:.1f} PB"
    except (ValueError, TypeError):
        return value


@register.filter
def dict_key(dictionary, key):
    """
    Alternative to lookup filter for compatibility
    """
    return lookup(dictionary, key) 