from db import get_db_connection


def seed_admin(name, email, password, pincode, city_id=None, role="SUPER_ADMIN"):
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
        "INSERT INTO SUPER_ADMIN (name, email, password, role, pincode, city_id) VALUES (%s, %s, %s, %s, %s, %s)",
        (name, email, password, role, pincode, city_id),
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
    city_id_input = input("Admin city_id (optional): ").strip()
    city_id = int(city_id_input) if city_id_input.isdigit() else None
    seed_admin(name, email, password, pincode, city_id)
