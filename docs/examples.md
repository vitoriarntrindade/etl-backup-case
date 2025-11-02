# Exemplos de Uso

## 🎯 Cenários Comuns

### 1. Backup de Documentos

```yaml
# config.yaml
backup:
  source_directory: "/home/user/Documents"
  file_extensions: [".pdf", ".docx", ".xlsx", ".pptx"]
  exclude_patterns: ["~$*", ".tmp"]
  delete_after_upload: false

s3:
  bucket_name: "company-docs-backup"
  prefix: "documents/2025/"
```

### 2. Backup de Logs com Limpeza

```yaml
backup:
  source_directory: "/var/log/myapp"
  file_extensions: [".log", ".txt"]
  delete_after_upload: true
  
logging:
  level: "WARNING"  # Menos verbose para produção
```

### 3. Backup Seletivo por Padrão

```yaml
backup:
  source_directory: "./data"
  include_patterns: ["backup_*", "export_*"]
  exclude_patterns: ["temp_*", "*.tmp", "*.cache"]
```

## 📅 Automação com Cron

### Backup Diário
```bash
# Adicionar ao crontab
0 2 * * * cd /path/to/pipeline && python pipeline.py >> /var/log/backup.log 2>&1
```

### Backup Semanal com Relatório
```bash
#!/bin/bash
# backup-weekly.sh
cd /path/to/pipeline
python pipeline.py --output-json /var/log/backup-$(date +\%Y\%m\%d).json
```

## 🔄 Scripts de Automação

### Script com Notificação
```bash
#!/bin/bash
# backup-with-notification.sh

RESULT_FILE="/tmp/backup-$(date +%Y%m%d).json"
cd /path/to/pipeline

if python pipeline.py --output-json "$RESULT_FILE"; then
    echo "✅ Backup concluído com sucesso" | mail -s "Backup OK" admin@company.com
else
    echo "❌ Backup falhou" | mail -s "Backup ERRO" admin@company.com
fi
```

### Script com Retry
```bash
#!/bin/bash
# backup-with-retry.sh

MAX_RETRIES=3
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if python pipeline.py; then
        echo "Backup concluído com sucesso"
        exit 0
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo "Tentativa $RETRY_COUNT falhou, tentando novamente..."
        sleep 300  # Aguardar 5 minutos
    fi
done

echo "Backup falhou após $MAX_RETRIES tentativas"
exit 1
```

## 🐳 Uso com Docker

### Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "pipeline.py"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  backup:
    build: .
    volumes:
      - ./data:/app/data:ro
      - ./config.yaml:/app/config.yaml:ro
      - ./logs:/app/logs
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    restart: unless-stopped
```

## 📊 Monitoramento e Alertas

### Script de Monitoramento
```python
#!/usr/bin/env python3
# monitor-backup.py

import json
import sys
from datetime import datetime, timedelta

def check_backup_status(json_file):
    with open(json_file) as f:
        data = json.load(f)
    
    success_rate = data.get('success_rate_percent', 0)
    
    if success_rate < 95:
        print(f"⚠️ Taxa de sucesso baixa: {success_rate}%")
        return False
    
    print(f"✅ Backup OK: {success_rate}% sucesso")
    return True

if __name__ == "__main__":
    if not check_backup_status(sys.argv[1]):
        sys.exit(1)
```

### Integração com Prometheus
```python
# metrics.py
from prometheus_client import CollectorRegistry, Gauge, write_to_textfile

def export_metrics(results_json):
    registry = CollectorRegistry()
    
    success_rate = Gauge('backup_success_rate', 'Taxa de sucesso do backup', registry=registry)
    total_files = Gauge('backup_total_files', 'Total de arquivos processados', registry=registry)
    
    success_rate.set(results_json['success_rate_percent'])
    total_files.set(results_json['total_files'])
    
    write_to_textfile('/var/lib/prometheus/backup_metrics.prom', registry)
```

## 🚨 Tratamento de Erros

### Script Robusto
```bash
#!/bin/bash
# robust-backup.sh

set -euo pipefail

# Configurações
CONFIG_FILE="config.yaml"
LOG_FILE="/var/log/backup-$(date +%Y%m%d).log"
LOCK_FILE="/tmp/backup.lock"

# Verificar se já está executando
if [ -f "$LOCK_FILE" ]; then
    echo "Backup já está em execução" >&2
    exit 1
fi

# Criar lock
echo $$ > "$LOCK_FILE"

# Cleanup function
cleanup() {
    rm -f "$LOCK_FILE"
}
trap cleanup EXIT

# Verificar dependências
command -v python >/dev/null 2>&1 || { echo "Python não encontrado" >&2; exit 1; }

# Executar backup
python pipeline.py --config "$CONFIG_FILE" 2>&1 | tee "$LOG_FILE"
```