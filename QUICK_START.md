# Quick Start Guide - PIPELINE_SQLSERVER

**เครื่องมือนำเข้าข้อมูล Excel/CSV เข้า SQL Server แบบง่าย ไม่ต้องเขียนโค้ด**

พร้อมใช้งานใน 5 นาที! 🚀

## ⚡ การติดตั้งเร็ว (5 ขั้นตอน)

### 1. Download และ Setup
```bash
git clone https://github.com/yourusername/PIPELINE_SQLSERVER.git
cd PIPELINE_SQLSERVER
```

### 2. ติดตั้ง Dependencies
```bash
# Windows (แนะนำ)
install_requirements.bat

# หรือใช้ pip
pip install -r requirements.txt
```

### 3. ตั้งค่าเบื้องต้น
```bash
# รันสคริปต์ตั้งค่า (จะสร้าง .env และตรวจสอบระบบ)
python install_requirements.py
```

### 4. แก้ไขการตั้งค่าฐานข้อมูล
แก้ไขไฟล์ `.env` ที่ถูกสร้างขึ้น:
```env
DB_SERVER=localhost\SQLEXPRESS
DB_NAME=YourDatabase
# สำหรับ Windows Auth ให้เว้นว่าง username/password
DB_USERNAME=
DB_PASSWORD=
```

### 5. รัน!
```bash
# GUI Application
python pipeline_gui_app.py

# หรือ CLI (ถ้าต้องการประมวลผลอัตโนมัติ)
python auto_process_cli.py "C:\path\to\your\data"
```

---

## 🎯 การใช้งานแรก (First Time Setup)

### GUI Mode
1. **เปิดโปรแกรม**: รัน `python pipeline_gui_app.py`
2. **ทดสอบการเชื่อมต่อ**: โปรแกรมจะทดสอบการเชื่อมต่อฐานข้อมูลอัตโนมัติ
3. **เลือกโฟลเดอร์**: เลือกโฟลเดอร์ที่มีไฟล์ Excel/CSV
4. **ตั้งค่าประเภทไฟล์**: กำหนดชนิดข้อมูลสำหรับแต่ละไฟล์
5. **ประมวลผล**: คลิก Upload Files

### CLI Mode (สำหรับงานอัตโนมัติ)
```bash
# ประมวลผลไฟล์ในโฟลเดอร์อัตโนมัติ
python auto_process_cli.py "C:\data\folder"

# ดูข้อมูลรายละเอียด
python auto_process_cli.py --verbose "C:\data\folder"
```

---

## 📋 ตัวอย่างการใช้งาน

### ตัวอย่างที่ 1: ไฟล์ Excel เดียว (GUI)
```
1. วางไฟล์ sales_data.xlsx ในโฟลเดอร์ C:\data\
2. รัน: python pipeline_gui_app.py
3. เลือกโฟลเดอร์ C:\data\
4. ตั้งค่าประเภทไฟล์: sales_data (จากตัวอย่างไฟล์จริง)
5. กำหนดชนิดข้อมูลแต่ละคอลัมน์
6. กดค้นหาข้อมูล
7. เลือกไฟล์ที่ต้องการอัปโหลด
8. กดอัปโหลด
```

### ตัวอย่างที่ 2: หลายไฟล์ประจำวัน (CLI)
```
1. วางไฟล์ inventory_*.csv ในโฟลเดอร์ที่ข้อมูลจะเข้ามาทุกวัน
2. รัน CLI: python auto_process_cli.py "C:\daily\data"
3. ระบบจะ:
   - ทำความสะอาดข้อมูลอัตโนมัติ
   - บันทึกเวลาอัปโหลดท้ายตาราง  
   - ล้างข้อมูลเก่าและใส่ข้อมูลใหม่
   - ย้ายไฟล์ที่ประมวลผลแล้ว
```

### ตัวอย่างที่ 3: การประมวลผลประจำ
```bash
# สร้าง batch file สำหรับรันประจำ
echo python auto_process_cli.py "C:\daily\reports" > daily_process.bat
# รันทุกวันผ่าน Task Scheduler
```

---

## 🔧 การตั้งค่าขั้นสูง

### การตั้งค่าประเภทข้อมูล
ตั้งค่าประเภทข้อมูลสำหรับแต่ละคอลัมน์:

#### ใน GUI:
- Settings Tab → Column Settings
- เลือกประเภทไฟล์ → ตั้งค่าแต่ละคอลัมน์

#### แก้ไขไฟล์ `config/dtype_settings.json`:
```json
{
    "sales_data": {
        "Date": "DATE",
        "Product": "NVARCHAR(255)",
        "Amount": "DECIMAL(18,2)",
        "Customer": "NVARCHAR(500)"
    }
}
```

### การตั้งค่า Column Mapping
แก้ไขไฟล์ `config/column_settings.json`:
```json
{
    "sales_data": {
        "Date": "sale_date",
        "Product": "product_name", 
        "Amount": "amount",
        "Customer": "customer_name"
    }
}
```

---

## ⚠️ Troubleshooting เร็ว

### ❌ ไม่สามารถเชื่อมต่อฐานข้อมูล
```bash
# ตรวจสอบ environment variables
python auto_process_cli.py --verbose

# ตรวจสอบ SQL Server service
services.msc → SQL Server

# ทดสอบการเชื่อมต่อ
sqlcmd -S localhost\SQLEXPRESS -E
```

### ❌ ไม่พบไฟล์ .env
```bash
# สร้างใหม่
python install_requirements.py

# หรือสร้างเอง
echo DB_SERVER=localhost\SQLEXPRESS > .env
echo DB_NAME=YourDatabase >> .env
```

### ❌ ไม่สามารถอ่านไฟล์ Excel
1. ปิดไฟล์ Excel ถ้าเปิดอยู่
2. ตรวจสอบสิทธิ์การเข้าถึงไฟล์
3. ตรวจสอบนามสกุลไฟล์ (.xlsx, .xls, .csv)

### ❌ CLI ไม่ประมวลผลไฟล์
1. ตั้งค่าประเภทไฟล์ใน GUI ก่อน
2. ตรวจสอบว่าไฟล์อยู่ในโฟลเดอร์ที่ระบุ
3. รัน `--verbose` เพื่อดูรายละเอียด

---

## 📚 เอกสารเพิ่มเติม

- **[README.md](README.md)**: เอกสารฉบับเต็ม
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: สถาปัตยกรรมระบบ  
- **[CHANGELOG.md](CHANGELOG.md)**: ประวัติการอัปเดต
- **[services/README.md](services/README.md)**: เอกสาร API

---

## 🚀 เคล็ดลับเพื่อประสิทธิภาพ

### สำหรับไฟล์ขนาดใหญ่:
- ใช้ CLI แทน GUI
- แบ่งไฟล์เป็นชิ้นเล็กๆ ถ้าเป็นไปได้
- ปิดโปรแกรมอื่นๆ ที่ไม่จำเป็น

### สำหรับการประมวลผลจำนวนมาก:
```bash
# ใช้ batch processing
for /d %%i in (C:\data\*) do python auto_process_cli.py "%%i"
```

### สำหรับการใช้งานประจำ:
- ตั้ง Task Scheduler ใน Windows
- สร้าง batch file สำหรับการทำงานอัตโนมัติ
- ใช้ logging เพื่อติดตามผลการทำงาน

---

## 📞 การขอความช่วยเหลือ

- **GitHub Issues**: สำหรับรายงานปัญหาและขอฟีเจอร์ใหม่
- **เอกสาร**: อ่าน README.md และ ARCHITECTURE.md
- **Code Examples**: ดูตัวอย่างใน services/ และ ui/

**Ready to go! 🎉**