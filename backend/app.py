from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
import base64
import hashlib
import os
import re
import secrets
import smtplib
import ssl
from datetime import datetime, timedelta
from email.message import EmailMessage
from functools import wraps
from mimetypes import guess_type

import jwt
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from marshmallow import Schema, ValidationError, fields, validate
from mysql.connector import Error
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from config import (
    ACCESS_TOKEN_MINUTES,
    JWT_SECRET,
    RATE_LIMIT_AUTH,
    RATE_LIMIT_DEFAULT,
    RATE_LIMIT_ORDER,
    REFRESH_TOKEN_DAYS,
    SMTP_FROM,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USER,
    UPLOAD_DIR,
    FLASK_DEBUG,
    GEMINI_API_KEY,
    GEMINI_MODEL,
)
from db import get_db_connection

app = Flask(__name__)
CORS(app)
limiter = Limiter(get_remote_address, app=app, default_limits=[RATE_LIMIT_DEFAULT])

os.makedirs(UPLOAD_DIR, exist_ok=True)


# -----------------------------
# Helpers
# -----------------------------

def create_access_token(user_id, role):
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_MINUTES),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def generate_refresh_token():
    return secrets.token_urlsafe(48)


def hash_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def store_refresh_token(user_id, role, refresh_token):
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_DAYS)
    token_hash = hash_token(refresh_token)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO REFRESH_TOKEN (user_id, role, token_hash, expires_at) VALUES (%s, %s, %s, %s)",
        (user_id, role, token_hash, expires_at),
    )
    conn.commit()
    cur.close()
    conn.close()


def revoke_refresh_token(token_hash):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE REFRESH_TOKEN SET revoked_at = %s WHERE token_hash = %s AND revoked_at IS NULL",
        (datetime.utcnow(), token_hash),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_refresh_token_record(token_hash):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM REFRESH_TOKEN WHERE token_hash = %s",
        (token_hash,),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def send_email(to_email, subject, body):
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASSWORD or not SMTP_FROM:
        app.logger.info("SMTP not configured; skipping email to %s", to_email)
        return False
    message = EmailMessage()
    message["From"] = SMTP_FROM
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(message)
        return True
    except Exception as exc:
        app.logger.exception("Email send failed: %s", exc)
        return False


_COMPOSITION_STOPWORDS = {
    "mg",
    "ml",
    "mcg",
    "g",
    "kg",
    "iu",
    "tablet",
    "tablets",
    "capsule",
    "capsules",
    "tab",
    "cap",
}


def extract_composition_tokens(text):
    if not text:
        return []
    cleaned = re.sub(r"[^a-z0-9+ ]", " ", text.lower())
    cleaned = re.sub(r"\b\d+(?:\.\d+)?\b", " ", cleaned)
    tokens = [
        token
        for token in cleaned.split()
        if len(token) >= 3 and token not in _COMPOSITION_STOPWORDS
    ]
    seen = set()
    result = []
    for token in tokens:
        if token not in seen:
            seen.add(token)
            result.append(token)
    return result


_GEMINI_MODEL_CACHE = None


def list_gemini_models(api_version):
    try:
        url = f"https://generativelanguage.googleapis.com/{api_version}/models"
        response = requests.get(url, params={"key": GEMINI_API_KEY}, timeout=30)
        if response.status_code >= 400:
            app.logger.error("Gemini model list error (%s): %s", api_version, response.text)
            return []
        data = response.json()
        return data.get("models", [])
    except Exception as exc:
        app.logger.exception("Gemini model list failed (%s): %s", api_version, exc)
        return []


def pick_gemini_model():
    for api_version in ("v1", "v1beta"):
        models = list_gemini_models(api_version)
        candidates = [
            model.get("name")
            for model in models
            if "generateContent" in model.get("supportedGenerationMethods", [])
        ]
        if candidates:
            for name in candidates:
                if "flash" in name:
                    return api_version, name
            return api_version, candidates[0]
    return None, None


def extract_gemini_text(file_path, mime_type):
    if not GEMINI_API_KEY:
        app.logger.warning("Gemini OCR skipped: GEMINI_API_KEY is not set")
        return None
    if not mime_type or not mime_type.startswith("image/"):
        return None

    try:
        with open(file_path, "rb") as handle:
            image_data = base64.b64encode(handle.read()).decode("ascii")

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": "Extract all readable text from this prescription image. Return plain text only."},
                        {"inline_data": {"mime_type": mime_type, "data": image_data}},
                    ],
                }
            ]
        }
        api_version = "v1"
        model_path = GEMINI_MODEL if GEMINI_MODEL.startswith("models/") else f"models/{GEMINI_MODEL}"
        url = f"https://generativelanguage.googleapis.com/{api_version}/{model_path}:generateContent"
        response = requests.post(url, params={"key": GEMINI_API_KEY}, json=payload, timeout=30)
        if response.status_code == 404:
            app.logger.error("Gemini OCR error response: %s", response.text)
            global _GEMINI_MODEL_CACHE
            if _GEMINI_MODEL_CACHE is None:
                _GEMINI_MODEL_CACHE = pick_gemini_model()
            fallback_version, fallback_model = _GEMINI_MODEL_CACHE
            if fallback_version and fallback_model:
                app.logger.warning("Gemini OCR retrying with model: %s (%s)", fallback_model, fallback_version)
                fallback_url = f"https://generativelanguage.googleapis.com/{fallback_version}/{fallback_model}:generateContent"
                response = requests.post(
                    fallback_url,
                    params={"key": GEMINI_API_KEY},
                    json=payload,
                    timeout=30,
                )
        if response.status_code >= 400:
            app.logger.error("Gemini OCR error response: %s", response.text)
        response.raise_for_status()
        data = response.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return None
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            return None
        text = " ".join(part.get("text", "") for part in parts if part.get("text"))
        text = text.strip() if text else None
        return text
    except Exception as exc:
        app.logger.exception("Gemini OCR failed: %s", exc)
        return None


def parse_json(schema):
    data = request.get_json(silent=True)
    if data is None:
        return None, {"_schema": ["Invalid or missing JSON body"]}
    try:
        return schema.load(data), None
    except ValidationError as err:
        return None, err.messages


def auth_required(roles=None):
    def decorator(fn):
        @wraps(fn)
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

            if payload.get("type") != "access":
                return jsonify({"error": "Invalid token type"}), 401

            sub_value = payload.get("sub")
            if isinstance(sub_value, str) and sub_value.isdigit():
                payload["sub"] = int(sub_value)

            if roles and payload.get("role") not in roles:
                return jsonify({"error": "Forbidden"}), 403

            request.user = payload
            return fn(*args, **kwargs)

        return wrapper

    return decorator


class CustomerRegisterSchema(Schema):
    first_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True, validate=validate.Length(max=150))
    phone = fields.String(required=True, validate=validate.Regexp(r"^[0-9+()\- ]{7,20}$"))
    password = fields.String(required=True, validate=validate.Length(min=8, max=128))
    street = fields.String(required=True, validate=validate.Length(min=1, max=255))
    pincode = fields.String(required=True, validate=validate.Length(min=3, max=20))
    city_id = fields.Integer(required=True)


class PharmacyRegisterSchema(Schema):
    pharmacy_name = fields.String(required=True, validate=validate.Length(min=1, max=150))
    license_number = fields.String(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True, validate=validate.Length(max=150))
    phone = fields.String(required=True, validate=validate.Regexp(r"^[0-9+()\- ]{7,20}$"))
    password = fields.String(required=True, validate=validate.Length(min=8, max=128))
    street = fields.String(required=True, validate=validate.Length(min=1, max=255))
    pincode = fields.String(required=True, validate=validate.Length(min=3, max=20))
    city_id = fields.Integer(required=True)
    latitude = fields.Float(load_default=None, allow_none=True, validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(load_default=None, allow_none=True, validate=validate.Range(min=-180, max=180))


class LoginSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=150))
    password = fields.String(required=True, validate=validate.Length(min=8, max=128))


class RefreshSchema(Schema):
    refresh_token = fields.String(required=True, validate=validate.Length(min=20, max=500))


class OrderItemSchema(Schema):
    medicine_id = fields.Integer(required=True)
    quantity = fields.Integer(required=True, validate=validate.Range(min=1, max=1000))


class PlaceOrderSchema(Schema):
    pharmacy_id = fields.Integer(required=True)
    items = fields.List(fields.Nested(OrderItemSchema), required=True, validate=validate.Length(min=1))
    prescription_id = fields.Integer(load_default=None, allow_none=True)


class UpdateOrderStatusSchema(Schema):
    order_status = fields.String(required=True, validate=validate.OneOf(["ACCEPTED", "REJECTED", "SHIPPED", "DELIVERED"]))


# -----------------------------
# Health
# -----------------------------

@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


# -----------------------------
# Cities
# -----------------------------

@app.get("/cities/search")
def search_cities():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"cities": []}), 200

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT city_id, city_name, state FROM CITY WHERE city_name LIKE %s ORDER BY city_name LIMIT 20",
        (f"%{query}%",),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({"cities": rows}), 200


@app.get("/cities")
def list_cities():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT city_id, city_name, state FROM CITY ORDER BY city_name")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({"cities": rows}), 200


# -----------------------------
# Auth
# -----------------------------

@app.post("/auth/customer/register")
@limiter.limit(RATE_LIMIT_AUTH)
def customer_register():
    data, errors = parse_json(CustomerRegisterSchema())
    if errors:
        return jsonify({"errors": errors}), 400

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
        access_token = create_access_token(customer_id, "customer")
        refresh_token = generate_refresh_token()
        store_refresh_token(customer_id, "customer", refresh_token)
        if data.get("email"):
            send_email(
                data["email"],
                "Welcome to MediMart",
                (
                    f"Hi {data.get('first_name', '')} {data.get('last_name', '')},\n\n"
                    "Your MediMart account is ready. You can now browse pharmacies and place orders.\n"
                ),
            )
        return (
            jsonify({"customer_id": customer_id, "access_token": access_token, "refresh_token": refresh_token}),
            201,
        )
    except Error as exc:
        if "Duplicate entry" in str(exc):
            return jsonify({"errors": {"email": ["Email already exists"]}}), 409
        return jsonify({"error": "DB error"}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.post("/auth/customer/login")
@limiter.limit(RATE_LIMIT_AUTH)
def customer_login():
    data, errors = parse_json(LoginSchema())
    if errors:
        return jsonify({"errors": errors}), 400
    email = data["email"]
    password = data["password"]

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM CUSTOMER WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user:
        return jsonify({"errors": {"email": ["Email not found"]}}), 404
    if not check_password_hash(user["password"], password):
        return jsonify({"errors": {"password": ["Invalid password"]}}), 401

    access_token = create_access_token(user["customer_id"], "customer")
    refresh_token = generate_refresh_token()
    store_refresh_token(user["customer_id"], "customer", refresh_token)
    user.pop("password", None)
    return jsonify({"customer": user, "access_token": access_token, "refresh_token": refresh_token}), 200


@app.post("/auth/pharmacy/register")
@limiter.limit(RATE_LIMIT_AUTH)
def pharmacy_register():
    data, errors = parse_json(PharmacyRegisterSchema())
    if errors:
        return jsonify({"errors": errors}), 400

    hashed_pw = generate_password_hash(data["password"])
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO PHARMACY
            (pharmacy_name, license_number, email, phone, password, street, pincode, city_id, latitude, longitude)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
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
                data.get("latitude"),
                data.get("longitude"),
            ),
        )
        conn.commit()
        pharmacy_id = cur.lastrowid
        access_token = create_access_token(pharmacy_id, "pharmacy")
        refresh_token = generate_refresh_token()
        store_refresh_token(pharmacy_id, "pharmacy", refresh_token)
        return (
            jsonify(
                {
                    "pharmacy_id": pharmacy_id,
                    "approval_status": "PENDING",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
            ),
            201,
        )
    except Error as exc:
        if "Duplicate entry" in str(exc):
            return jsonify({"errors": {"email": ["Email already exists"]}}), 409
        return jsonify({"error": "DB error"}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.post("/auth/pharmacy/login")
@limiter.limit(RATE_LIMIT_AUTH)
def pharmacy_login():
    data, errors = parse_json(LoginSchema())
    if errors:
        return jsonify({"errors": errors}), 400
    email = data["email"]
    password = data["password"]

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM PHARMACY WHERE email = %s", (email,))
    pharmacy = cur.fetchone()
    cur.close()
    conn.close()

    if not pharmacy:
        return jsonify({"errors": {"email": ["Email not found"]}}), 404
    if not check_password_hash(pharmacy["password"], password):
        return jsonify({"errors": {"password": ["Invalid password"]}}), 401

    if pharmacy["approval_status"] != "APPROVED":
        return jsonify({"error": "Pharmacy not approved"}), 403

    access_token = create_access_token(pharmacy["pharmacy_id"], "pharmacy")
    refresh_token = generate_refresh_token()
    store_refresh_token(pharmacy["pharmacy_id"], "pharmacy", refresh_token)
    pharmacy.pop("password", None)
    return jsonify({"pharmacy": pharmacy, "access_token": access_token, "refresh_token": refresh_token}), 200


@app.post("/auth/admin/login")
@limiter.limit(RATE_LIMIT_AUTH)
def admin_login():
    data, errors = parse_json(LoginSchema())
    if errors:
        return jsonify({"errors": errors}), 400
    email = data["email"]
    password = data["password"]

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM SUPER_ADMIN WHERE email = %s", (email,))
    admin = cur.fetchone()
    cur.close()
    conn.close()

    if not admin:
        return jsonify({"errors": {"email": ["Email not found"]}}), 404
    if admin["password"] != password:
        return jsonify({"errors": {"password": ["Invalid password"]}}), 401

    access_token = create_access_token(admin["admin_id"], "admin")
    refresh_token = generate_refresh_token()
    store_refresh_token(admin["admin_id"], "admin", refresh_token)
    admin.pop("password", None)
    if admin.get("email"):
        send_email(
            admin["email"],
            "MediMart Admin Login Alert",
            "A login to your MediMart admin account was detected. If this was not you, please reset your password.",
        )
    return jsonify({"admin": admin, "access_token": access_token, "refresh_token": refresh_token}), 200


@app.post("/auth/admin/register")
@limiter.limit(RATE_LIMIT_AUTH)
def admin_register():
    data, errors = parse_json(LoginSchema())
    if errors:
        return jsonify({"errors": errors}), 400
    email = data["email"]
    password = data["password"]

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM SUPER_ADMIN WHERE email = %s", (email,))
    admin = cur.fetchone()
    cur.close()
    conn.close()

    if not admin:
        return jsonify({"errors": {"email": ["Email not found"]}}), 404
    if admin["password"] != password:
        return jsonify({"errors": {"password": ["Invalid password"]}}), 401

    access_token = create_access_token(admin["admin_id"], "admin")
    refresh_token = generate_refresh_token()
    store_refresh_token(admin["admin_id"], "admin", refresh_token)
    admin.pop("password", None)
    if admin.get("email"):
        send_email(
            admin["email"],
            "MediMart Admin Login Alert",
            "A login to your MediMart admin account was detected. If this was not you, please reset your password.",
        )
    return jsonify({"admin": admin, "access_token": access_token, "refresh_token": refresh_token}), 200


@app.post("/auth/refresh")
@limiter.limit(RATE_LIMIT_AUTH)
def refresh_token():
    data, errors = parse_json(RefreshSchema())
    if errors:
        return jsonify({"errors": errors}), 400

    refresh_token_value = data["refresh_token"]
    token_hash = hash_token(refresh_token_value)
    record = get_refresh_token_record(token_hash)
    if not record:
        return jsonify({"error": "Invalid refresh token"}), 401
    if record.get("revoked_at"):
        return jsonify({"error": "Refresh token revoked"}), 401
    if record.get("expires_at") and record["expires_at"] <= datetime.utcnow():
        return jsonify({"error": "Refresh token expired"}), 401

    revoke_refresh_token(token_hash)
    access_token = create_access_token(record["user_id"], record["role"])
    new_refresh_token = generate_refresh_token()
    store_refresh_token(record["user_id"], record["role"], new_refresh_token)
    return jsonify({"access_token": access_token, "refresh_token": new_refresh_token}), 200


@app.post("/auth/logout")
@limiter.limit(RATE_LIMIT_AUTH)
def logout():
    data, errors = parse_json(RefreshSchema())
    if errors:
        return jsonify({"errors": errors}), 400

    token_hash = hash_token(data["refresh_token"])
    revoke_refresh_token(token_hash)
    return jsonify({"message": "Logged out"}), 200


# -----------------------------
# Customer: Search
# -----------------------------

@app.get("/medicines/search")
@auth_required(roles=["customer"])
def search_medicines():
    name = request.args.get("name", "").strip()
    category = request.args.get("category", "").strip()
    pincode = request.args.get("pincode")
    user_lat = request.args.get("lat")
    user_lng = request.args.get("lng")

    try:
        user_lat = float(user_lat) if user_lat else None
        user_lng = float(user_lng) if user_lng else None
    except ValueError:
        return jsonify({"error": "Invalid latitude/longitude"}), 400

    if (user_lat is None) != (user_lng is None):
        return jsonify({"error": "Both lat and lng are required"}), 400

    if user_lat is not None and (user_lat < -90 or user_lat > 90 or user_lng < -180 or user_lng > 180):
        return jsonify({"error": "Latitude/longitude out of range"}), 400

    customer_id = request.user.get("sub")
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT city_id FROM CUSTOMER WHERE customer_id = %s", (customer_id,))
    customer_row = cur.fetchone()
    if not customer_row:
        cur.close()
        conn.close()
        return jsonify({"error": "Customer not found"}), 404
    city_id = customer_row.get("city_id")

    distance_expr = (
        "CASE WHEN p.latitude IS NULL OR p.longitude IS NULL THEN NULL ELSE "
        "(6371 * ACOS( COS(RADIANS(%s)) * COS(RADIANS(p.latitude)) * "
        "COS(RADIANS(p.longitude) - RADIANS(%s)) + SIN(RADIANS(%s)) * SIN(RADIANS(p.latitude)) )) END"
    )
    include_distance = user_lat is not None and user_lng is not None

    select_fields = (
        "m.medicine_id, m.medicine_name, m.category, m.description, m.manufacturer, m.batch_no, m.mfg_date, "
        "m.price, m.stock_quantity, m.expiry_date, m.requires_prescription, p.pharmacy_id, p.pharmacy_name, "
        "p.street, p.pincode, "
    )
    if include_distance:
        select_fields += f"{distance_expr} AS distance_km, "
    select_fields += "c.city_name, c.state "

    base_query = (
        f"SELECT {select_fields}"
        "FROM MEDICINE m "
        "JOIN PHARMACY p ON m.pharmacy_id = p.pharmacy_id "
        "JOIN CITY c ON p.city_id = c.city_id "
        "WHERE p.approval_status = 'APPROVED' AND m.stock_quantity > 0"
    )
    filters = []
    params = []
    if include_distance:
        params.extend([user_lat, user_lng, user_lat])

    if name:
        filters.append("m.medicine_name LIKE %s")
        params.append(f"%{name}%")
    if category:
        filters.append("m.category = %s")
        params.append(category)
    if city_id:
        filters.append("c.city_id = %s")
        params.append(city_id)
    if pincode:
        filters.append("p.pincode = %s")
        params.append(pincode)

    query = base_query
    if filters:
        query += " AND " + " AND ".join(filters)
    if include_distance:
        query += " ORDER BY (distance_km IS NULL) ASC, distance_km ASC"

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
@limiter.limit(RATE_LIMIT_ORDER)
def place_order():
    data, errors = parse_json(PlaceOrderSchema())
    if errors:
        return jsonify({"errors": errors}), 400
    customer_id = request.user.get("sub")
    pharmacy_id = data["pharmacy_id"]
    items = data["items"]
    prescription_id = data.get("prescription_id")

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

        cur.close()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT email, first_name, phone FROM CUSTOMER WHERE customer_id = %s", (customer_id,))
        customer = cur.fetchone() or {}
        cur.execute("SELECT email, pharmacy_name, phone FROM PHARMACY WHERE pharmacy_id = %s", (pharmacy_id,))
        pharmacy = cur.fetchone() or {}
        cur.close()

        if customer.get("email"):
            send_email(
                customer["email"],
                "MediMart Order Placed",
                f"Your MediMart order #{order_id} was placed successfully.",
            )
        if pharmacy.get("email"):
            send_email(
                pharmacy["email"],
                "New MediMart Order",
                f"New MediMart order #{order_id} placed for {pharmacy.get('pharmacy_name', 'your pharmacy')}.",
            )

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


@app.post("/orders/<int:order_id>/cancel")
@auth_required(roles=["customer"])
@limiter.limit(RATE_LIMIT_ORDER)
def cancel_order(order_id):
    customer_id = request.user.get("sub")
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT order_status FROM ORDERS WHERE order_id = %s AND customer_id = %s",
        (order_id, customer_id),
    )
    order_row = cur.fetchone()
    if not order_row:
        cur.close()
        conn.close()
        return jsonify({"error": "Order not found"}), 404

    if order_row["order_status"] not in {"PENDING", "ACCEPTED"}:
        cur.close()
        conn.close()
        return jsonify({"error": "Order cannot be cancelled now"}), 400

    cur.execute(
        "UPDATE ORDERS SET order_status = 'CANCELLED' WHERE order_id = %s AND customer_id = %s",
        (order_id, customer_id),
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"order_id": order_id, "order_status": "CANCELLED"}), 200


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

    mime_type = file.mimetype or guess_type(file_path)[0]
    app.logger.info(
        "Prescription upload: file=%s mime=%s api_key_loaded=%s",
        file_path,
        mime_type,
        bool(GEMINI_API_KEY),
    )
    ocr_text = extract_gemini_text(file_path, mime_type)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO PRESCRIPTION (customer_id, order_id, doctor_name, file_path, ocr_text) VALUES (%s, %s, %s, %s, %s)",
        (customer_id, order_id, doctor_name, file_path, ocr_text),
    )
    conn.commit()
    prescription_id = cur.lastrowid
    cur.close()
    conn.close()

    return jsonify(
        {
            "prescription_id": prescription_id,
            "file_path": file_path,
            "ocr_text": ocr_text,
        }
    ), 201



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
@limiter.limit(RATE_LIMIT_ORDER)
def update_order_status(order_id):
    pharmacy_id = request.user.get("sub")
    data, errors = parse_json(UpdateOrderStatusSchema())
    if errors:
        return jsonify({"errors": errors}), 400
    status = data["order_status"]

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT order_status, customer_id FROM ORDERS WHERE order_id = %s AND pharmacy_id = %s",
        (order_id, pharmacy_id),
    )
    order_row = cur.fetchone()
    if not order_row:
        cur.close()
        conn.close()
        return jsonify({"error": "Order not found"}), 404

    current_status = order_row["order_status"]
    allowed_transitions = {
        "PENDING": {"ACCEPTED", "REJECTED"},
        "ACCEPTED": {"SHIPPED", "REJECTED"},
        "SHIPPED": {"DELIVERED"},
        "DELIVERED": set(),
        "REJECTED": set(),
        "CANCELLED": set(),
    }
    if status not in allowed_transitions.get(current_status, set()):
        cur.close()
        conn.close()
        return jsonify({"error": f"Invalid status transition from {current_status}"}), 400

    cur.execute(
        "UPDATE ORDERS SET order_status = %s WHERE order_id = %s AND pharmacy_id = %s",
        (status, order_id, pharmacy_id),
    )
    conn.commit()

    customer_id = order_row["customer_id"]
    cur.execute("SELECT email FROM CUSTOMER WHERE customer_id = %s", (customer_id,))
    customer = cur.fetchone() or {}
    if customer.get("email"):
        send_email(
            customer["email"],
            "MediMart Order Update",
            f"Your MediMart order #{order_id} status is now {status}.",
        )

    cur.close()
    conn.close()

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
    cur.execute("SELECT city_id, pincode FROM SUPER_ADMIN WHERE admin_id = %s", (admin_id,))
    admin = cur.fetchone()
    if not admin:
        cur.close()
        conn.close()
        return jsonify({"error": "Admin not found"}), 404

    if admin.get("city_id"):
        cur.execute(
            "SELECT * FROM PHARMACY WHERE approval_status = 'PENDING' AND city_id = %s",
            (admin["city_id"],),
        )
    else:
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

    cur.execute("SELECT city_id, pincode FROM SUPER_ADMIN WHERE admin_id = %s", (admin_id,))
    admin = cur.fetchone()
    if not admin:
        cur.close()
        conn.close()
        return jsonify({"error": "Admin not found"}), 404

    scope_field = "city_id" if admin.get("city_id") else "pincode"
    scope_value = admin.get("city_id") or admin.get("pincode")

    if status:
        status = status.upper().strip()
        if status not in {"PENDING", "APPROVED", "REJECTED"}:
            cur.close()
            conn.close()
            return jsonify({"error": "Invalid status"}), 400
        cur.execute(
            f"SELECT * FROM PHARMACY WHERE approval_status = %s AND {scope_field} = %s",
            (status, scope_value),
        )
    else:
        cur.execute(
            f"SELECT * FROM PHARMACY WHERE {scope_field} = %s",
            (scope_value,),
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
    cur.execute("SELECT city_id, pincode FROM SUPER_ADMIN WHERE admin_id = %s", (admin_id,))
    admin = cur.fetchone()
    if not admin:
        cur.close()
        conn.close()
        return jsonify({"error": "Admin not found"}), 404

    cur.execute(
        "SELECT city_id, pincode, email, pharmacy_name, phone FROM PHARMACY WHERE pharmacy_id = %s",
        (pharmacy_id,),
    )
    pharmacy = cur.fetchone()
    if not pharmacy:
        cur.close()
        conn.close()
        return jsonify({"error": "Pharmacy not found"}), 404

    if admin.get("city_id"):
        if pharmacy.get("city_id") != admin.get("city_id"):
            cur.close()
            conn.close()
            return jsonify({"error": "Forbidden"}), 403
    elif pharmacy["pincode"] != admin["pincode"]:
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

    if status == "APPROVED" and pharmacy.get("email"):
        send_email(
            pharmacy["email"],
            "MediMart Pharmacy Approved",
            f"Hello {pharmacy.get('pharmacy_name', '')},\n\nYour pharmacy has been approved by the MediMart admin. You can now log in and accept orders.\n",
        )
    elif status == "REJECTED" and pharmacy.get("email"):
        send_email(
            pharmacy["email"],
            "MediMart Pharmacy Rejected",
            f"Hello {pharmacy.get('pharmacy_name', '')},\n\nYour pharmacy registration was rejected by the MediMart admin.\n",
        )
    return jsonify({"pharmacy_id": pharmacy_id, "approval_status": status}), 200


if __name__ == "__main__":
    app.run(debug=FLASK_DEBUG)
