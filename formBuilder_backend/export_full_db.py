"""
Script pour exporter la base de données complète avec les données
"""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from datetime import datetime
import json

async def export_database_with_data():
    """Exporter le schéma ET les données de la base"""
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    output_file = f"database_full_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- =====================================================\n")
        f.write("-- FormBuilder Database FULL Backup (Schema + Data)\n")
        f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("-- =====================================================\n\n")
        f.write("-- Usage: psql -U postgres -d formbuilder_db < this_file.sql\n\n")
        
        async with engine.connect() as conn:
            # 1. Lister toutes les tables
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                AND table_name != 'alembic_version'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result]
            
            print(f"\n📋 Tables trouvées: {len(tables)}")
            for table in tables:
                print(f"  - {table}")
            
            # 2. Désactiver les contraintes temporairement
            f.write("\n-- Désactiver les contraintes de clés étrangères\n")
            f.write("SET session_replication_role = 'replica';\n\n")
            
            # 3. Pour chaque table, exporter le schéma et les données
            for table in tables:
                print(f"\n🔄 Export de {table}...")
                
                # Compter les lignes
                result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                row_count = result.scalar()
                
                f.write(f"\n-- =====================================================\n")
                f.write(f"-- Table: {table} ({row_count} rows)\n")
                f.write(f"-- =====================================================\n\n")
                
                # Obtenir les colonnes
                result = await conn.execute(text(f"""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = :table_name
                    ORDER BY ordinal_position
                """), {"table_name": table})
                
                columns_info = [(row[0], row[1], row[2], row[3]) for row in result]
                column_names = [col[0] for col in columns_info]
                
                # CREATE TABLE
                f.write(f"DROP TABLE IF EXISTS {table} CASCADE;\n")
                f.write(f"CREATE TABLE {table} (\n")
                
                col_defs = []
                for col_name, data_type, nullable, default in columns_info:
                    col_def = f"  {col_name} "
                    
                    # Type de données
                    if data_type == 'character varying':
                        col_def += "VARCHAR(255)"
                    elif data_type == 'timestamp without time zone':
                        col_def += "TIMESTAMP"
                    elif data_type == 'timestamp with time zone':
                        col_def += "TIMESTAMP WITH TIME ZONE"
                    elif data_type == 'ARRAY':
                        col_def += "TEXT[]"
                    elif data_type == 'USER-DEFINED':
                        col_def += "TEXT"
                    else:
                        col_def += data_type.upper()
                    
                    if nullable == 'NO':
                        col_def += " NOT NULL"
                    
                    if default and 'nextval' not in str(default):
                        col_def += f" DEFAULT {default}"
                    
                    col_defs.append(col_def)
                
                f.write(",\n".join(col_defs))
                f.write("\n);\n\n")
                
                # Exporter les données
                if row_count and row_count > 0:
                    print(f"  📊 Export de {row_count} lignes...")
                    
                    result = await conn.execute(text(f"SELECT * FROM {table}"))
                    rows = result.fetchall()
                    
                    if rows:
                        f.write(f"-- Données pour {table}\n")
                        
                        for row in rows:
                            values = []
                            for i, value in enumerate(row):
                                if value is None:
                                    values.append("NULL")
                                elif isinstance(value, (dict, list)):
                                    # Pour JSONB
                                    json_str = json.dumps(value, ensure_ascii=False).replace("'", "''")
                                    values.append(f"'{json_str}'::jsonb")
                                elif isinstance(value, bool):
                                    values.append("TRUE" if value else "FALSE")
                                elif isinstance(value, (int, float)):
                                    values.append(str(value))
                                elif isinstance(value, datetime):
                                    values.append(f"'{value.isoformat()}'")
                                else:
                                    # String
                                    escaped = str(value).replace("'", "''")
                                    values.append(f"'{escaped}'")
                            
                            f.write(f"INSERT INTO {table} ({', '.join(column_names)}) VALUES ({', '.join(values)});\n")
                        
                        f.write("\n")
                    
                    print(f"  ✅ {row_count} lignes exportées")
                else:
                    f.write(f"-- Aucune donnée dans {table}\n\n")
                    print(f"  ⚠️  Table vide")
            
            # 4. Réactiver les contraintes
            f.write("\n-- Réactiver les contraintes de clés étrangères\n")
            f.write("SET session_replication_role = 'origin';\n\n")
            
            # 5. Réinitialiser les séquences
            f.write("\n-- =====================================================\n")
            f.write("-- Réinitialiser les séquences\n")
            f.write("-- =====================================================\n\n")
            
            for table in tables:
                try:
                    result = await conn.execute(text(f"""
                        SELECT pg_get_serial_sequence('{table}', 'id')
                    """))
                    seq_name = result.scalar()
                    
                    if seq_name:
                        f.write(f"SELECT setval('{seq_name}', (SELECT MAX(id) FROM {table}), true);\n")
                except:
                    pass
    
    print(f"\n✅ Backup complet exporté dans: {output_file}")
    print(f"📊 {len(tables)} tables exportées avec leurs données")
    print(f"\n📖 Pour restaurer:")
    print(f"   psql -U postgres -d formbuilder_db < {output_file}")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(export_database_with_data())
