import psycopg2
import pandas as pd
import os

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

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir('data')

    student_data = pd.read_excel('Community Service Hours by Class.xlsx', sheet_name=None)
    
    for sheet in student_data:
        for _, row in student_data[sheet].iterrows():
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

    os.chdir('c2026 Comm Svs by Student')
    for file in os.listdir():
        if file.endswith('.xlsx'):
            df = pd.read_excel(file)
            # Get student info from first row only
            first_row = df.iloc[0]
            student_id = None
            try:
                # First, let's see what columns are actually in the dataframe
                print(f"Available columns: {list(first_row.index)}")
                
                # Try to find the student
                cur.execute("SELECT id FROM users WHERE last_name = %s AND first_name = %s", (first_row['Last name'], first_row['Preferred Name']))
                result = cur.fetchone()
                if result:
                    student_id = result[0]
                    first_name = first_row['Preferred Name']
                    last_name = first_row['Last name']
                    graduation_year = first_row['Class Yr']
                    print(f"Found student {last_name}, {first_name} ({graduation_year}) with ID: {student_id}")
                else:
                    print(f"Student {last_name}, {first_name} ({graduation_year}) not found in database")
                    continue
            except Exception as e:
                print(f"Error finding student {first_row['Last name']}, {first_row['Preferred Name']}: {e}")
                continue
            
            # Process all rows for this student
            for index, row in df.iterrows():
                row_lower = {col.lower(): val for col, val in row.items()}
                if student_id is not None:
                    contact_name = 'N/A'
                    contact_email = 'N/A'
                    description = 'N/A'
                    proof_of_service = 'N/A'
                    act_desc = row_lower['activity_description']
                    
                    # Handle missing or non-string activity descriptions
                    if pd.isna(act_desc) or not isinstance(act_desc, str):
                        continue
                    elif "Total Hours" in act_desc:
                        break
                    elif "," in act_desc:
                        # some descriptions have a comma separating event name and dates
                        event_name = act_desc.split(",", maxsplit=1)[0].strip()
                        dates = [act_desc.split(",", maxsplit=1)[1].strip()]
                    elif "/" in act_desc:
                        # some descriptions have no comma, so we use the first month/day/year formatted date
                        first_slash = act_desc.index("/")
                        next_slash = act_desc.index("/", first_slash + 1)
                        date_str = act_desc[(first_slash - 2):(next_slash + 3)].strip()
                        dates = [date_str]
                        event_name = act_desc.split(date_str)[0].strip()
                    else:
                        # some dates are not in month/day/year format, in which case we will just use the academic year (AY)
                        event_name = act_desc.strip()
                        print(f"Event name: {event_name}")
                        try:
                            dates = [str(int(row_lower['academic \nyear']))]
                        except:
                            dates = ['N/A']
                    if not pd.isna(row_lower['outside dxsf hrs']):
                        organization_name = 'N/A'                        
                        hours = row_lower['outside dxsf hrs']
                        is_in_school = False
                    elif not pd.isna(row_lower['at dxsf hours']):
                        organization_name = 'Dexter Southfield'
                        hours = row_lower['at dxsf hours']
                        is_in_school = True
                    else:
                        continue
                    try:
                        cur.execute("INSERT INTO service_records (student_id, dates, organization_name, event_name, contact_name, contact_email, hours, description, proof_of_service, is_in_school, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (student_id, dates, organization_name, event_name, contact_name, contact_email, hours, description, proof_of_service, is_in_school, 'approved'))
                        print(f"Inserted service record for {last_name}, {first_name} ({graduation_year}). {student_id} {dates} {organization_name} {event_name} {contact_name} {contact_email} {hours} {description} {proof_of_service} {is_in_school}")
                    except Exception as e:
                        print(f"Error inserting service record for {last_name}, {first_name} ({graduation_year}): {e}")
                        continue
                else:
                    print(f"Index {index}: Student {row_lower['last name']}, {row_lower['preferred name']} ({row_lower['class yr']}) not found")


    cur.execute("""
        CREATE TABLE events (
            id SERIAL PRIMARY KEY,
            creator_id INTEGER NOT NULL,
            FOREIGN KEY (creator_id) REFERENCES users(id),
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
