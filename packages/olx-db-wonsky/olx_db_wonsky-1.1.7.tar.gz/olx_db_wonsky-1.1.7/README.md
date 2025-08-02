# OLX Database Package

A Python package for OLX database models and migrations.

## Installation

```bash
pip install olx-db-wonsky
```

For development installation:

```bash
# Install package in development mode
pip install -e .

# Install development dependencies (including Alembic for migrations)
pip install -r requirements-dev.txt
```

## Configuration

The package uses environment variables for configuration:

- `OLX_DB_URL`: Database URL (required)
- `OLX_DEFAULT_SENDING_FREQUENCY_MINUTES`: Default sending frequency in minutes (default: 60)
- `OLX_DEFAULT_LAST_MINUTES_GETTING`: Default last minutes for getting items (default: 30)

You can set these environment variables directly or use a `.env` file.

## Usage

### Database Models

```python
from olx_db.db import get_db, MonitoringTask, ItemRecord

# Use the database session
with next(get_db()) as db:
    tasks = db.query(MonitoringTask).all()
    # ...
```

### Migrations

#### Local Development

For local development, use the provided script:

```bash
# Create a new migration
python scripts/run_migrations.py makemigrations "migration message"

# Apply migrations
python scripts/run_migrations.py migrate
```

#### Docker

To run migrations in Docker:

```bash
# Start the database and run migrations
docker-compose up migrations

# Or build and run locally
./scripts/build_and_run_local.sh
```

#### Building and Publishing Docker Image

To build and push the migrations Docker image to Docker Hub:

```bash
# Build and push for multiple architectures (amd64, arm64)
./scripts/build_and_push.sh
```

## Project Structure

```
├── alembic/                 # Alembic migrations
│   └── versions/            # Migration versions
├── olx_db/                  # Main package
│   └── db/                  # Database models and functions
├── scripts/                 # Utility scripts
│   ├── run_migrations.py    # Script to run migrations
│   ├── build_and_push.sh    # Script to build and push Docker image
│   └── build_and_run_local.sh # Script to build and run locally
├── alembic.ini              # Alembic configuration
├── docker-compose.yml       # Docker Compose configuration
├── migrations.Dockerfile    # Dockerfile for migrations
└── pyproject.toml           # Package configuration
```

## Docker Support

Example `docker-compose.yml`:

```yaml
version: '3'

services:
  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=myuser
      - POSTGRES_PASSWORD=mypassword
      - POSTGRES_DB=mydatabase
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  migrations:
    build:
      context: .
      dockerfile: migrations.Dockerfile
    environment:
      - OLX_DB_URL=postgresql://myuser:mypassword@db:5432/mydatabase
    depends_on:
      - db
    command: python /app/scripts/run_migrations.py migrate

volumes:
  postgres_data:
```
