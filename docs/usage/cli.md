# Interface CLI

## 🎮 Comandos Disponíveis

### Comando Principal
```bash
python pipeline.py [OPÇÕES]
```

## 📋 Opções Disponíveis

| Opção | Descrição | Exemplo |
|-------|-----------|---------|
| `--config` | Arquivo de configuração | `--config custom.yaml` |
| `--dry-run` | Modo simulação | `--dry-run` |
| `--create-config` | Criar configuração | `--create-config` |
| `--status` | Verificar status | `--status` |
| `--output-json` | Saída em JSON | `--output-json results.json` |
| `--verbose` | Log detalhado | `--verbose` |
| `--help` | Ajuda | `--help` |

## 🚀 Exemplos Práticos

### Backup Básico
```bash
python pipeline.py
```

### Backup com Configuração Personalizada
```bash
python pipeline.py --config production.yaml
```

### Teste sem Executar
```bash
python pipeline.py --dry-run --verbose
```

### Backup com Métricas
```bash
python pipeline.py --output-json backup-$(date +%Y%m%d).json
```

## 📊 Códigos de Saída

| Código | Significado |
|--------|-------------|
| `0` | Sucesso completo |
| `1` | Erro de configuração |
| `2` | Backup com falhas parciais |
| `130` | Interrompido pelo usuário |