import os
from datetime import datetime, timedelta

import jwt
from flask import Flask, jsonify, request
from flask_cors import CORS
from mysql.connector import Error
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from config import JWT_EXPIRES_DAYS, JWT_SECRET, UPLOAD_DIR
from db import get_db_connection

app = Flask(__name__)
CORS(app)

os.makedirs(UPLOAD_DIR, exist_ok=True)


# -----------------------------
# Helpers
# -----------------------------

def create_token(user_id, role):
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRES_DAYS),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def auth_required(roles=None):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify({"error": "Missing token"}), 401

            token = auth_header.replace("Bearer ", "", 1).strip()
            try:
                payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401

            sub_value = payload.get("sub")
            if isinstance(sub_value, str) and sub_value.isdigit():
                payload["sub"] = int(sub_value)

            if roles and payload.get("role") not in roles:
                return jsonify({"error": "Forbidden"}), 403

            request.user = payload
            return fn(*args, **kwargs)

        wrapper.__name__ = fn.__name__
        return wrapper

    return decorator


# -----------------------------
# Health
# -----------------------------

@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


# -----------------------------
# Auth
# -----------------------------

@app.post("/auth/customer/register")
def customer_register():
    data = request.get_json(silent=True) or {}
    required = ["first_name", "last_name", "email", "phone", "password", "street", "pincode", "city_id"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing fields"}), 400

    hashed_pw = generate_password_hash(data["password"])
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO CUSTOMER
            (first_name, last_name, email, phone, password, street, pincode, city_id)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                data["first_name"],
                data["last_name"],
                data["email"],
                data["phone"],
                hashed_pw,
                data["street"],
                data["pincode"],
                data["city_id"],
            ),
        )
        conn.commit()
        customer_id = cur.lastrowid
        token = create_token(customer_id, "customer")
        return jsonify({"customer_id": customer_id, "token": token}), 201
    except Error as exc:
        if "Duplicate entry" in str(exc):
            return jsonify({"error": "Email already exists"}), 409
        return jsonify({"error": "DB error"}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.post("/auth/customer/login")
def customer_login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM CUSTOMER WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_token(user["customer_id"], "customer")
    user.pop("password", None)
    return jsonify({"customer": user, "token": token}), 200


@app.post("/auth/pharmacy/register")
def pharmacy_register():
    data = request.get_json(silent=True) or {}
    required = ["pharmacy_name", "license_number", "email", "phone", "password", "street", "pincode", "city_id"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing fields"}), 400

    hashed_pw = generate_password_hash(data["password"])
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO PHARMACY
            (pharmacy_name, license_number, email, phone, password, street, pincode, city_id)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                data["pharmacy_name"],
                data["license_number"],
                data["email"],
                data["phone"],
                hashed_pw,
                data["street"],
                data["pincode"],
                data["city_id"],
            ),
        )
        conn.commit()
        pharmacy_id = cur.lastrowid
        token = create_token(pharmacy_id, "pharmacy")
        return jsonify({"pharmacy_id": pharmacy_id, "approval_status": "PENDING", "token": token}), 201
    except Error as exc:
        if "Duplicate entry" in str(exc):
            return jsonify({"error": "Email already exists"}), 409
        return jsonify({"error": "DB error"}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.post("/auth/pharmacy/login")
def pharmacy_login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM PHARMACY WHERE email = %s", (email,))
    pharmacy = cur.fetchone()
    cur.close()
    conn.close()

    if not pharmacy or not check_password_hash(pharmacy["password"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    if pharmacy["approval_status"] != "APPROVED":
        return jsonify({"error": "Pharmacy not approved"}), 403

    token = create_token(pharmacy["pharmacy_id"], "pharmacy")
    pharmacy.pop("password", None)
    return jsonify({"pharmacy": pharmacy, "token": token}), 200


@app.post("/auth/admin/login")
def admin_login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM SUPER_ADMIN WHERE email = %s", (email,))
    admin = cur.fetchone()
    cur.close()
    conn.close()

    if not admin or not check_password_hash(admin["password"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_token(admin["admin_id"], "admin")
    admin.pop("password", None)
    return jsonify({"admin": admin, "token": token}), 200


# -----------------------------
# Customer: Search
# -----------------------------

@app.get("/medicines/search")
def search_medicines():
    name = request.args.get("name", "").strip()
    category = request.args.get("category", "").strip()
    city_id = request.args.get("city_id")
    pincode = request.args.get("pincode")

    query = (
        "SELECT m.medicine_id, m.medicine_name, m.category, m.description, m.manufacturer, m.batch_no, m.mfg_date, "
        "m.price, m.stock_quantity, m.expiry_date, m.requires_prescription, p.pharmacy_id, p.pharmacy_name, "
        "p.street, p.pincode, "
        "c.city_name, c.state "
        "FROM MEDICINE m "
        "JOIN PHARMACY p ON m.pharmacy_id = p.pharmacy_id "
        "JOIN CITY c ON p.city_id = c.city_id "
        "WHERE p.approval_status = 'APPROVED' AND m.stock_quantity > 0"
    )
    params = []

    if name:
        query += " AND m.medicine_name LIKE %s"
        params.append(f"%{name}%")
    if category:
        query += " AND m.category = %s"
        params.append(category)
    if city_id:
        query += " AND c.city_id = %s"
        params.append(city_id)
    if pincode:
        query += " AND p.pincode = %s"
        params.append(pincode)

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify({"results": rows}), 200


# -----------------------------
# Customer: Orders + Prescriptions
# -----------------------------

@app.post("/orders")
@auth_required(roles=["customer"])
def place_order():
    data = request.get_json(silent=True) or {}
    customer_id = request.user.get("sub")
    pharmacy_id = data.get("pharmacy_id")
    items = data.get("items", [])
    prescription_id = data.get("prescription_id")

    if not pharmacy_id or not items:
        return jsonify({"error": "Missing pharmacy or items"}), 400

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT approval_status FROM PHARMACY WHERE pharmacy_id = %s", (pharmacy_id,))
    pharmacy = cur.fetchone()
    if not pharmacy or pharmacy["approval_status"] != "APPROVED":
        cur.close()
        conn.close()
        return jsonify({"error": "Pharmacy not approved"}), 403

    medicine_ids = [item.get("medicine_id") for item in items]
    if any(mid is None for mid in medicine_ids):
        cur.close()
        conn.close()
        return jsonify({"error": "Invalid medicine items"}), 400

    placeholders = ",".join(["%s"] * len(medicine_ids))
    cur.execute(
        f"SELECT medicine_id, price, stock_quantity, requires_prescription FROM MEDICINE WHERE medicine_id IN ({placeholders}) AND pharmacy_id = %s",
        tuple(medicine_ids) + (pharmacy_id,),
    )
    meds = cur.fetchall()

    if len(meds) != len(medicine_ids):
        cur.close()
        conn.close()
        return jsonify({"error": "Medicine not found for this pharmacy"}), 400

    requires_rx = any(m["requires_prescription"] for m in meds)
    if requires_rx and not prescription_id:
        cur.close()
        conn.close()
        return jsonify({"error": "Prescription required"}), 400

    med_lookup = {m["medicine_id"]: m for m in meds}

    try:
        cur.execute(
            "INSERT INTO ORDERS (customer_id, pharmacy_id) VALUES (%s, %s)",
            (customer_id, pharmacy_id),
        )
        order_id = cur.lastrowid

        for item in items:
            med_id = item.get("medicine_id")
            qty = int(item.get("quantity", 0))
            if qty <= 0:
                raise ValueError("Invalid quantity")

            med = med_lookup[med_id]
            if med["stock_quantity"] < qty:
                raise ValueError("Insufficient stock")

            subtotal = float(med["price"]) * qty
            cur.execute(
                "INSERT INTO ORDER_ITEM (order_id, medicine_id, quantity, subtotal) VALUES (%s, %s, %s, %s)",
                (order_id, med_id, qty, subtotal),
            )
            cur.execute(
                "UPDATE MEDICINE SET stock_quantity = stock_quantity - %s WHERE medicine_id = %s AND stock_quantity >= %s",
                (qty, med_id, qty),
            )
            if cur.rowcount == 0:
                raise ValueError("Insufficient stock")

        if prescription_id:
            cur.execute(
                "UPDATE PRESCRIPTION SET order_id = %s WHERE prescription_id = %s AND customer_id = %s",
                (order_id, prescription_id, customer_id),
            )

        conn.commit()
        return jsonify({"order_id": order_id}), 201
    except ValueError as exc:
        conn.rollback()
        return jsonify({"error": str(exc)}), 400
    except Error as exc:
        conn.rollback()
        app.logger.exception("DB error during order placement: %s", exc)
        return jsonify({"error": "DB error"}), 500
    finally:
        cur.close()
        conn.close()


@app.get("/orders/customer/<int:customer_id>")
@auth_required(roles=["customer"])
def list_customer_orders(customer_id):
    if request.user.get("sub") != customer_id:
        return jsonify({"error": "Forbidden"}), 403

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT o.order_id, o.order_date, o.order_status, p.pharmacy_name
        FROM ORDERS o
        JOIN PHARMACY p ON o.pharmacy_id = p.pharmacy_id
        WHERE o.customer_id = %s
        ORDER BY o.order_date DESC
        """,
        (customer_id,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify({"orders": rows}), 200


@app.get("/orders/<int:order_id>")
@auth_required(roles=["customer"])
def get_order_details(order_id):
    customer_id = request.user.get("sub")
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT o.order_id, o.order_date, o.order_status, p.pharmacy_id, p.pharmacy_name
        FROM ORDERS o
        JOIN PHARMACY p ON o.pharmacy_id = p.pharmacy_id
        WHERE o.order_id = %s AND o.customer_id = %s
        """,
        (order_id, customer_id),
    )
    order_row = cur.fetchone()
    if not order_row:
        cur.close()
        conn.close()
        return jsonify({"error": "Order not found"}), 404

    cur.execute(
        """
        SELECT oi.medicine_id, m.medicine_name, m.price AS unit_price, oi.quantity, oi.subtotal
        FROM ORDER_ITEM oi
        JOIN MEDICINE m ON oi.medicine_id = m.medicine_id
        WHERE oi.order_id = %s
        """,
        (order_id,),
    )
    items = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify({"order": order_row, "items": items}), 200


@app.post("/prescriptions")
@auth_required(roles=["customer"])
def upload_prescription():
    customer_id = request.user.get("sub")
    doctor_name = request.form.get("doctor_name")
    order_id = request.form.get("order_id")
    file = request.files.get("file")

    if not doctor_name or not file:
        return jsonify({"error": "Missing doctor name or file"}), 400

    filename = secure_filename(file.filename)
    if not filename:
        return jsonify({"error": "Invalid filename"}), 400

    unique_name = f"{customer_id}_{int(datetime.utcnow().timestamp())}_{filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    file.save(file_path)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO PRESCRIPTION (customer_id, order_id, doctor_name, file_path) VALUES (%s, %s, %s, %s)",
        (customer_id, order_id, doctor_name, file_path),
    )
    conn.commit()
    prescription_id = cur.lastrowid
    cur.close()
    conn.close()

    return jsonify({"prescription_id": prescription_id, "file_path": file_path}), 201


# -----------------------------
# Pharmacy: Orders + Stock
# -----------------------------

@app.get("/pharmacy/orders")
@auth_required(roles=["pharmacy"])
def list_pharmacy_orders():
    pharmacy_id = request.user.get("sub")
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT o.order_id, o.order_date, o.order_status, c.first_name, c.last_name
        FROM ORDERS o
        JOIN CUSTOMER c ON o.customer_id = c.customer_id
        WHERE o.pharmacy_id = %s
        ORDER BY o.order_date DESC
        """,
        (pharmacy_id,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({"orders": rows}), 200


@app.patch("/orders/<int:order_id>")
@auth_required(roles=["pharmacy"])
def update_order_status(order_id):
    pharmacy_id = request.user.get("sub")
    data = request.get_json(silent=True) or {}
    status = data.get("order_status")
    if status not in {"ACCEPTED", "REJECTED"}:
        return jsonify({"error": "Invalid status"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE ORDERS SET order_status = %s WHERE order_id = %s AND pharmacy_id = %s",
        (status, order_id, pharmacy_id),
    )
    conn.commit()
    updated = cur.rowcount
    cur.close()
    conn.close()

    if updated == 0:
        return jsonify({"error": "Order not found"}), 404

    return jsonify({"order_id": order_id, "order_status": status}), 200


@app.get("/pharmacy/stock")
@auth_required(roles=["pharmacy"])
def list_stock():
    pharmacy_id = request.user.get("sub")
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM MEDICINE WHERE pharmacy_id = %s ORDER BY medicine_name",
        (pharmacy_id,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({"medicines": rows}), 200


@app.post("/pharmacy/stock")
@auth_required(roles=["pharmacy"])
def add_stock():
    pharmacy_id = request.user.get("sub")
    data = request.get_json(silent=True) or {}
    required = [
        "medicine_name",
        "category",
        "price",
        "stock_quantity",
        "expiry_date",
        "requires_prescription",
        "batch_no",
        "mfg_date",
    ]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing fields"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO MEDICINE
        (medicine_name, category, description, manufacturer, batch_no, mfg_date, price, stock_quantity, expiry_date, requires_prescription, pharmacy_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            data["medicine_name"],
            data["category"],
            data.get("description"),
            data.get("manufacturer"),
            data["batch_no"],
            data["mfg_date"],
            data["price"],
            data["stock_quantity"],
            data["expiry_date"],
            bool(data["requires_prescription"]),
            pharmacy_id,
        ),
    )
    conn.commit()
    medicine_id = cur.lastrowid
    cur.close()
    conn.close()

    return jsonify({"medicine_id": medicine_id}), 201


@app.patch("/pharmacy/stock/<int:medicine_id>")
@auth_required(roles=["pharmacy"])
def update_stock(medicine_id):
    pharmacy_id = request.user.get("sub")
    data = request.get_json(silent=True) or {}
    fields = []
    params = []

    for key in [
        "medicine_name",
        "category",
        "description",
        "manufacturer",
        "batch_no",
        "mfg_date",
        "price",
        "stock_quantity",
        "expiry_date",
        "requires_prescription",
    ]:
        if key in data:
            fields.append(f"{key} = %s")
            params.append(data[key])

    if not fields:
        return jsonify({"error": "No fields to update"}), 400

    params.extend([medicine_id, pharmacy_id])
    query = f"UPDATE MEDICINE SET {', '.join(fields)} WHERE medicine_id = %s AND pharmacy_id = %s"

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, tuple(params))
    conn.commit()
    updated = cur.rowcount
    cur.close()
    conn.close()

    if updated == 0:
        return jsonify({"error": "Medicine not found"}), 404

    return jsonify({"medicine_id": medicine_id}), 200


# -----------------------------
# Admin: Approvals
# -----------------------------

@app.get("/admin/pharmacies/pending")
@auth_required(roles=["admin"])
def list_pending_pharmacies():
    admin_id = request.user.get("sub")
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT pincode FROM SUPER_ADMIN WHERE admin_id = %s", (admin_id,))
    admin = cur.fetchone()
    if not admin:
        cur.close()
        conn.close()
        return jsonify({"error": "Admin not found"}), 404

    cur.execute(
        "SELECT * FROM PHARMACY WHERE approval_status = 'PENDING' AND pincode = %s",
        (admin["pincode"],),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({"pharmacies": rows}), 200


@app.get("/admin/pharmacies")
@auth_required(roles=["admin"])
def list_pharmacies_by_status():
    admin_id = request.user.get("sub")
    status = request.args.get("status")
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT pincode FROM SUPER_ADMIN WHERE admin_id = %s", (admin_id,))
    admin = cur.fetchone()
    if not admin:
        cur.close()
        conn.close()
        return jsonify({"error": "Admin not found"}), 404

    if status:
        status = status.upper().strip()
        if status not in {"PENDING", "APPROVED", "REJECTED"}:
            cur.close()
            conn.close()
            return jsonify({"error": "Invalid status"}), 400
        cur.execute(
            "SELECT * FROM PHARMACY WHERE approval_status = %s AND pincode = %s",
            (status, admin["pincode"]),
        )
    else:
        cur.execute(
            "SELECT * FROM PHARMACY WHERE pincode = %s",
            (admin["pincode"],),
        )

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({"pharmacies": rows}), 200


@app.patch("/admin/pharmacies/<int:pharmacy_id>")
@auth_required(roles=["admin"])
def approve_pharmacy(pharmacy_id):
    admin_id = request.user.get("sub")
    data = request.get_json(silent=True) or {}
    status = data.get("approval_status")
    if status not in {"APPROVED", "REJECTED"}:
        return jsonify({"error": "Invalid status"}), 400

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT pincode FROM SUPER_ADMIN WHERE admin_id = %s", (admin_id,))
    admin = cur.fetchone()
    if not admin:
        cur.close()
        conn.close()
        return jsonify({"error": "Admin not found"}), 404

    cur.execute("SELECT pincode FROM PHARMACY WHERE pharmacy_id = %s", (pharmacy_id,))
    pharmacy = cur.fetchone()
    if not pharmacy:
        cur.close()
        conn.close()
        return jsonify({"error": "Pharmacy not found"}), 404

    if pharmacy["pincode"] != admin["pincode"]:
        cur.close()
        conn.close()
        return jsonify({"error": "Forbidden"}), 403

    cur = conn.cursor()
    cur.execute(
        "UPDATE PHARMACY SET approval_status = %s WHERE pharmacy_id = %s",
        (status, pharmacy_id),
    )
    conn.commit()
    updated = cur.rowcount
    cur.close()
    conn.close()

    if updated == 0:
        return jsonify({"error": "Pharmacy not found"}), 404

    return jsonify({"pharmacy_id": pharmacy_id, "approval_status": status}), 200


if __name__ == "__main__":
    app.run(debug=True)
