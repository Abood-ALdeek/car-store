from urllib.parse import quote

from django.contrib import admin
from django.utils.html import format_html

from .models import Brand, Car, CarImage, ContactMessage, SiteSettings

admin.site.site_url = "/"


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = [
        ("الاسم والشعار", {"fields": ["name_ar", "name_en", "slogan_ar", "slogan_en", "logo", "hero_image"]}),
        ("من نحن", {"fields": ["about_ar", "about_en"]}),
        ("التواصل", {"fields": ["phone", "whatsapp", "email", "address_ar", "address_en",
                                "hours_ar", "hours_en", "map_url", "facebook", "instagram"]}),
        ("العملة", {"fields": ["currency_ar", "currency_en"]}),
    ]

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name_ar", "name_en", "car_count"]
    search_fields = ["name_ar", "name_en"]

    @admin.display(description="عدد السيارات")
    def car_count(self, obj):
        return obj.cars.count()


class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 3
    fields = ["preview", "image", "order"]
    readonly_fields = ["preview"]

    @admin.display(description="معاينة")
    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html('<img class="thumb-img" src="{}">', obj.image.url)
        return "—"


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ["thumb", "title", "condition_pill", "price_display", "mileage_display",
                    "is_featured", "is_sold", "is_published"]
    list_display_links = ["thumb", "title"]
    list_editable = ["is_featured", "is_sold", "is_published"]
    list_filter = ["condition", "brand", "is_sold", "is_featured", "is_published", "fuel", "transmission"]
    search_fields = ["model_name", "brand__name_ar", "brand__name_en"]
    list_select_related = ["brand"]
    list_per_page = 20
    inlines = [CarImageInline]
    actions = ["mark_sold", "mark_available", "mark_featured"]
    readonly_fields = ["image_preview"]
    save_on_top = True
    fieldsets = [
        ("البيانات الأساسية", {"fields": ["brand", "model_name", "year", "condition", "price"]}),
        ("المواصفات", {"fields": ["mileage", "transmission", "fuel", "engine", "color_ar", "color_en"]}),
        ("الوصف", {"fields": ["description_ar", "description_en"]}),
        ("الصورة الرئيسية", {"fields": ["image_preview", "main_image"]}),
        ("العرض على الموقع", {"fields": ["is_featured", "is_sold", "is_published"]}),
    ]

    @admin.display(description="صورة")
    def thumb(self, obj):
        if obj.main_image:
            return format_html('<img class="thumb-img" src="{}">', obj.main_image.url)
        return "—"

    @admin.display(description="السيارة", ordering="model_name")
    def title(self, obj):
        return format_html("<b>{} {}</b><br><small style='color:#64748b'>{}</small>",
                           obj.brand.name_ar, obj.model_name, obj.year)

    @admin.display(description="الحالة", ordering="condition")
    def condition_pill(self, obj):
        if obj.is_sold:
            return format_html('<span class="pill pill-sold">مباعة</span>')
        cls = "pill-new" if obj.condition == Car.NEW else "pill-used"
        return format_html('<span class="pill {}">{}</span>', cls, obj.get_condition_display())

    @admin.display(description="السعر", ordering="price")
    def price_display(self, obj):
        return f"{int(obj.price):,}" if obj.price else "عند الطلب"

    @admin.display(description="الممشى", ordering="mileage")
    def mileage_display(self, obj):
        return f"{obj.mileage:,} كم"

    @admin.display(description="المعاينة")
    def image_preview(self, obj):
        if obj.main_image:
            return format_html('<img class="preview-img" src="{}">', obj.main_image.url)
        return "لا توجد صورة بعد"

    @admin.action(description="تعليم كمباعة")
    def mark_sold(self, request, queryset):
        queryset.update(is_sold=True)

    @admin.action(description="تعليم كمتوفرة")
    def mark_available(self, request, queryset):
        queryset.update(is_sold=False)

    @admin.action(description="تعليم كمميزة")
    def mark_featured(self, request, queryset):
        queryset.update(is_featured=True)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["status", "sender", "car", "short_message", "created", "reply"]
    list_display_links = ["sender"]
    list_filter = ["is_read", "created"]
    search_fields = ["name", "phone", "message"]
    readonly_fields = ["name", "phone", "email", "message", "car", "created", "reply_buttons"]
    fields = ["reply_buttons", "name", "phone", "email", "car", "message", "created", "is_read"]
    actions = ["mark_read", "mark_unread"]
    list_select_related = ["car", "car__brand"]

    def change_view(self, request, object_id, form_url="", extra_context=None):
        # Opening a message marks it as read.
        ContactMessage.objects.filter(pk=object_id, is_read=False).update(is_read=True)
        return super().change_view(request, object_id, form_url, extra_context)

    @admin.display(description="الحالة", ordering="is_read")
    def status(self, obj):
        if obj.is_read:
            return format_html('<span class="pill pill-read">مقروءة</span>')
        return format_html('<span class="pill pill-unread">جديدة</span>')

    @admin.display(description="المرسل", ordering="name")
    def sender(self, obj):
        style = "font-weight:800" if not obj.is_read else ""
        return format_html('<span style="{}">{}</span><br><small dir="ltr" style="color:#64748b">{}</small>',
                           style, obj.name, obj.phone)

    @admin.display(description="الرسالة")
    def short_message(self, obj):
        return obj.message[:70]

    def _wa_number(self, phone):
        digits = "".join(ch for ch in phone if ch.isdigit())
        if digits.startswith("00"):
            digits = digits[2:]
        elif digits.startswith("0"):
            digits = "962" + digits[1:]  # local Jordanian number
        return digits

    @admin.display(description="رد")
    def reply(self, obj):
        text = quote(f"مرحباً {obj.name}، بخصوص رسالتك على موقعنا")
        return format_html(
            '<a class="button" style="background:#25d366;padding:6px 12px" target="_blank" rel="noopener" '
            'href="https://wa.me/{}?text={}">واتساب</a>', self._wa_number(obj.phone), text)

    @admin.display(description="الرد على الزبون")
    def reply_buttons(self, obj):
        text = quote(f"مرحباً {obj.name}، بخصوص رسالتك على موقعنا")
        return format_html(
            '<a class="button" style="background:#25d366" target="_blank" rel="noopener" href="https://wa.me/{}?text={}">رد عبر واتساب</a> '
            '<a class="button" href="tel:{}">اتصال</a>', self._wa_number(obj.phone), text, obj.phone)

    @admin.action(description="تعليم كمقروءة")
    def mark_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description="تعليم كغير مقروءة")
    def mark_unread(self, request, queryset):
        queryset.update(is_read=False)

    def has_add_permission(self, request):
        return False
