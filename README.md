# bot_influencer_NLP

Proyek deteksi bot/influencer palsu di Instagram & TikTok menggunakan analisis anomali engagement dan NLP terhadap komentar, dengan output berupa skor kredibilitas engagement yang ditampilkan melalui dashboard.

## Pembagian Tugas

### 1. Data / ML Engineer — Data & Algoritma Deteksi

**A. Pengumpulan Data**
- Membangun scraper (Instagram: instaloader/snscrape, atau resmi via Meta Graph API bila memungkinkan; TikTok: TikTok-Api/unofficial scraper).
- Mengumpulkan data profil (followers, following, jumlah post, bio), data post (likes, komentar, timestamp), dan data komentar (teks, username, waktu).
- Menyimpan data mentah ke format terstruktur (CSV/JSON) yang siap diproses backend.

**B. Preprocessing & Fitur**
- Membersihkan teks komentar (hapus emoji berlebih, normalisasi bahasa gaul, stopword removal Bahasa Indonesia/Inggris).
- Membuat fitur numerik: rasio follower/following, engagement rate, konsistensi waktu posting, keberagaman kata dalam komentar.

**C. Algoritma Deteksi**
- Deteksi anomali engagement (Isolation Forest, Z-score, atau clustering seperti DBSCAN) untuk menandai lonjakan like/komentar tidak wajar.
- Analisis NLP komentar: deteksi komentar generik/berulang (cosine similarity, TF-IDF), deteksi bot berdasarkan pola bahasa (template komentar yang sama di banyak post).
- (Opsional) Sentiment analysis untuk mengukur kualitas interaksi, bukan cuma kuantitas.

**D. Skoring**
- Menyusun formula skor kredibilitas engagement (gabungan skor anomali + skor NLP + rasio engagement), skala 0–100.
- Dokumentasi cara skor dihitung (bobot tiap komponen) agar bisa dijelaskan ke tim lain dan di laporan akhir.

**Output ke tim lain:** fungsi/skrip Python (atau notebook) yang menerima data mentah → mengeluarkan skor kredibilitas per akun, dalam format JSON/dict yang bisa dipanggil backend.

---

### 2. Backend Engineer — API, Database & Logic

**A. Desain Database**
- Skema tabel: `influencers` (profil dasar), `performance_history` (snapshot metrik per waktu), `detection_results` (skor & label bot/tidak per waktu cek), `comments` (opsional, untuk audit trail).
- Pilih DB (PostgreSQL/MySQL untuk relasional, atau MongoDB kalau data lebih fleksibel/semi-terstruktur).

**B. API Development**
- Endpoint utama: `POST /analyze` (trigger analisis akun baru), `GET /influencer/{id}` (ambil hasil skor & histori), `GET /report` (data untuk dashboard/export).
- Integrasi modul ML: memanggil skrip/model dari tim Data Engineer, menyimpan hasilnya ke DB.
- Validasi input & error handling (akun private, akun tidak ditemukan, rate limit dari IG/TikTok).

**C. Automation & Rate Limiting**
- Scheduler (Celery/APScheduler/cron) untuk update data berkala tanpa kena rate limit dari platform.
- Sistem antrian (queue) kalau banyak permintaan analisis masuk bersamaan.
- Logging & monitoring sederhana untuk memantau kegagalan scraping/API call.

**Output ke tim lain:** dokumentasi API (Swagger/OpenAPI) supaya tim Frontend tahu endpoint, format request, dan format response.

---

### 3. Frontend & Product Lead — Dashboard UI/UX & Produk

**A. Desain Tampilan**
- Wireframe/mockup halaman utama: input username → hasil skor kredibilitas + grafik pendukung (tren engagement, distribusi komentar, dsb).
- Visualisasi data: line chart (histori performa), gauge/skor meter (skor kredibilitas), badge (bot/tidak).

**B. Fitur Interaktif**
- Search bar untuk cari akun influencer.
- Filter (berdasarkan skor, kategori niche, tanggal analisis).
- Fitur export laporan ke PDF/CSV.

**C. Manajemen Proyek**
- Menyusun timeline/milestone proyek (kapan data siap, kapan API siap, kapan integrasi dimulai).
- Memastikan komunikasi antar tim lancar, termasuk format data yang disepakati bersama dari awal agar tidak ada mismatch saat integrasi.
- Melakukan testing end-to-end sebelum demo/submit tugas.

**Output ke tim lain:** kebutuhan format data dari backend (field apa saja yang perlu ditampilkan) disampaikan di awal supaya backend bisa desain API yang sesuai.

---

## Alur Ketergantungan Antar Tim

| Tahap | Penanggung Jawab | Butuh Dari Siapa |
|---|---|---|
| Scraping & data mentah | ML Engineer | — |
| Desain skema database | Backend Engineer | Contoh struktur data dari ML Engineer |
| Bangun API | Backend Engineer | Skor sudah bisa dihasilkan ML Engineer |
| Desain dashboard | Frontend Lead | Endpoint API sudah tersedia (mockup bisa dimulai lebih awal) |
| Integrasi & testing | Semua tim | API stabil + dashboard siap |

## Tech Stack (Usulan)

- **ML/Data:** Python, Pandas, Scikit-learn, NLTK/Sastrawi, instaloader/snscrape
- **Backend:** FastAPI/Django, PostgreSQL/MongoDB, Celery/APScheduler
- **Frontend:** React/Next.js atau Streamlit, Chart.js/Recharts
