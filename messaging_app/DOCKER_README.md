# Messaging App - Docker Deployment

## Prerequisites
- Docker installed
- Docker Compose installed

## Quick Start

1. **Build and start services:**
```bash
   docker-compose up --build -d
```

2. **Check status:**
```bash
   docker-compose ps
```

3. **View logs:**
```bash
   docker-compose logs -f web
```

4. **Access the application:**
   - API: http://localhost:8000/api/v1/
   - Admin: http://localhost:8000/admin/

## Create Superuser
```bash
docker-compose exec web python manage.py createsuperuser
```

## Useful Commands

### Start/Stop Services
```bash
docker-compose up -d        # Start
docker-compose down         # Stop
docker-compose restart web  # Restart web service
```

### Database Operations
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create migrations
docker-compose exec web python manage.py makemigrations

# Access database
docker-compose exec db psql -U postgres -d messaging_app_db
```

### Logs
```bash
docker-compose logs -f web  # Web service logs
docker-compose logs -f db   # Database logs
docker-compose logs -f      # All logs
```

## Project Structure
```
messaging_app/
├── Dockerfile              # Docker image configuration
├── docker-compose.yml      # Multi-container setup
├── requirements.txt        # Python dependencies
├── .dockerignore          # Files to exclude from build
├── manage.py
├── messaging_app/
│   └── settings.py
└── chats/
```

## Environment Variables
Configured in docker-compose.yml:
- DB_HOST=db
- DB_NAME=messaging_app_db
- DB_USER=postgres
- DB_PASSWORD=Sxeteaact2p9
- DEBUG=True
- ALLOWED_HOSTS=*

## Troubleshooting

**Container won't start:**
```bash
docker-compose logs web
```

**Database connection issues:**
```bash
docker-compose logs db
docker-compose exec db pg_isready -U postgres
```

**Reset everything:**
```bash
docker-compose down -v
docker-compose up --build -d
```
