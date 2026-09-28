# Tienda API

## Ejecutar con Docker
                                        
1. Copia `.env.example` a `.env`.
2. Cambia `POSTGRES_PASSWORD` y, si vas a subir imágenes, configura `CLOUDINARY_URL` con las credenciales de tu cuenta.
3. Ejecuta `docker compose up --build`.

La API estará disponible en `http://localhost:8000` y la documentación interactiva en `http://localhost:8000/docs`. Al iniciar, el contenedor aplica las migraciones de Alembic. PostgreSQL conserva sus datos en el volumen `postgres_data`.

La contraseña predeterminada es solo para desarrollo local; cámbiala antes de cualquier despliegue.

Para detener los contenedores, ejecuta `docker compose down`. Para borrar también los datos de PostgreSQL, ejecuta `docker compose down -v`.
