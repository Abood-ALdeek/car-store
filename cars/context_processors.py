from .models import SiteSettings
from .translations import DEFAULT_LANG, texts_for


def site(request):
    lang = getattr(request, "LANG", DEFAULT_LANG)
    s = SiteSettings.load()
    en = lang == "en"
    return {
        "lang": lang,
        "dir": "ltr" if en else "rtl",
        "t": texts_for(lang),
        "site": s,
        "site_name": s.name_en if en else s.name_ar,
        "site_slogan": s.slogan_en if en else s.slogan_ar,
        "site_address": s.address_en if en else s.address_ar,
        "site_hours": s.hours_en if en else s.hours_ar,
        "currency": s.currency_en if en else s.currency_ar,
    }
