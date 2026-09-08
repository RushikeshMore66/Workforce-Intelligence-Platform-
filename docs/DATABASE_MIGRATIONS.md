# Database Migrations

This project uses [Alembic](https://alembic.sqlalchemy.org/) alongside SQLAlchemy for database schema migrations. 

## 1. Migration Architecture
- The database schema is defined entirely in the SQLAlchemy ORM models (found in `app.models`).
- Alembic tracks these models and generates migration scripts that can safely update the PostgreSQL schema.
- **Application Startup**: The application deliberately **does not** automatically create tables on startup (e.g. `Base.metadata.create_all()`). Alembic owns schema management to ensure safe rollbacks and evolution in production environments.

## 2. How to Create a Migration
After you modify a SQLAlchemy model, you must generate a migration script:
```bash
alembic revision --autogenerate -m "Add description of your changes here"
```
*Note: Always review the generated script in `migrations/versions/` to verify it accurately reflects your intended schema changes.*

## 3. How to Upgrade
To apply pending migrations to your database:
```bash
alembic upgrade head
```

## 4. How to Downgrade
To revert the last applied migration:
```bash
alembic downgrade -1
```
To revert all migrations (useful for development):
```bash
alembic downgrade base
```

## 5. How to Check Migration Status
To see the currently applied migration revision:
```bash
alembic current
```
To view all available migration heads:
```bash
alembic heads
```
To view the full history of migrations:
```bash
alembic history
```

## 6. Fresh Database Setup
For a completely new installation:
1. Ensure your `.env` contains the correct `DATABASE_URL`.
2. Run `alembic upgrade head`.

## 7. Existing Database Handling
If you have an existing development database that was created previously using `Base.metadata.create_all()`, it lacks the `alembic_version` table.
- **Option A (Recommended for local dev):** Drop the existing database, create a fresh one, and run `alembic upgrade head`.
- **Option B (Data retention needed):** Manually stamp the database with the initial migration revision using:
  ```bash
  alembic stamp head
  ```
  *(Only do this if you are absolutely certain the existing schema perfectly matches the models.)*

## 8. Production Deployment Migration Process
During a production deployment, run `alembic upgrade head` after updating the application code but before starting the new application instances. This should be integrated into your CI/CD pipeline.

## 9. Why Application Startup Does Not Use create_all()
Using `create_all()` silently applies schema creation but fails to manage modifications (like adding columns or changing types). By removing it, we enforce that Alembic is the single source of truth for schema state, ensuring predictable, trackable, and safe migrations across environments.
