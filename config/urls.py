from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path, re_path
from django.views.static import serve

admin.site.site_header = "لوحة تحكم معرض السيارات"
admin.site.site_title = "لوحة التحكم"
admin.site.index_title = "إدارة الموقع"

urlpatterns = [
    path("healthz", lambda request: HttpResponse("ok", content_type="text/plain")),
    path("admin/", admin.site.urls),
    path("", include("cars.urls")),
    # Uploaded car photos (small site: Django serves them itself, also in production).
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]

handler404 = "cars.views.not_found"
