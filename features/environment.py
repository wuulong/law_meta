
import psycopg2
import os

# --- Database Connection Settings ---
# It's recommended to use a dedicated test database for test isolation.
# These settings can be read from environment variables for flexibility across different environments.
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "test_law_db_agent")

def before_all(context):
    """Run once before all tests start."""
    context.db_params = {
        'host': DB_HOST,
        'port': DB_PORT,
        'user': DB_USER,
        'password': DB_PASSWORD,
        'dbname': DB_NAME
    }
    print(f"BDD tests starting, using database: {DB_NAME}")
    # You can check here if the database schema exists or run initialization scripts.

def before_scenario(context, scenario):
    """Run before each test scenario."""
    try:
        context.conn = psycopg2.connect(**context.db_params)
        context.cursor = context.conn.cursor()
    except psycopg2.Error as e:
        raise ConnectionError(f"Could not connect to the test database: {e}")

    # Clear relevant tables to ensure scenario independence.
    # The order of clearing is important due to foreign key constraints.
    tables_to_clear = [
        "legal_concepts",
        "law_hierarchy_relationships",
        "law_relationships",
        "articles",
        "laws"
    ]
    for table in tables_to_clear:
        try:
            # TRUNCATE ... RESTART IDENTITY CASCADE clears the table and resets sequences.
            context.cursor.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")
        except psycopg2.errors.UndefinedTable:
            # If the test schema doesn't contain a certain table, ignore the error.
            print(f"Warning: Table '{table}' does not exist, skipping truncation.")
            context.conn.rollback()  # Rollback the failed transaction
        except psycopg2.Error as e:
            print(f"Error: Failed to truncate table {table}: {e}")
            context.conn.rollback()

    context.conn.commit()

def after_scenario(context, scenario):
    """Run after each test scenario."""
    if hasattr(context, 'cursor') and context.cursor:
        context.cursor.close()
    if hasattr(context, 'conn') and context.conn:
        context.conn.close()
