# Pipeline de Backup S3

Pipeline automatizada para backup de arquivos locais para Amazon S3 com Python e boto3.

## 🚀 Características

- **Backup Automatizado**: Lista arquivos em diretório específico e faz upload para S3
- **Validação Robusta**: Verifica integridade dos uploads antes de deletar arquivos locais
- **Tratamento de Erros**: Registro detalhado de erros e recuperação automática
- **Configuração Flexível**: Suporte a arquivos YAML e variáveis de ambiente
- **Logging Avançado**: Sistema de logs com rotação e diferentes níveis
- **Type Hints**: Código totalmente tipado seguindo melhores práticas
- **PEP 8**: Código formatado e validado com Black, Flake8 e MyPy
- **Dry Run**: Modo de simulação para testar sem executar operações reais

## 📁 Estrutura do Projeto

```
etl-backup-case/
├── src/                          # Código fonte principal
│   ├── __init__.py              # Inicialização do pacote
│   ├── backup_pipeline.py       # Pipeline principal
│   ├── config.py               # Gerenciamento de configurações
│   ├── file_manager.py         # Operações de arquivo
│   ├── logger.py               # Sistema de logging
│   └── s3_manager.py           # Operações S3
├── pipeline.py                 # Script principal
├── requirements.txt            # Dependências de produção
├── requirements-dev.txt        # Dependências de desenvolvimento
├── config.yaml.template       # Modelo de configuração
├── .env.template              # Modelo de variáveis de ambiente
├── .flake8                    # Configuração do Flake8
├── .pre-commit-config.yaml    # Configuração de pre-commit hooks
├── mypy.ini                   # Configuração do MyPy
├── pyproject.toml             # Configuração do Black
├── check_code.sh              # Script de verificação de qualidade
└── README.md                  # Esta documentação
```

## 🔧 Instalação

### 1. Clone o repositório

```bash
    git clone <repository-url>
    cd etl-backup-case
```

### 2. Crie um ambiente virtual

```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### 3. Instale as dependências

```bash
  # Dependências de produção
    pip install -r requirements.txt
    
    # Para desenvolvimento (opcional)
    pip install -r requirements-dev.txt
```

### 4. Configure as credenciais AWS

#### Opção 1: Arquivo de configuração YAML

```bash
    # Crie o arquivo de configuração a partir do template
    cp config.yaml.template config.yaml
    
    # Edite e configure suas credenciais
    nano config.yaml
```

#### Opção 2: Variáveis de ambiente

```bash
  # Crie o arquivo .env a partir do template
    cp .env.template .env
    
    # Edite e configure suas credenciais
    nano .env
```

## ⚙️ Configuração

### Arquivo `config.yaml`

```yaml
aws:
  access_key_id: "sua_access_key_aqui"
  secret_access_key: "sua_secret_key_aqui"
  region: "us-east-1"
  
s3:
  bucket_name: "seu-bucket-backup"
  prefix: "backups/"  # Prefixo opcional para organizar arquivos
  
backup:
  source_directory: "/caminho/para/backup"
  file_extensions: ["*.txt", "*.pdf", "*.docx"]  # ["*"] para todos os arquivos
  delete_after_upload: false  # true para deletar arquivos locais após upload
  
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  log_file: "logs/backup.log"
  max_log_size_mb: 10
  backup_count: 5
```

### Variáveis de Ambiente (arquivo `.env`)

```bash
    AWS_ACCESS_KEY_ID=sua_access_key_aqui
    AWS_SECRET_ACCESS_KEY=sua_secret_key_aqui
    AWS_DEFAULT_REGION=us-east-1
    S3_BUCKET_NAME=seu-bucket-backup
```

> **Nota**: As variáveis de ambiente têm prioridade sobre o arquivo de configuração.

## 🚀 Uso

### Comandos Básicos

```bash
  # Criar arquivo de configuração de exemplo
python pipeline.py --create-config

# Verificar status da configuração
python pipeline.py --status

# Executar backup
python pipeline.py

# Executar backup com arquivo de configuração específico
python pipeline.py --config minha_config.yaml

# Executar em modo dry-run (simulação)
python pipeline.py --dry-run

# Salvar resultados em JSON
python pipeline.py --output-json resultados.json
```

### Exemplos Avançados

```bash
  # Backup com configuração personalizada e saída detalhada
    python pipeline.py --config production.yaml --verbose
    
    # Simulação de backup para testar configuração
    python pipeline.py --dry-run --verbose
    
    # Backup com log de resultados
    python pipeline.py --output-json backup_$(date +%Y%m%d_%H%M%S).json
```

## 🔍 Funcionalidades Detalhadas

### 1. **Listagem de Arquivos**
- Busca recursiva em diretórios e subdiretórios
- Filtros por extensão de arquivo configuráveis
- Validação de permissões de acesso

### 2. **Upload para S3**
- Verificação de conectividade e acesso ao bucket
- Upload com verificação de integridade
- Tratamento de erros de rede e autenticação
- Geração de chaves S3 organizadas

### 3. **Deleção Segura**
- Deleção apenas após upload bem-sucedido
- Validações de segurança (arquivos dentro do diretório de origem)
- Configurável (pode ser desabilitada)
- Limpeza automática de diretórios vazios

### 4. **Logging Avançado**
- Logs em arquivo com rotação automática
- Diferentes níveis de verbosidade
- Timestamps e formatação estruturada
- Logs separados para console e arquivo

### 5. **Tratamento de Erros**
- Recuperação automática de falhas temporárias
- Registro detalhado de erros
- Continuidade da operação mesmo com falhas parciais
- Relatório final com estatísticas

## 🧪 Desenvolvimento e Qualidade

### Verificação de Qualidade do Código

```bash
    # Executar todas as verificações
    ./check_code.sh
    
    # Verificações individuais
    black --check src/ pipeline.py          # Formatação
    flake8 src/ pipeline.py                 # Linting
    mypy src/ pipeline.py                   # Type checking
```

### Formatação Automática

```bash
    # Formatar código automaticamente
    black src/ pipeline.py
```

### Pre-commit Hooks

```bash
    # Instalar pre-commit hooks
    pre-commit install
    
    # Executar em todos os arquivos
    pre-commit run --all-files
```

## 📊 Monitoramento e Logs

### Estrutura de Logs

```
logs/
├── backup.log           # Log principal
├── backup.log.1         # Backup rotacionado
├── backup.log.2         # Backup rotacionado
└── ...
```

### Exemplo de Log

```
2024-11-01 10:30:15 - backup_pipeline - INFO - Iniciando operação: listar_arquivos - Diretório: /home/user/documents
2024-11-01 10:30:15 - backup_pipeline - INFO - Encontrados 25 arquivos para backup
2024-11-01 10:30:16 - backup_pipeline - INFO - upload bem-sucedido: /home/user/documents/file1.pdf
2024-11-01 10:30:18 - backup_pipeline - INFO - Arquivo deletado: /home/user/documents/file1.pdf
```

## 🔒 Segurança

### Boas Práticas Implementadas

1. **Credenciais**: Nunca hardcoded, sempre via configuração ou variáveis de ambiente
2. **Validação**: Verificação de caminhos para evitar operações fora do diretório configurado
3. **Permissões**: Verificação de permissões antes de operações de arquivo
4. **Logs**: Logs não expõem informações sensíveis
5. **Integridade**: Verificação de integridade dos uploads antes de deletar arquivos locais

### Configuração de Credenciais AWS

#### Método 1: AWS CLI (Recomendado)

```bash
    aws configure
```

#### Método 2: Arquivo de configuração

```yaml
    aws:
      access_key_id: "AKIA..."
      secret_access_key: "..."
      region: "us-east-1"
```

#### Método 3: Variáveis de ambiente

```bash
    export AWS_ACCESS_KEY_ID="AKIA..."
    export AWS_SECRET_ACCESS_KEY="..."
    export AWS_DEFAULT_REGION="us-east-1"
```

## 🚨 Solução de Problemas

### Problemas Comuns

#### 1. Erro de credenciais AWS

```
❌ Erro: AWS Access Key ID inválido
```

**Solução**: Verifique suas credenciais AWS no arquivo de configuração ou variáveis de ambiente.

#### 2. Bucket não encontrado

```
❌ Erro: Bucket não encontrado: meu-bucket
```

**Solução**: Verifique se o bucket existe e se você tem permissões para acessá-lo.

#### 3. Diretório de origem não existe

```
❌ Erro: Diretório de origem não existe: /caminho/inexistente
```

**Solução**: Verifique o caminho no arquivo de configuração.

#### 4. Permissão negada

```
❌ Erro: Permissão negada para deletar arquivo
```

**Solução**: Verifique as permissões dos arquivos e do usuário executando o script.

### Debug

```bash
# Executar com logs detalhados
python pipeline.py --verbose

# Verificar configuração
python pipeline.py --status

# Testar sem executar operações reais
python pipeline.py --dry-run --verbose
```

## 📈 Códigos de Saída

| Código | Significado |
|--------|-------------|
| 0      | Sucesso total |
| 1      | Erro fatal (configuração, conexão, etc.) |
| 2      | Sucesso parcial (alguns uploads falharam) |
| 130    | Interrompido pelo usuário (Ctrl+C) |



