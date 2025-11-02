# 📚 Tutorial Passo a Passo - Pipeline de Backup S3

Este tutorial vai te ensinar **do zero** como configurar e usar a pipeline de backup S3.

## 🎯 O que você vai aprender

- Como escolher o diretório para backup
- Como configurar suas credenciais AWS
- Como personalizar quais tipos de arquivo fazer backup
- Como testar antes de executar
- Como executar o backup real

---

## 📋 Pré-requisitos

Antes de começar, você precisa ter:

1. **Python 3.8+** instalado
2. **Conta AWS** com permissões no S3
3. **Bucket S3** criado (vou te ensinar a criar)

---

## 🚀 Passo 1: Preparando o Ambiente

### 1.1 Baixe o projeto

```bash
# Clone ou baixe os arquivos do projeto
cd /caminho/onde/voce/quer/o/projeto
# (os arquivos já estão no seu diretório atual)
```

### 1.2 Instale as dependências

```bash
# Instala as bibliotecas necessárias
pip install -r requirements.txt
```

**✅ Pronto!** O ambiente está configurado.

---

## 🔧 Passo 2: Configuração Inicial

### 2.1 Crie o arquivo de configuração

```bash
# Cria um arquivo de configuração padrão
python pipeline.py --create-config
```

Isso vai criar o arquivo `config.yaml` com configurações de exemplo.

### 2.2 Abra o arquivo config.yaml

Abra o arquivo `config.yaml` que foi criado. Você verá algo assim:

```yaml
aws:
  access_key_id: "your_access_key_here"    # ← VOCÊ PRECISA MUDAR ISSO
  secret_access_key: "your_secret_key_here" # ← VOCÊ PRECISA MUDAR ISSO
  region: "us-east-1"

s3:
  bucket_name: "your-backup-bucket"        # ← VOCÊ PRECISA MUDAR ISSO
  prefix: "backups/"

backup:
  source_directory: "/path/to/backup"      # ← AQUI VOCÊ ESCOLHE O DIRETÓRIO!
  file_extensions: ["*.txt", "*.pdf", "*.docx"]
  delete_after_upload: false

logging:
  level: "INFO"
  log_file: "logs/backup.log"
  max_log_size_mb: 10
  backup_count: 5
```

---

## 🗂️ Passo 3: Escolhendo o Diretório de Backup

### 3.1 Entenda o que é o `source_directory`

O `source_directory` é **a pasta que você quer fazer backup**. Pode ser:

- Seus documentos: `/home/seu-usuario/Documents`
- Uma pasta específica: `/home/seu-usuario/Projetos/importante`
- Qualquer pasta no seu computador

### 3.2 Exemplo prático - Vamos criar uma pasta de teste

```bash
# Cria uma pasta de exemplo
mkdir -p /home/klg-02/meus-arquivos-importantes

# Cria alguns arquivos de exemplo
echo "Relatório importante" > /home/klg-02/meus-arquivos-importantes/relatorio.txt
echo "Apresentação da empresa" > /home/klg-02/meus-arquivos-importantes/apresentacao.pdf
echo "Planilha de vendas" > /home/klg-02/meus-arquivos-importantes/vendas.xlsx
```

### 3.3 Configure no config.yaml

Edite o arquivo `config.yaml` e mude esta linha:

```yaml
backup:
  source_directory: "/home/klg-02/meus-arquivos-importantes"  # ← SUA PASTA AQUI
```

**💡 Dica:** Você pode usar **qualquer pasta** que quiser:
- `/home/seu-nome/Documents`
- `/home/seu-nome/Fotos`
- `/home/seu-nome/Projetos`

---

## 🔑 Passo 4: Configurando AWS (Credenciais)

### 4.1 Obtenha suas credenciais AWS

1. **Entre no Console AWS**: https://aws.amazon.com/console/
2. **Vá em IAM > Users > Seu usuário > Security credentials**
3. **Clique em "Create access key"**
4. **Anote o Access Key ID e Secret Access Key**

### 4.2 Configure no arquivo

Edite o `config.yaml`:

```yaml
aws:
  access_key_id: "AKIA1234567890EXEMPLO"     # ← Cole seu Access Key aqui
  secret_access_key: "abc123def456ghi789"    # ← Cole seu Secret Key aqui
  region: "us-east-1"                        # ← Pode deixar assim
```

### 4.3 Configure o bucket S3

```yaml
s3:
  bucket_name: "meu-bucket-backup-pessoal"   # ← Nome do seu bucket
  prefix: "backups/"                         # ← Pasta dentro do bucket (opcional)
```

**📝 Nota:** Se o bucket não existir, você precisa criar no Console AWS primeiro.

---

## 🎛️ Passo 5: Personalizando o Backup

### 5.1 Escolha quais tipos de arquivo fazer backup

No `config.yaml`, você pode configurar quais arquivos quer:

```yaml
backup:
  file_extensions: 
    - "*.txt"      # Arquivos de texto
    - "*.pdf"      # PDFs
    - "*.docx"     # Word
    - "*.xlsx"     # Excel
    - "*.jpg"      # Fotos JPEG
    - "*.png"      # Fotos PNG
    - "*"          # TODOS os arquivos (cuidado!)
```

### 5.2 Configure se quer deletar os arquivos originais

```yaml
backup:
  delete_after_upload: false  # false = mantém arquivos originais
                              # true = deleta após upload (CUIDADO!)
```

**⚠️ ATENÇÃO:** Só mude para `true` se você tem certeza! Os arquivos serão deletados da sua máquina.

---

## 🧪 Passo 6: Testando a Configuração

### 6.1 Verifique se está tudo certo

```bash
# Verifica se a configuração está válida
python pipeline.py --status
```

Se aparecer "✅ Configuração válida", está tudo certo!

### 6.2 Teste sem executar (modo simulação)

```bash
# Executa em modo "dry-run" - não faz upload nem deleta nada
python pipeline.py --dry-run --verbose
```

Isso vai mostrar **exatamente** o que seria feito, mas **sem executar**!

Você verá algo assim:
```
🔍 Executando em modo DRY-RUN (simulação)
📦 Encontrados 3 arquivos para backup
[DRY-RUN] Simulando upload: /home/klg-02/meus-arquivos-importantes/relatorio.txt
[DRY-RUN] Simulando upload: /home/klg-02/meus-arquivos-importantes/apresentacao.pdf
[DRY-RUN] Simulando upload: /home/klg-02/meus-arquivos-importantes/vendas.xlsx
✅ Taxa de sucesso: 100.0%
```

---

## 🚀 Passo 7: Executando o Backup Real

### 7.1 Execute o backup

Quando estiver satisfeito com o teste, execute:

```bash
# Executa o backup real
python pipeline.py
```

### 7.2 Acompanhe o progresso

Você verá algo assim:

```
🚀 Inicializando Pipeline de Backup S3...
📦 Encontrados 3 arquivos para backup
Processando arquivo 1/3: /home/klg-02/meus-arquivos-importantes/relatorio.txt
✅ Upload bem-sucedido: relatorio.txt
Processando arquivo 2/3: /home/klg-02/meus-arquivos-importantes/apresentacao.pdf
✅ Upload bem-sucedido: apresentacao.pdf
Processando arquivo 3/3: /home/klg-02/meus-arquivos-importantes/vendas.xlsx
✅ Upload bem-sucedido: vendas.xlsx

📈 RESULTADOS FINAIS
Total de arquivos: 3
Uploads bem-sucedidos: 3
Taxa de sucesso: 100.0%
```

### 7.3 Verifique no AWS S3

1. Entre no Console AWS
2. Vá em S3
3. Abra seu bucket
4. Você verá seus arquivos na pasta "backups/"

---

## 🎯 Exemplos Práticos Comuns

### Exemplo 1: Backup da pasta Documentos

```yaml
backup:
  source_directory: "/home/seu-nome/Documents"
  file_extensions: ["*.pdf", "*.docx", "*.txt"]
  delete_after_upload: false
```

### Exemplo 2: Backup de fotos

```yaml
backup:
  source_directory: "/home/seu-nome/Pictures"
  file_extensions: ["*.jpg", "*.jpeg", "*.png", "*.raw"]
  delete_after_upload: false
```

### Exemplo 3: Backup de projeto específico

```yaml
backup:
  source_directory: "/home/seu-nome/Projetos/projeto-importante"
  file_extensions: ["*"]  # Todos os arquivos
  delete_after_upload: false
```

---

## 🔄 Comandos Úteis

```bash
# Ver ajuda
python pipeline.py --help

# Criar nova configuração
python pipeline.py --create-config

# Verificar configuração atual
python pipeline.py --status

# Testar sem executar
python pipeline.py --dry-run

# Backup com arquivo de config específico
python pipeline.py --config minha-config.yaml

# Salvar relatório em JSON
python pipeline.py --output-json resultado.json
```

---

## ❗ Problemas Comuns e Soluções

### ❌ "Arquivo de configuração não encontrado"
**Solução:** Execute `python pipeline.py --create-config`

### ❌ "AWS Access Key ID inválido"
**Solução:** Verifique suas credenciais no `config.yaml`

### ❌ "Bucket não encontrado"
**Solução:** Crie o bucket no Console AWS primeiro

### ❌ "Diretório não existe"
**Solução:** Verifique se o caminho no `source_directory` está correto

### ❌ "Permissão negada"
**Solução:** Verifique se você tem permissão para ler a pasta escolhida

---

## 🎉 Parabéns!

Agora você sabe como:
- ✅ Escolher qualquer diretório para backup
- ✅ Configurar credenciais AWS
- ✅ Personalizar tipos de arquivo
- ✅ Testar antes de executar
- ✅ Fazer backup real

**💡 Dica final:** Sempre teste com `--dry-run` primeiro!