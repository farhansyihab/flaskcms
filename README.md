# FlaskCMS

FlaskCMS adalah Content Management System (CMS) berbasis **Flask** yang dirancang ringan, modular, dan mendukung **Static Site Generation (SSG)** melalui proses *bakery*.

Proyek ini memisahkan dengan tegas:

* **Aplikasi Admin (Dynamic)** → untuk pengelolaan konten
* **Website Publik (Static HTML)** → hasil bake SSG

Pendekatan ini membuat website publik sangat cepat, aman, dan murah untuk di-host.

---

## ✨ Fitur Utama

* Manajemen halaman (Pages)
* Manajemen artikel / berita
* SEO-friendly (meta title, description, sitemap)
* Social media preview (OG tags)
* Search berbasis JSON (static search)
* Static Site Generator (mirip Wagtail Bakery)
* Pagination artikel (SSG)
* RSS / Feed XML
* Role-based admin (opsional)

---

## 🏗 Arsitektur

```
FlaskCMS
├── app/                # Aplikasi Flask (admin + public preview)
├── bakery/             # Engine Static Site Generator
├── backups/            # Firestore JSON backup
├── templates/          # Template Jinja2
├── static/             # Asset statis (CSS, JS, images)
├── bake.py             # CLI untuk proses SSG
└── run.py              # Menjalankan FlaskCMS
```

---

## ⚙️ Kebutuhan Sistem

* Python >= 3.9
* Virtualenv (disarankan)

---

## 🚀 Instalasi

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## ▶️ Menjalankan Aplikasi

```bash
python3 run.py
```

Akses admin:

```
http://localhost:5000/admin
```

---

## 🧁 Static Site Generation (Bakery)

FlaskCMS menggunakan **Firestore JSON backup** sebagai sumber data untuk menghasilkan HTML statis.

### Contoh perintah bake:

```bash
python3 bake.py --backup backups/firestore_backup.json --output dist
```

Hasil bake akan berada di folder:

```
dist/
```

---

## 🔒 Keamanan

* Website publik **tidak membutuhkan database**
* Admin dapat dijalankan secara lokal / terbatas
* Cocok untuk deployment Cloud Run + Cloudflare

---

## 🎯 Tujuan Proyek

* Alternatif ringan dari Django + Wagtail
* Cocok untuk website pemerintahan, sekolah, organisasi
* Fokus pada performa, kesederhanaan, dan kontrol penuh

---

