# Configuração PostgreSQL - Agenda Digital

Este guia explica como configurar e usar o PostgreSQL do Render na sua aplicação Agenda Digital.

## 🚀 Configuração Rápida

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Testar Conexão
```bash
python test_db.py
```

### 3. Migrar Dados (se necessário)
Se você tem dados no SQLite local que deseja migrar:
```bash
python migrate_to_postgres.py
```

## 🔧 Configurações

### Variável de Ambiente
A aplicação usa a variável de ambiente `DATABASE_URL`. No Render, ela será configurada automaticamente.

Para desenvolvimento local, você pode:

1. **Usar SQLite (padrão)**: Não defina a variável `DATABASE_URL`
2. **Usar PostgreSQL do Render**: Defina a variável de ambiente:
   ```bash
   set DATABASE_URL=postgresql://bancodeenderecos_user:GWLa4Qo4t4gFaPElKZaJWu9YK0nwmiz8@dpg-d3097rnfte5s73f3qj50-a.oregon-postgres.render.com/bancodeenderecos
   ```

### Deploy no Render

1. Conecte seu repositório ao Render
2. Configure a variável de ambiente `DATABASE_URL` com a URL fornecida
3. O Render detectará automaticamente o `requirements.txt` e `app.py`

## 📊 Estrutura do Banco

### Tabelas Criadas Automaticamente
- `usuarios`: Armazena usuários do sistema
- `enderecos`: Armazena os endereços da agenda

### Usuário Padrão
- **Username**: admin
- **Senha**: 1234

## 🔍 Verificação

### Testar Localmente
```bash
python app.py
```
Acesse: http://localhost:5000

### Verificar Logs
A aplicação mostra logs de conexão no console quando inicia.

## 🛠️ Solução de Problemas

### Erro de Conexão
1. Verifique se a URL do banco está correta
2. Teste a conexão com `python test_db.py`
3. Verifique se o serviço PostgreSQL está ativo no Render

### Dados Não Aparecem
1. Execute `python migrate_to_postgres.py` para migrar dados existentes
2. Verifique se as tabelas foram criadas corretamente

### Performance
A aplicação está configurada com:
- `pool_pre_ping=True`: Verifica conexões antes de usar
- `pool_recycle=300`: Recicla conexões a cada 5 minutos

## 📝 Notas Importantes

- A aplicação funciona tanto com SQLite quanto PostgreSQL
- Os dados são migrados automaticamente na primeira execução
- O usuário admin é criado automaticamente se não existir
- A aplicação detecta automaticamente o tipo de banco pela URL
