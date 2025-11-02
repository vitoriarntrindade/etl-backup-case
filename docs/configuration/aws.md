# Configuração AWS e Credenciais

## 🔑 Configuração de Credenciais AWS

### Método 1: AWS CLI (Recomendado)

```bash
# Instalar AWS CLI
pip install awscli

# Configurar credenciais
aws configure
```

Você será solicitado a fornecer:
- **Access Key ID**: Sua chave de acesso AWS
- **Secret Access Key**: Sua chave secreta AWS  
- **Default region**: Região padrão (ex: `us-east-1`)
- **Default output format**: `json`

### Método 2: Variáveis de Ambiente

Crie/edite o arquivo `.env`:

```bash
cp .env.template .env
```

Configure as variáveis:

```env
# Credenciais AWS
AWS_ACCESS_KEY_ID=sua_access_key_aqui
AWS_SECRET_ACCESS_KEY=sua_secret_key_aqui
AWS_DEFAULT_REGION=us-east-1

# Configurações S3 (opcional - override)
S3_BUCKET_NAME=meu-bucket-backup
S3_PREFIX=backups/
```

### Método 3: IAM Roles (EC2/ECS)

Para ambientes AWS, use IAM Roles em vez de credenciais estáticas.

## 🪣 Configuração do Bucket S3

### Criar Bucket

```bash
# Via AWS CLI
aws s3 mb s3://meu-bucket-backup --region us-east-1
```

### Configurar Permissões

Política IAM mínima necessária:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::meu-bucket-backup",
                "arn:aws:s3:::meu-bucket-backup/*"
            ]
        }
    ]
}
```

## 🔐 Segurança e Boas Práticas

### Rotação de Credenciais
- ✅ Gere novas access keys periodicamente
- ✅ Desative keys antigas após rotação
- ✅ Use AWS Secrets Manager para produção

### Princípio do Menor Privilégio
- ✅ Conceda apenas permissões necessárias
- ✅ Use bucket-specific policies
- ✅ Implemente MFA quando possível

### Monitoramento
- ✅ Habilite CloudTrail para auditoria
- ✅ Configure alertas de custos
- ✅ Monitore uso com CloudWatch

## ✅ Verificação da Configuração

### Teste de Conectividade

```bash
# Verificar credenciais
aws sts get-caller-identity

# Listar buckets
aws s3 ls

# Testar acesso ao bucket específico
aws s3 ls s3://meu-bucket-backup/
```

### Teste com a Pipeline

```bash
# Verificar configuração
python pipeline.py --status

# Teste dry-run
python pipeline.py --dry-run
```

## 🚨 Troubleshooting

### Erro: "Unable to locate credentials"
- Verifique o arquivo `.env`
- Confirme configuração do AWS CLI
- Valide variáveis de ambiente

### Erro: "Access Denied"
- Revisar políticas IAM
- Verificar permissões do bucket
- Confirmar região do bucket

### Erro: "Bucket does not exist"
- Confirmar nome do bucket
- Verificar região configurada
- Criar bucket se necessário

!!! warning "Importante"
    Nunca commitir credenciais AWS no Git. Use sempre `.env` local ou IAM Roles.

!!! tip "Próximo Passo"
    Agora execute seu primeiro [backup de teste](../usage/dry-run.md).