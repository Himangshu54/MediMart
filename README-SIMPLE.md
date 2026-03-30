# 🎉 MediMart - Simple E-Commerce (No Database!)

A **lightweight pharmacy e-commerce website** with tons of features but **NO DATABASE REQUIRED!**

Perfect for showcasing frontend skills and e-commerce features without backend complexity.

---

## ✨ Features

### 🛒 Shopping Features
- ✅ Product Catalog with 12+ Products
- ✅ Search & Filter (by name, category, price)
- ✅ Product Details with Reviews
- ✅ Shopping Cart (Add/Remove/Update)
- ✅ Checkout Process
- ✅ Order History

### 🔐 User Features
- ✅ User Registration & Login
- ✅ User Dashboard
- ✅ Multiple Address Management
- ✅ Order Tracking

### 👑 Admin Features
- ✅ Admin Dashboard
- ✅ Sales Statistics
- ✅ Order Management

### 🎨 UI/UX Features
- ✅ Beautiful Responsive Design
- ✅ Dark Mode Support
- ✅ Loading States
- ✅ Toast Notifications
- ✅ Mobile Friendly
- ✅ 7 Reusable Components (Button, Input, Card, Modal, etc.)

---

## 🚀 Quick Start (5 Minutes!)

### Prerequisites
- **Node.js 18+** (Download from https://nodejs.org/)
- That's it! No database, no extra setup!

### Installation

**Step 1: Install Dependencies**
```powershell
# Backend (Simple version - no database!)
cd MediMart/simple-backend

npm install
```

**Step 2: Start the Simple API**
```powershell
node server.js
```

**Step 3: Open the Frontend**
```powershell
# Option A: open directly
start ..\simple-frontend\index.html

# Option B: serve with Python
cd ..\simple-frontend
python -m http.server 5500
```

Open:
```
http://localhost:5500
```

**Step 4: (Optional) Point the Frontend to Another API**
Edit the meta tag in [simple-frontend/index.html](simple-frontend/index.html):
```
<meta name="api-base-url" content="http://localhost:5000">
```

**Step 5: Test Accounts**
- User: user@medimart.com / password123
- Admin: admin@medimart.com / admin123
