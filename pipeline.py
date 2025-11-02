#!/usr/bin/env python3
"""
Script principal da Pipeline de Backup S3.
Executa backup automatizado de arquivos locais para Amazon S3.
"""

import argparse
import json
import sys
from pathlib import Path

from src import BackupPipeline, BackupPipelineError, BackupResults, ConfigManager


def setup_argparse() -> argparse.ArgumentParser:
    """
    Configura argumentos da linha de comando.

    Returns:
        argparse.ArgumentParser: Parser configurado
    """
    parser = argparse.ArgumentParser(
        description="Pipeline de Backup S3 - Backup automatizado de arquivos para Amazon S3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  # Backup com configuração padrão
  python pipeline.py

  # Backup com arquivo de configuração específico
  python pipeline.py --config my_config.yaml

  # Execução em modo dry-run (simulação)
  python pipeline.py --dry-run

  # Criar arquivo de configuração de exemplo
  python pipeline.py --create-config

  # Exibir status da configuração
  python pipeline.py --status
        """,
    )

    parser.add_argument(
        "--config",
        "-c",
        default="config.yaml",
        help="Caminho para o arquivo de configuração (padrão: config.yaml)",
    )

    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Executa em modo simulação (não faz upload nem deleção real)",
    )

    parser.add_argument(
        "--create-config",
        action="store_true",
        help="Cria um arquivo de configuração de exemplo",
    )

    parser.add_argument(
        "--status",
        "-s",
        action="store_true",
        help="Exibe o status da configuração atual",
    )

    parser.add_argument(
        "--output-json", help="Salva resultados da execução em arquivo JSON"
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Saída mais detalhada"
    )

    return parser


def create_sample_config(config_path: str) -> None:
    """
    Cria um arquivo de configuração de exemplo.

    Args:
        config_path: Caminho onde criar o arquivo
    """
    try:
        config_manager = ConfigManager()
        config_manager.create_sample_config(config_path)
        print(f"✅ Arquivo de configuração criado: {config_path}")
        print("📝 Edite o arquivo e configure suas credenciais AWS antes de usar.")

    except Exception as e:
        print(f"❌ Erro ao criar arquivo de configuração: {e}")
        sys.exit(1)


def show_status(config_path: str) -> None:
    """
    Exibe o status da configuração atual.

    Args:
        config_path: Caminho do arquivo de configuração
    """
    try:
        pipeline = BackupPipeline(config_path)
        pipeline.initialize()

        status = pipeline.get_status()

        print("📊 STATUS DA CONFIGURAÇÃO")
        print("=" * 40)
        print(f"Arquivo de configuração: {config_path}")
        print(f"Diretório de origem: {status['source_directory']}")
        print(f"Bucket S3: {status['bucket_name']}")
        print(
            f"Deletar após upload: {'Sim' if status['delete_after_upload'] else 'Não'}"
        )
        print("✅ Configuração válida e conexão S3 verificada")

    except FileNotFoundError:
        print(f"❌ Arquivo de configuração não encontrado: {config_path}")
        print("💡 Use --create-config para criar um arquivo de exemplo")
        sys.exit(1)

    except BackupPipelineError as e:
        print(f"❌ Erro na configuração: {e}")
        sys.exit(1)


def save_results_json(results: BackupResults, output_path: str) -> None:
    """
    Salva os resultados em arquivo JSON.

    Args:
        results: Resultados da execução
        output_path: Caminho do arquivo de saída
    """
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"📄 Resultados salvos em: {output_path}")

    except Exception as e:
        print(f"⚠️  Erro ao salvar resultados JSON: {e}")


def main() -> None:
    """Função principal do script."""
    parser = setup_argparse()
    args = parser.parse_args()

    # Criar configuração de exemplo
    if args.create_config:
        create_sample_config(args.config)
        return

    # Exibir status
    if args.status:
        show_status(args.config)
        return

    # Verificar se arquivo de configuração existe
    if not Path(args.config).exists():
        print(f"❌ Arquivo de configuração não encontrado: {args.config}")
        print("💡 Use --create-config para criar um arquivo de exemplo")
        sys.exit(1)

    try:
        # Inicializa pipeline
        print("🚀 Inicializando Pipeline de Backup S3...")
        pipeline = BackupPipeline(args.config)
        pipeline.initialize()

        if args.dry_run:
            print("🔍 Executando em modo DRY-RUN (simulação)")

        # Executa backup
        results = pipeline.run_backup(dry_run=args.dry_run)

        # Assertions para MyPy
        assert pipeline.config is not None

        # Exibe resultados resumidos no console
        print("\n📈 RESULTADOS FINAIS")
        print("=" * 30)
        print(f"Total de arquivos: {results.total_files}")
        print(f"Uploads bem-sucedidos: {results.successful_uploads}")
        print(f"Uploads falharam: {results.failed_uploads}")
        print(f"Taxa de sucesso: {results.success_rate:.1f}%")
        print(f"Duração: {results.duration:.2f} segundos")

        if pipeline.config.backup.delete_after_upload:
            print(f"Arquivos deletados: {results.deleted_files}")
            print(f"Falhas na deleção: {results.failed_deletions}")

        # Salva resultados em JSON se solicitado
        if args.output_json:
            save_results_json(results, args.output_json)

        # Determina código de saída baseado nos resultados
        if results.failed_uploads > 0:
            print("\n⚠️  Backup concluído com algumas falhas")
            sys.exit(2)
        elif results.total_files == 0:
            print("\n💭 Nenhum arquivo encontrado para backup")
            sys.exit(0)
        else:
            print("\n✅ Backup concluído com sucesso!")
            sys.exit(0)

    except BackupPipelineError as e:
        print(f"\n❌ Erro na pipeline: {e}")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⏹️  Backup interrompido pelo usuário")
        sys.exit(130)

    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
