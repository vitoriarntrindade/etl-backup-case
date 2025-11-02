# Guia Rápido

## 🚀 Primeiros Passos

### 1. Configuração Inicial

```bash
# Criar configuração
python pipeline.py --create-config

# Verificar status
python pipeline.py --status
```

### 2. Primeiro Backup (Teste)

```bash
# Executar em modo dry-run
python pipeline.py --dry-run
```

### 3. Backup Real

```bash
# Backup com configuração padrão
python pipeline.py

# Backup com saída JSON
python pipeline.py --output-json backup-results.json
```

## 📁 Estrutura de Arquivos

```
etl-backup-case/
├── config.yaml              # Configuração principal
├── .env                     # Variáveis de ambiente
├── logs/                    # Logs da pipeline
├── manifests/               # Manifestos de backup
├── test_data/               # Dados para teste
└── pipeline.py              # Script principal
```

## ⚙️ Configuração Básica

### config.yaml
```yaml
aws:
  region: "us-east-1"

s3:
  bucket_name: "meu-bucket-backup"
  prefix: "backups/"

backup:
  source_directory: "./test_data"
  file_extensions: [".txt", ".json", ".xml"]
  delete_after_upload: false

logging:
  level: "INFO"
  log_to_file: true
```

### .env
```env
AWS_ACCESS_KEY_ID=sua_access_key
AWS_SECRET_ACCESS_KEY=sua_secret_key
```

## 🎯 Cenários Comuns

### Backup Seletivo
```bash
# Configurar filtros no config.yaml
backup:
  file_extensions: [".pdf", ".docx"]
  exclude_patterns: ["temp*", "*.tmp"]
```

### Backup com Limpeza
```bash
# Habilitar deleção após upload
backup:
  delete_after_upload: true
```

### Backup Agendado
```bash
# Adicionar ao crontab
0 2 * * * cd /path/to/project && python pipeline.py
```

## 📊 Monitoramento

### Logs em Tempo Real
```bash
tail -f logs/backup_pipeline.log
```

### Métricas JSON
```bash
python pipeline.py --output-json metrics.json
cat metrics.json | jq '.success_rate_percent'
```

## 🔧 Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| "Credenciais inválidas" | Verificar `.env` e AWS CLI |
| "Bucket não encontrado" | Confirmar nome e região |
| "Permissão negada" | Revisar políticas IAM |
| "Nenhum arquivo encontrado" | Verificar `source_directory` |

## 💡 Dicas Importantes

!!! tip "Performance"
    - Use filtros para reduzir número de arquivos
    - Configure logs com nível WARNING em produção
    - Monitore custos S3 regularmente

!!! warning "Segurança"
    - Nunca commitar credenciais
    - Use IAM roles quando possível
    - Habilite versionamento S3

!!! success "Automação"
    - Integre com cron para backups regulares
    - Use `--output-json` para monitoramento
    - Configure alertas baseados em métricas