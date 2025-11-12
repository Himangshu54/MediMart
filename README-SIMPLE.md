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
cd MediMart/backend
npm install cors express
npm install -D typescript ts-node @types/node @types/express @types/cors

# Frontend
cd ../frontend
npm install
```

**Step 2: Create Environment Files**

Create `backend/.env`:
```env
PORT=5000
```

Create `frontend/.env`:
```env
VITE_API_URL=http://localhost:5000/api
```

**Step 3: Run the Project**
```powershell
# Terminal 1: Backend
cd backend
npx ts-node src/server-simple.ts

# Terminal 2: Frontend
cd frontend
npm run dev
```

**Step 4: Open in Browser**
```
http://localhost:5173
```

---

## 🎯 Test Accounts

### User Account
- **Email:** user@medimart.com
- **Password:** password123

### Admin Account
- **Email:** admin@medimart.com
- **Password:** admin123

---

## 📦 What's Included

### Mock Data (No Database!)
- **12 Products** across 8 categories
- **2 Users** (regular user + admin)
- **Sample Orders** for testing
- All data stored in **memory** (resets on restart)

### Categories
1. Pain Relief
2. Antibiotics  
3. Vitamins & Supplements
4. Diabetes Care
5. Digestive Health
6. Health Devices
7. Allergy Relief
8. First Aid
9. Personal Care

### Sample Products
- Paracetamol, Amoxicillin, Vitamin C
- Insulin, Omeprazole, BP Monitor
- Cetirizine, First Aid Kit, Metformin
- Hand Sanitizer, N95 Masks, Omega-3

---

## 🏗️ Project Structure

```
MediMart/
├── backend/
│   └── src/
│       ├── server-simple.ts      # Simple Express server
│       └── data/
│           └── mockData.ts       # Mock products, users, orders
├── frontend/
│   └── src/
│       ├── components/           # 7 reusable components
│       ├── pages/                # 9 pages
│       ├── contexts/             # Auth, Cart, Theme
│       └── api/                  # API service
└── package.json files
```

---

## 📱 Pages Included

### Public Pages
- ✅ Home Page - Hero section, features
- ✅ Products Page - Grid with filters
- ✅ Product Detail - Full details with reviews
- ✅ Login Page - User authentication
- ✅ Register Page - New user signup

### Protected Pages
- ✅ Cart Page - Shopping cart
- ✅ Checkout Page - Address & payment
- ✅ User Dashboard - Order history, stats
- ✅ Admin Dashboard - Sales analytics

---

## 🎨 UI Components

All fully functional and styled with TailwindCSS:

1. **Button** - 6 variants, 3 sizes, icons, loading states
2. **Input** - Labels, errors, validation
3. **Card** - Hoverable, multiple padding options
4. **Modal** - 4 sizes, backdrop, animations
5. **LoadingSpinner** - 3 sizes, full-screen mode
6. **Badge** - 6 variants, 3 sizes
7. **Alert** - 4 types, auto-close

---

## 🔄 How It Works (No Database!)

### Data Storage
- All data stored in **JavaScript objects** in memory
- Products, users, orders defined in `mockData.ts`
- Cart stored in `Map<userId, items>`
- Sessions stored in `Map<token, userId>`

### Authentication
- Simple token-based auth (for demo)
- Tokens stored in memory (clears on restart)
- No JWT libraries needed

### State Management
- React Context API for Auth & Cart
- No Redux needed - kept simple!

---

## 🎯 API Endpoints

### Auth
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Products
- `GET /api/products` - List all products (with filters)
- `GET /api/products/:id` - Get single product
- `GET /api/products/categories/all` - Get categories

### Cart
- `GET /api/cart` - Get user cart
- `POST /api/cart/add` - Add to cart
- `PUT /api/cart/:productId` - Update quantity
- `DELETE /api/cart/:productId` - Remove item

### Orders
- `POST /api/orders` - Create order
- `GET /api/orders` - Get user orders
- `GET /api/orders/:id` - Get single order

### Admin
- `GET /api/admin/stats` - Dashboard statistics

---

## 💡 Why This Version?

### ✅ Advantages
- **Zero Setup** - No database installation
- **Fast Start** - Running in 5 minutes
- **Easy to Share** - Just clone and run
- **Perfect for Demo** - Shows all features
- **Beginner Friendly** - Understand the code easily
- **No Costs** - No cloud services needed

### 📚 Perfect For
- Learning e-commerce concepts
- Frontend portfolio projects
- UI/UX demonstrations
- Quick prototypes
- Teaching React/TypeScript
- Interview projects

---

## 🚀 What You Get

### Frontend (React)
- ✅ 9 Complete Pages (2,500+ LOC)
- ✅ 7 Reusable Components (600+ LOC)
- ✅ 3 Context Providers (400+ LOC)
- ✅ Responsive Design
- ✅ Dark Mode
- ✅ TailwindCSS Styling

### Backend (Node.js)
- ✅ RESTful API (300 LOC)
- ✅ Mock Data Store (200 LOC)
- ✅ CORS Enabled
- ✅ Simple Auth
- ✅ All CRUD Operations

### Total
- **3,500+ lines of clean, working code**
- **No database complexity**
- **Runs anywhere Node.js runs**

---

## 🎓 Learning Points

This project demonstrates:
- React Hooks (useState, useEffect, useContext)
- React Router for navigation
- Context API for state management
- TypeScript for type safety
- TailwindCSS for styling
- RESTful API design
- Authentication flow
- Shopping cart logic
- Form handling
- Responsive design
- Dark mode implementation

---

## 📝 Data Persistence

**Important:** Data is stored in memory and will **reset when server restarts**.

To add persistence:
- Option 1: Use browser `localStorage` for cart
- Option 2: Add `json-server` for simple file-based storage
- Option 3: Connect to real database later (MongoDB, PostgreSQL)

---

## 🎨 Customization

### Add More Products
Edit `backend/src/data/mockData.ts`:
```typescript
{
  id: 'p13',
  name: 'Your Product',
  price: 99.00,
  category: 'New Category',
  // ... other fields
}
```

### Change Colors
Edit `frontend/tailwind.config.js` for theme colors

### Add Features
- Payment gateway integration
- Image upload
- Product reviews
- Wishlist
- Notifications

---

## 🚀 Next Steps

Once comfortable with this version:

1. **Add Real Database** - Use the full version with MongoDB
2. **Deploy** - Host on Vercel (frontend) + Render (backend)
3. **Add Payments** - Integrate Razorpay/Stripe
4. **Add Images** - Use Cloudinary for uploads
5. **Add Email** - Send order confirmations
6. **Add Testing** - Write unit tests

---

## 🎉 You're Ready!

Your simple e-commerce website is ready to run!

```powershell
cd backend && npx ts-node src/server-simple.ts
# In another terminal:
cd frontend && npm run dev
```

Open http://localhost:5173 and start shopping! 🛒

---

## 📄 License

MIT License - Free to use for learning and projects!

---

**Built with ❤️ for easy learning and quick demos!**
