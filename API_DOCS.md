# API Documentation - Face Recognition Attendance System

Base URL: `http://localhost:8001`

**Note**: Port 8001 digunakan untuk Python API, sedangkan port 8000 untuk Laravel.

## Table of Contents
- [Authentication](#authentication)
- [Health Check](#health-check)
- [Face Registration](#face-registration)
- [Face Recognition & Attendance](#face-recognition--attendance)
- [Statistics](#statistics)
- [Utilities](#utilities)
- [Response Format](#response-format)
- [Error Codes](#error-codes)

---

## Authentication

**Note**: Authentication belum diimplementasikan. Untuk production, tambahkan API Key atau JWT token.

---

## Health Check

### GET /
Root endpoint

**Response:**
```json
{
  "message": "Face Recognition Attendance System API",
  "version": "1.0.0",
  "status": "running"
}
```

### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-10T10:30:00",
  "model_loaded": true
}
```

### GET /status
System status dengan detail

**Response:**
```json
{
  "status": "running",
  "model_loaded": true,
  "total_employees": 150,
  "total_registered_faces": 148,
  "total_attendance_today": 95,
  "current_meal_time": "lunch",
  "meal_time_active": true
}
```

---

## Face Registration

### POST /api/face/register
Register face baru untuk karyawan

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  - `employee_id` (form field, required): ID karyawan
  - `file` (file upload, required): Foto wajah (JPG/PNG)

**Example (cURL):**
```bash
curl -X POST "http://localhost:8001/api/face/register" \
  -F "employee_id=EMP001" \
  -F "file=@photo.jpg"
```

**Example (JavaScript):**
```javascript
const formData = new FormData();
formData.append('employee_id', 'EMP001');
formData.append('file', photoFile);

fetch('http://localhost:8001/api/face/register', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Face berhasil di-register untuk karyawan EMP001",
  "employee_id": "EMP001",
  "confidence": 0.9876,
  "bbox": [120.5, 150.3, 380.2, 450.8]
}
```

**Response (Error - No Face):**
```json
{
  "success": false,
  "error": "Tidak ada wajah terdeteksi di image. Pastikan wajah terlihat jelas.",
  "status_code": 400
}
```

### POST /api/face/update
Update face registration existing

**Request:** Same as `/api/face/register`

**Response:** Same as `/api/face/register`

### DELETE /api/face/delete/{employee_id}
Delete face registration

**Request:**
- Method: `DELETE`
- URL Parameter: `employee_id`

**Example:**
```bash
curl -X DELETE "http://localhost:8001/api/face/delete/EMP001"
```

**Response:**
```json
{
  "success": true,
  "message": "Face data deleted untuk karyawan EMP001",
  "deleted_images": 3
}
```

---

## Face Recognition & Attendance

### POST /api/attendance/checkin
Check-in attendance dengan face recognition

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  - `file` (file upload, required): Foto wajah untuk check-in

**Example (cURL):**
```bash
curl -X POST "http://localhost:8001/api/attendance/checkin" \
  -F "file=@checkin_photo.jpg"
```

**Example (JavaScript with Webcam):**
```javascript
// Capture from webcam
const canvas = document.getElementById('canvas');
canvas.toBlob(blob => {
  const formData = new FormData();
  formData.append('file', blob, 'webcam.jpg');
  
  fetch('http://localhost:8001/api/attendance/checkin', {
    method: 'POST',
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log('Check-in berhasil:', data.employee_name);
    } else {
      console.log('Check-in gagal:', data.message);
    }
  });
});
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Selamat datang! Absensi lunch berhasil.",
  "employee_id": "EMP001",
  "employee_name": "John Doe",
  "similarity": 0.876,
  "confidence": 0.9876,
  "can_attend": true,
  "meal_type": "lunch",
  "attendance_id": 12345
}
```

**Response (Face Not Recognized):**
```json
{
  "success": false,
  "message": "Wajah tidak dikenali. Silakan daftar terlebih dahulu.",
  "similarity": 0.0,
  "confidence": 0.9654,
  "can_attend": false,
  "employee_id": null,
  "employee_name": null,
  "meal_type": null,
  "attendance_id": null
}
```

**Response (Already Attended):**
```json
{
  "success": false,
  "message": "Anda sudah absen lunch hari ini.",
  "employee_id": "EMP001",
  "employee_name": "John Doe",
  "similarity": 0.876,
  "confidence": 0.9876,
  "can_attend": false,
  "meal_type": "lunch",
  "attendance_id": null
}
```

**Response (No Face Detected):**
```json
{
  "success": false,
  "message": "Tidak ada wajah terdeteksi. Posisikan wajah dengan jelas.",
  "can_attend": false,
  "employee_id": null,
  "employee_name": null,
  "similarity": null,
  "confidence": null,
  "meal_type": null,
  "attendance_id": null
}
```

### POST /api/face/recognize
Face recognition saja (tanpa create attendance)

**Request:** Same as `/api/attendance/checkin`

**Response:**
```json
{
  "success": true,
  "message": "Wajah berhasil dikenali",
  "employee_id": "EMP001",
  "employee_name": "John Doe",
  "similarity": 0.876,
  "confidence": 0.9876,
  "can_attend": true
}
```

---

## Statistics

### GET /api/stats/registered-faces
Get jumlah wajah yang sudah terdaftar

**Response:**
```json
{
  "total_registered": 148,
  "employee_ids": ["EMP001", "EMP002", "EMP003", "..."]
}
```

---

## Utilities

### GET /api/util/reload-embeddings
Reload embeddings dari disk

**Response:**
```json
{
  "success": true,
  "message": "Embeddings reloaded successfully",
  "total_loaded": 148
}
```

---

## Response Format

### Success Response
```json
{
  "success": true,
  "message": "Success message",
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "detail": "Detailed error information",
  "status_code": 400
}
```

---

## Error Codes

| Status Code | Description |
|------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input, no face detected, etc. |
| 404 | Not Found - Employee or resource not found |
| 500 | Internal Server Error - Server error |

### Common Error Messages

**Face Registration:**
- "File harus berupa image"
- "Image tidak valid atau terlalu kecil"
- "Tidak ada wajah terdeteksi di image"

**Face Recognition:**
- "Tidak ada wajah terdeteksi"
- "Wajah tidak dikenali"
- "Database wajah kosong"

**Attendance:**
- "Anda sudah absen [meal_type] hari ini"
- "Tidak dalam waktu makan"

---

## Testing Examples

### Python (requests)

```python
import requests

# Register face
with open('photo.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/api/face/register',
        data={'employee_id': 'EMP001'},
        files={'file': f}
    )
    print(response.json())

# Check-in
with open('checkin.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/api/attendance/checkin',
        files={'file': f}
    )
    print(response.json())
```

### PHP (Laravel)

```php
use Illuminate\Support\Facades\Http;

// Register face
$response = Http::attach(
    'file', 
    file_get_contents($request->file('photo')),
    'photo.jpg'
)->post('http://localhost:8001/api/face/register', [
    'employee_id' => 'EMP001'
]);

$result = $response->json();
```

### JavaScript (Axios)

```javascript
import axios from 'axios';

// Register face
const formData = new FormData();
formData.append('employee_id', 'EMP001');
formData.append('file', photoFile);

const response = await axios.post(
  'http://localhost:8001/api/face/register',
  formData,
  {
    headers: { 'Content-Type': 'multipart/form-data' }
  }
);

console.log(response.data);
```

---

## Interactive Documentation

Untuk interactive API documentation, buka:

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

---

## Rate Limiting

**Current**: No rate limiting

**Production Recommendation**:
- 10 requests per minute per IP untuk registration
- 30 requests per minute per IP untuk recognition
- 100 requests per minute per IP untuk read-only endpoints

---

## Support

Untuk pertanyaan atau issue terkait API, silakan hubungi developer atau buat issue di repository.
