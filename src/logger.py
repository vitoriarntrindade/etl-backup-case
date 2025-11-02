"""
Sistema de logging configurável para a pipeline de backup S3.
Fornece logging estruturado com rotação de arquivos e diferentes níveis.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from .config import LoggingConfig


class LoggerManager:
    """Gerenciador de logging da aplicação."""

    def __init__(self, config: LoggingConfig, logger_name: str = "backup_pipeline"):
        """
        Inicializa o gerenciador de logging.

        Args:
            config: Configuração de logging
            logger_name: Nome do logger
        """
        self.config = config
        self.logger_name = logger_name
        self._logger: Optional[logging.Logger] = None

    def get_logger(self) -> logging.Logger:
        """
        Obtém o logger configurado.

        Returns:
            logging.Logger: Logger configurado
        """
        if self._logger is None:
            self._logger = self._setup_logger()
        return self._logger

    def _setup_logger(self) -> logging.Logger:
        """
        Configura o logger com handlers de console e arquivo.

        Returns:
            logging.Logger: Logger configurado
        """
        logger = logging.getLogger(self.logger_name)
        logger.setLevel(getattr(logging, self.config.level))

        # Remove handlers existentes para evitar duplicação
        logger.handlers.clear()

        # Formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, self.config.level))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler com rotação
        log_file_path = Path(self.config.log_file)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            filename=str(log_file_path),
            maxBytes=self.config.max_log_size_mb * 1024 * 1024,  # Convert MB to bytes
            backupCount=self.config.backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(getattr(logging, self.config.level))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Previne propagação para o root logger
        logger.propagate = False

        return logger

    def log_operation_start(self, operation: str, details: str = "") -> None:
        """
        Registra o início de uma operação.

        Args:
            operation: Nome da operação
            details: Detalhes adicionais
        """
        message = f"Iniciando operação: {operation}"
        if details:
            message += f" - {details}"
        self.get_logger().info(message)

    def log_operation_success(self, operation: str, details: str = "") -> None:
        """
        Registra o sucesso de uma operação.

        Args:
            operation: Nome da operação
            details: Detalhes adicionais
        """
        message = f"Operação concluída com sucesso: {operation}"
        if details:
            message += f" - {details}"
        self.get_logger().info(message)

    def log_operation_error(
        self, operation: str, error: Exception, details: str = ""
    ) -> None:
        """
        Registra erro em uma operação.

        Args:
            operation: Nome da operação
            error: Exceção ocorrida
            details: Detalhes adicionais
        """
        message = f"Erro na operação: {operation} - {str(error)}"
        if details:
            message += f" - {details}"
        self.get_logger().error(message, exc_info=True)

    def log_file_operation(
        self,
        operation: str,
        file_path: str,
        success: bool = True,
        error: Optional[Exception] = None,
    ) -> None:
        """
        Registra operação em arquivo específico.

        Args:
            operation: Tipo de operação (upload, delete, etc.)
            file_path: Caminho do arquivo
            success: Se a operação foi bem-sucedida
            error: Exceção se houve erro
        """
        if success:
            self.get_logger().info(f"{operation} bem-sucedido: {file_path}")
        else:
            error_msg = str(error) if error else "Erro desconhecido"
            self.get_logger().error(f"Falha no {operation}: {file_path} - {error_msg}")

    def log_pipeline_summary(
        self,
        total_files: int,
        successful_uploads: int,
        failed_uploads: int,
        deleted_files: int,
    ) -> None:
        """
        Registra resumo da execução da pipeline.

        Args:
            total_files: Total de arquivos processados
            successful_uploads: Uploads bem-sucedidos
            failed_uploads: Uploads falharam
            deleted_files: Arquivos deletados localmente
        """
        summary = (
            f"Resumo da execução - Total: {total_files}, "
            f"Uploads bem-sucedidos: {successful_uploads}, "
            f"Uploads falharam: {failed_uploads}, "
            f"Arquivos deletados: {deleted_files}"
        )
        self.get_logger().info(summary)


def setup_logger(
    config: LoggingConfig, logger_name: str = "backup_pipeline"
) -> logging.Logger:
    """
    Função utilitária para configurar um logger rapidamente.

    Args:
        config: Configuração de logging
        logger_name: Nome do logger

    Returns:
        logging.Logger: Logger configurado
    """
    manager = LoggerManager(config, logger_name)
    return manager.get_logger()
