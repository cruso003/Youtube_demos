# PostgreSQL Migration Plan for Universal AI Platform

## 1. Install PostgreSQL and Python Dependencies
- Install PostgreSQL server (if not already running)
- Install `psycopg2` or `asyncpg` (for async), and `SQLAlchemy` for ORM support:
  ```sh
  pip install sqlalchemy psycopg2-binary
  ```

## 2. Database Schema Design
- Tables: `users`, `api_keys`, `credit_transactions`
- Example schema (to be implemented in SQLAlchemy models):

### users
- id (UUID, primary key)
- email (unique)
- name
- created_at
- updated_at

### api_keys
- id (UUID, primary key)
- user_id (foreign key to users)
- api_key (unique, string)
- created_at
- revoked (boolean)

### credit_transactions
- id (UUID, primary key)
- user_id (foreign key to users)
- credits (int)
- amount_usd (float)
- transaction_id (unique, string)
- description
- created_at

## 3. Update Backend Code
- Replace SQLite logic with SQLAlchemy models and PostgreSQL connection.
- Refactor credit, user, and API key management to use new models.
- Implement API key generation and assignment after $5+ purchase.

## 4. Migration Scripts
- Use Alembic for migrations:
  ```sh
  pip install alembic
  alembic init alembic
  # Edit alembic.ini and env.py for PostgreSQL
  # Create and apply migration scripts
  ```

## 5. Environment Variables
- Add `DATABASE_URL` for PostgreSQL connection string.

## 6. Test and Deploy
- Test all endpoints and payment flows.
- Deploy with PostgreSQL in production.

---

**Next step:**
- Scaffold SQLAlchemy models and update the backend to use PostgreSQL.
