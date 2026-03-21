# 🏥 MediMart - Online Medical Store

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

MediMart includes two runnable setups:

1) **Full backend**: Flask + MySQL API with authentication, orders, and prescription uploads.
2) **Simple demo**: Node.js + Express API with in-memory data, serving a static HTML/CSS/JS frontend.

## ✨ Highlights

- Customer, pharmacy, and admin flows
- Medicine search by category/city/pincode
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

Open:
```
http://localhost:3000
```

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
```

2) Install and run the API:
```bash
cd backend
python -m pip install -r requirements.txt
python app.py
```

3) Serve the frontend:
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
- `GET /medicines/categories`

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
- `PUT /pharmacy/stock/<medicine_id>`

**Admin**
- `GET /admin/pharmacies`
- `PUT /admin/pharmacies/<pharmacy_id>`

**Prescription Upload**
- `POST /prescriptions`

## 📄 License

MIT License. See [LICENSE](LICENSE).
