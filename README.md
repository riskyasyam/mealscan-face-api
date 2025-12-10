# Face Recognition Attendance System

Sistem absensi makan karyawan menggunakan Face Recognition dengan **ArcFace + MobileFaceNet** (lightweight, optimal untuk CPU).

## 📋 Arsitektur Sistem

### Backend (Python - FastAPI)
- **Face Recognition**: InsightFace dengan model `antelopev2`
- **Model**: ArcFace + MobileFaceNet (ringan, cepat di CPU)
- **API**: FastAPI untuk REST endpoints
- **Storage**: File system untuk embeddings & images

### Frontend (Laravel)
- **Admin Panel**: Manajemen karyawan, upload foto, setting waktu makan
- **Karyawan Page**: Interface absensi dengan webcam/upload foto
- **Database**: MySQL untuk data karyawan, attendance logs, settings

## 🚀 Setup Backend (Python)

### 1. Install Dependencies

```bash
cd api
pip install -r requirements.txt
```

### 2. Download Model InsightFace

Model akan otomatis di-download saat pertama kali run. Pastikan koneksi internet stabil.

Model `antelopev2` (~50MB) akan tersimpan di:
- Windows: `C:\Users\<username>\.insightface\models\antelopev2`
- Linux/Mac: `~/.insightface/models/antelopev2`

### 3. Run Server

```bash
# Development mode
python main.py

# Atau dengan uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

API akan berjalan di: `http://localhost:8001`

### 4. Test API

Buka browser: `http://localhost:8001/docs` untuk Swagger UI documentation.

## 📁 Struktur Project

```
face_recog_makan/
├── api/
│   ├── main.py              # FastAPI application
│   ├── utils.py             # Face recognition utilities
│   ├── schemas.py           # Pydantic schemas
│   └── requirements.txt     # Python dependencies
├── data/
│   ├── faces/              # Stored face images
│   └── embeddings/         # Stored face embeddings (.pkl)
├── models/
│   └── insightface/        # InsightFace models (auto-download)
└── notebooks/
    └── test_arcface.ipynb  # Testing & benchmark notebook
```

## 🔌 API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /status` - System status

### Face Registration
- `POST /api/face/register` - Register face baru
- `POST /api/face/update` - Update face existing
- `DELETE /api/face/delete/{employee_id}` - Delete face

### Face Recognition & Attendance
- `POST /api/attendance/checkin` - Check-in dengan face recognition
- `POST /api/face/recognize` - Recognize face only (tanpa attendance)

### Statistics
- `GET /api/stats/registered-faces` - Get total registered faces

### Utilities
- `GET /api/util/reload-embeddings` - Reload embeddings dari disk

## 📊 Database Schema (Laravel)

### Tables

#### 1. employees
```sql
CREATE TABLE employees (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    department VARCHAR(50),
    position VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    INDEX idx_employee_id (employee_id)
);
```

#### 2. face_embeddings
```sql
CREATE TABLE face_embeddings (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    employee_id VARCHAR(50) NOT NULL,
    embedding_path VARCHAR(255) NOT NULL,
    face_image_path VARCHAR(255) NOT NULL,
    confidence_score FLOAT,
    bbox JSON,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    INDEX idx_employee_id (employee_id)
);
```

#### 3. meal_time_settings
```sql
CREATE TABLE meal_time_settings (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    meal_type ENUM('breakfast', 'lunch', 'dinner') UNIQUE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Default settings
INSERT INTO meal_time_settings (meal_type, start_time, end_time, is_active) VALUES
('breakfast', '06:00:00', '08:00:00', TRUE),
('lunch', '11:30:00', '13:30:00', TRUE),
('dinner', '17:30:00', '19:30:00', TRUE);
```

#### 4. attendance_logs
```sql
CREATE TABLE attendance_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    employee_id VARCHAR(50) NOT NULL,
    meal_type ENUM('breakfast', 'lunch', 'dinner') NOT NULL,
    status ENUM('present', 'absent', 'late') NOT NULL,
    attendance_date DATE NOT NULL,
    attendance_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    similarity_score FLOAT,
    confidence_score FLOAT,
    created_at TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    UNIQUE KEY unique_attendance (employee_id, meal_type, attendance_date),
    INDEX idx_date (attendance_date),
    INDEX idx_employee (employee_id)
);
```

## 🔗 Integrasi Laravel dengan Python API

### 1. Setup Environment Laravel

```env
# .env
PYTHON_API_URL=http://localhost:8001
PYTHON_API_TIMEOUT=30
```

### 2. Laravel HTTP Client

```php
// app/Services/FaceRecognitionService.php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Http\UploadedFile;

class FaceRecognitionService
{
    protected $baseUrl;
    
    public function __construct()
    {
        $this->baseUrl = config('services.python_api.url', 'http://localhost:8001');
    }
    
    /**
     * Register face untuk employee
     */
    public function registerFace(string $employeeId, UploadedFile $photo)
    {
        $response = Http::timeout(30)
            ->attach('file', file_get_contents($photo), $photo->getClientOriginalName())
            ->post("{$this->baseUrl}/api/face/register", [
                'employee_id' => $employeeId
            ]);
        
        return $response->json();
    }
    
    /**
     * Check-in attendance dengan face recognition
     */
    public function checkIn(UploadedFile $photo)
    {
        $response = Http::timeout(30)
            ->attach('file', file_get_contents($photo), $photo->getClientOriginalName())
            ->post("{$this->baseUrl}/api/attendance/checkin");
        
        return $response->json();
    }
    
    /**
     * Recognize face only (tanpa create attendance)
     */
    public function recognizeFace(UploadedFile $photo)
    {
        $response = Http::timeout(30)
            ->attach('file', file_get_contents($photo), $photo->getClientOriginalName())
            ->post("{$this->baseUrl}/api/face/recognize");
        
        return $response->json();
    }
    
    /**
     * Delete face registration
     */
    public function deleteFace(string $employeeId)
    {
        $response = Http::timeout(30)
            ->delete("{$this->baseUrl}/api/face/delete/{$employeeId}");
        
        return $response->json();
    }
    
    /**
     * Get system status
     */
    public function getStatus()
    {
        $response = Http::timeout(5)
            ->get("{$this->baseUrl}/status");
        
        return $response->json();
    }
}
```

### 3. Laravel Controller Example

```php
// app/Http/Controllers/AttendanceController.php

namespace App\Http\Controllers;

use App\Services\FaceRecognitionService;
use Illuminate\Http\Request;
use App\Models\AttendanceLog;

class AttendanceController extends Controller
{
    protected $faceService;
    
    public function __construct(FaceRecognitionService $faceService)
    {
        $this->faceService = $faceService;
    }
    
    /**
     * Check-in attendance
     */
    public function checkIn(Request $request)
    {
        $request->validate([
            'photo' => 'required|image|max:5120' // Max 5MB
        ]);
        
        // Call Python API
        $result = $this->faceService->checkIn($request->file('photo'));
        
        if ($result['success']) {
            // Save to database
            $attendance = AttendanceLog::create([
                'employee_id' => $result['employee_id'],
                'meal_type' => $result['meal_type'],
                'status' => 'present',
                'attendance_date' => now()->toDateString(),
                'similarity_score' => $result['similarity'],
                'confidence_score' => $result['confidence']
            ]);
            
            return response()->json([
                'success' => true,
                'message' => $result['message'],
                'data' => $attendance
            ]);
        }
        
        return response()->json([
            'success' => false,
            'message' => $result['message']
        ], 400);
    }
}
```

## 🎯 Workflow Sistem

### Admin Flow
1. **Tambah Karyawan**
   - Admin input data karyawan di Laravel
   - Upload foto wajah
   - Laravel call Python API: `POST /api/face/register`
   - Python extract & save embedding
   - Laravel save metadata ke database

2. **Setting Waktu Makan**
   - Admin set waktu makan (pagi, siang, malam) di Laravel
   - Simpan di table `meal_time_settings`

### Employee Flow
1. **Absensi Makan**
   - Karyawan buka halaman absensi
   - Ambil foto via webcam atau upload
   - Laravel call Python API: `POST /api/attendance/checkin`
   - Python recognize face & return employee_id
   - Laravel cek waktu makan saat ini
   - Laravel save attendance ke database
   - Tampilkan konfirmasi

## 📈 Performance

### Model antelopev2 (CPU)
- **Face Detection**: ~100-200ms
- **Embedding Extraction**: ~50-100ms
- **Total Processing**: ~150-300ms per image
- **Throughput**: ~3-6 FPS

### Optimization Tips
1. Resize image ke max 1280x720 sebelum upload
2. Use good lighting untuk foto
3. Pastikan wajah terlihat jelas
4. Gunakan cache untuk embeddings (sudah implemented)

## 🔒 Security Considerations

1. **API Authentication**: Tambahkan API key/token untuk production
2. **Rate Limiting**: Limit request per IP
3. **Image Validation**: Validate file type & size
4. **Data Privacy**: Encrypt embeddings di production
5. **HTTPS**: Gunakan HTTPS untuk production

## 🐛 Troubleshooting

### Model tidak ter-download
```bash
# Manual download
cd ~/.insightface/models
wget https://github.com/deepinsight/insightface/releases/download/v0.7/antelopev2.zip
unzip antelopev2.zip
```

### Import error
```bash
# Reinstall dependencies
pip uninstall insightface onnxruntime
pip install insightface==0.7.3 onnxruntime==1.16.3
```

### Slow processing
- Pastikan menggunakan CPU provider
- Reduce detection size: `det_size=(320, 320)`
- Resize image sebelum process

## 📝 TODO / Future Improvements

- [ ] Add GPU support (onnxruntime-gpu)
- [ ] Add multiple face support per employee
- [ ] Add liveness detection (anti-spoofing)
- [ ] Add face quality check
- [ ] Add Redis cache untuk embeddings
- [ ] Add WebSocket untuk real-time updates
- [ ] Add Docker deployment
- [ ] Add face comparison history
- [ ] Add attendance reports & analytics
- [ ] Add mobile app support

## 📞 Support

Untuk pertanyaan atau issue, silakan buat issue di repository atau hubungi developer.

---

**Created by**: Your Name  
**Date**: December 2025  
**Version**: 1.0.0
