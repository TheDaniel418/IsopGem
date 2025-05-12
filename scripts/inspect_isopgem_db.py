import os
import sqlite3


def inspect_db(db_path):
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"\nDatabase: {db_path}\n")

    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print("Tables:")
    for table in tables:
        print(f"  - {table}")
    print()

    # Show schema and sample data for each table
    for table in tables:
        print(f"Table: {table}")
        # Show schema
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        print("  Columns:")
        for col in columns:
            print(f"    - {col[1]} ({col[2]})")
        # Show row count
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        print(f"  Row count: {count}")
        # Show first 5 rows
        cursor.execute(f"SELECT * FROM {table} LIMIT 5;")
        rows = cursor.fetchall()
        if rows:
            print("  Sample rows:")
            for row in rows:
                print(f"    {row}")
        else:
            print("  No data.")
        print()
    conn.close()


if __name__ == "__main__":
    db_path = os.path.join(os.path.expanduser("~"), ".isopgem", "data", "ditrunes.db")
    output_path = os.path.join(os.path.dirname(__file__), "db_inspection_output.txt")
    import sys

    original_stdout = sys.stdout
    with open(output_path, "w") as f:
        sys.stdout = f
        inspect_db(db_path)
        # Print all 729 entries
        import sqlite3

        print("\nAll 729 entries in 'ditrunes':\n")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ditrunes ORDER BY decimal ASC;")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
        conn.close()
        sys.stdout = original_stdout
    print(f"Inspection complete. Output written to {output_path}")
