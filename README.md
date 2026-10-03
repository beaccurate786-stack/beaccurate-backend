# AI Attendance System development environment

This repository provides a Docker-based Django, Django REST Framework, and MySQL 8.0 development environment. It intentionally does not add attendance, authentication, API, database-model, or AI features.

## Start the environment

1. Copy `.env.example` to `.env` if the file is absent, then set safe local development passwords and a Django secret key.
2. Build and start the services:

   ```powershell
   docker compose up --build
   ```

3. Apply the standard Django migrations in a second terminal:

   ```powershell
   docker compose exec web python manage.py migrate
   ```

Django is available at http://localhost:8000. Confirm its configuration with `docker compose exec web python manage.py check`.

## Database connection

The Django container connects to MySQL at `db:3306`, where `db` is the Docker Compose service name. `localhost` would refer to the Django container itself, so it must not be used as the database host inside Docker. Credentials and database settings come only from `.env`.

To open a MySQL shell:

```powershell
docker compose exec db mysql -u attendance_user -p ai_attendance_db
```

## Daily commands

```powershell
docker compose up
docker compose down
docker compose logs
docker compose logs web
docker compose logs db
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

`mysql_data` is a named Docker volume, so `docker compose down` preserves database data. Do not use `docker compose down -v` unless you intentionally want to delete the local database volume.
