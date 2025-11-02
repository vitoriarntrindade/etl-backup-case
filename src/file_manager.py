"""
Gerenciador de operações de arquivo para a pipeline de backup.
Responsável por listar arquivos locais e deletar após upload bem-sucedido.
"""

import fnmatch
import os
from pathlib import Path
from typing import List, Optional, Tuple

from .config import BackupConfig
from .logger import LoggerManager


class FileOperationError(Exception):
    """Exceção customizada para erros de operação de arquivo."""

    pass


class FileManager:
    """Gerenciador de operações de arquivo local."""

    def __init__(self, backup_config: BackupConfig, logger_manager: LoggerManager):
        """
        Inicializa o gerenciador de arquivos.

        Args:
            backup_config: Configuração de backup
            logger_manager: Gerenciador de logging
        """
        self.backup_config = backup_config
        self.logger_manager = logger_manager
        self.logger = logger_manager.get_logger()

    def list_files_to_backup(self) -> List[str]:
        """
        Lista todos os arquivos que devem ser incluídos no backup.

        Returns:
            List[str]: Lista de caminhos absolutos dos arquivos

        Raises:
            FileOperationError: Se houver erro ao listar arquivos
        """
        source_path = Path(self.backup_config.source_directory)

        if not source_path.exists():
            raise FileOperationError(f"Diretório de origem não existe: {source_path}")

        if not source_path.is_dir():
            raise FileOperationError(f"Caminho não é um diretório: {source_path}")

        self.logger_manager.log_operation_start(
            "listar_arquivos", f"Diretório: {source_path}"
        )

        try:
            all_files = []

            # Itera por todos os arquivos no diretório e subdiretórios
            for file_path in source_path.rglob("*"):
                if file_path.is_file():
                    if self._should_include_file(file_path):
                        all_files.append(str(file_path.absolute()))

            self.logger.info(f"Encontrados {len(all_files)} arquivos para backup")

            # Log detalhado dos arquivos encontrados
            for file_str in all_files:
                self.logger.debug(f"Arquivo para backup: {file_str}")

            return sorted(all_files)

        except Exception as e:
            self.logger_manager.log_operation_error("listar_arquivos", e)
            raise FileOperationError(f"Erro ao listar arquivos: {e}")

    def _should_include_file(self, file_path: Path) -> bool:
        """
        Verifica se um arquivo deve ser incluído no backup baseado nas extensões configuradas.

        Args:
            file_path: Caminho do arquivo

        Returns:
            bool: True se o arquivo deve ser incluído
        """
        # Se não há filtros de extensão ou é ['*'], inclui todos os arquivos
        extensions = self.backup_config.file_extensions
        if not extensions or extensions == ["*"]:
            return True

        file_name = file_path.name.lower()

        # Verifica cada padrão de extensão
        for pattern in extensions:
            # Remove * inicial se presente e adiciona se necessário
            pattern = pattern.lower()
            if not pattern.startswith("*"):
                pattern = "*" + pattern

            if fnmatch.fnmatch(file_name, pattern):
                return True

        return False

    def delete_file_safely(self, file_path: str) -> Tuple[bool, str]:
        """
        Deleta um arquivo local de forma segura após validações.

        Args:
            file_path: Caminho do arquivo a ser deletado

        Returns:
            Tuple[bool, str]: (sucesso, mensagem_ou_erro)
        """
        path = Path(file_path)

        # Validações de segurança
        if not path.exists():
            error_msg = f"Arquivo não encontrado para deleção: {file_path}"
            self.logger.warning(error_msg)
            return False, error_msg

        if not path.is_file():
            error_msg = f"Caminho não é um arquivo: {file_path}"
            self.logger.error(error_msg)
            return False, error_msg

        # Verifica se o arquivo está dentro do diretório de origem (segurança)
        source_path = Path(self.backup_config.source_directory).resolve()
        try:
            path.resolve().relative_to(source_path)
        except ValueError:
            error_msg = f"Arquivo fora do diretório de origem: {file_path}"
            self.logger.error(error_msg)
            return False, error_msg

        # Verifica se deve deletar baseado na configuração
        if not self.backup_config.delete_after_upload:
            msg = f"Deleção desabilitada na configuração: {file_path}"
            self.logger.debug(msg)
            return True, msg

        self.logger_manager.log_operation_start(
            "deletar_arquivo", f"Arquivo: {file_path}"
        )

        try:
            # Obtém informações do arquivo antes de deletar
            file_size = path.stat().st_size

            # Deleta o arquivo
            path.unlink()

            # Verifica se foi deletado
            if not path.exists():
                success_msg = f"Arquivo deletado com sucesso ({file_size} bytes)"
                self.logger_manager.log_file_operation("delete", file_path, True)
                return True, success_msg
            else:
                error_msg = "Arquivo ainda existe após tentativa de deleção"
                self.logger_manager.log_file_operation(
                    "delete", file_path, False, Exception(error_msg)
                )
                return False, error_msg

        except PermissionError as e:
            error_msg = f"Permissão negada para deletar arquivo: {e}"
            self.logger_manager.log_file_operation("delete", file_path, False, e)
            return False, error_msg

        except OSError as e:
            error_msg = f"Erro do sistema ao deletar arquivo: {e}"
            self.logger_manager.log_file_operation("delete", file_path, False, e)
            return False, error_msg

        except Exception as e:
            error_msg = f"Erro inesperado ao deletar arquivo: {e}"
            self.logger_manager.log_file_operation("delete", file_path, False, e)
            return False, error_msg

    def get_file_info(self, file_path: str) -> dict:
        """
        Obtém informações detalhadas sobre um arquivo.

        Args:
            file_path: Caminho do arquivo

        Returns:
            dict: Informações do arquivo
        """
        path = Path(file_path)

        if not path.exists():
            return {"error": "Arquivo não encontrado"}

        if not path.is_file():
            return {"error": "Caminho não é um arquivo"}

        try:
            stat = path.stat()
            return {
                "name": path.name,
                "absolute_path": str(path.absolute()),
                "size_bytes": stat.st_size,
                "size_human": self._format_file_size(stat.st_size),
                "modified_time": stat.st_mtime,
                "is_readable": os.access(path, os.R_OK),
                "extension": path.suffix.lower(),
            }
        except Exception as e:
            return {"error": f"Erro ao obter informações: {e}"}

    def _format_file_size(self, size_bytes: int) -> str:
        """
        Formata o tamanho do arquivo em formato legível.

        Args:
            size_bytes: Tamanho em bytes

        Returns:
            str: Tamanho formatado
        """
        size_float = float(size_bytes)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_float < 1024.0:
                return f"{size_float:.1f} {unit}"
            size_float /= 1024.0
        return f"{size_float:.1f} PB"

    def create_backup_manifest(
        self, files: List[str], output_path: Optional[str] = None
    ) -> str:
        """
        Cria um manifest com a lista de arquivos e suas informações.

        Args:
            files: Lista de arquivos
            output_path: Caminho para salvar o manifest (opcional)

        Returns:
            str: Caminho do arquivo manifest criado
        """
        if output_path is None:
            timestamp = self._get_timestamp()
            # Cria manifest em diretório dedicado
            manifests_dir = Path("manifests")
            manifests_dir.mkdir(exist_ok=True)
            output_path = str(manifests_dir / f"backup_manifest_{timestamp}.txt")

        manifest_path = Path(output_path)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(manifest_path, "w", encoding="utf-8") as f:
                f.write(f"# Backup Manifest - {self._get_timestamp()}\n")
                f.write(
                    f"# Diretório de origem: {self.backup_config.source_directory}\n"
                )
                f.write(f"# Total de arquivos: {len(files)}\n\n")

                total_size = 0
                for file_path in files:
                    info = self.get_file_info(file_path)
                    if "error" not in info:
                        size_bytes = info["size_bytes"]
                        size_human = info["size_human"]
                        total_size += size_bytes
                        f.write(f"{file_path} ({size_human})\n")
                    else:
                        f.write(f"{file_path} (ERRO: {info['error']})\n")

                f.write(f"\n# Tamanho total: {self._format_file_size(total_size)}\n")

            self.logger.info(f"Manifest criado: {manifest_path}")
            return str(manifest_path)

        except Exception as e:
            error_msg = f"Erro ao criar manifest: {e}"
            self.logger.error(error_msg)
            raise FileOperationError(error_msg)

    def _get_timestamp(self) -> str:
        """Obtém timestamp formatado para nomes de arquivo."""
        from datetime import datetime

        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def cleanup_empty_directories(self) -> int:
        """
        Remove diretórios vazios após a deleção de arquivos.

        Returns:
            int: Número de diretórios removidos
        """
        if not self.backup_config.delete_after_upload:
            return 0

        source_path = Path(self.backup_config.source_directory)
        removed_count = 0

        try:
            # Itera pelos diretórios de forma reversa (filhos primeiro)
            for dir_path in sorted(source_path.rglob("*"), reverse=True):
                if dir_path.is_dir() and dir_path != source_path:
                    try:
                        # Tenta remover se estiver vazio
                        dir_path.rmdir()
                        self.logger.debug(f"Diretório vazio removido: {dir_path}")
                        removed_count += 1
                    except OSError:
                        # Diretório não está vazio, continua
                        continue

            if removed_count > 0:
                self.logger.info(f"Removidos {removed_count} diretórios vazios")

        except Exception as e:
            self.logger.warning(f"Erro ao limpar diretórios vazios: {e}")

        return removed_count
