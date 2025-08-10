"""
File Service สำหรับ PIPELINE_SQLSERVER (รุ่นใหม่ที่จัดระเบียบแล้ว)

เป็น orchestrator ที่รวม services ต่างๆ เข้าด้วยกัน:
- FileReaderService: อ่านและตรวจจับไฟล์
- DataProcessorService: ประมวลผลและตรวจสอบข้อมูล
- FileManagementService: จัดการไฟล์

ตัวอย่างการใช้งาน:
    # สำหรับ GUI
    file_service = FileService(log_callback=gui_log_function)
    
    # สำหรับ CLI
    file_service = FileService(log_callback=logging.info)
    
    # การใช้งานปกติ (interface เดิม)
    success, df = file_service.read_excel_file("data.xlsx", "sales_data")
    
    # การใช้งานแยกส่วน
    file_info = file_service.get_file_info("data.xlsx")
    validation = file_service.validate_file_before_processing("data.xlsx", "sales_data")
"""

from typing import Optional, Tuple, Any, Dict
import logging
import pandas as pd

from .file_reader_service import FileReaderService
from .data_processor_service import DataProcessorService  
from .file_management_service import FileManagementService
from performance_optimizations import PerformanceOptimizer
from config.settings import settings_manager


class FileService:
    """
    บริการไฟล์หลัก (orchestrator)
    
    รับผิดชอบ:
    - การประสานงานระหว่าง services ต่างๆ
    - การอ่านและประมวลผลไฟล์แบบครบวงจร
    - การให้ interface เดียวกันกับระบบเดิม
    """
    
    def __init__(self, search_path: Optional[str] = None, log_callback: Optional[callable] = None) -> None:
        """
        เริ่มต้น FileService
        
        Args:
            search_path (Optional[str]): ที่อยู่โฟลเดอร์สำหรับค้นหาไฟล์
            log_callback (Optional[callable]): ฟังก์ชันสำหรับแสดง log
        """
        self.log_callback = log_callback if log_callback else logging.info
        
        # สร้าง services
        self.file_reader = FileReaderService(search_path, self.log_callback)
        self.data_processor = DataProcessorService(self.log_callback)
        self.file_manager = FileManagementService(search_path)
        
        # อัปเดตข้อมูลจาก SettingsManager
        self.file_reader.column_settings = settings_manager.column_settings
        self.file_reader.dtype_settings = settings_manager.dtype_settings
        self.file_reader._settings_loaded = True
        
        self.data_processor.column_settings = settings_manager.column_settings  
        self.data_processor.dtype_settings = settings_manager.dtype_settings
        self.data_processor._settings_loaded = True
        
        # สร้าง performance optimizer
        self.performance_optimizer = PerformanceOptimizer(self.log_callback)
        
        # เก็บ reference สำหรับ backward compatibility
        self.search_path = self.file_reader.search_path
        self.column_settings = settings_manager.column_settings

    # ========================
    # Main Interface Methods
    # ========================

    def read_excel_file(self, file_path, logic_type):
        """
        อ่านไฟล์ Excel หรือ CSV ตามประเภทที่กำหนด โดยไม่ใช้ระบบแก้ไขอัตโนมัติ
        
        Args:
            file_path: ที่อยู่ไฟล์
            logic_type: ประเภทไฟล์
            ไม่มีการใช้งานระบบแก้ไขอัตโนมัติ
        """
        try:
            # รีเซ็ต log flags สำหรับไฟล์ใหม่
            self.data_processor._reset_log_flags()
            
            # อ่านไฟล์ด้วย Performance Optimizer
            if file_path.lower().endswith('.csv'):
                file_type = 'csv'
            elif file_path.lower().endswith('.xls'):
                file_type = 'excel_xls'
            else:
                file_type = 'excel'
            
            success, df = self.performance_optimizer.read_large_file_chunked(file_path, file_type)
            if not success:
                return False, "ไม่สามารถอ่านไฟล์ได้"
            
            # Apply column mapping (พิจารณาทิศทาง mapping ให้ตรงกับ header ของไฟล์)
            col_map = self.file_reader.build_rename_mapping_for_dataframe(df.columns, logic_type)
            if col_map:
                self.log_callback(f"🔄 ปรับชื่อคอลัมน์ตาม mapping ({len(col_map)} คอลัมน์)")
                df.rename(columns=col_map, inplace=True)
            
            # ปรับปรุง memory usage
            df = self.performance_optimizer.optimize_memory_usage(df)
            
            # หมายเหตุ: การตรวจสอบข้อมูลจะทำใน staging table ด้วย SQL แทน pandas
            self.log_callback(f"🔄 นำเข้าเป็น NVARCHAR(MAX) ทั้งหมด แล้วตรวจสอบและแปลงด้วย SQL")
            
            # ทำความสะอาด memory
            self.performance_optimizer.cleanup_memory()
            
            self.log_callback(f"\n🎉 ประมวลผลไฟล์เสร็จสิ้น")
            return True, df
            
        except Exception as e:
            error_msg = f"❌ เกิดข้อผิดพลาดขณะอ่านไฟล์: {e}"
            self.log_callback(error_msg)
            return False, error_msg
    
    # ========================
    # Delegation Methods
    # ========================
    
    def set_search_path(self, path):
        """ตั้งค่า path สำหรับค้นหาไฟล์ Excel"""
        self.search_path = path
        self.file_reader.set_search_path(path)

    def find_data_files(self):
        """ค้นหาไฟล์ Excel และ CSV ใน path ที่กำหนด"""
        return self.file_reader.find_data_files()

    def detect_file_type(self, file_path):
        """ตรวจสอบประเภทของไฟล์"""
        return self.file_reader.detect_file_type(file_path)

    def get_column_name_mapping(self, file_type):
        """รับ mapping ชื่อคอลัมน์ตามประเภทไฟล์"""
        return self.file_reader.get_column_name_mapping(file_type)

    def get_required_dtypes(self, file_type):
        """รับ dtype ของคอลัมน์ตามประเภทไฟล์"""
        return self.data_processor.get_required_dtypes(file_type)

    def validate_columns(self, df, logic_type):
        """ตรวจสอบคอลัมน์ที่จำเป็น"""
        return self.data_processor.validate_columns(df, logic_type)

    def comprehensive_data_validation(self, df, logic_type):
        """ตรวจสอบข้อมูลอย่างละเอียดก่อนประมวลผล"""
        return self.data_processor.comprehensive_data_validation(df, logic_type)

    def check_invalid_numeric(self, df, logic_type):
        """ตรวจสอบค่าที่ไม่ใช่ตัวเลขในคอลัมน์ที่เป็นตัวเลข"""
        return self.data_processor.check_invalid_numeric(df, logic_type)

    def generate_pre_processing_report(self, df, logic_type):
        """สร้างรายงานสรุปก่อนประมวลผลข้อมูล (deprecated - ใช้ SQL validation แทน)"""
        return self.data_processor.generate_pre_processing_report(df, logic_type)

    def apply_dtypes(self, df, file_type):
        """แปลงประเภทข้อมูลตามการตั้งค่า"""
        return self.data_processor.apply_dtypes(df, file_type)

    def move_uploaded_files(self, file_paths, logic_types=None):
        """ย้ายไฟล์ที่อัปโหลดแล้วไปยังโฟลเดอร์ Uploaded_Files"""
        return self.file_manager.move_uploaded_files(file_paths, logic_types, self.search_path)

    # ========================
    # Legacy Methods (เก็บไว้เพื่อ backward compatibility)
    # ========================
    
    def get_required_columns(self, file_type):
        """(Deprecated) ใช้ get_required_dtypes แทน"""
        return self.data_processor.get_required_dtypes(file_type)

    def standardize_column_name(self, col_name):
        """แปลงชื่อคอลัมน์ให้เป็นรูปแบบมาตรฐาน"""
        return self.file_reader.standardize_column_name(col_name)

    def normalize_col(self, col):
        """ปรับปรุงการ normalize column"""
        return self.file_reader.normalize_col(col)

    def load_settings(self):
        """โหลดการตั้งค่าใหม่จาก SettingsManager"""
        # โหลดการตั้งค่าใหม่จาก SettingsManager
        settings_manager.load_all_settings()
        
        # อัปเดตข้อมูลใน file_reader และ data_processor
        self.file_reader.column_settings = settings_manager.column_settings
        self.file_reader.dtype_settings = settings_manager.dtype_settings
        self.file_reader._settings_loaded = True
        
        self.data_processor.column_settings = settings_manager.column_settings  
        self.data_processor.dtype_settings = settings_manager.dtype_settings
        self.data_processor._settings_loaded = True
        
        # อัปเดต reference ใน FileService
        self.column_settings = settings_manager.column_settings

    def _process_dataframe_in_chunks(self, df, process_func, logic_type, chunk_size=5000):
        """ประมวลผล DataFrame แบบ chunk (legacy wrapper)"""
        return self.data_processor.process_dataframe_in_chunks(df, process_func, logic_type, chunk_size)

    def _reset_log_flags(self):
        """รีเซ็ต log flags (legacy wrapper)"""
        self.data_processor._reset_log_flags()

    def clean_numeric_columns(self, df, file_type):
        """ทำความสะอาดข้อมูลคอลัมน์ตัวเลข"""
        return self.data_processor.clean_numeric_columns(df, file_type)

    def truncate_long_strings(self, df, logic_type):
        """ตัดข้อมูล string ที่ยาวเกินกำหนด"""
        return self.data_processor.truncate_long_strings(df, logic_type)

    # ลบฟังก์ชันที่เกี่ยวข้องกับ auto-fix ออก (decommissioned)

    def upload_data_with_auto_schema_update(self, df, logic_type, processing_report=None, schema_name='bronze'):
        """
        อัปโหลดข้อมูลพร้อมการอัพเดท schema อัตโนมัติ
        
        Args:
            df: DataFrame ที่จะอัปโหลด
            logic_type: ประเภทไฟล์
            processing_report: (ไม่ใช้งาน)
            schema_name: ชื่อ schema ในฐานข้อมูล
            
        Returns:
            Tuple[bool, str]: (สำเร็จหรือไม่, ข้อความผลลัพธ์)
        """
        try:
            from services.database_service import DatabaseService
            
            # สร้าง database service
            db_service = DatabaseService()
            
            # ตรวจสอบการเชื่อมต่อ
            connection_ok, conn_msg = db_service.check_connection()
            if not connection_ok:
                return False, f"ไม่สามารถเชื่อมต่อฐานข้อมูลได้: {conn_msg}"
            
            # ได้ required columns ตามการตั้งค่าล่าสุด
            required_cols = self.get_required_dtypes(logic_type)
            if not required_cols:
                return False, "ไม่พบการตั้งค่าประเภทข้อมูล"
            
            # ไม่รองรับ auto-fix อีกต่อไป จึงไม่ใช้ force_recreate จาก processing_report
            force_recreate = False
            
            # อัปโหลดข้อมูล
            success, upload_msg = db_service.upload_data(
                df=df,
                logic_type=logic_type,
                required_cols=required_cols,
                schema_name=schema_name,
                log_func=self.log_callback,
                force_recreate=force_recreate
            )
            
            return success, upload_msg
            
        except Exception as e:
            error_msg = f"❌ เกิดข้อผิดพลาดในการอัปโหลด: {e}"
            self.log_callback(error_msg)
            return False, error_msg

    # ลบเมธอด read_and_upload_with_auto_fix (decommissioned)

    def print_detailed_validation_report(self, df, logic_type):
        """แสดงรายงานการตรวจสอบข้อมูลแบบละเอียด (legacy method)"""
        # สร้างรายงานแบบละเอียด
        self.log_callback("\n" + "="*80)
        self.log_callback("🔍 รายงานการตรวจสอบข้อมูลแบบละเอียด")
        self.log_callback("="*80)
        
        # ข้อมูลพื้นฐาน
        self.log_callback(f"📊 ข้อมูลพื้นฐาน:")
        self.log_callback(f"   • จำนวนแถวทั้งหมด: {len(df):,}")
        self.log_callback(f"   • จำนวนคอลัมน์ทั้งหมด: {len(df.columns)}")
        self.log_callback(f"   • ประเภทไฟล์: {logic_type}")
        
        # ใช้ comprehensive validation
        validation_result = self.comprehensive_data_validation(df, logic_type)
        
        if validation_result['summary']:
            self.log_callback("\n📋 สรุปการตรวจสอบ:")
            for msg in validation_result['summary']:
                self.log_callback(f"   • {msg}")
        
        self.log_callback("="*80)
