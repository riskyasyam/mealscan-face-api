# Quick Start Guide

## 🚀 Getting Started (5 Menit)

### 1. Install Dependencies

```bash
cd api
pip install -r requirements.txt
```

**Catatan**: Proses install membutuhkan waktu ~5-10 menit tergantung koneksi internet.

### 2. Run Server

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

**Manual:**
```bash
python main.py
```

Server akan berjalan di: `http://localhost:8001`

### 3. Test API

Buka browser: `http://localhost:8001/docs`

Atau test dengan cURL:
```bash
curl http://localhost:8001/health
```

---

## 📝 Test Face Recognition

### 1. Siapkan Foto Test

Siapkan 2-3 foto wajah untuk testing:
- `photo1.jpg` - Foto untuk register
- `photo2.jpg` - Foto yang sama untuk test recognition

### 2. Register Face

```bash
curl -X POST "http://localhost:8001/api/face/register" \
  -F "employee_id=TEST001" \
  -F "file=@photo1.jpg"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Face berhasil di-register untuk karyawan TEST001",
  "employee_id": "TEST001",
  "confidence": 0.98,
  "bbox": [...]
}
```

### 3. Test Recognition

```bash
curl -X POST "http://localhost:8001/api/face/recognize" \
  -F "file=@photo2.jpg"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Wajah berhasil dikenali",
  "employee_id": "TEST001",
  "similarity": 0.87,
  "confidence": 0.98
}
```

### 4. Test di Notebook

Buka `notebooks/test_arcface.ipynb` dan jalankan cell-cell nya untuk testing lebih detail.

---

## 🔧 Troubleshooting

### Error: Model tidak terdownload

Model akan otomatis didownload saat pertama kali run. Jika error:

1. Cek koneksi internet
2. Download manual:
```bash
# Windows
mkdir %USERPROFILE%\.insightface\models
cd %USERPROFILE%\.insightface\models

# Linux/Mac
mkdir -p ~/.insightface/models
cd ~/.insightface/models

# Download model (link akan muncul di error message)
```

### Error: Import not found

```bash
pip uninstall insightface onnxruntime
pip install insightface==0.7.3 onnxruntime==1.16.3
```

### API Lambat

1. Reduce detection size di `main.py`:
```python
face_system = FaceRecognitionSystem(
    det_size=(320, 320)  # Default: (640, 640)
)
```

2. Resize foto sebelum upload (max 1280x720)

---

## 📊 Next Steps

### Untuk Laravel Integration:

1. **Setup Database**
   - Lihat `LARAVEL_INTEGRATION.md` untuk migration examples
   - Run migrations di Laravel project

2. **Create Service Class**
   - Copy `FaceRecognitionService.php` dari dokumentasi
   - Setup di `config/services.php`

3. **Test Integration**
   - Test register face dari Laravel
   - Test check-in dari Laravel

### Untuk Production:

1. **Add Authentication**
   - Implementasikan API Key atau JWT
   - Update CORS settings

2. **Add Rate Limiting**
   - Implementasikan rate limiting per IP

3. **Deploy**
   - Deploy Python API ke server (Docker recommended)
   - Deploy Laravel ke server
   - Setup reverse proxy (Nginx)

---

## 📚 Documentation

- **README.md** - Overview & setup
- **API_DOCS.md** - API documentation lengkap
- **LARAVEL_INTEGRATION.md** - Laravel integration guide
- **notebooks/test_arcface.ipynb** - Testing & benchmarking

**Port Configuration:**
- Python API: `http://localhost:8001`
- Laravel: `http://localhost:8000`

---

## 💡 Tips

1. **Good Photo Quality**
   - Wajah harus terlihat jelas
   - Lighting yang baik
   - Tidak blur
   - 1 wajah per foto untuk registration

2. **Performance**
   - First request akan lebih lambat (model loading)
   - Subsequent requests lebih cepat (~150-300ms)
   - Embeddings di-cache di memory

3. **Security**
   - Jangan commit `.env` file
   - Use HTTPS di production
   - Add authentication
   - Encrypt embeddings di production

---

## 🎯 Workflow Lengkap

```
1. Admin Register Employee
   Laravel → POST /api/face/register → Python API
   ↓
   Python extract & save embedding
   ↓
   Laravel save metadata to DB

2. Employee Check-in
   Laravel (webcam) → POST /api/attendance/checkin → Python API
   ↓
   Python recognize face
   ↓
   Laravel save attendance to DB
   ↓
   Show confirmation

3. Admin View Reports
   Laravel query attendance_logs
   ↓
   Generate reports & statistics
```

---

## 📞 Support

Jika ada pertanyaan atau issue:
1. Check dokumentasi lengkap di `README.md`
2. Check API docs di `http://localhost:8001/docs`
3. Check code examples di `LARAVEL_INTEGRATION.md`

Happy coding! 🚀
