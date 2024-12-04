# Website Forum - Aray

Proyek ini adalah aplikasi web sederhana yang dibangun menggunakan Flask dan SQLAlchemy. Aplikasi ini memungkinkan pengguna untuk mendaftar, masuk, dan mengelola sesi mereka. Data pengguna disimpan dalam database SQLite.

## Fitur

- Pendaftaran pengguna dengan validasi input
- Login pengguna dengan pengecekan email dan password
- Manajemen sesi pengguna
- Pesan kesalahan yang informatif

## Prerequisites

Sebelum menjalankan aplikasi ini, pastikan Anda memiliki Python dan pip terinstal di sistem Anda. Anda juga perlu menginstal beberapa paket yang diperlukan.

## Instalasi

1. **Clone repositori ini:**
 ```bash
 git clone https://github.com/username/repo-name.git cd repo-name
 ```

2. **Buat dan aktifkan lingkungan virtual (opsional tetapi disarankan):**
```bash
python -m venv venv source venv/bin/activate # Untuk Linux/Mac venv\Scripts\activate # Untuk Windows
```

3. **Instal dependensi yang diperlukan:**
```bash
pip install Flask Flask-SQLAlchemy
```

4. **Jalankan aplikasi:**
```bash
python app.py
```


5. **Akses aplikasi di browser:**

```bash
Buka [http://127.0.0.1:5000](http://127.0.0.1:5000) di browser Anda.
```

## Cara Menggunakan

1. **Pendaftaran:**
   - Masukkan nama, email, dan password di halaman utama dan klik "Daftar".
   - Jika email sudah terdaftar, Anda akan menerima pesan kesalahan.

2. **Login:**
   - Masukkan email dan password yang telah didaftarkan.
   - Jika berhasil, Anda akan diarahkan ke halaman pengguna.

3. **Logout:**
   - Klik tombol logout untuk keluar dari sesi.

## Kontribusi

Soon

## Penulis

- [Muhammad Akbar Pradana / Devaaldo](https://github.com/devaaldo)
