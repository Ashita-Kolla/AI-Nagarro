import sqlite3

def delete_table(db_path, table_name):
    # Establish connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Run the SQL DROP TABLE command
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    
    # Commit changes and close
    conn.commit()
    conn.close()
    print(f"Table '{table_name}' has been deleted!")

# Example usage (assuming your DB is in the same directory as this script)
delete_table("trixie_wellness.db", "mood_logs")
delete_table("trixie_wellness.db", "journal_metadata")
delete_table("trixie_wellness.db", "reminders")
delete_table("trixie_wellness.db", "reminder_history")
