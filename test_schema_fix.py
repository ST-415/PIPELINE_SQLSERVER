#!/usr/bin/env python3
"""
ไฟล์ทดสอบเพื่อทดสอบการแก้ไข schema ของฐานข้อมูล
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.database_service import DatabaseService
from services.file_service import FileService
from sqlalchemy.types import Text, NVARCHAR
import pandas as pd

def test_schema_fix():
    """ทดสอบการแก้ไข schema ของฐานข้อมูล"""
    
    print("🔧 ทดสอบการแก้ไข Database Schema")
    print("=" * 50)
    
    # สร้าง services
    file_service = FileService(log_callback=print)
    db_service = DatabaseService()
    
    # ตรวจสอบการเชื่อมต่อ
    connected, msg = db_service.check_connection()
    if not connected:
        print(f"❌ ไม่สามารถเชื่อมต่อฐานข้อมูล: {msg}")
        return
    
    print("✅ เชื่อมต่อฐานข้อมูลสำเร็จ")
    
    # ดู dtype configuration สำหรับ order_jst
    dtypes = file_service.get_required_dtypes('order_jst')
    target_col = 'หมายเหตุจากผู้ขาย'
    
    if target_col not in dtypes:
        print(f"❌ ไม่พบคอลัมน์ '{target_col}' ใน configuration")
        return
    
    dtype = dtypes[target_col]
    print(f"📋 คอลัมน์ '{target_col}': {type(dtype).__name__}")
    
    if not isinstance(dtype, Text):
        print(f"❌ คอลัมน์ '{target_col}' ไม่ได้ถูกตั้งค่าเป็น Text() (NVARCHAR(MAX))")
        return
    
    print(f"✅ คอลัมน์ '{target_col}' ถูกตั้งค่าเป็น Text() (NVARCHAR(MAX)) แล้ว")
    
    # สร้างข้อมูลทดสอบ
    long_text = "Natdanai Khamun*7/21/2025 3:12:04 PM*???*579615583724930442 LM-01-056*0;LM-03-002*0;LM-03-018*0; Pu" * 20
    
    test_df = pd.DataFrame({
        'หมายเลขคำสั่งซื้อภายใน': ['TEST_107194'],
        'หมายเลขการสั่งซื้อออนไลน์': ['579615768430216923'],
        'จำนวนชิ้น': [1],
        'สถานะคำสั่งซื้อ': ['จัดส่งแล้ว'],
        'บริษัทขนส่ง': ['J&T Express'],
        'เลขพัสดุ': ['761626121712'],
        'สถานะขนส่ง': ['จัดส่งแล้ว'],
        'สถานะการจัดส่งแพลตฟอร์ม': ['เชื่อมต่อแพลตฟอร์มสําเร็จ'],
        'เวลาสั่งซื้อ': ['2025-07-14 12:23:56'],
        'เวลาชำระเงิน': ['2025-07-14 12:23:56'],
        'ร้านค้า​': ['BIG_T Tiktok'],
        'ป้ายแท็ก': ['พิมพ์แล้ว,ลงทะเบียนแล้ว'],
        'หมายเหตุจากผู้ขาย': [long_text],  # ข้อมูลยาวมาก
        'ราคาสินค้าทั้งหมด': [679.0],
        'ประเภทของรายการสั่งซื้อ': ['คำสั่งซื้อปกติ'],
        'น้ำหนัก': [0],
        'ปริมาตร': [0],
        'คลังสินค้าส่งออก': ['EPBIGT'],
        'วันที่จัดส่ง': ['2025-07-14 15:26:14'],
        'วันสิ้นสุดเข้ารับพัสดุ': ['2025-07-15 23:59:59'],
        'กำหนดส่งสินค้า': ['2025-07-14 23:59:59'],
        'เวลาที่เหลือในการจัดส่ง': [None],
        'ผู้จัดจําหน่าย': [None],
        'ตัวแทนจำหน่าย': [None],
        'ส่งออกให้คลังอื่นหรือไม่': [None],
        'วิธีการส่ง': [None],
        'เวลาที่ระบบสร้างขึ้น': ['2025-07-14 12:24:11'],
        'เวลาที่แก้ไขในระบบ': ['2025-07-27 11:28:54'],
        'จํานวนสินค้าตีกลับ': [0],
        'จํานวนเงินที่คืน': [0.0],
        'สินค้าตีกลับจริง': [0],
        'รหัสสินค้า': ['FT-04-066'],
        'ชื่อสินค้า': ['ถังพ่นยาแบตเตอร์รี่ 20L รุ่น KingKong Tomitsu'],
        'รูปแบบสินค้า': ['FT-04-066'],
        'คุณสมบัติสินค้า': ['ค่าเริ่มต้น'],
        'ของแถมหรือไม่': [None],
        'ราคาต่อหน่วย': [679.0],
        'ราคาปกติ': [679.0],
        'จำนวน': [1]
    })
    
    print(f"\n📊 ข้อมูลทดสอบ:")
    print(f"   - ความยาวข้อมูลหมายเหตุ: {len(long_text)} ตัวอักษร")
    print(f"   - จำนวนแถว: {len(test_df)}")
    
    # ลองอัปโหลดข้อมูล (ซึ่งจะสร้าง/อัปเดต schema อัตโนมัติ)
    print(f"\n🚀 ทดสอบการอัปโหลดข้อมูล...")
    
    success, message = db_service.upload_data(
        test_df, 
        'order_jst', 
        dtypes, 
        schema_name='bronze', 
        log_func=print
    )
    
    if success:
        print(f"\n✅ อัปโหลดข้อมูลสำเร็จ!")
        print(f"📋 ข้อความ: {message}")
    else:
        print(f"\n❌ อัปโหลดข้อมูลไม่สำเร็จ:")
        print(f"📋 ข้อผิดพลาด: {message}")
    
    print(f"\n🎯 การทดสอบเสร็จสิ้น")

if __name__ == "__main__":
    try:
        test_schema_fix()
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดขณะทดสอบ: {e}")
        import traceback
        traceback.print_exc()