"""
Gerenciador de operações S3 para a pipeline de backup.
Fornece funcionalidades para upload de arquivos com tratamento de erros robusto.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, cast

import boto3
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    NoCredentialsError,
    PartialCredentialsError,
)

from .config import AWSConfig, S3Config
from .logger import LoggerManager


class S3UploadError(Exception):
    """Exceção customizada para erros de upload S3."""

    pass


class S3Manager:
    """Gerenciador de operações S3."""

    def __init__(
        self, aws_config: AWSConfig, s3_config: S3Config, logger_manager: LoggerManager
    ):
        """
        Inicializa o gerenciador S3.

        Args:
            aws_config: Configuração AWS
            s3_config: Configuração S3
            logger_manager: Gerenciador de logging
        """
        self.aws_config = aws_config
        self.s3_config = s3_config
        self.logger_manager = logger_manager
        self.logger = logger_manager.get_logger()
        self._s3_client: Optional[boto3.client] = None

    @property
    def s3_client(self) -> boto3.client:
        """
        Obtém o cliente S3 configurado.

        Returns:
            boto3.client: Cliente S3 configurado

        Raises:
            S3UploadError: Se não conseguir criar o cliente S3
        """
        if self._s3_client is None:
            self._s3_client = self._create_s3_client()
        return self._s3_client

    def _create_s3_client(self) -> boto3.client:
        """
        Cria e configura o cliente S3.

        Returns:
            boto3.client: Cliente S3 configurado

        Raises:
            S3UploadError: Se não conseguir criar o cliente
        """
        try:
            client = boto3.client(
                "s3",
                aws_access_key_id=self.aws_config.access_key_id,
                aws_secret_access_key=self.aws_config.secret_access_key,
                region_name=self.aws_config.region,
            )

            # Testa a conexão listando buckets
            client.list_buckets()
            self.logger.info("Cliente S3 criado e testado com sucesso")
            return client

        except NoCredentialsError:
            raise S3UploadError("Credenciais AWS não foram encontradas")
        except PartialCredentialsError:
            raise S3UploadError("Credenciais AWS incompletas")
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "InvalidAccessKeyId":
                raise S3UploadError("AWS Access Key ID inválido")
            elif error_code == "SignatureDoesNotMatch":
                raise S3UploadError("AWS Secret Access Key inválido")
            else:
                raise S3UploadError(f"Erro ao criar cliente S3: {e}")
        except Exception as e:
            raise S3UploadError(f"Erro inesperado ao criar cliente S3: {e}")

    def verify_bucket_access(self) -> bool:
        """
        Verifica se o bucket existe e é acessível.

        Returns:
            bool: True se o bucket é acessível

        Raises:
            S3UploadError: Se o bucket não é acessível
        """
        try:
            self.s3_client.head_bucket(Bucket=self.s3_config.bucket_name)
            self.logger.info(
                f"Acesso ao bucket verificado: {self.s3_config.bucket_name}"
            )
            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                raise S3UploadError(
                    f"Bucket não encontrado: {self.s3_config.bucket_name}"
                )
            elif error_code == "403":
                raise S3UploadError(
                    f"Acesso negado ao bucket: {self.s3_config.bucket_name}"
                )
            else:
                raise S3UploadError(f"Erro ao verificar bucket: {e}")
        except Exception as e:
            raise S3UploadError(f"Erro inesperado ao verificar bucket: {e}")

    def upload_file(
        self, local_file_path: str, s3_key: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Faz upload de um arquivo para S3.

        Args:
            local_file_path: Caminho local do arquivo
            s3_key: Chave S3 personalizada (opcional)

        Returns:
            Tuple[bool, str]: (sucesso, chave_s3_ou_erro)
        """
        local_path = Path(local_file_path)

        # Validações iniciais
        if not local_path.exists():
            error_msg = f"Arquivo não encontrado: {local_file_path}"
            self.logger.error(error_msg)
            return False, error_msg

        if not local_path.is_file():
            error_msg = f"Caminho não é um arquivo: {local_file_path}"
            self.logger.error(error_msg)
            return False, error_msg

        # Define a chave S3
        if s3_key is None:
            s3_key = self._generate_s3_key(local_path)

        self.logger_manager.log_operation_start(
            "upload",
            f"Arquivo: {local_file_path} -> s3://{self.s3_config.bucket_name}/{s3_key}",
        )

        try:
            # Obtém informações do arquivo
            file_size = local_path.stat().st_size
            self.logger.debug(f"Tamanho do arquivo: {file_size} bytes")

            # Faz o upload
            self.s3_client.upload_file(
                Filename=str(local_path), Bucket=self.s3_config.bucket_name, Key=s3_key
            )

            # Verifica se o upload foi bem-sucedido
            if self._verify_upload(s3_key, file_size):
                self.logger_manager.log_file_operation("upload", str(local_path), True)
                return True, s3_key
            else:
                error_msg = "Upload aparentemente bem-sucedido mas verificação falhou"
                self.logger_manager.log_file_operation(
                    "upload", str(local_path), False, Exception(error_msg)
                )
                return False, error_msg

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = f"Erro do cliente S3 ({error_code}): {e}"
            self.logger_manager.log_file_operation("upload", str(local_path), False, e)
            return False, error_msg

        except BotoCoreError as e:
            error_msg = f"Erro do BotoCore: {e}"
            self.logger_manager.log_file_operation("upload", str(local_path), False, e)
            return False, error_msg

        except Exception as e:
            error_msg = f"Erro inesperado no upload: {e}"
            self.logger_manager.log_file_operation("upload", str(local_path), False, e)
            return False, error_msg

    def _generate_s3_key(self, local_path: Path) -> str:
        """
        Gera a chave S3 para o arquivo.

        Args:
            local_path: Caminho local do arquivo

        Returns:
            str: Chave S3 gerada
        """
        # Remove caracteres especiais e espaços do nome do arquivo
        filename = local_path.name.replace(" ", "_")

        # Combina prefixo com nome do arquivo
        if self.s3_config.prefix:
            # Remove barras extras e garante que termina com /
            prefix = self.s3_config.prefix.strip("/")
            if prefix:
                return f"{prefix}/{filename}"

        return filename

    def _verify_upload(self, s3_key: str, expected_size: int) -> bool:
        """
        Verifica se o upload foi bem-sucedido.

        Args:
            s3_key: Chave do objeto S3
            expected_size: Tamanho esperado do arquivo

        Returns:
            bool: True se o arquivo existe e tem o tamanho correto
        """
        try:
            response = self.s3_client.head_object(
                Bucket=self.s3_config.bucket_name, Key=s3_key
            )

            actual_size = response["ContentLength"]
            if actual_size == expected_size:
                self.logger.debug(f"Upload verificado: {s3_key} ({actual_size} bytes)")
                return True
            else:
                self.logger.error(
                    f"Tamanho do arquivo no S3 não confere. "
                    f"Esperado: {expected_size}, Atual: {actual_size}"
                )
                return False

        except ClientError as e:
            self.logger.error(f"Erro ao verificar upload: {e}")
            return False

    def list_bucket_objects(self, prefix: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lista objetos no bucket S3.

        Args:
            prefix: Prefixo para filtrar objetos

        Returns:
            list: Lista de objetos no bucket
        """
        try:
            if prefix is None:
                prefix = self.s3_config.prefix

            response = self.s3_client.list_objects_v2(
                Bucket=self.s3_config.bucket_name, Prefix=prefix
            )

            contents = response.get("Contents", [])
            return cast(List[Dict[str, Any]], contents)

        except ClientError as e:
            self.logger.error(f"Erro ao listar objetos do bucket: {e}")
            return []

    def get_upload_url(self, s3_key: str) -> str:
        """
        Gera URL pública para o objeto S3.

        Args:
            s3_key: Chave do objeto S3

        Returns:
            str: URL do objeto
        """
        return f"https://{self.s3_config.bucket_name}.s3.{self.aws_config.region}.amazonaws.com/{s3_key}"
