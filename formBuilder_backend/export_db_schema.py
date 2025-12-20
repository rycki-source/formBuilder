"""
Script pour exporter le schéma de la base de données
"""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from datetime import datetime

async def export_database_schema():
    """Exporter le schéma complet de la base de données"""
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    output_file = f"database_schema_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- =====================================================\n")
        f.write("-- FormBuilder Database Schema Export\n")
        f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("-- =====================================================\n\n")
        
        async with engine.connect() as conn:
            # 1. Exporter les tables
            f.write("\n-- =====================================================\n")
            f.write("-- TABLES\n")
            f.write("-- =====================================================\n\n")
            
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result]
            
            for table in tables:
                f.write(f"\n-- Table: {table}\n")
                
                # Obtenir la définition de la table
                result = await conn.execute(text(f"""
                    SELECT column_name, data_type, character_maximum_length, 
                           is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = :table_name
                    ORDER BY ordinal_position
                """), {"table_name": table})
                
                columns = []
                for row in result:
                    col_name, data_type, max_length, nullable, default = row
                    
                    col_def = f"  {col_name} "
                    
                    if data_type == 'character varying':
                        col_def += f"VARCHAR({max_length})" if max_length else "VARCHAR"
                    elif data_type == 'timestamp without time zone':
                        col_def += "TIMESTAMP"
                    elif data_type == 'USER-DEFINED':
                        col_def += "TEXT"  # Pour les ENUM
                    else:
                        col_def += data_type.upper()
                    
                    if nullable == 'NO':
                        col_def += " NOT NULL"
                    
                    if default:
                        col_def += f" DEFAULT {default}"
                    
                    columns.append(col_def)
                
                f.write(f"CREATE TABLE IF NOT EXISTS {table} (\n")
                f.write(",\n".join(columns))
                
                # Obtenir les contraintes
                result = await conn.execute(text(f"""
                    SELECT constraint_name, constraint_type
                    FROM information_schema.table_constraints
                    WHERE table_name = :table_name
                    AND constraint_type IN ('PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE')
                """), {"table_name": table})
                
                constraints = list(result)
                if constraints:
                    f.write(",\n")
                    for i, (constraint_name, constraint_type) in enumerate(constraints):
                        if constraint_type == 'PRIMARY KEY':
                            result2 = await conn.execute(text(f"""
                                SELECT column_name
                                FROM information_schema.key_column_usage
                                WHERE constraint_name = :constraint_name
                            """), {"constraint_name": constraint_name})
                            pk_columns = [row[0] for row in result2]
                            f.write(f"  PRIMARY KEY ({', '.join(pk_columns)})")
                            if i < len(constraints) - 1:
                                f.write(",\n")
                
                f.write("\n);\n\n")
            
            # 2. Exporter les index
            f.write("\n-- =====================================================\n")
            f.write("-- INDEXES\n")
            f.write("-- =====================================================\n\n")
            
            result = await conn.execute(text("""
                SELECT indexname, tablename, indexdef
                FROM pg_indexes
                WHERE schemaname = 'public'
                AND indexname NOT LIKE '%_pkey'
                ORDER BY tablename, indexname
            """))
            
            for index_name, table_name, index_def in result:
                f.write(f"-- Index on {table_name}\n")
                f.write(f"{index_def};\n\n")
            
            # 3. Statistiques des données
            f.write("\n-- =====================================================\n")
            f.write("-- DATA STATISTICS\n")
            f.write("-- =====================================================\n\n")
            
            for table in tables:
                result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                f.write(f"-- {table}: {count} rows\n")
            
            # 4. Exporter quelques données de référence (utilisateurs admin)
            f.write("\n\n-- =====================================================\n")
            f.write("-- SAMPLE DATA (Admin User)\n")
            f.write("-- =====================================================\n\n")
            
            if 'user' in tables or 'utilisateur' in tables:
                table_name = 'user' if 'user' in tables else 'utilisateur'
                try:
                    result = await conn.execute(text(f"""
                        SELECT email, username, role, actif
                        FROM {table_name}
                        WHERE role = 'ADMIN'
                        LIMIT 5
                    """))
                    
                    f.write("-- Admin users found:\n")
                    for email, username, role, actif in result:
                        f.write(f"--   Email: {email}, Username: {username}, Role: {role}, Active: {actif}\n")
                except Exception as e:
                    f.write(f"-- Could not fetch admin users: {str(e)}\n")
    
    print(f"\n✅ Schéma exporté avec succès dans: {output_file}")
    print(f"📊 {len(tables)} tables exportées")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(export_database_schema())
