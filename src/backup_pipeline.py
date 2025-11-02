"""
Pipeline principal de backup para S3.
Orquestra todo o processo de backup, upload e limpeza de arquivos.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .config import AppConfig, ConfigManager
from .file_manager import FileManager
from .logger import LoggerManager
from .s3_manager import S3Manager


class BackupPipelineError(Exception):
    """Exceção customizada para erros da pipeline de backup."""

    pass


class BackupResults:
    """Classe para armazenar os resultados da execução da pipeline."""

    def __init__(self) -> None:
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.total_files = 0
        self.successful_uploads = 0
        self.failed_uploads = 0
        self.deleted_files = 0
        self.failed_deletions = 0
        self.upload_errors: List[Tuple[str, str]] = []  # (file_path, error_message)
        self.deletion_errors: List[Tuple[str, str]] = []  # (file_path, error_message)
        self.uploaded_files: List[Tuple[str, str]] = []  # (local_path, s3_key)

    def finish(self) -> None:
        """Marca o fim da execução."""
        self.end_time = datetime.now()

    @property
    def duration(self) -> float:
        """Duração da execução em segundos."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (datetime.now() - self.start_time).total_seconds()

    @property
    def success_rate(self) -> float:
        """Taxa de sucesso dos uploads (0-100)."""
        if self.total_files == 0:
            return 0.0
        return (self.successful_uploads / self.total_files) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Converte os resultados para dicionário."""
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration,
            "total_files": self.total_files,
            "successful_uploads": self.successful_uploads,
            "failed_uploads": self.failed_uploads,
            "deleted_files": self.deleted_files,
            "failed_deletions": self.failed_deletions,
            "success_rate_percent": self.success_rate,
            "upload_errors": self.upload_errors,
            "deletion_errors": self.deletion_errors,
            "uploaded_files": self.uploaded_files,
        }


class BackupPipeline:
    """Pipeline principal de backup para S3."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Inicializa a pipeline de backup.

        Args:
            config_path: Caminho para o arquivo de configuração
        """
        self.config_path = config_path
        self.config: Optional[AppConfig] = None
        self.logger_manager: Optional[LoggerManager] = None
        self.file_manager: Optional[FileManager] = None
        self.s3_manager: Optional[S3Manager] = None
        self._initialized = False

    def initialize(self) -> None:
        """
        Inicializa todos os componentes da pipeline.

        Raises:
            BackupPipelineError: Se houver erro na inicialização
        """
        try:
            # Carrega configuração
            config_manager = ConfigManager(self.config_path)
            self.config = config_manager.load_config()

            # Inicializa logger
            self.logger_manager = LoggerManager(self.config.logging)
            logger = self.logger_manager.get_logger()

            logger.info("Inicializando pipeline de backup S3")
            logger.info(f"Configuração carregada de: {self.config_path}")

            # Inicializa gerenciadores
            self.file_manager = FileManager(self.config.backup, self.logger_manager)
            self.s3_manager = S3Manager(
                self.config.aws, self.config.s3, self.logger_manager
            )

            # Verifica acesso ao bucket S3
            self.s3_manager.verify_bucket_access()

            self._initialized = True
            logger.info("Pipeline inicializada com sucesso")

        except Exception as e:
            error_msg = f"Erro na inicialização da pipeline: {e}"
            if self.logger_manager:
                self.logger_manager.get_logger().error(error_msg)
            raise BackupPipelineError(error_msg)

    def run_backup(self, dry_run: bool = False) -> BackupResults:
        """
        Executa o processo completo de backup.

        Args:
            dry_run: Se True, apenas simula a execução sem fazer upload/deleção

        Returns:
            BackupResults: Resultados da execução

        Raises:
            BackupPipelineError: Se a pipeline não foi inicializada
        """
        if not self._initialized:
            raise BackupPipelineError(
                "Pipeline não foi inicializada. Chame initialize() primeiro."
            )

        # Assertions para MyPy - garantem que os atributos não são None após initialize()
        assert self.config is not None
        assert self.logger_manager is not None
        assert self.file_manager is not None
        assert self.s3_manager is not None

        results = BackupResults()
        logger = self.logger_manager.get_logger()

        try:
            logger.info("=" * 60)
            logger.info("INICIANDO PIPELINE DE BACKUP S3")
            logger.info("=" * 60)

            if dry_run:
                logger.info("MODO DRY-RUN: Nenhuma operação será executada")

            # 1. Lista arquivos para backup
            logger.info("Fase 1: Listando arquivos para backup...")
            files_to_backup = self.file_manager.list_files_to_backup()
            results.total_files = len(files_to_backup)

            if results.total_files == 0:
                logger.warning("Nenhum arquivo encontrado para backup")
                results.finish()
                return results

            logger.info(f"Encontrados {results.total_files} arquivos para backup")

            # 2. Cria manifest de backup
            if not dry_run:
                manifest_path = self.file_manager.create_backup_manifest(
                    files_to_backup
                )
                logger.info(f"Manifest criado: {manifest_path}")

            # 3. Executa upload dos arquivos
            logger.info("Fase 2: Executando uploads para S3...")
            self._upload_files(files_to_backup, results, dry_run)

            # 4. Deleta arquivos locais se configurado
            if self.config.backup.delete_after_upload:
                logger.info("Fase 3: Deletando arquivos locais...")
                self._delete_local_files(results, dry_run)

                # 5. Limpa diretórios vazios
                if not dry_run:
                    removed_dirs = self.file_manager.cleanup_empty_directories()
                    if removed_dirs > 0:
                        logger.info(f"Removidos {removed_dirs} diretórios vazios")

            # Finaliza resultados
            results.finish()

            # Log do resumo final
            self._log_final_summary(results)

            return results

        except Exception as e:
            results.finish()
            self.logger_manager.log_operation_error("backup_pipeline", e)
            raise BackupPipelineError(f"Erro na execução da pipeline: {e}")

    def _upload_files(
        self, files: List[str], results: BackupResults, dry_run: bool
    ) -> None:
        """
        Executa upload dos arquivos para S3.

        Args:
            files: Lista de arquivos para upload
            results: Objeto de resultados
            dry_run: Se True, apenas simula
        """
        assert self.logger_manager is not None
        assert self.s3_manager is not None

        logger = self.logger_manager.get_logger()

        for i, file_path in enumerate(files, 1):
            logger.info(f"Processando arquivo {i}/{len(files)}: {file_path}")

            if dry_run:
                logger.info(f"[DRY-RUN] Simulando upload: {file_path}")
                results.successful_uploads += 1
                continue

            try:
                success, result = self.s3_manager.upload_file(file_path)

                if success:
                    results.successful_uploads += 1
                    results.uploaded_files.append(
                        (file_path, result)
                    )  # result é a s3_key
                    logger.info(f"Upload bem-sucedido: {file_path} -> {result}")
                else:
                    results.failed_uploads += 1
                    results.upload_errors.append(
                        (file_path, result)
                    )  # result é a mensagem de erro
                    logger.error(f"Falha no upload: {file_path} - {result}")

            except Exception as e:
                results.failed_uploads += 1
                error_msg = f"Erro inesperado no upload: {e}"
                results.upload_errors.append((file_path, error_msg))
                logger.error(f"Erro no upload de {file_path}: {e}")

    def _delete_local_files(self, results: BackupResults, dry_run: bool) -> None:
        """
        Deleta arquivos locais que foram uploadados com sucesso.

        Args:
            results: Objeto de resultados
            dry_run: Se True, apenas simula
        """
        assert self.logger_manager is not None
        assert self.file_manager is not None

        logger = self.logger_manager.get_logger()

        # Só deleta arquivos que foram uploadados com sucesso
        for file_path, s3_key in results.uploaded_files:
            if dry_run:
                logger.info(f"[DRY-RUN] Simulando deleção: {file_path}")
                results.deleted_files += 1
                continue

            try:
                success, message = self.file_manager.delete_file_safely(file_path)

                if success:
                    results.deleted_files += 1
                    logger.info(f"Arquivo deletado: {file_path}")
                else:
                    results.failed_deletions += 1
                    results.deletion_errors.append((file_path, message))
                    logger.warning(f"Falha na deleção: {file_path} - {message}")

            except Exception as e:
                results.failed_deletions += 1
                error_msg = f"Erro inesperado na deleção: {e}"
                results.deletion_errors.append((file_path, error_msg))
                logger.error(f"Erro na deleção de {file_path}: {e}")

    def _log_final_summary(self, results: BackupResults) -> None:
        """
        Registra o resumo final da execução.

        Args:
            results: Resultados da execução
        """
        assert self.logger_manager is not None
        assert self.config is not None

        logger = self.logger_manager.get_logger()

        logger.info("=" * 60)
        logger.info("RESUMO DA EXECUÇÃO")
        logger.info("=" * 60)
        logger.info(f"Duração: {results.duration:.2f} segundos")
        logger.info(f"Total de arquivos: {results.total_files}")
        logger.info(f"Uploads bem-sucedidos: {results.successful_uploads}")
        logger.info(f"Uploads falharam: {results.failed_uploads}")
        logger.info(f"Taxa de sucesso: {results.success_rate:.1f}%")

        if self.config.backup.delete_after_upload:
            logger.info(f"Arquivos deletados: {results.deleted_files}")
            logger.info(f"Falhas na deleção: {results.failed_deletions}")

        if results.upload_errors:
            logger.warning("Erros de upload:")
            for file_path, error in results.upload_errors:
                logger.warning(f"  {file_path}: {error}")

        if results.deletion_errors:
            logger.warning("Erros de deleção:")
            for file_path, error in results.deletion_errors:
                logger.warning(f"  {file_path}: {error}")

        # Log estruturado para análise
        self.logger_manager.log_pipeline_summary(
            results.total_files,
            results.successful_uploads,
            results.failed_uploads,
            results.deleted_files,
        )

        logger.info("=" * 60)

    def get_status(self) -> Dict[str, Any]:
        """
        Obtém o status atual da pipeline.

        Returns:
            Dict: Status da pipeline
        """
        return {
            "initialized": self._initialized,
            "config_path": self.config_path,
            "source_directory": (
                self.config.backup.source_directory if self.config else None
            ),
            "bucket_name": self.config.s3.bucket_name if self.config else None,
            "delete_after_upload": (
                self.config.backup.delete_after_upload if self.config else None
            ),
        }
