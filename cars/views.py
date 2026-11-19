from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import ContactForm
from .models import Brand, Car
from .translations import LANGS, texts_for

SORTS = {
    "new": ["-created"],
    "price_asc": [F("price").asc(nulls_last=True)],
    "price_desc": [F("price").desc(nulls_last=True)],
    "year": ["-year", "-created"],
    "km": ["mileage"],
}


def available_cars():
    return Car.objects.filter(is_published=True).select_related("brand")


def home(request):
    cars = available_cars()
    for_sale = cars.filter(is_sold=False)
    stats = for_sale.aggregate(
        total=Count("id"),
        new=Count("id", filter=Q(condition=Car.NEW)),
        used=Count("id", filter=Q(condition=Car.USED)),
    )
    brands = Brand.objects.filter(cars__in=for_sale).distinct()
    stats["brands"] = brands.count()
    featured = list(for_sale.filter(is_featured=True)[:6])
    # Slideshow: cars with a photo, featured ones first, up to 5.
    slides = [c for c in featured if c.main_image]
    if len(slides) < 5:
        more = for_sale.exclude(main_image="").exclude(pk__in=[c.pk for c in slides]).order_by("-created")
        slides += list(more[:5 - len(slides)])
    hero_car = slides[0] if slides else None
    return render(request, "cars/home.html", {
        "brands": Brand.objects.annotate(
            n=Count("cars", filter=Q(cars__is_sold=False, cars__is_published=True))
        ).filter(n__gt=0),
        "hero_car": hero_car,
        "slides": slides,
        "years": range(timezone.now().year + 1, 2004, -1),
        "featured": featured,
        "latest": for_sale.order_by("-created")[:6],
        "stats": stats,
        "page": "home",
    })


def car_list(request):
    cars = available_cars()
    g = request.GET

    q = g.get("q", "").strip()
    if q:
        cars = cars.filter(
            Q(model_name__icontains=q) | Q(brand__name_ar__icontains=q) | Q(brand__name_en__icontains=q)
        )
    condition = g.get("condition", "")
    if condition in (Car.NEW, Car.USED):
        cars = cars.filter(condition=condition)
    brand = g.get("brand", "")
    if brand.isdigit():
        cars = cars.filter(brand_id=int(brand))
    max_price = g.get("max_price", "")
    if max_price.isdigit():
        cars = cars.filter(price__lte=int(max_price))
    min_year = g.get("min_year", "")
    if min_year.isdigit():
        cars = cars.filter(year__gte=int(min_year))
    sort = g.get("sort", "new")
    cars = cars.order_by("is_sold", *SORTS.get(sort, SORTS["new"]))

    page_obj = Paginator(cars, 12).get_page(g.get("page"))
    return render(request, "cars/car_list.html", {
        "page_obj": page_obj,
        "brands": Brand.objects.filter(cars__is_published=True).distinct(),
        "f": {"q": q, "condition": condition, "brand": brand, "max_price": max_price,
              "min_year": min_year, "sort": sort},
        "sorts": list(SORTS),
        "years": range(timezone.now().year + 1, 2004, -1),
        "filtered": any([q, condition, brand, max_price, min_year]),
        "page": "cars",
    })


def car_detail(request, pk):
    car = get_object_or_404(available_cars().prefetch_related("images"), pk=pk)
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if not form.is_spam():
            msg = form.save(commit=False)
            msg.car = car
            msg.save()
        messages.success(request, texts_for(request.LANG)["sent_ok"])
        return redirect(car.get_absolute_url() + "#ask")
    similar = (available_cars().filter(is_sold=False)
               .filter(Q(brand=car.brand) | Q(condition=car.condition))
               .exclude(pk=car.pk)[:3])
    return render(request, "cars/car_detail.html", {
        "car": car, "form": form, "similar": similar, "page": "cars",
    })


def about(request):
    return render(request, "cars/about.html", {"page": "about"})


def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if not form.is_spam():
            form.save()
        messages.success(request, texts_for(request.LANG)["sent_ok"])
        return redirect("contact")
    return render(request, "cars/contact.html", {"form": form, "page": "contact"})


def set_language(request, code):
    nxt = request.GET.get("next", "/")
    if not url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        nxt = "/"
    response = HttpResponseRedirect(nxt)
    if code in LANGS:
        response.set_cookie("lang", code, max_age=365 * 24 * 3600, samesite="Lax")
    return response


def not_found(request, exception=None):
    return render(request, "cars/404.html", {"page": ""}, status=404)
