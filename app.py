import psycopg2
from datetime import datetime

# -----------------------------
# DATABASE SETTINGS
# Change these to match your PG installation.
# -----------------------------
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "assignment3"   # YOUR DATABASE
DB_USER = "postgres"      # whatever you use to log in
DB_PASS = "channi123" # your PostgreSQL password
# -----------------------------


# This function opens a connection to PostgreSQL
def conn():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )


# CRUD FUNCTIONS

def getAllStudents():
    """Fetch and print all students from the table."""
    with conn() as c, c.cursor() as cur:
        cur.execute("""
            SELECT student_id, first_name, last_name, email, enrollment_date
            FROM students
            ORDER BY student_id;
        """)
        rows = cur.fetchall()

        if not rows:
            print("\n(no students found)\n")
            return

        print("\nID  | Name                | Email                     | Enrolled")
        print("-" * 70)
        for sid, first, last, email, edate in rows:
            name = f"{first} {last}"
            edate = edate.isoformat() if edate else ""
            print(f"{sid:<4}| {name:<19}| {email:<25}| {edate}")
        print()


def addStudent():
    """Ask user for student info and insert a new row."""
    print("\n-- Add Student --")
    first = input("First name: ").strip()
    last = input("Last name: ").strip()
    email = input("Email: ").strip()
    date_str = input("Enrollment date (YYYY-MM-DD or blank): ").strip()

    # Convert string to date object
    edate = None
    if date_str:
        try:
            edate = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format.\n")
            return

    with conn() as c, c.cursor() as cur:
        try:
            cur.execute("""
                INSERT INTO students (first_name, last_name, email, enrollment_date)
                VALUES (%s, %s, %s, %s)
                RETURNING student_id;
            """, (first, last, email, edate))

            new_id = cur.fetchone()[0]
            print(f"Student added with ID = {new_id}\n")

        except psycopg2.errors.UniqueViolation:
            # Happens if the email already exists
            c.rollback()
            print("Error: That email already exists.\n")


def updateStudentEmail():
    """Update only the email of a student."""
    print("\n-- Update Student Email --")
    try:
        sid = int(input("Student ID: ").strip())
    except ValueError:
        print("Invalid ID.\n")
        return

    new_email = input("New email: ").strip()

    with conn() as c, c.cursor() as cur:
        cur.execute("""
            UPDATE students
            SET email = %s
            WHERE student_id = %s;
        """, (new_email, sid))

        print(f"Rows updated: {cur.rowcount}\n")


def deleteStudent():
    """Delete a student by ID."""
    print("\n-- Delete Student --")
    try:
        sid = int(input("Student ID: ").strip())
    except ValueError:
        print("Invalid ID.\n")
        return

    with conn() as c, c.cursor() as cur:
        cur.execute("""
            DELETE FROM students
            WHERE student_id = %s;
        """, (sid,))
        print(f"Rows deleted: {cur.rowcount}\n")


# Menu functionality

MENU = """
Choose an action:
  1) List all students
  2) Add a student
  3) Update a student's email
  4) Delete a student
  5) Quit
> """

# terminal interface
def main():
    print("PostgreSQL Students CLI")

    # Continues until user chooses Quit
    while True:
        choice = input(MENU).strip()

        if choice == "1":
            getAllStudents()
        elif choice == "2":
            addStudent()
        elif choice == "3":
            updateStudentEmail()
        elif choice == "4":
            deleteStudent()
        elif choice in ("5", "q", "quit", "exit"):
            print("Goodbye!")
            break
        else:
            print("Invalid choice.\n")


if __name__ == "__main__":
    main()
