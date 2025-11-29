# بنية المشروع | Architecture

## نظرة عامة

نظام Smart Parking System مبني على بنية معمارية احترافية قابلة للتوسع، مع فصل واضح بين المكونات.

## البنية المعمارية

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Routes     │  │   Schemas    │  │  Middleware  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                 Service Layer                            │
│  ┌──────────────────────────────────────────────────┐   │
│  │         ParkingService                           │   │
│  │  - Business Logic                                │   │
│  │  - Data Validation                               │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┴─────────────────┐
        ▼                                   ▼
┌──────────────────┐            ┌──────────────────┐
│  Core Modules    │            │  Database Layer   │
│  ┌────────────┐  │            │  ┌────────────┐  │
│  │ Detector   │  │            │  │  Models    │  │
│  │ Predictor  │  │            │  │  Database  │  │
│  │ Processor  │  │            │  │  Service   │  │
│  └────────────┘  │            │  └────────────┘  │
└──────────────────┘            └──────────────────┘
```

## المكونات الرئيسية

### 1. Core Modules (`app/core/`)

#### `detector.py` - ParkingSpotDetector
- **المسؤولية**: كشف أماكن الانتظار من صورة الـ mask
- **الوظائف**:
  - تحميل صورة الـ mask
  - استخدام Connected Components للكشف
  - استخراج ROI لكل مكان

#### `predictor.py` - ParkingSpotPredictor
- **المسؤولية**: التنبؤ بحالة المكان (فارغ/مشغول)
- **الوظائف**:
  - تحميل نموذج ML
  - معالجة الصورة (resize, flatten)
  - التنبؤ بالحالة

#### `processor.py` - VideoProcessor
- **المسؤولية**: معالجة الفيديو وإدارة دورة الحياة
- **الوظائف**:
  - قراءة الإطارات
  - حساب الفروقات بين الإطارات
  - تحديث حالة الأماكن
  - رسم التعليقات التوضيحية

### 2. API Layer (`app/api/`)

#### `routes.py`
- **المسؤولية**: تعريف endpoints للـ API
- **Endpoints**:
  - `GET /api/v1/status` - حالة النظام
  - `GET /api/v1/spots` - جميع الأماكن
  - `GET /api/v1/spots/{id}` - مكان محدد
  - `GET /api/v1/statistics` - إحصائيات
  - `POST /api/v1/process` - بدء المعالجة

#### `schemas.py`
- **المسؤولية**: تعريف Pydantic schemas للتحقق من البيانات

### 3. Service Layer (`app/services/`)

#### `parking_service.py`
- **المسؤولية**: منطق العمل (Business Logic)
- **الوظائف**:
  - حفظ الأماكن في قاعدة البيانات
  - حفظ الحالات التاريخية
  - حفظ الإحصائيات
  - استرجاع البيانات

### 4. Database Layer (`app/db/`)

#### `models.py`
- **المسؤولية**: تعريف نماذج قاعدة البيانات
- **النماذج**:
  - `ParkingSpot` - أماكن الانتظار
  - `SpotStatus` - الحالات التاريخية
  - `SystemStatistics` - إحصائيات النظام

#### `database.py`
- **المسؤولية**: إدارة الاتصال بقاعدة البيانات
- **الوظائف**:
  - إنشاء engine
  - إدارة الجلسات
  - تهيئة الجداول

### 5. Utils (`app/utils/`)

#### `config.py`
- **المسؤولية**: إدارة الإعدادات
- **الميزات**:
  - استخدام Pydantic Settings
  - قراءة من `.env`
  - التحقق من الإعدادات

#### `logger.py`
- **المسؤولية**: إعداد نظام التسجيل
- **الميزات**:
  - Loguru للـ logging
  - Console + File logging
  - Rotation و compression

## تدفق البيانات

### معالجة الفيديو:

```
Video File
    │
    ▼
VideoProcessor.initialize()
    │
    ▼
Detector.detect_spots() ──► Mask Image
    │
    ▼
VideoProcessor.process_frame()
    │
    ├─► Calculate Differences
    │
    ├─► Select Spots to Check
    │
    └─► Predictor.predict() ──► ML Model
            │
            ▼
        Update Status
            │
            ▼
        Annotate Frame
            │
            ▼
        Display/Save
```

### API Request:

```
Client Request
    │
    ▼
FastAPI Router
    │
    ▼
Route Handler
    │
    ▼
ParkingService
    │
    ├─► Database Query
    │
    └─► Return Response
```

## التصميمات المستخدمة

### 1. Separation of Concerns
- كل مكون له مسؤولية واحدة واضحة
- فصل منطق العمل عن الوصول للبيانات

### 2. Dependency Injection
- استخدام FastAPI Depends
- سهولة الاختبار والاستبدال

### 3. Repository Pattern
- ParkingService كطبقة وسيطة
- إخفاء تفاصيل قاعدة البيانات

### 4. Factory Pattern
- إنشاء المكونات من خلال factories
- سهولة التكوين

## قابلية التوسع

### إضافة ميزات جديدة:

1. **Real-time WebSocket**: إضافة WebSocket للبث المباشر
2. **Multiple Cameras**: دعم كاميرات متعددة
3. **Advanced ML Models**: استبدال النموذج بنماذج أكثر تطوراً
4. **Mobile App**: إضافة تطبيق موبايل
5. **Analytics Dashboard**: لوحة تحكم للإحصائيات

### تحسينات الأداء:

1. **Async Processing**: استخدام async/await
2. **Caching**: إضافة Redis للـ caching
3. **Queue System**: استخدام Celery للمهام الخلفية
4. **GPU Acceleration**: استخدام GPU للمعالجة

## الأمان

- **Input Validation**: استخدام Pydantic
- **Error Handling**: معالجة شاملة للأخطاء
- **Logging**: تسجيل جميع العمليات
- **Environment Variables**: حماية البيانات الحساسة

## الاختبار

- **Unit Tests**: اختبار كل مكون بشكل منفصل
- **Integration Tests**: اختبار التكامل بين المكونات
- **API Tests**: اختبار endpoints

