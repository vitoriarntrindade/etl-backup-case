# Instalação

## 📋 Pré-requisitos

- **Python 3.12+** 
- **Conta AWS** com permissões S3
- **Git** para clonagem do repositório

## 🚀 Instalação Rápida

### 1. Clonar o Repositório

```bash
git clone https://github.com/vitoriarntrindade/etl-backup-case.git
cd etl-backup-case
```

### 2. Criar Ambiente Virtual

=== "Linux/macOS"
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

=== "Windows"
    ```cmd
    python -m venv .venv
    .venv\Scripts\activate
    ```

### 3. Instalar Dependências

```bash
# Dependências de produção
pip install -r requirements.txt

# Para desenvolvimento (opcional)
pip install -r requirements-dev.txt
```

## 📦 Dependências

### Produção
- **boto3** - SDK AWS para Python
- **pydantic** - Validação de dados
- **pyyaml** - Parser YAML
- **python-dotenv** - Variáveis de ambiente

### Desenvolvimento
- **black** - Formatação de código
- **flake8** - Linting
- **mypy** - Type checking
- **pre-commit** - Hooks de commit

## ✅ Verificação da Instalação

```bash
# Verificar versão do Python
python --version

# Verificar instalação da pipeline
python pipeline.py --help

# Verificar qualidade do código (dev)
bash check_code.sh
```

## 🔧 Configuração Inicial

Após a instalação, configure a pipeline:

```bash
# Criar arquivo de configuração
python pipeline.py --create-config

# Criar arquivo de variáveis de ambiente
cp .env.template .env
```

!!! tip "Próximos Passos"
    - Configure suas [credenciais AWS](configuration/aws.md)
    - Execute seu primeiro [backup de teste](usage/dry-run.md)

## 🐳 Docker (Opcional)

Para ambientes containerizados:

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "pipeline.py"]
```

## 🧪 Verificação da Configuração

```bash
# Verificar configuração
python pipeline.py --status

# Teste de conectividade
python pipeline.py --dry-run
```