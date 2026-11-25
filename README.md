# Titanic Passenger Safety Prediction

Aplikasi web full-stack untuk memprediksi peluang keselamatan penumpang Titanic menggunakan model Random Forest yang sudah dilatih. Backend dibangun dengan FastAPI, frontend menggunakan Blazor Server dengan Bootstrap 5, dan keduanya terhubung melalui REST API JSON.

## Ringkasan

Proyek ini memisahkan tiga lapisan utama:

1. Model machine learning hasil training (`titanic_rf_model.pkl`) beserta preprocessor yang menyimpan statistik imputasi dan skema encoding dari data latih.
2. Backend FastAPI yang memuat bundle model sekali saat startup, memvalidasi request dengan Pydantic, menjalankan preprocessor yang sama dengan saat training, lalu mengembalikan prediksi dan probabilitas.
3. Frontend Blazor Server yang menampilkan formulir terstruktur, validasi langsung, serta panel hasil dengan indikator probabilitas dan penjelasan faktor.

Alur data:

```text
Browser (Blazor)
  -> POST /api/predict (JSON)
  -> Pydantic validation
  -> TitanicPreprocessor.transform (identik dengan training)
  -> RandomForestClassifier.predict / predict_proba
  -> JSON response
  -> UI badge, progress bar, dan ringkasan faktor
```

## Struktur folder

```text
S.O.S/
├── backend/
│   ├── app/
│   │   ├── config.py            pembacaan .env dan konfigurasi server
│   │   ├── errors.py            tipe error dan envelope error terstruktur
│   │   ├── main.py              aplikasi FastAPI, CORS, exception handler, endpoint
│   │   ├── ml_service.py        pemuatan model dan logika prediksi
│   │   └── schemas.py           Pydantic schema dan mapping ke data mentah training
│   ├── models/
│   │   └── titanic_rf_model.pkl bundle model + preprocessor
│   ├── titanic_rf/
│   │   ├── __init__.py          ekspor minim agar pickle dapat dimuat
│   │   └── features.py          salinan persis preprocessor saat training
│   ├── tests/test_api.py        pengujian endpoint dengan TestClient
│   ├── .env                     konfigurasi lokal (dibuat dari .env.example)
│   ├── .env.example
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── run.py                   entrypoint Uvicorn yang membaca .env
├── frontend/
│   ├── TitanicSafetyApp/
│   │   ├── Components/
│   │   │   ├── App.razor        root HTML, CSS, dan script Blazor
│   │   │   ├── Routes.razor     router dengan render mode InteractiveServer
│   │   │   ├── Layout/MainLayout.razor
│   │   │   ├── Pages/Index.razor halaman utama dan state management UI
│   │   │   ├── PassengerForm.razor formulir dan validasi client-side
│   │   │   └── PredictionResult.razor empty/loading/error/success panel
│   │   ├── Configuration/EnvFileConfigurationExtensions.cs
│   │   ├── Models/              form model dan DTO request/response API
│   │   ├── Services/            API client, exception, dan penjelas faktor
│   │   ├── wwwroot/             CSS aplikasi dan Bootstrap lokal
│   │   ├── Program.cs
│   │   ├── TitanicSafetyApp.csproj
│   │   └── Properties/launchSettings.json
│   ├── .env
│   └── .env.example
├── titanic_rf/                  kode training asli (sumber features.py)
├── titanic_rf_model.pkl         model hasil training asli
├── main.py                      pipeline training dataset
└── README.md
```

## Prasyarat

- Python 3.11 atau lebih baru (proyek ini diuji dengan Python 3.14).
- .NET SDK 10.0 atau lebih baru.
- Koneksi internet hanya diperlukan saat instalasi paket; Bootstrap sudah disimpan lokal di `wwwroot/lib/bootstrap`.

## Instalasi dan menjalankan

### 1. Backend FastAPI

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
python run.py
```

Server akan berjalan di `http://localhost:8000`. Dokumentasi interaktif tersedia di `http://localhost:8000/docs`.

Jika hanya menjalankan produksi, gunakan `pip install -r requirements.txt` tanpa paket pengujian.

### 2. Frontend Blazor

Buka terminal kedua:

```bash
cd frontend
cp .env.example .env
cd TitanicSafetyApp
dotnet run
```

`launchSettings.json` menetapkan alamat `http://localhost:5055`, sehingga aplikasi dapat dibuka di `http://localhost:5055`. Untuk menimpa alamat, jalankan `dotnet run --urls http://localhost:8080`.

Pastikan backend berjalan lebih dulu agar indikator status di header menampilkan "Backend & model siap".

## Konfigurasi environment

Backend membaca `backend/.env` melalui `python-dotenv`:

| Variabel | Default | Keterangan |
|---|---|---|
| `MODEL_PATH` | `./models/titanic_rf_model.pkl` | Path bundle model; relatif terhadap folder `backend` |
| `API_HOST` | `0.0.0.0` | Alamat bind Uvicorn |
| `API_PORT` | `8000` | Port Uvicorn |
| `LOG_LEVEL` | `info` | Level logging Uvicorn |
| `ALLOWED_ORIGINS` | localhost:5055, localhost:5000, localhost:3000 | Daftar origin yang diizinkan CORS, dipisah koma |

Frontend membaca `frontend/.env` dengan loader sederhana di `EnvFileConfigurationExtensions.cs`. Variabel lingkungan sistem dengan nama sama memiliki prioritas lebih tinggi.

| Variabel | Default | Keterangan |
|---|---|---|
| `API_BASE_URL` | `http://localhost:8000` | Base URL backend API |
| `DATA_PROTECTION_KEYS_PATH` | `./App_Data/keys` | Lokasi penyimpanan kunci Data Protection Blazor Server |

Untuk produksi, ubah `ALLOWED_ORIGINS` ke domain frontend yang sebenarnya dan `API_BASE_URL` ke URL API produksi. Hindari penggunaan wildcard pada CORS bila API membutuhkan pembatasan akses.

## API reference

### `GET /api/health`

Mengembalikan status server dan kondisi model.

```json
{
  "status": "ok",
  "model_loaded": true,
  "model_type": "RandomForestClassifier",
  "feature_count": 15,
  "message": "Model dan preprocessor siap digunakan.",
  "api_version": "1.0.0"
}
```

Jika model gagal dimuat, response tetap `200` dengan `status: "degraded"` dan `model_loaded: false`, disertai pesan kesalahan pada field `message`. Endpoint `/api/predict` akan mengembalikan `500` dalam kondisi tersebut.

### `POST /api/predict`

Request body:

| Field | Tipe | Batasan | Keterangan |
|---|---|---|---|
| `pclass` | int | 1, 2, 3 | Kelas penumpang |
| `sex` | string | `male` / `female` | Jenis kelamin |
| `age` | float | 0.1 - 100 | Usia dalam tahun |
| `sibsp` | int | >= 0 | Jumlah saudara/pasangan di kapal |
| `parch` | int | >= 0 | Jumlah orang tua/anak di kapal |
| `fare` | float | >= 0 | Tarif tiket |
| `embarked` | string | `S` / `C` / `Q` | Pelabuhan keberangkatan |
| `title` | string | `Mr` / `Mrs` / `Miss` / `Master` / `Rare` | Gelar; opsional jika `name` dikirim |
| `name` | string | teks | Opsional; gelar diekstrak otomatis dengan aturan training |
| `has_cabin` | int/bool | 0 atau 1 | Apakah nomor kabin tercatat |

Contoh request:

```json
{
  "pclass": 1,
  "sex": "female",
  "age": 35,
  "sibsp": 1,
  "parch": 0,
  "fare": 80.0,
  "embarked": "C",
  "title": "Mrs",
  "has_cabin": 1
}
```

Response sukses:

```json
{
  "survived": 1,
  "label": "Selamat",
  "probability_survived": 0.9986,
  "probability_not_survived": 0.0014,
  "risk_level": "Rendah"
}
```

`risk_level` menggambarkan risiko **tidak selamat**: `Rendah` jika probabilitas selamat minimal 0,75; `Sedang` jika 0,40 sampai di bawah 0,75; `Tinggi` jika di bawah 0,40.

### Error response

Semua error menggunakan envelope yang konsisten:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Data penumpang tidak valid. Periksa kembali field yang ditandai.",
    "details": [
      {"field": "pclass", "message": "Input should be less than or equal to 3", "type": "less_than_equal"}
    ]
  }
}
```

| HTTP | `code` | Penyebab |
|---|---|---|
| 422 | `VALIDATION_ERROR` | Field wajib hilang, tipe salah, atau nilai di luar batas |
| 500 | `MODEL_NOT_LOADED` | File model tidak ditemukan atau gagal di-unpickle |
| 500 | `PREDICTION_FAILED` | Preprocessing atau inferensi menimbulkan exception |
| 500 | `INTERNAL_ERROR` | Kesalahan internal lain |

Frontend membaca envelope ini dan menampilkan pesan beserta kode error pada banner merah.

## Konsistensi preprocessing

Bundle model berisi dua objek: `model` (`RandomForestClassifier`) dan `preprocessor` (`TitanicPreprocessor`). Keduanya dibuat oleh pipeline training di `main.py` dan disimpan dengan `joblib`.

Karena pickle menyimpan referensi kelas `titanic_rf.features.TitanicPreprocessor`, folder `backend/titanic_rf/` berisi salinan persis `features.py` dari kode training. File `__init__.py` sengaja dibuat minimal agar hanya modul `features` yang dimuat saat unpickling, sehingga backend tidak memerlukan matplotlib atau seaborn.

Schema API menerima field sederhana (`title`, `has_cabin`), lalu `to_raw_passenger()` mengubahnya menjadi format mentah yang diharapkan preprocessor:

- `title` menjadi `Name` dengan pola `Passenger, <Title>. <sex>`, agar `extract_title` menghasilkan gelar yang sama seperti saat training.
- `has_cabin` menjadi `Cabin` berisi nilai saat bernilai 1, atau `None` saat 0. Preprocessor menghitung `HasCabin` dari ketersediaan nilai kabin.
- `FamilySize` dan `IsAlone` dihitung ulang dari `SibSp` dan `Parch` oleh preprocessor yang sama.

Dengan cara ini tidak ada duplikasi logika imputasi atau encoding antara training dan serving.

## Detail frontend

- `Index.razor` dan `Routes.razor` berjalan dengan `@rendermode InteractiveServer`; `Program.cs` mendaftarkan `AddInteractiveServerComponents()` dan `AddInteractiveServerRenderMode()`. `EditForm` diberi `FormName="TitanicPredictionForm"`, sehingga submit tidak bergantung pada POST Static SSR. Komponen `FocusOnNavigate` sengaja tidak dipakai agar tidak ada fokus otomatis dan outline biru pada judul halaman.
- `PassengerForm.razor` menggunakan `EditForm`, `DataAnnotationsValidator`, dan `ValidationMessage`. Perubahan pada field memicu validasi langsung; `OnValidSubmit` hanya dipanggil bila seluruh aturan terpenuhi. Kelas penumpang memakai segmented control, tarif memakai prefiks GBP (`£`), dan data kabin memakai checkbox standar yang rapi di dalam grid.
- Tombol "Preset: Kelas 1", "Preset: Kelas 3", dan "Reset" berada di action bar bersama tombol aksi utama.
- Setiap input memiliki label dan teks bantuan operasional yang ringkas, tanpa jargon teknis.
- `Index.razor` menyimpan state: empty sebelum prediksi, loading berupa overlay di atas panel hasil tanpa pergeseran layout, success dengan badge status, angka probabilitas besar, bar presisi, dan daftar parameter, serta error banner bila layanan tidak merespons.
- Jika input diubah setelah prediksi, panel hasil menampilkan catatan bahwa hasil perlu dijalankan ulang.
- `TitanicApiClient` memakai `IHttpClientFactory`, menetapkan `BaseAddress` dari `.env`, timeout 8 detik, dan menerjemahkan error timeout, koneksi gagal, serta payload error API menjadi `TitanicApiException`. Komponen UI tidak berisi logika HTTP maupun kredensial.
- `FactorExplainer` menghasilkan ringkasan faktor berdasarkan parameter yang dimasukkan pengguna.
- Antarmuka memakai application shell enterprise: header 56px, latar `#F8FAFC`, panel putih dengan border `#E2E8F0`, radius 8px, tipografi Inter/system dengan angka `tabular-nums`, workspace dua kolom proporsional 7:5, panel hasil sticky di desktop, dan footer penuh yang tidak terpotong. Ikonografi menggunakan SVG bergaya Lucide melalui komponen `AppIcon.razor`.

## Pengujian

Backend:

```bash
cd backend
.venv/bin/python -m pytest tests -q
```

Pengujian mencakup health check dengan model termuat, prediksi kelas satu, ekstraksi gelar dari `name`, penerimaan `has_cabin` boolean, validasi 422 terstruktur, dan simulasi model belum dimuat yang menghasilkan 500.

Frontend:

```bash
cd frontend/TitanicSafetyApp
dotnet build -c Release
```

## Pemecahan masalah

- `MODEL_NOT_LOADED` saat prediksi: pastikan `MODEL_PATH` di `backend/.env` benar dan file `backend/models/titanic_rf_model.pkl` tersedia. Periksa log saat startup untuk detail exception.
- Error `InconsistentVersionWarning` saat memuat model: pasang versi scikit-learn yang sama dengan saat training, lalu jalankan ulang backend.
- Status frontend tetap "Backend tidak tersedia": pastikan backend berjalan, `API_BASE_URL` di `frontend/.env` sesuai port backend, dan origin frontend tercantum di `ALLOWED_ORIGINS`.
- Port sudah dipakai: ubah `API_PORT` di `backend/.env` atau gunakan `dotnet run --urls http://localhost:<port>` dan sesuaikan kedua file `.env`.
- Kunci Data Protection gagal ditulis: arahkan `DATA_PROTECTION_KEYS_PATH` ke direktori yang dapat ditulis oleh pengguna yang menjalankan aplikasi.

## Catatan

Prediksi ini adalah estimasi berbasis pola pada dataset Titanic dan tidak dimaksudkan sebagai informasi historis yang pasti untuk individu tertentu. Untuk kebutuhan produksi, gunakan HTTPS, simpan kunci Data Protection di penyimpanan terkelola, dan batasi origin CORS sesuai domain resmi.
