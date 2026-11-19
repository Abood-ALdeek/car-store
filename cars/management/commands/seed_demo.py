"""Fill the site with demo cars (with generated studio pictures) so it doesn't look empty.

    python manage.py seed_demo           add demo data (only if there are no cars yet)
    python manage.py seed_demo --reset   delete ALL cars and brands first, then add demo data
    python manage.py seed_demo --images  only redraw the pictures of the demo cars
"""
import io
import math

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from cars.models import Brand, Car, SiteSettings

BRANDS = [
    ("تويوتا", "Toyota"), ("هيونداي", "Hyundai"), ("كيا", "Kia"), ("مرسيدس", "Mercedes-Benz"),
    ("بي إم دبليو", "BMW"), ("نيسان", "Nissan"), ("فورد", "Ford"), ("تسلا", "Tesla"),
]

# brand, model, year, condition, price, km, transmission, fuel, color_ar, color_en, engine, featured, sold, rgb, shape
CARS = [
    ("Toyota", "Camry", 2025, "new", 32500, 0, "auto", "hybrid", "أبيض لؤلؤي", "Pearl white", "2.5L Hybrid", True, False, (228, 230, 235), "sedan"),
    ("Hyundai", "Tucson", 2025, "new", 29900, 0, "auto", "petrol", "رمادي", "Grey", "2.0L", True, False, (112, 118, 128), "suv"),
    ("Mercedes-Benz", "C200", 2021, "used", 38000, 46000, "auto", "petrol", "أسود", "Black", "1.5L Turbo", True, False, (34, 36, 42), "sedan"),
    ("Kia", "Sportage", 2024, "new", 27500, 0, "auto", "petrol", "أحمر", "Red", "1.6L Turbo", False, False, (176, 22, 34), "suv"),
    ("BMW", "X5", 2020, "used", 45000, 72000, "auto", "diesel", "أزرق", "Blue", "3.0L", True, False, (28, 62, 140), "suv"),
    ("Nissan", "Altima", 2019, "used", 14500, 98000, "auto", "petrol", "فضي", "Silver", "2.5L", False, False, (170, 176, 184), "sedan"),
    ("Ford", "Ranger", 2022, "used", 26000, 51000, "manual", "diesel", "برتقالي", "Orange", "2.0L Bi-Turbo", False, False, (210, 98, 24), "suv"),
    ("Tesla", "Model 3", 2023, "used", 33000, 22000, "auto", "electric", "أبيض", "White", "", True, False, (240, 241, 244), "sedan"),
    ("Toyota", "Land Cruiser", 2018, "used", None, 135000, "auto", "petrol", "ذهبي", "Gold", "4.6L V8", False, False, (176, 148, 96), "suv"),
    ("Hyundai", "Elantra", 2017, "used", 9800, 160000, "auto", "petrol", "أسود", "Black", "1.6L", False, True, (38, 38, 44), "sedan"),
]

DESC_AR = ("سيارة بحالة ممتازة، مفحوصة بالكامل وجاهزة للاستخدام. صيانة دورية ونظافة عالية من الداخل والخارج.\n"
           "يمكنك زيارة المعرض لمعاينة السيارة وتجربتها.")
DESC_EN = ("Excellent condition, fully inspected and ready to drive. Regular servicing and very clean inside and out.\n"
           "Visit the showroom to see and test-drive the car.")

# Car shapes in a 200 x 100 design grid (front of the car is on the right).
SHAPES = {
    "sedan": {
        "body": [(6, 58), (7, 49), (12, 45), (30, 41), (50, 39), (64, 27), (78, 21.5), (112, 20.5), (127, 22.5),
                 (147, 36), (172, 40), (188, 45), (194, 52), (194, 60), (188, 63), (12, 63)],
        "windows": [[(57, 38.5), (68, 28.5), (80, 24.5), (98, 24), (98, 38.5)],
                    [(102, 38.5), (102, 24), (117, 24.5), (124, 27), (139, 38.5)]],
        "shoulder": 44.5,
    },
    "suv": {
        "body": [(5, 57), (5, 41), (9, 31), (19, 22.5), (40, 19), (121, 18), (135, 20.5), (153, 33.5), (176, 37.5),
                 (190, 42), (195, 50), (195, 60), (188, 63), (12, 63)],
        "windows": [[(14, 33.5), (22, 25.5), (40, 23), (64, 22.5), (64, 33.5)],
                    [(68, 33.5), (68, 22.5), (103, 22.3), (103, 33.5)],
                    [(107, 33.5), (107, 22.3), (126, 23), (132, 26), (145, 33.5)]],
        "shoulder": 40.5,
    },
}
WHEELS = (44, 156)
WHEEL_Y, WHEEL_R = 60, 11.5


def mix(c1, c2, k):
    return tuple(int(a + (b - a) * k) for a, b in zip(c1, c2))


def car_picture(rgb, shape="sedan", out=(1200, 840), ss=3):
    """Draw a studio picture of a car: spotlight backdrop, reflective floor, shaded paint, alloy wheels."""
    W, H = out[0] * ss, out[1] * ss
    floor_y = int(H * .76)

    # backdrop: dark gradient + soft spotlight
    bg = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        k = y / H
        d.line([(0, y), (W, y)], fill=mix((22, 28, 44), (52, 60, 78), k) if y < floor_y else mix((40, 46, 60), (16, 20, 30), (y - floor_y) / (H - floor_y)))
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse([W * .15, -H * .35, W * .85, H * .75], fill=120)
    glow = glow.filter(ImageFilter.GaussianBlur(W * .08))
    bg = Image.composite(Image.new("RGB", (W, H), (120, 132, 156)), bg, glow)
    d = ImageDraw.Draw(bg)
    d.line([(0, floor_y), (W, floor_y)], fill=(70, 78, 96), width=ss)

    # car layer
    s = W * .8 / 200
    ox = (W - 200 * s) / 2
    oy = floor_y - (WHEEL_Y + WHEEL_R) * s
    P = lambda x, y: (ox + x * s, oy + y * s)
    spec = SHAPES[shape]

    car = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon([P(*p) for p in spec["body"]], fill=255)
    paint = Image.new("RGB", (W, H))
    pd = ImageDraw.Draw(paint)
    top, bottom = oy + 18 * s, oy + 63 * s
    light, dark = mix(rgb, (255, 255, 255), .35), mix(rgb, (0, 0, 0), .45)
    for y in range(int(top), int(bottom) + 1):
        k = (y - top) / (bottom - top)
        col = mix(light, rgb, k / .45) if k < .45 else mix(rgb, dark, (k - .45) / .55)
        pd.line([(0, y), (W, y)], fill=col)
    car.paste(paint, (0, 0), mask)
    cd = ImageDraw.Draw(car)

    # wheel arches
    for wx in WHEELS:
        r = (WHEEL_R + 2.2) * s
        cx, cy = P(wx, WHEEL_Y)
        cd.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=(14, 14, 18, 255))
        cd.rectangle([cx - r, cy, cx + r, oy + 63 * s], fill=(14, 14, 18, 255))

    # lines: shoulder highlight, lower crease, door seam, sill
    sh = spec["shoulder"]
    cd.line([P(12, sh), P(188, sh - 1)], fill=mix(rgb, (255, 255, 255), .55) + (170,), width=int(1.2 * s))
    cd.line([P(14, 54), P(190, 53)], fill=mix(rgb, (0, 0, 0), .3) + (200,), width=int(.8 * s))
    cd.line([P(100, sh + 1), P(100, 61)], fill=mix(rgb, (0, 0, 0), .4) + (200,), width=int(.5 * s))
    cd.line([P(60, 61), P(140, 61)], fill=(20, 20, 24, 230), width=int(2 * s))

    # windows with a soft reflection
    for win in spec["windows"]:
        pts = [P(*p) for p in win]
        cd.polygon(pts, fill=(24, 32, 46, 255))
        wm = Image.new("L", (W, H), 0)
        ImageDraw.Draw(wm).polygon(pts, fill=255)
        refl = Image.new("L", (W, H), 0)
        x0 = min(p[0] for p in pts)
        ImageDraw.Draw(refl).polygon([(x0 + 4 * s, oy + 40 * s), (x0 + 14 * s, oy + 18 * s), (x0 + 20 * s, oy + 18 * s), (x0 + 10 * s, oy + 40 * s)], fill=70)
        car.paste(Image.new("RGBA", (W, H), (200, 220, 240, 255)), (0, 0), ImageChops.multiply(wm, refl))
    cd = ImageDraw.Draw(car)

    # lights and mirror
    front_x = 194 if shape == "sedan" else 195
    cd.polygon([P(front_x - 12, 45.5), P(front_x - 1, 48), P(front_x - 1, 51), P(front_x - 10, 50)], fill=(245, 245, 235, 255))
    cd.polygon([P(6.5, 47), P(13, 46), P(13, 50), P(7, 51)], fill=(200, 20, 30, 255))
    mx = 132 if shape == "sedan" else 140
    cd.polygon([P(mx, 35), P(mx + 6, 34), P(mx + 6, 38), P(mx, 38)], fill=mix(rgb, (0, 0, 0), .25) + (255,))

    # wheels
    for wx in WHEELS:
        cx, cy = P(wx, WHEEL_Y)
        R = WHEEL_R * s
        cd.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(16, 16, 18, 255))
        rr = R * .64
        cd.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(188, 192, 200, 255))
        cd.ellipse([cx - rr * .86, cy - rr * .86, cx + rr * .86, cy + rr * .86], fill=(60, 64, 72, 255))
        for i in range(5):
            a = math.radians(i * 72 - 90)
            cd.line([(cx, cy), (cx + math.cos(a) * rr * .86, cy + math.sin(a) * rr * .86)], fill=(200, 204, 212, 255), width=int(1.6 * s))
        h = rr * .26
        cd.ellipse([cx - h, cy - h, cx + h, cy + h], fill=(150, 154, 162, 255))

    # shadow + floor reflection
    shadow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shadow).ellipse([P(4, WHEEL_Y + WHEEL_R - 4)[0], P(0, WHEEL_Y + WHEEL_R - 4)[1], P(196, 0)[0], P(0, WHEEL_Y + WHEEL_R + 4)[1]], fill=210)
    shadow = shadow.filter(ImageFilter.GaussianBlur(5 * s))
    bg = Image.composite(Image.new("RGB", (W, H), (5, 7, 12)), bg, shadow)

    refl = car.transpose(Image.FLIP_TOP_BOTTOM)
    shift = int(2 * floor_y - H)
    refl_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    refl_layer.paste(refl, (0, shift), refl)
    fade = Image.new("L", (W, H), 0)
    fd = ImageDraw.Draw(fade)
    span = H - floor_y
    for y in range(floor_y, H):
        fd.line([(0, y), (W, y)], fill=int(55 * max(0, 1 - (y - floor_y) / (span * .55))))
    alpha = ImageChops.multiply(refl_layer.split()[3], fade)
    refl_layer.putalpha(alpha)
    bg = bg.convert("RGBA")
    bg.alpha_composite(refl_layer)
    bg.alpha_composite(car)

    img = bg.convert("RGB").resize(out, Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=88, optimize=True)
    return buf.getvalue()



def demo_filename(brand, model):
    return f"demo-{brand.lower()}-{model.lower().replace(' ', '-')}.jpg"


class Command(BaseCommand):
    help = "Add demo brands and cars"

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="delete all cars and brands first")
        parser.add_argument("--images", action="store_true", help="only redraw demo car pictures")

    def handle(self, *args, **opts):
        SiteSettings.load()
        if opts["images"]:
            return self.redraw()
        if opts["reset"]:
            Car.objects.all().delete()
            Brand.objects.all().delete()
        if Car.objects.exists():
            self.stdout.write("Cars already exist - nothing added. Use --reset to start over.")
            return

        brands = {en: Brand.objects.get_or_create(name_en=en, defaults={"name_ar": ar})[0] for ar, en in BRANDS}
        for (b, model, year, cond, price, km, trans, fuel, c_ar, c_en, eng, feat, sold, rgb, shape) in CARS:
            car = Car(
                brand=brands[b], model_name=model, year=year, condition=cond, price=price, mileage=km,
                transmission=trans, fuel=fuel, color_ar=c_ar, color_en=c_en, engine=eng,
                description_ar=DESC_AR, description_en=DESC_EN, is_featured=feat, is_sold=sold,
            )
            car.main_image.save(demo_filename(b, model), ContentFile(car_picture(rgb, shape)), save=False)
            car.save()
        self.stdout.write(self.style.SUCCESS(f"Added {len(CARS)} demo cars."))

    def redraw(self):
        """Redraw pictures only for cars that still use a demo picture (never touches real photos)."""
        specs = {(b, m): (rgb, shape) for (b, m, *_rest, rgb, shape) in CARS}
        done = 0
        for car in Car.objects.select_related("brand"):
            key = (car.brand.name_en, car.model_name)
            if key not in specs or not car.main_image.name.startswith("cars/demo-"):
                continue
            path = car.main_image.path
            with open(path, "wb") as fh:
                fh.write(car_picture(*specs[key]))
            done += 1
        self.stdout.write(self.style.SUCCESS(f"Redrew {done} demo pictures."))
