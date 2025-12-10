# 🔧 TROUBLESHOOTING - Meal Time & Face Recognition

## ❌ Issue 1: "No active meal time" Badge

### Penyebab:
Controller tidak mendeteksi meal time dengan benar dari database.

### Solusi:

#### 1. Cek Database
```sql
SELECT * FROM meal_time_settings WHERE is_active = 1;
```

Harus ada 3 rows dengan format:
```
breakfast: 06:00:00 - 08:00:00
lunch: 11:00:00 - 13:00:00  
dinner: 17:00:00 - 19:00:00
```

#### 2. Pastikan Model MealTimeSetting Benar

File: `app/Models/MealTimeSetting.php`

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Carbon\Carbon;

class MealTimeSetting extends Model
{
    protected $fillable = ['meal_type', 'start_time', 'end_time', 'is_active'];

    protected $casts = [
        'is_active' => 'boolean',
    ];

    public static function getCurrentMealType()
    {
        $now = Carbon::now()->format('H:i:s');
        
        $setting = self::where('is_active', true)
            ->whereRaw('? BETWEEN start_time AND end_time', [$now])
            ->first();
        
        return $setting ? $setting->meal_type : null;
    }
}
```

#### 3. Test di Tinker

```bash
php artisan tinker
```

```php
use App\Models\MealTimeSetting;
use Carbon\Carbon;

// Check current time
echo Carbon::now()->format('H:i:s');  // e.g., "17:45:00"

// Check meal type
$mealType = MealTimeSetting::getCurrentMealType();
dd($mealType);  // Should return "dinner" if time is 17:45
```

#### 4. Update Controller

File: `app/Http/Controllers/AttendanceController.php`

```php
public function index()
{
    $currentMealType = MealTimeSetting::getCurrentMealType();
    
    $attendances = AttendanceLog::with('employee')
        ->whereDate('attendance_time', today())
        ->orderBy('attendance_time', 'desc')
        ->get();

    return view('attendance.index', compact('currentMealType', 'attendances'));
}
```

---

## ❌ Issue 2: Wajah Tidak Terdeteksi

### Penyebab:
1. Python API tidak running
2. Laravel tidak bisa connect ke Python API
3. Employee belum register face

### Solusi:

#### 1. Pastikan Python API Running

```bash
# Terminal 1 - Python API
cd C:\path\to\face_recog_makan\api
python main.py

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

#### 2. Test Python API

```bash
# Test health
curl http://localhost:8001/health

# Expected:
# {"status":"healthy","timestamp":"...","model_loaded":true}

# Test list employees
curl http://localhost:8001/employees

# Expected:
# {"success":true,"employees":["123456","789012"],"count":2}
```

#### 3. Update Laravel .env

File: `.env`

```env
FACE_RECOGNITION_API_URL=http://localhost:8001
```

#### 4. Update FaceRecognitionService

File: `app/Services/FaceRecognitionService.php`

```php
<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class FaceRecognitionService
{
    protected $apiUrl;

    public function __construct()
    {
        $this->apiUrl = config('services.face_recognition.api_url', 'http://localhost:8001');
    }

    public function checkHealth()
    {
        try {
            $response = Http::timeout(5)->get("{$this->apiUrl}/health");
            return $response->successful() ? $response->json() : null;
        } catch (\Exception $e) {
            Log::error('Python API health check failed: ' . $e->getMessage());
            return null;
        }
    }

    public function recognizeFace($imagePath)
    {
        try {
            Log::info('Recognizing face from: ' . $imagePath);
            
            $response = Http::timeout(30)
                ->attach('file', file_get_contents($imagePath), basename($imagePath))
                ->post("{$this->apiUrl}/recognize");

            if ($response->successful()) {
                $result = $response->json();
                Log::info('Recognition result:', $result);
                return $result;
            }

            Log::error('Recognition failed:', $response->json());
            return [
                'success' => false,
                'message' => 'Failed to recognize face'
            ];

        } catch (\Exception $e) {
            Log::error('Error recognizing face: ' . $e->getMessage());
            return [
                'success' => false,
                'message' => $e->getMessage()
            ];
        }
    }

    public function registerFace($employeeId, $imagePath, $employeeName = null)
    {
        try {
            Log::info("Registering face for employee: {$employeeId}");
            
            $response = Http::timeout(30)
                ->attach('file', file_get_contents($imagePath), basename($imagePath))
                ->post("{$this->apiUrl}/api/face/register", [
                    'employee_id' => $employeeId
                ]);

            if ($response->successful()) {
                $result = $response->json();
                Log::info('Registration result:', $result);
                return $result;
            }

            Log::error('Registration failed:', $response->json());
            return [
                'success' => false,
                'message' => 'Failed to register face'
            ];

        } catch (\Exception $e) {
            Log::error('Error registering face: ' . $e->getMessage());
            return [
                'success' => false,
                'message' => $e->getMessage()
            ];
        }
    }
}
```

#### 5. Update AttendanceController checkIn Method

File: `app/Http/Controllers/AttendanceController.php`

```php
use App\Services\FaceRecognitionService;
use App\Models\MealTimeSetting;
use App\Models\AttendanceLog;
use App\Models\Employee;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;

public function checkIn(Request $request)
{
    try {
        // Validate request
        $request->validate([
            'image' => 'required|string',
            'quantity' => 'required|integer|min:1|max:10'
        ]);

        // Check meal time
        $currentMealType = MealTimeSetting::getCurrentMealType();
        
        if (!$currentMealType) {
            return response()->json([
                'success' => false,
                'message' => 'Tidak dalam waktu makan. Silakan cek jadwal makan.'
            ], 400);
        }

        // Decode base64 image
        $imageData = $request->input('image');
        $imageData = str_replace('data:image/jpeg;base64,', '', $imageData);
        $imageData = str_replace(' ', '+', $imageData);
        $decodedImage = base64_decode($imageData);

        // Save temporary file
        $tempPath = storage_path('app/temp/capture_' . time() . '.jpg');
        if (!file_exists(dirname($tempPath))) {
            mkdir(dirname($tempPath), 0755, true);
        }
        file_put_contents($tempPath, $decodedImage);

        // Call face recognition service
        $faceService = new FaceRecognitionService();
        $result = $faceService->recognizeFace($tempPath);

        // Clean up temp file
        if (file_exists($tempPath)) {
            unlink($tempPath);
        }

        // Check recognition result
        if (!$result['success']) {
            return response()->json([
                'success' => false,
                'message' => $result['message'] ?? 'Wajah tidak dikenali'
            ], 400);
        }

        $employeeId = $result['employee_id'] ?? $result['nik'] ?? null;
        
        if (!$employeeId) {
            return response()->json([
                'success' => false,
                'message' => 'Employee ID tidak ditemukan'
            ], 400);
        }

        // Get employee from database
        $employee = Employee::where('nik', $employeeId)->first();
        
        if (!$employee) {
            return response()->json([
                'success' => false,
                'message' => 'Karyawan tidak terdaftar di database'
            ], 404);
        }

        // Check if already attended today for this meal type
        $existingAttendance = AttendanceLog::where('nik', $employeeId)
            ->where('meal_type', $currentMealType)
            ->whereDate('attendance_time', today())
            ->first();

        if ($existingAttendance) {
            return response()->json([
                'success' => false,
                'message' => "Anda sudah absen {$currentMealType} hari ini"
            ], 400);
        }

        // Save attendance
        $attendance = AttendanceLog::create([
            'nik' => $employeeId,
            'meal_type' => $currentMealType,
            'quantity' => $request->input('quantity'),
            'attendance_time' => now(),
            'similarity_score' => $result['similarity'] ?? null,
            'confidence_score' => $result['confidence'] ?? null
        ]);

        return response()->json([
            'success' => true,
            'message' => "Absensi {$currentMealType} berhasil! Selamat makan.",
            'nik' => $employeeId,
            'employee_id' => $employeeId,
            'employee_name' => $employee->name,
            'meal_type' => $currentMealType,
            'quantity' => $attendance->quantity
        ]);

    } catch (\Exception $e) {
        Log::error('Check-in error: ' . $e->getMessage());
        Log::error($e->getTraceAsString());
        
        return response()->json([
            'success' => false,
            'message' => 'Terjadi kesalahan: ' . $e->getMessage()
        ], 500);
    }
}
```

---

## 📝 Checklist Testing

### Python API:
- [ ] Python API running di port 8001
- [ ] Endpoint /health returns {"status":"healthy"}
- [ ] Endpoint /employees returns list of NIKs
- [ ] Folder `data/embeddings/` ada file *.pkl

### Laravel:
- [ ] MealTimeSetting::getCurrentMealType() return correct meal
- [ ] Database meal_time_settings has 3 active rows
- [ ] FaceRecognitionService can connect to Python API
- [ ] Employee sudah register face (ada file embedding)

### Browser:
- [ ] Camera permission granted
- [ ] Video feed muncul (terbalik/mirror OK)
- [ ] Badge shows correct meal type (not "No active meal time")
- [ ] Console tidak ada error

---

## 🚀 Quick Fix Commands

```bash
# 1. Re-seed database
php artisan migrate:fresh --seed

# 2. Clear Laravel cache
php artisan config:clear
php artisan cache:clear

# 3. Test meal time detection
php artisan tinker
MealTimeSetting::getCurrentMealType();

# 4. Check Python API
curl http://localhost:8001/health
curl http://localhost:8001/employees

# 5. Check Laravel logs
tail -f storage/logs/laravel.log
```

---

## 📞 Still Not Working?

1. Check Laravel logs: `storage/logs/laravel.log`
2. Check Python API terminal output
3. Check browser console (F12)
4. Verify employee has registered face embedding
