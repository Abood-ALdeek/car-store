from urllib.parse import quote

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Line icons (24x24, stroke = currentColor)
ICONS = {
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18"/>',
    "gauge": '<path d="M12 14l4-4"/><path d="M3.3 17a9 9 0 1 1 17.4 0"/><circle cx="12" cy="14" r="1.2"/>',
    "gear": '<circle cx="6" cy="6" r="2"/><circle cx="12" cy="6" r="2"/><circle cx="18" cy="6" r="2"/><circle cx="6" cy="18" r="2"/><circle cx="12" cy="18" r="2"/><path d="M6 8v8M12 8v8M18 8v4H6"/>',
    "fuel": '<path d="M4 21V5a2 2 0 0 1 2-2h7a2 2 0 0 1 2 2v16M3 21h13M4 11h11"/><path d="M15 8l3 3v6a1.5 1.5 0 0 0 3 0V9l-3-3"/>',
    "engine": '<path d="M5 9h3V7h6v2h2l2 2h2v6h-2l-2 2H8l-3-3z"/><path d="M2 12h3"/>',
    "palette": '<path d="M12 3a9 9 0 1 0 0 18c1.1 0 1.5-.8 1.5-1.5 0-.9-.6-1.2-.6-2 0-.9.7-1.5 1.6-1.5H17a4 4 0 0 0 4-4c0-4.9-4-9-9-9Z"/><circle cx="7.5" cy="11" r="1"/><circle cx="10" cy="7.5" r="1"/><circle cx="14.5" cy="7.5" r="1"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    "tag": '<path d="M3 12V4a1 1 0 0 1 1-1h8l9 9-9 9z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
    "car": '<path d="M5 17H3v-5l2-5h11l3 5h2v5h-2"/><circle cx="7.5" cy="17" r="2"/><circle cx="16.5" cy="17" r="2"/><path d="M9.5 17h5M5 12h14"/>',
    "headset": '<path d="M4 14v-2a8 8 0 0 1 16 0v2"/><rect x="2.5" y="14" width="4" height="6" rx="1.5"/><rect x="17.5" y="14" width="4" height="6" rx="1.5"/><path d="M20 20c0 1-1 2-3 2h-3"/>',
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
    "pin": '<path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "key": '<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M16 7l3 3M14 9l2 2"/>',
    "list": '<path d="M9 6h11M9 12h11M9 18h11"/><circle cx="4.5" cy="6" r="1"/><circle cx="4.5" cy="12" r="1"/><circle cx="4.5" cy="18" r="1"/>',
    "sliders": '<path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0"/><circle cx="16" cy="6" r="2"/><circle cx="10" cy="12" r="2"/><circle cx="18" cy="18" r="2"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.5 3.8 5.5 3.8 9s-1.3 6.5-3.8 9c-2.5-2.5-3.8-5.5-3.8-9S9.5 5.5 12 3z"/>',
    "share": '<circle cx="18" cy="5" r="2.5"/><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="19" r="2.5"/><path d="M8.2 10.8l7.6-4.4M8.2 13.2l7.6 4.4"/>',
}


@register.simple_tag
def icon(name, size=20, cls="icon"):
    """{% icon "gauge" %} -> inline SVG line icon"""
    body = ICONS.get(name, "")
    return mark_safe(
        f'<svg class="{cls}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" '
        f'aria-hidden="true">{body}</svg>'
    )


@register.simple_tag(takes_context=True)
def tr(context, obj, field):
    """{% tr car "description" %} -> description_ar or description_en, falling back to the other language."""
    lang = context.get("lang", "ar")
    other = "ar" if lang == "en" else "en"
    return getattr(obj, f"{field}_{lang}", "") or getattr(obj, f"{field}_{other}", "")


@register.simple_tag(takes_context=True)
def label(context, prefix, value):
    """{% label "fuel" car.fuel %} -> the translated text for fuel_petrol, etc."""
    return context["t"].get(f"{prefix}_{value}", value)


@register.filter
def num(value):
    """1234567 -> 1,234,567"""
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return value


@register.filter
def urlq(value):
    return quote(str(value))


@register.simple_tag(takes_context=True)
def query(context, **kwargs):
    """Keep the current filters in the URL while changing one value (used for paging)."""
    params = context["request"].GET.copy()
    for key, val in kwargs.items():
        params[key] = val
    return params.urlencode()


@register.simple_tag
def admin_dashboard():
    """Numbers and recent items for the admin home page."""
    from cars.models import Brand, Car, ContactMessage

    cars = Car.objects.select_related("brand")
    return {
        "available": cars.filter(is_sold=False, is_published=True).count(),
        "sold": cars.filter(is_sold=True).count(),
        "hidden": cars.filter(is_published=False).count(),
        "unread": ContactMessage.objects.filter(is_read=False).count(),
        "messages_total": ContactMessage.objects.count(),
        "brands": Brand.objects.count(),
        "latest_messages": ContactMessage.objects.select_related("car", "car__brand")[:6],
        "latest_cars": cars.order_by("-created")[:6],
    }
