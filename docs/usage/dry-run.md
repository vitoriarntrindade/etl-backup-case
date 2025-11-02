# Modo Dry Run

## 🧪 O que é Dry Run?

O modo **Dry Run** simula toda a operação de backup sem executar ações reais, permitindo testar configurações e identificar problemas sem risco.

## 🚀 Como Usar

```bash
python pipeline.py --dry-run
```

## ✅ O que é Simulado

- ✅ **Listagem de arquivos** - Lista real dos arquivos encontrados
- ✅ **Validação S3** - Testa conectividade e permissões
- ✅ **Logs completos** - Gera logs como execução real
- ✅ **Métricas** - Calcula estatísticas de simulação

## ❌ O que NÃO é Executado

- ❌ **Upload para S3** - Nenhum arquivo é enviado
- ❌ **Deleção local** - Arquivos permanecem intactos
- ❌ **Manifest real** - Não cria arquivo de manifest

## 📋 Exemplo de Saída

```
🚀 Inicializando Pipeline de Backup S3...
🔍 Executando em modo DRY-RUN (simulação)

Fase 1: Listando arquivos para backup...
Encontrados 25 arquivos para backup

Fase 2: Executando uploads para S3...
[DRY-RUN] Simulando upload: /path/file1.txt
[DRY-RUN] Simulando upload: /path/file2.json

📈 RESULTADOS FINAIS
Total de arquivos: 25
Uploads bem-sucedidos: 25
Taxa de sucesso: 100.0%
```

## 🎯 Casos de Uso

### Validação de Configuração
```bash
# Testar nova configuração
python pipeline.py --config test.yaml --dry-run
```

### Estimativa de Transferência
```bash
# Ver quantos arquivos seriam transferidos
python pipeline.py --dry-run --verbose
```

### Debug de Problemas
```bash
# Identificar arquivos problemáticos
python pipeline.py --dry-run 2>&1 | grep ERROR
```

## 💡 Dicas

!!! tip "Sempre teste primeiro"
    Execute dry-run antes de qualquer backup em produção

!!! success "Validação completa"
    Dry-run testa conectividade S3 e permissões

!!! warning "Limitações"
    Não detecta problemas de upload específicos