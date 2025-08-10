# Services Module - PIPELINE_SQLSERVER

โฟลเดอร์ `services/` ถูกจัดระเบียบใหม่เพื่อแยกหน้าที่ให้ชัดเจนและง่ายต่อการบำรุงรักษา

## โครงสร้างใหม่

### 🗄️ DatabaseService (`database_service.py`)
**หน้าที่:** การจัดการฐานข้อมูล SQL Server
- การเชื่อมต่อฐานข้อมูล
- การอัปโหลดข้อมูล
- การจัดการ schema
- การตรวจสอบการเชื่อมต่อ

### 📖 FileReaderService (`file_reader_service.py`)
**หน้าที่:** การอ่านและตรวจจับไฟล์
- ค้นหาไฟล์ Excel/CSV
- อ่านไฟล์แบบพื้นฐาน
- ตรวจจับประเภทไฟล์อัตโนมัติ
- จัดการ column mapping
- ตรวจสอบโครงสร้างไฟล์

### ⚙️ DataProcessorService (`data_processor_service.py`)
**หน้าที่:** การประมวลผลและตรวจสอบข้อมูล
- ตรวจสอบความถูกต้องของข้อมูล (validation)
- แปลงประเภทข้อมูล (data type conversion)
- ทำความสะอาดข้อมูล (data cleaning)
- ตัดข้อมูลที่ยาวเกิน (string truncation)
- สร้างรายงานการตรวจสอบ

### 📁 FileManagementService (`file_management_service.py`)
**หน้าที่:** การจัดการไฟล์
- ย้ายไฟล์ที่ประมวลผลแล้ว
- จัดระเบียบโฟลเดอร์
- จัดการการตั้งค่า

### 🎛️ FileService (`file_service.py`)
**หน้าที่:** Orchestrator หลัก
- ประสานงานระหว่าง services ต่างๆ
- ให้ interface เดียวกันกับระบบเดิม (backward compatible)
- การอ่านและประมวลผลไฟล์แบบครบวงจร

### 🔐 PermissionCheckerService (`permission_checker_service.py`)
**หน้าที่:** ตรวจสอบสิทธิ์ของผู้ใช้/connection บน SQL Server
- ตรวจสิทธิ์ CRUD ขั้นพื้นฐานบน schema เป้าหมาย (เช่น `bronze`)
- สรุปสิทธิ์ที่ขาดและคำแนะนำการตั้งค่า

### ⚡ PreloadService (`preload_service.py`)
**หน้าที่:** โหลดการตั้งค่าที่จำเป็นล่วงหน้า
- โหลด column mapping และ dtype mapping จาก `config/`
- คืนค่าโครงสร้างที่พร้อมใช้ใน UI/Service อื่นๆ

## การใช้งาน

### Basic Usage (แบบเดิม - ยังใช้ได้)
```python
from services import FileService, DatabaseService

# สร้าง services
file_service = FileService(log_callback=print)
db_service = DatabaseService()

# อ่านและประมวลผลไฟล์
success, df = file_service.read_excel_file("data.xlsx", "sales_data")

# อัปโหลดไปฐานข้อมูล
if success:
    dtypes = file_service.get_required_dtypes("sales_data")
    result = db_service.upload_data(df, "sales_data", dtypes)
```

### Advanced Usage (ใช้ services แยก)
```python
from services import FileReaderService, DataProcessorService, FileManagementService

# อ่านไฟล์อย่างเดียว
reader = FileReaderService()
success, df = reader.read_file_basic("data.xlsx")

# ตรวจสอบข้อมูลอย่างเดียว  
processor = DataProcessorService()
validation = processor.comprehensive_data_validation(df, "sales_data")

# จัดการไฟล์
manager = FileManagementService()
result = manager.move_processed_files("/path/to/processed/files")
```

## การเปลี่ยนแปลง

### ✅ สิ่งที่ยังใช้ได้ (Backward Compatible)
- `FileService` - ยังทำงานเหมือนเดิม
- `DatabaseService` - ไม่เปลี่ยนแปลง
- การ import แบบเดิม: `from services import FileService, DatabaseService`
- Methods หลักทั้งหมดยังใช้ได้

### 🆕 สิ่งที่เพิ่มเข้ามา
- **Services แยกตามหน้าที่:** สามารถใช้แต่ละ service แยกได้
- **Better separation of concerns:** แต่ละ service มีหน้าที่ชัดเจน
- **เพิ่ม methods ใหม่:**
  - `FileReaderService.peek_file_structure()`
  - `FileReaderService.get_file_info()`
  - `FileReaderService.validate_file_before_processing()`
  - และอื่นๆ

### 🗑️ สิ่งที่ Deprecated
- Legacy database methods ใน `FileService` (เช่น `upload_to_sql`)
- จะได้รับคำเตือนแต่ยังใช้ได้

## ประโยชน์ของการจัดระเบียบใหม่

1. **📦 Modularity**: แต่ละ service มีหน้าที่ชัดเจน
2. **🔧 Maintainability**: ง่ายต่อการแก้ไขและพัฒนา
3. **🧪 Testability**: ทดสอบแต่ละ service ได้แยกกัน
4. **🔄 Reusability**: สามารถใช้ service ใดๆ แยกได้
5. **⚡ Performance**: แยก responsibilities ทำให้เร็วขึ้น
6. **🔒 Backward Compatibility**: โค้ดเดิมยังใช้ได้

## ไฟล์ที่เก็บไว้เพื่อการอ้างอิง

- (ถ้ามี) `file_service_old.py` - FileService เดิมก่อนการจัดระเบียบ (backup)

---

**หมายเหตุ:** การจัดระเบียบนี้ไม่ทำให้โค้ดเดิมเสีย แต่จะช่วยให้การพัฒนาต่อไปง่ายขึ้นและมีประสิทธิภาพมากขึ้น
