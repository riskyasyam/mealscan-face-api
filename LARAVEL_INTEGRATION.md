# Laravel Migration Examples

## Migration: Create Employees Table

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('employees', function (Blueprint $table) {
            $table->id();
            $table->string('employee_id', 50)->unique();
            $table->string('name', 100);
            $table->string('email', 100)->nullable();
            $table->string('phone', 20)->nullable();
            $table->string('department', 50)->nullable();
            $table->string('position', 50)->nullable();
            $table->boolean('is_active')->default(true);
            $table->timestamps();
            
            $table->index('employee_id');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('employees');
    }
};
```

## Migration: Create Face Embeddings Table

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('face_embeddings', function (Blueprint $table) {
            $table->id();
            $table->string('employee_id', 50);
            $table->string('embedding_path', 255);
            $table->string('face_image_path', 255);
            $table->float('confidence_score')->nullable();
            $table->json('bbox')->nullable();
            $table->timestamps();
            
            $table->foreign('employee_id')
                  ->references('employee_id')
                  ->on('employees')
                  ->onDelete('cascade');
            
            $table->index('employee_id');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('face_embeddings');
    }
};
```

## Migration: Create Meal Time Settings Table

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('meal_time_settings', function (Blueprint $table) {
            $table->id();
            $table->enum('meal_type', ['breakfast', 'lunch', 'dinner'])->unique();
            $table->time('start_time');
            $table->time('end_time');
            $table->boolean('is_active')->default(true);
            $table->timestamps();
        });
        
        // Insert default values
        DB::table('meal_time_settings')->insert([
            [
                'meal_type' => 'breakfast',
                'start_time' => '06:00:00',
                'end_time' => '08:00:00',
                'is_active' => true,
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'meal_type' => 'lunch',
                'start_time' => '11:30:00',
                'end_time' => '13:30:00',
                'is_active' => true,
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'meal_type' => 'dinner',
                'start_time' => '17:30:00',
                'end_time' => '19:30:00',
                'is_active' => true,
                'created_at' => now(),
                'updated_at' => now(),
            ],
        ]);
    }

    public function down(): void
    {
        Schema::dropIfExists('meal_time_settings');
    }
};
```

## Migration: Create Attendance Logs Table

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('attendance_logs', function (Blueprint $table) {
            $table->id();
            $table->string('employee_id', 50);
            $table->enum('meal_type', ['breakfast', 'lunch', 'dinner']);
            $table->enum('status', ['present', 'absent', 'late'])->default('present');
            $table->date('attendance_date');
            $table->timestamp('attendance_time')->useCurrent();
            $table->float('similarity_score')->nullable();
            $table->float('confidence_score')->nullable();
            $table->timestamps();
            
            $table->foreign('employee_id')
                  ->references('employee_id')
                  ->on('employees')
                  ->onDelete('cascade');
            
            // Unique constraint: 1 attendance per employee per meal type per day
            $table->unique(['employee_id', 'meal_type', 'attendance_date'], 'unique_attendance');
            
            $table->index('attendance_date');
            $table->index('employee_id');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('attendance_logs');
    }
};
```

## Model Examples

### Employee Model

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasOne;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Employee extends Model
{
    protected $fillable = [
        'employee_id',
        'name',
        'email',
        'phone',
        'department',
        'position',
        'is_active',
    ];

    protected $casts = [
        'is_active' => 'boolean',
    ];

    public function faceEmbedding(): HasOne
    {
        return $this->hasOne(FaceEmbedding::class, 'employee_id', 'employee_id');
    }

    public function attendanceLogs(): HasMany
    {
        return $this->hasMany(AttendanceLog::class, 'employee_id', 'employee_id');
    }
    
    public function hasFaceRegistered(): bool
    {
        return $this->faceEmbedding()->exists();
    }
}
```

### AttendanceLog Model

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class AttendanceLog extends Model
{
    protected $fillable = [
        'employee_id',
        'meal_type',
        'status',
        'attendance_date',
        'attendance_time',
        'similarity_score',
        'confidence_score',
    ];

    protected $casts = [
        'attendance_date' => 'date',
        'attendance_time' => 'datetime',
        'similarity_score' => 'float',
        'confidence_score' => 'float',
    ];

    public function employee(): BelongsTo
    {
        return $this->belongsTo(Employee::class, 'employee_id', 'employee_id');
    }
}
```

### MealTimeSetting Model

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Carbon\Carbon;

class MealTimeSetting extends Model
{
    protected $fillable = [
        'meal_type',
        'start_time',
        'end_time',
        'is_active',
    ];

    protected $casts = [
        'start_time' => 'datetime:H:i:s',
        'end_time' => 'datetime:H:i:s',
        'is_active' => 'boolean',
    ];

    public static function getCurrentMealType(): ?string
    {
        $now = Carbon::now()->format('H:i:s');
        
        $setting = self::where('is_active', true)
            ->where('start_time', '<=', $now)
            ->where('end_time', '>=', $now)
            ->first();
        
        return $setting?->meal_type;
    }
    
    public function isActiveNow(): bool
    {
        if (!$this->is_active) {
            return false;
        }
        
        $now = Carbon::now()->format('H:i:s');
        return $now >= $this->start_time && $now <= $this->end_time;
    }
}
```

## API Routes

```php
<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\EmployeeController;
use App\Http\Controllers\AttendanceController;
use App\Http\Controllers\MealTimeController;

// Employee Management
Route::prefix('employees')->group(function () {
    Route::get('/', [EmployeeController::class, 'index']);
    Route::post('/', [EmployeeController::class, 'store']);
    Route::get('/{employee}', [EmployeeController::class, 'show']);
    Route::put('/{employee}', [EmployeeController::class, 'update']);
    Route::delete('/{employee}', [EmployeeController::class, 'destroy']);
    
    // Face registration
    Route::post('/{employee}/register-face', [EmployeeController::class, 'registerFace']);
    Route::delete('/{employee}/delete-face', [EmployeeController::class, 'deleteFace']);
});

// Attendance
Route::prefix('attendance')->group(function () {
    Route::post('/checkin', [AttendanceController::class, 'checkIn']);
    Route::get('/today', [AttendanceController::class, 'today']);
    Route::get('/history', [AttendanceController::class, 'history']);
    Route::get('/stats', [AttendanceController::class, 'stats']);
});

// Meal Time Settings
Route::prefix('meal-times')->group(function () {
    Route::get('/', [MealTimeController::class, 'index']);
    Route::get('/current', [MealTimeController::class, 'current']);
    Route::put('/{mealType}', [MealTimeController::class, 'update']);
});
```
