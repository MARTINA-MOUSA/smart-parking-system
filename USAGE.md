# دليل الاستخدام | Usage Guide

## البدء السريع

### 1. إعداد البيئة

```bash
# إنشاء virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# تثبيت المتطلبات
pip install -r requirements.txt
```

### 2. إعداد الملفات

1. انسخ `env.example` إلى `.env`:
```bash
cp env.example .env
```

2. ضع ملف الـ mask في `data/masks/` (مثال: `mask_1920_1080.png`)

3. ضع ملفات الفيديو في `data/videos/`

4. ضع نموذج ML في `models/` (مثال: `model.p`)

### 3. تشغيل النظام

#### معالجة فيديو مباشرة:

```bash
python run.py --video ./data/videos/parking_1920_1080_loop.mp4
```

#### تشغيل API Server:

```bash
python run.py --api
```

أو:

```bash
uvicorn app.main:app --reload --port 8000
```

#### استخدام Docker:

```bash
docker-compose up -d
```

## استخدام API

### الحصول على حالة النظام

```bash
curl http://localhost:8000/api/v1/status
```

### الحصول على جميع أماكن الانتظار

```bash
curl http://localhost:8000/api/v1/spots
```

### الحصول على مكان محدد

```bash
curl http://localhost:8000/api/v1/spots/0
```

### الحصول على الإحصائيات

```bash
curl http://localhost:8000/api/v1/statistics
```

### بدء معالجة فيديو

```bash
curl -X POST http://localhost:8000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{"video_path": "./data/videos/parking.mp4", "save_to_db": true}'
```

## الوثائق التفاعلية

بعد تشغيل API Server، يمكنك الوصول إلى:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## إعدادات متقدمة

### تعديل معاملات المعالجة

في ملف `.env`:

```env
PROCESSING_STEP=30          # معالجة كل 30 إطار
DIFF_THRESHOLD=0.4         # عتبة التغيير (0-1)
RESIZE_WIDTH=15            # عرض الصورة للموديل
RESIZE_HEIGHT=15           # ارتفاع الصورة للموديل
```

### استخدام قاعدة بيانات PostgreSQL

```env
DATABASE_URL=postgresql://user:password@localhost/parking_db
```

## استكشاف الأخطاء

### المشكلة: لا يمكن تحميل الموديل

**الحل**: تأكد من وجود ملف `model.p` في مجلد `models/`

### المشكلة: لا يمكن تحميل الـ mask

**الحل**: تأكد من وجود ملف الـ mask في المسار المحدد في `.env`

### المشكلة: خطأ في قاعدة البيانات

**الحل**: تأكد من إنشاء مجلد `data/` وتأكد من صلاحيات الكتابة

## أمثلة الكود

### استخدام النظام برمجياً

```python
from app.core.detector import ParkingSpotDetector
from app.core.predictor import ParkingSpotPredictor
from app.core.processor import VideoProcessor
from app.utils.config import settings

# تهيئة المكونات
detector = ParkingSpotDetector(str(settings.get_mask_path()))
predictor = ParkingSpotPredictor(str(settings.get_model_path()))

# إنشاء المعالج
processor = VideoProcessor(
    detector=detector,
    predictor=predictor,
    processing_step=30,
    diff_threshold=0.4
)

# تهيئة المعالج بالفيديو
processor.initialize(video_path="./data/videos/parking.mp4")

# معالجة الإطارات
while True:
    frame = processor.process_frame()
    if frame is None:
        break
    
    # عرض أو حفظ الإطار
    cv2.imshow('Parking', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# الحصول على الإحصائيات
stats = processor.get_statistics()
print(stats)

# تحرير الموارد
processor.release()
```

