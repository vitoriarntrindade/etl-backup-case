"""
Módulo de configuração para a pipeline de backup S3.
Gerencia o carregamento e validação das configurações da aplicação.
"""

import os
from pathlib import Path
from typing import List, Optional

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator


class AWSConfig(BaseModel):
    """Configurações de autenticação AWS."""

    access_key_id: str = Field(..., description="AWS Access Key ID")
    secret_access_key: str = Field(..., description="AWS Secret Access Key")
    region: str = Field(default="us-east-1", description="AWS Region")

    @validator("access_key_id", "secret_access_key")
    def validate_credentials(cls, value: str) -> str:
        """Valida se as credenciais não estão vazias."""
        if not value or value.strip() == "":
            raise ValueError("Credenciais AWS não podem estar vazias")
        return value.strip()


class S3Config(BaseModel):
    """Configurações do bucket S3."""

    bucket_name: str = Field(..., description="Nome do bucket S3")
    prefix: str = Field(
        default="", description="Prefixo para organizar arquivos no bucket"
    )

    @validator("bucket_name")
    def validate_bucket_name(cls, value: str) -> str:
        """Valida o nome do bucket S3."""
        if not value or value.strip() == "":
            raise ValueError("Nome do bucket S3 não pode estar vazio")
        return value.strip()


class BackupConfig(BaseModel):
    """Configurações do processo de backup."""

    source_directory: str = Field(..., description="Diretório local para backup")
    file_extensions: List[str] = Field(
        default=["*"], description="Extensões de arquivo para backup"
    )
    delete_after_upload: bool = Field(
        default=False,
        description="Se deve deletar arquivos locais após upload bem-sucedido",
    )

    @validator("source_directory")
    def validate_source_directory(cls, value: str) -> str:
        """Valida se o diretório de origem existe."""
        path = Path(value)
        if not path.exists():
            raise ValueError(f"Diretório de origem não existe: {value}")
        if not path.is_dir():
            raise ValueError(f"Caminho não é um diretório: {value}")
        return str(path.absolute())


class LoggingConfig(BaseModel):
    """Configurações de logging."""

    level: str = Field(default="INFO", description="Nível de log")
    log_file: str = Field(default="logs/backup.log", description="Arquivo de log")
    max_log_size_mb: int = Field(default=10, description="Tamanho máximo do log em MB")
    backup_count: int = Field(default=5, description="Número de backups de log")

    @validator("level")
    def validate_log_level(cls, value: str) -> str:
        """Valida o nível de log."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if value.upper() not in valid_levels:
            raise ValueError(f"Nível de log inválido. Use: {', '.join(valid_levels)}")
        return value.upper()


class AppConfig(BaseModel):
    """Configuração principal da aplicação."""

    aws: AWSConfig
    s3: S3Config
    backup: BackupConfig
    logging: LoggingConfig


class ConfigManager:
    """Gerenciador de configurações da aplicação."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa o gerenciador de configurações.

        Args:
            config_path: Caminho para o arquivo de configuração YAML
        """
        self.config_path = config_path or "config.yaml"
        self._load_environment_variables()

    def _load_environment_variables(self) -> None:
        """Carrega variáveis de ambiente do arquivo .env se existir."""
        env_file = Path(".env")
        if env_file.exists():
            load_dotenv(env_file)

    def load_config(self) -> AppConfig:
        """
        Carrega e valida a configuração da aplicação.

        Returns:
            AppConfig: Configuração validada da aplicação

        Raises:
            FileNotFoundError: Se o arquivo de configuração não for encontrado
            ValueError: Se a configuração for inválida
        """
        config_file = Path(self.config_path)

        if not config_file.exists():
            raise FileNotFoundError(
                f"Arquivo de configuração não encontrado: {self.config_path}. "
                f"Copie {self.config_path}.template para {self.config_path} e configure."
            )

        try:
            with open(config_file, "r", encoding="utf-8") as file:
                config_data = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise ValueError(f"Erro ao ler arquivo de configuração YAML: {e}")

        # Sobrescreve com variáveis de ambiente se disponíveis
        config_data = self._override_with_env_vars(config_data)

        try:
            return AppConfig(**config_data)
        except Exception as e:
            raise ValueError(f"Erro na validação da configuração: {e}")

    def _override_with_env_vars(self, config_data: dict) -> dict:
        """
        Sobrescreve configurações com variáveis de ambiente.

        Args:
            config_data: Dados de configuração do arquivo YAML

        Returns:
            dict: Configuração com variáveis de ambiente aplicadas
        """
        # AWS credentials
        if "aws" not in config_data:
            config_data["aws"] = {}

        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        if aws_access_key:
            config_data["aws"]["access_key_id"] = aws_access_key

        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        if aws_secret_key:
            config_data["aws"]["secret_access_key"] = aws_secret_key

        aws_region = os.getenv("AWS_DEFAULT_REGION")
        if aws_region:
            config_data["aws"]["region"] = aws_region

        # S3 bucket
        if "s3" not in config_data:
            config_data["s3"] = {}

        s3_bucket = os.getenv("S3_BUCKET_NAME")
        if s3_bucket:
            config_data["s3"]["bucket_name"] = s3_bucket

        return config_data

    def create_sample_config(self, output_path: str = "config.yaml") -> None:
        """
        Cria um arquivo de configuração de exemplo.

        Args:
            output_path: Caminho para o arquivo de configuração de saída
        """
        sample_config = {
            "aws": {
                "access_key_id": "your_access_key_here",
                "secret_access_key": "your_secret_key_here",
                "region": "us-east-1",
            },
            "s3": {"bucket_name": "your-backup-bucket", "prefix": "backups/"},
            "backup": {
                "source_directory": "/path/to/backup",
                "file_extensions": ["*.txt", "*.pdf", "*.docx"],
                "delete_after_upload": False,
            },
            "logging": {
                "level": "INFO",
                "log_file": "logs/backup.log",
                "max_log_size_mb": 10,
                "backup_count": 5,
            },
        }

        with open(output_path, "w", encoding="utf-8") as file:
            yaml.dump(sample_config, file, default_flow_style=False, indent=2)

        print(f"Arquivo de configuração de exemplo criado em: {output_path}")
