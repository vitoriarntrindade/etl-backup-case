"""
Pipeline de Backup S3 - Pacote principal.
Fornece funcionalidades para backup automatizado de arquivos para Amazon S3.
"""

from .backup_pipeline import BackupPipeline, BackupResults, BackupPipelineError
from .config import AppConfig, ConfigManager
from .file_manager import FileManager, FileOperationError
from .logger import LoggerManager, setup_logger
from .s3_manager import S3Manager, S3UploadError

__version__ = "1.0.0"
__author__ = "Pipeline de Backup S3"
__description__ = "Pipeline automatizada para backup de arquivos para Amazon S3"

__all__ = [
    "BackupPipeline",
    "BackupResults",
    "BackupPipelineError",
    "AppConfig",
    "ConfigManager",
    "FileManager",
    "FileOperationError",
    "LoggerManager",
    "setup_logger",
    "S3Manager",
    "S3UploadError",
]
