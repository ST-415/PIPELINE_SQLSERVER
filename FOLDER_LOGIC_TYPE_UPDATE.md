# การปรับปรุง File Management Service - เพิ่มการตรวจสอบ Logic Type

## 📋 สรุปการเปลี่ยนแปลง

เพิ่มฟีเจอร์การตรวจสอบโฟลเดอร์ที่มีไฟล์และจัดกลุ่มตาม **logic type** เหมือนกับฟังก์ชัน `move_uploaded_files` ใน `FileService`

## ✨ ฟีเจอร์ใหม่

### 1. `find_folders_with_files()` 
- **หน้าที่**: ค้นหาโฟลเดอร์ที่มีไฟล์และจัดกลุ่มตาม logic type
- **ผลลัพธ์**: Dictionary ที่จัดกลุ่มโฟลเดอร์และไฟล์ตามประเภท
- **รูปแบบ output**:
```python
{
    'logic_type': {
        'folders': [list of folder paths],
        'files': [list of file paths], 
        'count': number of files
    }
}
```

### 2. `_detect_folder_logic_type()` 
- **หน้าที่**: ตรวจสอบประเภท logic type จากชื่อโฟลเดอร์และชื่อไฟล์
- **วิธีการ**: 
  - วิเคราะห์ชื่อไฟล์ในโฟลเดอร์ (เฉพาะ .xlsx, .xls, .csv)
  - ใช้ตัวอักษรจากชื่อไฟล์เป็นตัวระบุประเภท
  - fallback ไปใช้ชื่อโฟลเดอร์หากไม่พบจากไฟล์

### 3. `move_folders_by_logic_type()`
- **หน้าที่**: ย้ายโฟลเดอร์โดยจัดกลุ่มตาม logic type เหมือน `move_uploaded_files`
- **โครงสร้างปลายทาง**: `{dest_root}/Organized_Folders/{logic_type}/{yyyy-mm-dd}/`
- **คุณสมบัติ**:
  - ใช้ timestamp เมื่อชื่อโฟลเดอร์ซ้ำ
  - ย้ายทั้งโฟลเดอร์และไฟล์ภายใน
  - จัดกลุ่มผลลัพธ์ตาม logic type

### 4. `archive_old_files()` - ปรับปรุง
- **ลบพารามิเตอร์**: `organize_by_logic_type` (ใช้ logic type เสมอเพื่อความปลอดภัย)
- **คุณสมบัติใหม่**: 
  - จัดกลุ่มโฟลเดอร์ตาม logic type เสมอ เพื่อป้องกันการย้าย/ลบไฟล์ที่ไม่เกี่ยวข้อง
  - เพิ่มผลลัพธ์ `moved_folders_by_type` ใน return

### 5. `analyze_folder_structure()` & `print_folder_analysis()`
- **หน้าที่**: วิเคราะห์และแสดงสรุปโครงสร้างโฟลเดอร์
- **ข้อมูลที่แสดง**:
  - จำนวนโฟลเดอร์ว่าง
  - จำนวนโฟลเดอร์ที่มีไฟล์
  - จำนวนไฟล์ทั้งหมด
  - ประเภท logic type ที่พบ
  - รายละเอียดแต่ละประเภท

## 🔧 การใช้งาน

### ตัวอย่างการตรวจสอบโฟลเดอร์
```python
from services.file_management_service import FileManagementService

file_mgmt = FileManagementService()

# วิเคราะห์โครงสร้าง
analysis = file_mgmt.analyze_folder_structure("/path/to/folder")
file_mgmt.print_folder_analysis(analysis)

# ค้นหาโฟลเดอร์ที่มีไฟล์
folder_info = file_mgmt.find_folders_with_files("/path/to/folder")
```

### ตัวอย่างการย้ายโฟลเดอร์แบบจัดกลุ่ม
```python
# ย้ายโฟลเดอร์ตาม logic type
moved_results = file_mgmt.move_folders_by_logic_type(
    folder_info, 
    src_root="/source", 
    dest_root="/destination"
)

# ผลลัพธ์จะจัดกลุ่มตาม logic type
for logic_type, moves in moved_results.items():
    print(f"{logic_type}: {len(moves)} โฟลเดอร์")
```

### ตัวอย่างการจัดเก็บแบบจัดกลุ่ม
```python
# จัดเก็บไฟล์เก่าพร้อมจัดกลุ่มโฟลเดอร์ (ใช้ logic type เสมอเพื่อความปลอดภัย)
result = file_mgmt.archive_old_files(
    source_path="/data",
    archive_path="/archive", 
    days=30
)
```

## 📁 ไฟล์ที่เกี่ยวข้อง

1. **`services/file_management_service.py`** - ไฟล์หลักที่ปรับปรุง
2. **`example_folder_management_usage.py`** - ตัวอย่างการใช้งานฟีเจอร์ใหม่

## 🎯 ประโยชน์

1. **จัดระเบียบอัตโนมัติ**: โฟลเดอร์จะถูกจัดกลุ่มตาม logic type เหมือน `move_uploaded_files`
2. **โครงสร้างสม่ำเสมอ**: ใช้รูปแบบการจัดเก็บเดียวกันทั้งระบบ
3. **ติดตามได้ง่าย**: มีการแสดงผลและวิเคราะห์โครงสร้างโฟลเดอร์
4. **ความปลอดภัย**: ใช้ logic type เสมอ เพื่อป้องกันการย้าย/ลบไฟล์ที่ไม่เกี่ยวข้อง

## 🧪 การทดสอบ

รันไฟล์ตัวอย่าง:
```bash
python example_folder_management_usage.py
```

เลือกตัวอย่างที่ต้องการทดสอบ:
1. วิเคราะห์โครงสร้างโฟลเดอร์
2. จัดระเบียบโฟลเดอร์ตาม Logic Type  
3. จัดเก็บไฟล์เก่าแบบจัดกลุ่ม

## ✅ ความเข้ากันได้

- ฟีเจอร์เดิมยังคงทำงานได้ปกติ
- เพิ่มเติมฟังก์ชันใหม่โดยไม่กระทบต่อ API เดิม
- ใช้งานร่วมกับระบบที่มีอยู่ได้ทันที