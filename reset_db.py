import psycopg2
import pandas as pd

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
            id INTEGER PRIMARY KEY,
            email VARCHAR(255) NOT NULL,
            role VARCHAR(255) NOT NULL,
            password_salt VARCHAR(255) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL
        )
    """)

    cur.execute("INSERT INTO users (id, email, role, password_salt, password_hash, first_name, last_name) VALUES (1, 'admin@admin.com', 'admin', 'admin', 'admin', 'Admin', 'Admin')")

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
    
    student_data = pd.read_excel('data/Community Service Hours by Class.xlsx', sheet_name=None)
    
    for sheet in student_data:
        for index, row in student_data[sheet].iterrows():
            row_lower = {col.lower(): val for col, val in row.items()}
            # password is the same as the email
            if pd.notna(row_lower['user id']) and row_lower['user id']:
                # this user is listed twice
                if row_lower['user id'] == 4834445 and sheet == '2028':
                    continue
                else:
                    cur.execute("INSERT INTO users (id, email, role, password_salt, password_hash, first_name, last_name) VALUES (%s, %s, %s, %s, %s, %s, %s)", (int(row_lower['user id']), row_lower['email'], 'student', row_lower['email'], row_lower['email'], row_lower['first name'], row_lower['last name']))
                    cur.execute("INSERT INTO students (user_id, graduation_year, in_school_hours, out_of_school_hours, required_hours) VALUES (%s, %s, %s, %s, %s)", (int(row_lower['user id']), int(row_lower['yog']), row_lower['at dxsf hours'], row_lower['outside dxsf hrs'], row_lower['hours required']))


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
            is_in_school BOOLEAN NOT NULL,
            status VARCHAR(255) NOT NULL
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    init_db()
