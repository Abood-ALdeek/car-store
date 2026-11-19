from django.db import models
from django.urls import reverse


class SiteSettings(models.Model):
    """One row holding the store's name, contact details and page texts."""

    name_ar = models.CharField("اسم المعرض (عربي)", max_length=100, default="معرض السيارات")
    name_en = models.CharField("اسم المعرض (إنجليزي)", max_length=100, default="Car Store")
    slogan_ar = models.CharField("الشعار (عربي)", max_length=200, default="سيارتك القادمة تبدأ من هنا")
    slogan_en = models.CharField("الشعار (إنجليزي)", max_length=200, default="Your next car starts here")
    about_ar = models.TextField(
        "من نحن (عربي)",
        default="نحن معرض متخصص في بيع السيارات الجديدة والمستعملة. نقدم لك سيارات مفحوصة "
        "بأسعار واضحة وخدمة صادقة، ونساعدك في اختيار السيارة المناسبة لك ولعائلتك.",
    )
    about_en = models.TextField(
        "من نحن (إنجليزي)",
        default="We are a dealership for new and used cars. We offer inspected cars at clear "
        "prices with honest service, and we help you choose the right car for you and your family.",
    )
    phone = models.CharField("رقم الهاتف", max_length=30, default="+000 0000 0000")
    whatsapp = models.CharField(
        "رقم واتساب (أرقام فقط مع رمز الدولة)", max_length=20, blank=True, default="",
        help_text="مثال: 962790000000",
    )
    email = models.EmailField("البريد الإلكتروني", blank=True, default="")
    address_ar = models.CharField("العنوان (عربي)", max_length=200, default="المدينة، الشارع")
    address_en = models.CharField("العنوان (إنجليزي)", max_length=200, default="City, Street")
    hours_ar = models.CharField("أوقات الدوام (عربي)", max_length=100, default="السبت - الخميس: 9 صباحاً - 9 مساءً")
    hours_en = models.CharField("أوقات الدوام (إنجليزي)", max_length=100, default="Sat - Thu: 9 AM - 9 PM")
    map_url = models.URLField(
        "رابط خريطة جوجل (للتضمين)", blank=True, default="", max_length=1000,
        help_text="من خرائط جوجل: مشاركة ← تضمين خريطة ← انسخ الرابط الموجود داخل src",
    )
    currency_ar = models.CharField("العملة (عربي)", max_length=20, default="دينار")
    currency_en = models.CharField("العملة (إنجليزي)", max_length=20, default="JOD")
    logo = models.ImageField("الشعار (صورة)", upload_to="site/", blank=True)
    hero_image = models.ImageField("صورة الواجهة الرئيسية", upload_to="site/", blank=True)
    facebook = models.URLField("فيسبوك", blank=True, default="")
    instagram = models.URLField("إنستغرام", blank=True, default="")

    class Meta:
        verbose_name = "إعدادات الموقع"
        verbose_name_plural = "إعدادات الموقع"

    def __str__(self):
        return self.name_ar

    def save(self, *args, **kwargs):
        self.pk = 1  # always a single row
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Brand(models.Model):
    name_ar = models.CharField("الاسم (عربي)", max_length=60)
    name_en = models.CharField("الاسم (إنجليزي)", max_length=60)

    class Meta:
        verbose_name = "ماركة"
        verbose_name_plural = "الماركات"
        ordering = ["name_en"]

    def __str__(self):
        return f"{self.name_ar} / {self.name_en}"


class Car(models.Model):
    NEW, USED = "new", "used"
    CONDITION_CHOICES = [(NEW, "جديدة"), (USED, "مستعملة")]
    AUTO, MANUAL = "auto", "manual"
    TRANSMISSION_CHOICES = [(AUTO, "أوتوماتيك"), (MANUAL, "عادي (يدوي)")]
    FUEL_CHOICES = [
        ("petrol", "بنزين"),
        ("diesel", "ديزل"),
        ("hybrid", "هايبرد"),
        ("electric", "كهرباء"),
    ]

    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="cars", verbose_name="الماركة")
    model_name = models.CharField("الموديل", max_length=80, help_text="مثال: Camry")
    year = models.PositiveSmallIntegerField("سنة الصنع")
    condition = models.CharField("الحالة", max_length=10, choices=CONDITION_CHOICES, default=USED)
    price = models.DecimalField("السعر", max_digits=12, decimal_places=0, null=True, blank=True,
                                help_text="اتركه فارغاً لعرض «السعر عند الطلب»")
    mileage = models.PositiveIntegerField("الممشى (كم)", default=0)
    transmission = models.CharField("ناقل الحركة", max_length=10, choices=TRANSMISSION_CHOICES, default=AUTO)
    fuel = models.CharField("الوقود", max_length=10, choices=FUEL_CHOICES, default="petrol")
    color_ar = models.CharField("اللون (عربي)", max_length=40, blank=True)
    color_en = models.CharField("اللون (إنجليزي)", max_length=40, blank=True)
    engine = models.CharField("المحرك", max_length=40, blank=True, help_text="مثال: 2.5L")
    description_ar = models.TextField("الوصف (عربي)", blank=True)
    description_en = models.TextField("الوصف (إنجليزي)", blank=True)
    main_image = models.ImageField("الصورة الرئيسية", upload_to="cars/", blank=True)
    is_featured = models.BooleanField("مميزة (تظهر في الصفحة الرئيسية)", default=False)
    is_sold = models.BooleanField("مباعة", default=False)
    is_published = models.BooleanField("منشورة على الموقع", default=True)
    created = models.DateTimeField("تاريخ الإضافة", auto_now_add=True)

    class Meta:
        verbose_name = "سيارة"
        verbose_name_plural = "السيارات"
        ordering = ["is_sold", "-created"]

    def __str__(self):
        return f"{self.brand.name_en} {self.model_name} {self.year}"

    def get_absolute_url(self):
        return reverse("car_detail", args=[self.pk])


class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="images", verbose_name="السيارة")
    image = models.ImageField("صورة", upload_to="cars/")
    order = models.PositiveSmallIntegerField("الترتيب", default=0)

    class Meta:
        verbose_name = "صورة إضافية"
        verbose_name_plural = "صور إضافية"
        ordering = ["order", "id"]


class ContactMessage(models.Model):
    name = models.CharField("الاسم", max_length=100)
    phone = models.CharField("الهاتف", max_length=30)
    email = models.EmailField("البريد", blank=True)
    message = models.TextField("الرسالة")
    car = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True, blank=True,
                            related_name="messages", verbose_name="عن سيارة")
    is_read = models.BooleanField("مقروءة", default=False)
    created = models.DateTimeField("التاريخ", auto_now_add=True)

    class Meta:
        verbose_name = "رسالة"
        verbose_name_plural = "رسائل الزبائن"
        ordering = ["-created"]

    def __str__(self):
        return f"{self.name} - {self.phone}"
