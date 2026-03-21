from werkzeug.security import generate_password_hash
from db import get_db_connection


def seed_admin(name, email, password, pincode, role="SUPER_ADMIN"):
    hashed_pw = generate_password_hash(password)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT admin_id FROM SUPER_ADMIN WHERE email = %s", (email,))
    existing = cur.fetchone()
    if existing:
        print("Admin already exists")
        cur.close()
        conn.close()
        return

    cur.execute(
        "INSERT INTO SUPER_ADMIN (name, email, password, role, pincode) VALUES (%s, %s, %s, %s, %s)",
        (name, email, hashed_pw, role, pincode),
    )
    conn.commit()
    print("Admin created")
    cur.close()
    conn.close()


if __name__ == "__main__":
    name = input("Admin name: ").strip()
    email = input("Admin email: ").strip()
    password = input("Admin password: ").strip()
    pincode = input("Admin pincode: ").strip()
    seed_admin(name, email, password, pincode)
