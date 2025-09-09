#!/usr/bin/env python3
"""
Script para migrar dados do SQLite local para PostgreSQL do Render
"""

import os
import sqlite3
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def migrate_data():
    """Migra dados do SQLite para PostgreSQL"""
    
    # URLs dos bancos
    SQLITE_URL = "sqlite:///agenda.db"
    POSTGRES_URL = "postgresql://bancodeenderecos_user:GWLa4Qo4t4gFaPElKZaJWu9YK0nwmiz8@dpg-d3097rnfte5s73f3qj50-a.oregon-postgres.render.com/bancodeenderecos"
    
    try:
        print("🔄 Iniciando migração de dados...")
        
        # Conecta ao SQLite
        sqlite_engine = create_engine(SQLITE_URL)
        print("✅ Conectado ao SQLite local")
        
        # Conecta ao PostgreSQL
        postgres_engine = create_engine(POSTGRES_URL, pool_pre_ping=True)
        print("✅ Conectado ao PostgreSQL do Render")
        
        # Verifica se o arquivo SQLite existe
        if not os.path.exists("agenda.db"):
            print("⚠️  Arquivo agenda.db não encontrado. Nada para migrar.")
            return
        
        # Migra dados de usuários
        with sqlite_engine.connect() as sqlite_conn:
            with postgres_engine.connect() as postgres_conn:
                # Verifica se há usuários no SQLite
                result = sqlite_conn.execute(text("SELECT COUNT(*) FROM usuarios"))
                user_count = result.fetchone()[0]
                
                if user_count > 0:
                    print(f"👥 Migrando {user_count} usuários...")
                    users = sqlite_conn.execute(text("SELECT * FROM usuarios")).fetchall()
                    
                    for user in users:
                        postgres_conn.execute(text("""
                            INSERT INTO usuarios (id, username, senha_hash) 
                            VALUES (:id, :username, :senha_hash)
                            ON CONFLICT (id) DO NOTHING
                        """), {
                            'id': user[0],
                            'username': user[1], 
                            'senha_hash': user[2]
                        })
                    postgres_conn.commit()
                    print("✅ Usuários migrados com sucesso")
                
                # Verifica se há endereços no SQLite
                result = sqlite_conn.execute(text("SELECT COUNT(*) FROM enderecos"))
                address_count = result.fetchone()[0]
                
                if address_count > 0:
                    print(f"📍 Migrando {address_count} endereços...")
                    addresses = sqlite_conn.execute(text("SELECT * FROM enderecos")).fetchall()
                    
                    for address in addresses:
                        postgres_conn.execute(text("""
                            INSERT INTO enderecos (id, empresa, nome, rua, cidade) 
                            VALUES (:id, :empresa, :nome, :rua, :cidade)
                            ON CONFLICT (id) DO NOTHING
                        """), {
                            'id': address[0],
                            'empresa': address[1],
                            'nome': address[2], 
                            'rua': address[3],
                            'cidade': address[4]
                        })
                    postgres_conn.commit()
                    print("✅ Endereços migrados com sucesso")
                
                print(f"🎉 Migração concluída!")
                print(f"📊 Total: {user_count} usuários e {address_count} endereços migrados")
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")

if __name__ == "__main__":
    migrate_data()
