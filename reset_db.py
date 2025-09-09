import psycopg2

def init_db():

    conn = psycopg2.connect(
        host="localhost",
        database="app_db",
        user="postgres",
        password="password"
    )

    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS users CASCADE")
    cur.execute("DROP TABLE IF EXISTS students CASCADE")
    cur.execute("DROP TABLE IF EXISTS service_records CASCADE")
    cur.execute("DROP TABLE IF EXISTS events CASCADE")

    cur.execute("""
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) NOT NULL,
            role VARCHAR(255) NOT NULL,
            password_salt VARCHAR(255) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL
        )
    """)

    cur.execute("INSERT INTO users (email, role, password_salt, password_hash, first_name, last_name) VALUES ('admin@admin.com', 'admin', 'admin', 'admin', 'Admin', 'Admin')")

    cur.execute("""
        CREATE TABLE students (
            user_id INTEGER PRIMARY KEY,
            graduation_year INTEGER NOT NULL,
            in_school_hours INTEGER NOT NULL,
            out_of_school_hours INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cur.execute("""
        CREATE TABLE service_records (
            id SERIAL PRIMARY KEY,
            student_id INTEGER NOT NULL,
            date DATE NOT NULL,
            organization_name VARCHAR(255) NOT NULL,
            contact_name VARCHAR(255) NOT NULL,
            contact_email VARCHAR(255) NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(user_id)
        )
    """)

    cur.execute("""
        CREATE TABLE events (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            date DATE NOT NULL,
            description VARCHAR(255) NOT NULL,
            proof_of_service VARCHAR(255) NOT NULL,
            hours INTEGER NOT NULL,
            contact_name VARCHAR(255) NOT NULL,
            contact_email VARCHAR(255) NOT NULL,
            all_students INTEGER[] NOT NULL
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    init_db()