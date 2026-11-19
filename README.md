<p align="center">
  <img src="static/img/logo-mark.svg" alt="Car Store" width="150">
</p>

<h1 align="center">Car Store · Car Dealership Website</h1>

<p align="center">
  A bilingual (Arabic / English) website for a car dealership that sells <b>new and used cars</b>.<br>
  Visitors browse and filter cars, open a full details page and contact the showroom by <b>phone, WhatsApp or a form</b>.<br>
  The owner manages cars, photos, messages and all site texts from an Arabic admin panel, no coding needed.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white">
  <img alt="Django" src="https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white">
  <img alt="SQLite" src="https://img.shields.io/badge/SQLite-database-003B57?logo=sqlite&logoColor=white">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white">
  <img alt="JavaScript" src="https://img.shields.io/badge/JavaScript-vanilla-F7DF1E?logo=javascript&logoColor=black">
  <img alt="RTL" src="https://img.shields.io/badge/Arabic-RTL-c8102e">
</p>

<p align="center">
  <a href="https://www.linkedin.com/feed/update/urn:li:activity:7529216804431421440/">
    <img alt="Watch the project video on LinkedIn" src="https://img.shields.io/badge/Watch%20the%20video-LinkedIn-0A66C2?logo=linkedin&logoColor=white">
  </a>
</p>

<p align="center">
  <img src="docs/screenshots/cover.png" alt="Car Store on desktop and mobile" width="900">
</p>

---

## Screenshots

| Home (desktop) | Arabic · mobile |
|---|---|
| <img src="docs/screenshots/home-desktop.png" width="560"> | <img src="docs/screenshots/home-arabic-mobile.png" width="240"> |

| Car details | All cars with filters | Car page · Arabic mobile |
|---|---|---|
| <img src="docs/screenshots/car-page.png" width="360"> | <img src="docs/screenshots/cars-list.png" width="360"> | <img src="docs/screenshots/car-page-arabic-mobile.png" width="200"> |

| Admin dashboard | Admin · cars |
|---|---|
| <img src="docs/screenshots/admin-dashboard.png" width="440"> | <img src="docs/screenshots/admin-cars.png" width="440"> |

## Features

**For visitors**
- Arabic ⇄ English switch with a full right-to-left layout for Arabic
- Home page with a photo **slideshow** of featured cars (fade + slow zoom, swipe on phones), live price card and animated counters
- Search by brand or model, filters for new / used, brand, max price and year, plus sorting and paging
- Car page: photo gallery, price, specs with icons (year, mileage, gearbox, fuel, engine, color), share button
- Contact the showroom in one tap: **call**, **WhatsApp** (message pre-filled with the car and its link) or an inquiry form
- About and contact pages, map, opening hours, floating WhatsApp button
- Smooth animations: page loading bar, scroll reveal, hover effects; works on any screen size
- Custom logo: a car driving out of a shopping bag

**For the dealership owner (admin panel, in Arabic)**
- Dashboard with stats (cars available, sold, new messages, brands), latest messages and latest cars
- Add / edit cars with a main photo and extra photos, mark them featured, sold or hidden
- Customer messages inbox: opening a message marks it read, one-click **reply on WhatsApp** or call
- Site settings: store name, logo, slogan, phone, WhatsApp, address, hours, map, currency, "About us" text in both languages

**Security & reliability**
- CSRF protection on every form, honeypot field against spam bots
- Secrets and settings from environment variables, secure cookies behind HTTPS
- Safe redirects on the language switch, custom 404 page
- Docker health check and automatic restart

## Tech stack

| Layer | Tools |
|---|---|
| Backend | Python 3.12, Django 5.2, Gunicorn |
| Database | SQLite |
| Frontend | Django templates, plain CSS (RTL/LTR), vanilla JavaScript, inline SVG icons |
| Images & static files | Pillow, WhiteNoise |
| Deployment | Docker / Docker Compose on a Linux server, Cloudflare Tunnel |

## Run it yourself

**With Docker**
```bash
git clone https://github.com/Abood-ALdeek/car-store.git
cd car-store
cp .env.example .env      # then set DJANGO_SECRET_KEY and DJANGO_ALLOWED_HOSTS
docker compose up -d --build
docker compose exec carstore python manage.py createsuperuser
```
Then open `http://localhost:8095` (admin panel at `/admin/`).

**Without Docker**
```bash
python -m venv .venv
.venv/Scripts/activate        # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
python manage.py migrate
python manage.py create_admin  # creates the "admin" user, password saved in ADMIN-LOGIN.txt
python manage.py seed_demo     # optional: adds demo cars with generated pictures
python manage.py runserver
```

On Windows, `launcher.pyw` runs the site hidden in the background with a guard that restarts it if it stops (`run.bat`, `run.bat admin`, `run.bat stop`).

## Project structure

```
cars/            the app: models, views, admin, forms, translations, template tags
  templates/     public pages (home, cars, car page, about, contact)
templates/admin/ custom admin theme and dashboard
static/          CSS, JavaScript, logo
config/          Django settings and URLs
```

---

<p align="center">Built by <b>Abood Aldeek</b></p>
