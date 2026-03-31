# 🏥 MediMart - Online Medical Store

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

MediMart includes two runnable setups:

1) **Full backend**: Flask + MySQL API with authentication, orders, and prescription uploads.
2) **Simple demo**: Node.js + Express API with in-memory data, serving a static HTML/CSS/JS frontend.

## ✨ Highlights

- Customer, pharmacy, and admin flows
- Medicine search by category/city/pincode
- Location-aware sorting (nearest pharmacy first)
- Cart and order management
- Prescription uploads (JPG/PNG/PDF)
- Responsive UI with modern styling

## 🛠️ Tech Stack

**Frontend**
- HTML, CSS, Vanilla JavaScript

**Backend (Full)**
- Python, Flask, MySQL, JWT, Flask-CORS

**Backend (Simple Demo)**
- Node.js, Express, in-memory data

## 📁 Project Structure

```
MediMart/
├── backend/                  # Flask + MySQL API
├── simple-backend/           # Node.js demo API
├── simple-frontend/          # Static frontend (HTML/CSS/JS)
├── .github/workflows/        # CI workflows
├── README.md
└── README-SIMPLE.md          # Simple demo quick start
```

## 🚀 Run the Simple Demo (no DB)

**Prerequisites**: Node.js 18+

```bash
cd simple-backend
npm install
node server.js
```

Frontend (open directly or serve locally):
```bash
start ..\simple-frontend\index.html
```

Open:
```
http://localhost:3000
```

More details: see [README-SIMPLE.md](README-SIMPLE.md).

**Test credentials**
- User: user@medimart.com / password123
- Admin: admin@medimart.com / admin123

## 🚀 Run the Full Project (Flask + MySQL)

**Prerequisites**: Python 3.10+, MySQL 8+

1) Create `backend/.env`:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=medimart
JWT_SECRET=change-me
FLASK_DEBUG=false
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash
```

2) Load the database schema (and optional seed data):
```bash
mysql -u your_user -p medimart < medimart_schema.sql
mysql -u your_user -p medimart < seed.sql
```

If you already have a database, apply the OCR column migration:
```bash
mysql -u your_user -p medimart < backend/migrations/0005_gemini_ocr.sql
```

If you already have a database, apply the pharmacy location migration:
```bash
mysql -u your_user -p medimart < backend/migrations/0006_pharmacy_geo.sql
```

3) Install and run the API:
```bash
cd backend
python -m pip install -r requirements.txt
python app.py
```

4) Serve the frontend:
```bash
cd simple-frontend
python -m http.server 5500
```

Open:
```
http://localhost:5500
```

**Note**: The full backend requires a MySQL schema. Share a schema-only SQL dump with collaborators.

## 📱 Key API Routes (Full Backend)

**Auth**
- `POST /auth/customer/register`
- `POST /auth/customer/login`
- `POST /auth/pharmacy/register`
- `POST /auth/pharmacy/login`
- `POST /auth/admin/login`

**Medicines**
- `GET /medicines/search`

**Cart & Orders**
- `POST /cart/add`
- `GET /cart`
- `PUT /cart/update`
- `POST /orders`
- `GET /orders/customer/<id>`
- `GET /orders/<id>`

**Pharmacy**
- `GET /pharmacy/orders`
- `GET /pharmacy/stock`
- `PATCH /pharmacy/stock/<medicine_id>`

**Admin**
- `GET /admin/pharmacies`
- `PUT /admin/pharmacies/<pharmacy_id>`

**Prescription Upload**
- `POST /prescriptions`

## 📍 Location Notes

- Location sorting uses the browser GPS (free) and works on HTTPS or localhost.
- Pharmacy location capture during registration is optional.

## 📄 License

MIT License. See [LICENSE](LICENSE).
