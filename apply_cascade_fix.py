"""
Script para aplicar las restricciones CASCADE en la base de datos PostgreSQL
Ejecutar con: python apply_cascade_fix.py
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def apply_cascade_fix():
    """Aplica las restricciones CASCADE en la base de datos"""
    
    print("🔧 Iniciando aplicación de restricciones CASCADE...")
    
    # Obtener URL de la base de datos
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ Error: DATABASE_URL no está configurada en el archivo .env")
        print("   Por favor, configura DATABASE_URL en tu archivo .env")
        return False
    
    # Render usa postgres:// pero SQLAlchemy necesita postgresql+psycopg2://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
    
    print(f"📍 Conectando a base de datos...")
    
    try:
        # Crear engine
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Iniciar transacción
            trans = conn.begin()
            
            try:
                print("\n📋 Paso 1: Actualizando restricciones de pet_photos...")
                conn.execute(text("""
                    ALTER TABLE petcare.pet_photos 
                    DROP CONSTRAINT IF EXISTS pet_photos_pet_id_fkey;
                """))
                conn.execute(text("""
                    ALTER TABLE petcare.pet_photos 
                    ADD CONSTRAINT pet_photos_pet_id_fkey 
                    FOREIGN KEY (pet_id) 
                    REFERENCES petcare.pets(id) 
                    ON DELETE CASCADE;
                """))
                print("   ✅ pet_photos actualizado")
                
                print("\n📋 Paso 2: Actualizando restricciones de vaccinations...")
                conn.execute(text("""
                    ALTER TABLE petcare.vaccinations 
                    DROP CONSTRAINT IF EXISTS vaccinations_pet_id_fkey;
                """))
                conn.execute(text("""
                    ALTER TABLE petcare.vaccinations 
                    ADD CONSTRAINT vaccinations_pet_id_fkey 
                    FOREIGN KEY (pet_id) 
                    REFERENCES petcare.pets(id) 
                    ON DELETE CASCADE;
                """))
                print("   ✅ vaccinations actualizado")
                
                print("\n📋 Paso 3: Actualizando restricciones de dewormings...")
                conn.execute(text("""
                    ALTER TABLE petcare.dewormings 
                    DROP CONSTRAINT IF EXISTS dewormings_pet_id_fkey;
                """))
                conn.execute(text("""
                    ALTER TABLE petcare.dewormings 
                    ADD CONSTRAINT dewormings_pet_id_fkey 
                    FOREIGN KEY (pet_id) 
                    REFERENCES petcare.pets(id) 
                    ON DELETE CASCADE;
                """))
                print("   ✅ dewormings actualizado")
                
                print("\n📋 Paso 4: Actualizando restricciones de vet_visits...")
                conn.execute(text("""
                    ALTER TABLE petcare.vet_visits 
                    DROP CONSTRAINT IF EXISTS vet_visits_pet_id_fkey;
                """))
                conn.execute(text("""
                    ALTER TABLE petcare.vet_visits 
                    ADD CONSTRAINT vet_visits_pet_id_fkey 
                    FOREIGN KEY (pet_id) 
                    REFERENCES petcare.pets(id) 
                    ON DELETE CASCADE;
                """))
                print("   ✅ vet_visits actualizado")
                
                print("\n📋 Paso 5: Actualizando restricciones de nutrition_plans...")
                conn.execute(text("""
                    ALTER TABLE petcare.nutrition_plans 
                    DROP CONSTRAINT IF EXISTS nutrition_plans_pet_id_fkey;
                """))
                conn.execute(text("""
                    ALTER TABLE petcare.nutrition_plans 
                    ADD CONSTRAINT nutrition_plans_pet_id_fkey 
                    FOREIGN KEY (pet_id) 
                    REFERENCES petcare.pets(id) 
                    ON DELETE CASCADE;
                """))
                print("   ✅ nutrition_plans actualizado")
                
                print("\n📋 Paso 6: Actualizando restricciones de meals...")
                conn.execute(text("""
                    ALTER TABLE petcare.meals 
                    DROP CONSTRAINT IF EXISTS meals_pet_id_fkey;
                """))
                conn.execute(text("""
                    ALTER TABLE petcare.meals 
                    ADD CONSTRAINT meals_pet_id_fkey 
                    FOREIGN KEY (pet_id) 
                    REFERENCES petcare.pets(id) 
                    ON DELETE CASCADE;
                """))
                print("   ✅ meals actualizado")
                
                print("\n📋 Paso 7: Actualizando restricciones de reminders...")
                conn.execute(text("""
                    ALTER TABLE petcare.reminders 
                    DROP CONSTRAINT IF EXISTS reminders_pet_id_fkey;
                """))
                conn.execute(text("""
                    ALTER TABLE petcare.reminders 
                    ADD CONSTRAINT reminders_pet_id_fkey 
                    FOREIGN KEY (pet_id) 
                    REFERENCES petcare.pets(id) 
                    ON DELETE CASCADE;
                """))
                print("   ✅ reminders actualizado")
                
                print("\n📋 Paso 8: Actualizando restricciones de notifications...")
                conn.execute(text("""
                    ALTER TABLE petcare.notifications 
                    DROP CONSTRAINT IF EXISTS notifications_pet_id_fkey;
                """))
                conn.execute(text("""
                    ALTER TABLE petcare.notifications 
                    ADD CONSTRAINT notifications_pet_id_fkey 
                    FOREIGN KEY (pet_id) 
                    REFERENCES petcare.pets(id) 
                    ON DELETE CASCADE;
                """))
                print("   ✅ notifications actualizado")
                
                print("\n📋 Paso 9: Limpiando registros corruptos...")
                
                # Limpiar vacunaciones corruptas
                result = conn.execute(text("DELETE FROM petcare.vaccinations WHERE pet_id IS NULL;"))
                print(f"   ✅ Eliminadas {result.rowcount} vacunaciones corruptas")
                
                # Limpiar desparasitaciones corruptas
                result = conn.execute(text("DELETE FROM petcare.dewormings WHERE pet_id IS NULL;"))
                print(f"   ✅ Eliminadas {result.rowcount} desparasitaciones corruptas")
                
                # Limpiar visitas veterinarias corruptas
                result = conn.execute(text("DELETE FROM petcare.vet_visits WHERE pet_id IS NULL;"))
                print(f"   ✅ Eliminadas {result.rowcount} visitas veterinarias corruptas")
                
                # Limpiar comidas corruptas
                result = conn.execute(text("DELETE FROM petcare.meals WHERE pet_id IS NULL;"))
                print(f"   ✅ Eliminadas {result.rowcount} comidas corruptas")
                
                # Limpiar planes de nutrición corruptos
                result = conn.execute(text("DELETE FROM petcare.nutrition_plans WHERE pet_id IS NULL;"))
                print(f"   ✅ Eliminadas {result.rowcount} planes de nutrición corruptos")
                
                # Limpiar notificaciones corruptas
                result = conn.execute(text("DELETE FROM petcare.notifications WHERE pet_id IS NULL;"))
                print(f"   ✅ Eliminadas {result.rowcount} notificaciones corruptas")
                
                # Commit todas las transacciones
                trans.commit()
                
                print("\n✅ ¡Todas las restricciones CASCADE se aplicaron correctamente!")
                print("\n📊 Verificando restricciones aplicadas...")
                
                # Verificar restricciones
                result = conn.execute(text("""
                    SELECT 
                        tc.table_name, 
                        tc.constraint_name, 
                        rc.delete_rule
                    FROM 
                        information_schema.table_constraints AS tc 
                        JOIN information_schema.referential_constraints AS rc 
                            ON tc.constraint_name = rc.constraint_name
                    WHERE 
                        tc.table_schema = 'petcare'
                        AND tc.constraint_type = 'FOREIGN KEY'
                        AND rc.unique_constraint_name IN (
                            SELECT constraint_name 
                            FROM information_schema.table_constraints 
                            WHERE table_schema = 'petcare' 
                            AND table_name = 'pets' 
                            AND constraint_type = 'PRIMARY KEY'
                        )
                    ORDER BY tc.table_name, tc.constraint_name;
                """))
                
                print("\n📋 Restricciones aplicadas:")
                for row in result:
                    print(f"   ✅ {row[0]}.{row[1]} -> DELETE {row[2]}")
                
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"\n❌ Error durante la aplicación: {str(e)}")
                print("   Se hizo rollback de todos los cambios")
                return False
                
    except Exception as e:
        print(f"\n❌ Error conectando a la base de datos: {str(e)}")
        print("\n💡 Verifica que:")
        print("   1. DATABASE_URL esté correctamente configurada en .env")
        print("   2. La base de datos esté accesible")
        print("   3. Tengas permisos para modificar las restricciones")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 Script de Aplicación de Restricciones CASCADE")
    print("=" * 60)
    print("\n⚠️  IMPORTANTE: Este script modificará las restricciones de tu base de datos")
    print("   Asegúrate de tener un backup antes de continuar\n")
    
    respuesta = input("¿Deseas continuar? (s/n): ")
    if respuesta.lower() != 's':
        print("❌ Operación cancelada")
        exit(0)
    
    success = apply_cascade_fix()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ ¡Proceso completado exitosamente!")
        print("=" * 60)
        print("\n💡 Ahora puedes eliminar mascotas y todos sus registros")
        print("   relacionados se eliminarán automáticamente en cascada.")
    else:
        print("\n" + "=" * 60)
        print("❌ El proceso falló. Revisa los errores arriba.")
        print("=" * 60)

