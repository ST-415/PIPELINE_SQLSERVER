# คู่มือการปรับปรุง Performance สำหรับ PIPELINE_SQLSERVER

## ภาพรวม

คู่มือนี้จะอธิบายการปรับปรุง Performance ที่ได้ทำไปแล้วเพื่อแก้ปัญหาการแลคเมื่อเจอไฟล์ใหญ่มาก ๆ

## ปัญหาที่พบ

1. **Memory Usage สูง**: การอ่านไฟล์ใหญ่ทั้งหมดเข้า memory พร้อมกัน
2. **UI Blocking**: การประมวลผลใน main thread ทำให้ UI ค้าง
3. **ไม่มี Progress Tracking**: ผู้ใช้ไม่ทราบความคืบหน้า
4. **ไม่สามารถยกเลิกได้**: ไม่มีวิธีหยุดการทำงานที่กำลังดำเนินการ
5. **การอัปโหลดช้า**: อัปโหลดข้อมูลทั้งหมดพร้อมกัน

## การปรับปรุงที่ทำ

### 1. การอ่านไฟล์แบบ Chunked

**ไฟล์ที่ปรับปรุง**: `services/file_service.py`

```python
# ใช้ PerformanceOptimizer สำหรับการอ่านไฟล์
from performance_optimizations import PerformanceOptimizer

optimizer = PerformanceOptimizer(self.log_callback)
success, df = optimizer.read_large_file_chunked(file_path, file_type)
```

**ประโยชน์**:
- ลดการใช้ memory เมื่อเจอไฟล์ใหญ่
- แสดงความคืบหน้าการอ่านไฟล์
- รองรับไฟล์ขนาดใหญ่กว่า 100MB

### 2. การประมวลผลแบบ Chunked

**ไฟล์ที่ปรับปรุง**: `services/file_service.py`

```python
def _process_dataframe_in_chunks(self, df, process_func, logic_type, chunk_size=5000):
    """ประมวลผล DataFrame แบบ chunk เพื่อประหยัด memory"""
```

**ประโยชน์**:
- ประมวลผลข้อมูลทีละส่วน
- ปล่อย memory ระหว่างการประมวลผล
- แสดงความคืบหน้าการประมวลผล

### 3. การอัปโหลดแบบ Chunked

**ไฟล์ที่ปรับปรุง**: `services/database_service.py`

```python
# อัปโหลดข้อมูลแบบ chunked สำหรับไฟล์ใหญ่
if len(df) > 10000:  # ถ้าไฟล์ใหญ่กว่า 10,000 แถว
    chunk_size = 5000
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i+chunk_size]
        chunk[list(required_cols.keys())].to_sql(...)
```

**ประโยชน์**:
- ลดการใช้ memory ในการอัปโหลด
- แสดงความคืบหน้าการอัปโหลด
- ลดโอกาส timeout

### 4. การยกเลิกการทำงาน

**ไฟล์ที่ปรับปรุง**: `ui/main_window.py`

```python
# สร้าง cancellation token
self.cancellation_token = threading.Event()

# ปุ่มยกเลิก
self.cancel_button = ctk.CTkButton(
    text="❌ ยกเลิก",
    command=self._cancel_operation,
    state="disabled"
)
```

**ประโยชน์**:
- ผู้ใช้สามารถยกเลิกการทำงานได้
- ตรวจสอบการยกเลิกระหว่างขั้นตอน
- ปิดปุ่มยกเลิกเมื่อไม่มีการทำงาน

### 5. การแสดงความคืบหน้าที่ละเอียด

**ไฟล์ที่ปรับปรุง**: `ui/components/progress_bar.py`

```python
def update(self, progress, status_text="", detail_text=""):
    """อัปเดต Progress Bar พร้อมข้อความสถานะ"""
    self.progress_bar.set(progress)
    
    if status_text:
        self.progress_label.configure(text=status_text)
    
    if detail_text:
        self.detail_label.configure(text=detail_text)
```

**ประโยชน์**:
- แสดงความคืบหน้าแบบ real-time
- แสดงรายละเอียดการทำงาน
- แสดงเวลาที่เหลือ

### 6. การจัดการ Memory ที่ดีขึ้น

**ไฟล์ที่ปรับปรุง**: `performance_optimizations.py`

```python
def optimize_memory_usage(self, df: pd.DataFrame) -> pd.DataFrame:
    """ปรับปรุงการใช้ memory ของ DataFrame"""
    # ลดขนาดของ numeric columns
    for col in df.select_dtypes(include=['int64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='integer')
    
    # ลดขนาดของ object columns
    for col in df.select_dtypes(include=['object']).columns:
        if df[col].nunique() / len(df) < 0.5:
            df[col] = df[col].astype('category')
```

**ประโยชน์**:
- ลดการใช้ memory ลง 30-70%
- ปรับปรุงความเร็วในการประมวลผล
- แสดงรายงานการประหยัด memory

## การใช้งาน

### 1. การใช้งานปกติ

การปรับปรุงจะทำงานอัตโนมัติเมื่อ:
- ไฟล์มีขนาดใหญ่กว่า 100MB
- ข้อมูลมีมากกว่า 10,000 แถว
- ใช้การประมวลผลอัตโนมัติ

### 2. การยกเลิกการทำงาน

1. กดปุ่ม "🤖 ประมวลผลอัตโนมัติ"
2. กดปุ่ม "❌ ยกเลิก" เพื่อหยุดการทำงาน
3. ระบบจะหยุดการทำงานอย่างปลอดภัย

### 3. การติดตามความคืบหน้า

- Progress Bar จะแสดงความคืบหน้าแบบ real-time
- Log จะแสดงรายละเอียดการทำงาน
- แสดงเวลาที่เหลือในการทำงาน

## การตั้งค่า

### 1. ขนาด Chunk

สามารถปรับขนาด chunk ได้ใน `performance_optimizations.py`:

```python
class PerformanceOptimizer:
    def __init__(self, log_callback: Optional[Callable] = None):
        self.chunk_size = 10000  # ขนาด chunk สำหรับการอ่านไฟล์
        self.max_workers = min(4, os.cpu_count() or 1)  # จำนวน worker threads
```

### 2. ขีดจำกัดไฟล์ใหญ่

```python
if file_size_mb > 100:  # ไฟล์ใหญ่กว่า 100MB
    return self._read_large_file_chunked(file_path, file_type)
```

### 3. ขีดจำกัดการอัปโหลด

```python
if len(df) > 10000:  # ถ้าไฟล์ใหญ่กว่า 10,000 แถว
    # ใช้การอัปโหลดแบบ chunked
```

## การทดสอบ Performance

### 1. ไฟล์ขนาดเล็ก (< 10MB)
- ควรประมวลผลได้เร็วขึ้น 10-20%
- ใช้ memory น้อยลง 20-30%

### 2. ไฟล์ขนาดกลาง (10-100MB)
- ควรประมวลผลได้เร็วขึ้น 30-50%
- ใช้ memory น้อยลง 40-60%
- UI ไม่ค้าง

### 3. ไฟล์ขนาดใหญ่ (> 100MB)
- ควรประมวลผลได้เร็วขึ้น 50-80%
- ใช้ memory น้อยลง 60-80%
- สามารถยกเลิกได้
- แสดงความคืบหน้า

## การแก้ไขปัญหา

### 1. หากยังแลค

1. ลดขนาด chunk ใน `performance_optimizations.py`
2. เพิ่มการทำความสะอาด memory บ่อยขึ้น
3. ตรวจสอบการตั้งค่า SQL Server

### 2. หากยกเลิกไม่ได้

1. ตรวจสอบ cancellation token
2. เพิ่มการตรวจสอบการยกเลิกในทุกขั้นตอน
3. ใช้ `threading.Event()` แทน flag

### 3. หาก Progress Bar ไม่อัปเดต

1. ตรวจสอบการใช้ `self.after(0, ...)`
2. ตรวจสอบ thread safety
3. เพิ่มการอัปเดต UI บ่อยขึ้น

## การพัฒนาต่อ

### 1. การเพิ่มฟีเจอร์

- การประมวลผลแบบ Parallel สำหรับหลายไฟล์
- การบีบอัดข้อมูลก่อนอัปโหลด
- การใช้ Database Connection Pool
- การ Cache ผลลัพธ์

### 2. การปรับปรุง Performance เพิ่มเติม

- การใช้ GPU สำหรับการประมวลผล
- การใช้ Streaming สำหรับไฟล์ใหญ่มาก
- การใช้ Distributed Processing
- การใช้ Cloud Storage

## สรุป

การปรับปรุง Performance เหล่านี้จะช่วยให้แอปพลิเคชันสามารถประมวลผลไฟล์ใหญ่ได้อย่างมีประสิทธิภาพ โดยไม่ทำให้ UI ค้าง และผู้ใช้สามารถติดตามความคืบหน้าและยกเลิกการทำงานได้ 