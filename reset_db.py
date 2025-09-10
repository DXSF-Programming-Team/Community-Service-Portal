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
    cur.execute("INSERT INTO users (email, role, password_salt, password_hash, first_name, last_name) VALUES ('27mortry@dextersouthfield.org', 'student', 'ryry', 'ryry', 'Ryder', 'Morton')")

    cur.execute("""
        CREATE TABLE students (
            user_id INTEGER PRIMARY KEY,
            graduation_year INTEGER NOT NULL,
            in_school_hours INTEGER NOT NULL,
            out_of_school_hours INTEGER NOT NULL,
            required_hours INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cur.execute("INSERT INTO students (user_id, graduation_year, in_school_hours, out_of_school_hours, required_hours) VALUES (2, 2027, 0, 0, 40)")

    cur.execute("""
        CREATE TABLE service_records (
            id SERIAL PRIMARY KEY,
            student_id INTEGER NOT NULL,
            dates TEXT[] NOT NULL,
            organization_name VARCHAR(255) NOT NULL,
            event_name VARCHAR(255) NOT NULL,
            contact_name VARCHAR(255) NOT NULL,
            contact_email VARCHAR(255) NOT NULL,
            hours INTEGER NOT NULL,
            description VARCHAR(255) NOT NULL,
            proof_of_service VARCHAR(255) NOT NULL,
            is_in_school BOOLEAN NOT NULL,
            status VARCHAR(255) NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(user_id)
        )
    """)

    cur.execute("""
        CREATE TABLE events (
            id SERIAL PRIMARY KEY,
            creator_name VARCHAR(255) NOT NULL,
            creator_email VARCHAR(255) NOT NULL,
            dates TEXT[] NOT NULL,
            organization_name VARCHAR(255) NOT NULL,
            event_name VARCHAR(255) NOT NULL,
            location VARCHAR(255) NOT NULL,
            contact_name VARCHAR(255) NOT NULL,
            contact_email VARCHAR(255) NOT NULL,
            hours_offered INTEGER NOT NULL,
            description VARCHAR(255) NOT NULL,
            is_in_school BOOLEAN NOT NULL
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    init_db()