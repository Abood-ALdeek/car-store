from django.utils import translation

from .translations import DEFAULT_LANG, LANGS


class SiteLanguageMiddleware:
    """Use the visitor's chosen language (cookie) on the public site; keep the admin in Arabic."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = request.COOKIES.get("lang", DEFAULT_LANG)
        if lang not in LANGS:
            lang = DEFAULT_LANG
        request.LANG = lang
        translation.activate("ar" if request.path.startswith("/admin") else lang)
        response = self.get_response(request)
        translation.deactivate()
        return response
