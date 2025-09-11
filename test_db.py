#!/usr/bin/env python3
"""
Script para testar a conexão com o PostgreSQL do Render
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def test_connection():
    """Testa a conexão com o banco de dados"""
    
    # Usa variável de ambiente ou a URL direta do Render
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://bancodeenderecos_user:GWLa4Qo4t4gFaPElKZaJWu9YK0nwmiz8@dpg-d3097rnfte5s73f3qj50-a.oregon-postgres.render.com/bancodeenderecos")
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    if DATABASE_URL.startswith("postgresql://") and "+" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
    
    try:
        print("🔌 Testando conexão com PostgreSQL do Render...")
        
        # Cria engine com configurações otimizadas para PostgreSQL
        engine = create_engine(
            DATABASE_URL, 
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False
        )
        
        # Testa a conexão
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Conexão bem-sucedida!")
            print(f"📊 Versão do PostgreSQL: {version}")
            
            # Testa se as tabelas existem
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"📋 Tabelas encontradas: {tables}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    if success:
        print("\n🎉 Teste de conexão concluído com sucesso!")
        print("💡 Sua aplicação está pronta para usar o PostgreSQL do Render.")
    else:
        print("\n⚠️  Falha no teste de conexão.")
        print("💡 Verifique se a URL do banco está correta e se o serviço está ativo.")
