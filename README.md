# 🏥 MediMart - Full Stack Pharmacy E-Commerce Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Node.js Version](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen)](https://nodejs.org/)
[![React](https://img.shields.io/badge/React-18.x-61dafb)](https://reactjs.org/)

A modern, secure, and scalable full-stack pharmacy e-commerce web application built with React, Node.js, MongoDB, and advanced AI features.

## ✨ Features

### 🔐 User Features
- **Secure Authentication**: JWT-based auth with Google OAuth integration
- **Product Browsing**: Advanced search, filters, and category navigation
- **Smart Cart**: Persistent cart with coupon and discount management
- **Prescription Upload**: Secure upload with AI-powered OCR text extraction
- **Order Tracking**: Real-time order status and history
- **User Dashboard**: Profile management, address book, order history
- **Medicine Reminders**: Email notifications for medication schedules
- **Subscription Service**: Monthly auto-refill for regular medications

### 🤖 AI-Powered Features
- **OCR Prescription Reader**: Automatic medicine name extraction from prescriptions
- **AI Chatbot**: 24/7 assistance for product queries and order tracking
- **Medicine Recommender**: Intelligent product suggestions
- **Health Blog**: Dynamic articles on healthcare topics

### 👨‍💼 Admin Features
- **Product Management**: Complete CRUD operations with inventory tracking
- **Prescription Review**: Verify and approve uploaded prescriptions
- **Order Management**: Process orders and update delivery status
- **Analytics Dashboard**: Sales reports, revenue tracking, and insights
- **Banner Management**: Control homepage banners and promotional offers
- **User Management**: View and manage customer accounts

### 🌐 Additional Features
- **Multi-language Support**: English & Hindi (i18next)
- **Dark Mode**: Toggle between light and dark themes
- **Responsive Design**: Mobile-first, works on all devices
- **Payment Integration**: Razorpay & Stripe support
- **Invoice Generation**: Automated PDF invoices
- **Email Notifications**: Order confirmations and updates
- **Accessibility**: WCAG-compliant design

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 18 with Vite
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **State Management**: Context API / Redux Toolkit
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Forms**: React Hook Form + Zod validation
- **UI Components**: Custom + Headless UI
- **Icons**: React Icons / Lucide React
- **Animations**: Framer Motion

### Backend
- **Runtime**: Node.js 18+
- **Framework**: Express.js
- **Language**: TypeScript
- **Database**: MongoDB with Mongoose ODM
- **Authentication**: JWT + Passport.js
- **File Upload**: Multer + Cloudinary/AWS S3
- **Validation**: Zod
- **Logging**: Winston
- **Security**: Helmet, express-rate-limit, CORS
- **Email**: Nodemailer
- **Payment**: Razorpay/Stripe SDK
- **AI/ML**: OpenAI API, Tesseract.js

### DevOps & Deployment
- **Frontend Hosting**: Vercel
- **Backend Hosting**: Render / Railway / AWS EC2
- **Database**: MongoDB Atlas
- **File Storage**: Cloudinary / AWS S3
- **CI/CD**: GitHub Actions
- **Domain**: Cloudflare DNS

## 📁 Project Structure

```
MediMart/
├── frontend/                 # React + Vite frontend
│   ├── public/              # Static assets
│   ├── src/
│   │   ├── api/             # API service layer
│   │   ├── assets/          # Images, fonts, icons
│   │   ├── components/      # Reusable components
│   │   │   ├── common/      # Button, Input, Modal, etc.
│   │   │   ├── layout/      # Navbar, Footer, Sidebar
│   │   │   └── features/    # ProductCard, CartItem, etc.
│   │   ├── contexts/        # React contexts (Auth, Theme, Cart)
│   │   ├── hooks/           # Custom hooks
│   │   ├── pages/           # Route pages
│   │   ├── utils/           # Helper functions
│   │   ├── types/           # TypeScript types
│   │   ├── constants/       # App constants
│   │   ├── App.tsx          # Main app component
│   │   └── main.tsx         # Entry point
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── backend/                  # Node.js + Express backend
│   ├── src/
│   │   ├── config/          # Configuration files
│   │   ├── controllers/     # Route controllers
│   │   ├── middleware/      # Custom middleware
│   │   ├── models/          # Mongoose models
│   │   ├── routes/          # API routes
│   │   ├── services/        # Business logic
│   │   ├── utils/           # Helper functions
│   │   ├── validators/      # Zod schemas
│   │   ├── types/           # TypeScript types
│   │   └── server.ts        # Entry point
│   ├── uploads/             # Temporary file storage
│   ├── logs/                # Application logs
│   ├── package.json
│   ├── tsconfig.json
│   └── .env.example
│
├── .github/
│   └── workflows/           # CI/CD workflows
├── docs/                    # Additional documentation
├── .gitignore
├── LICENSE
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Node.js (v18 or higher)
- npm or yarn
- MongoDB (local or Atlas)
- Cloudinary account (for image uploads)
- Razorpay/Stripe account (for payments)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/medimart.git
cd medimart
```

2. **Setup Backend**
```bash
cd backend
npm install
cp .env.example .env
# Edit .env with your configuration
npm run dev
```

3. **Setup Frontend**
```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with your API URL
npm run dev
```

### Environment Variables

#### Backend (.env)
```env
NODE_ENV=development
PORT=5000
MONGODB_URI=mongodb://localhost:27017/medimart
JWT_SECRET=your_jwt_secret_key
JWT_EXPIRES_IN=7d

# OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Payment
RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password

# OpenAI (Optional)
OPENAI_API_KEY=your_openai_key

# Frontend URL
FRONTEND_URL=http://localhost:5173
```

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:5000/api
VITE_GOOGLE_CLIENT_ID=your_google_client_id
VITE_RAZORPAY_KEY=your_razorpay_key
```

## 📱 API Documentation

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/google` - Google OAuth login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password

### Products
- `GET /api/products` - Get all products (with filters)
- `GET /api/products/:id` - Get single product
- `POST /api/products` - Create product (Admin)
- `PUT /api/products/:id` - Update product (Admin)
- `DELETE /api/products/:id` - Delete product (Admin)

### Cart
- `GET /api/cart` - Get user cart
- `POST /api/cart` - Add item to cart
- `PUT /api/cart/:itemId` - Update cart item
- `DELETE /api/cart/:itemId` - Remove from cart
- `DELETE /api/cart` - Clear cart

### Orders
- `POST /api/orders` - Create new order
- `GET /api/orders` - Get user orders
- `GET /api/orders/:id` - Get single order
- `PUT /api/orders/:id/cancel` - Cancel order

### Prescriptions
- `POST /api/prescriptions` - Upload prescription
- `GET /api/prescriptions` - Get user prescriptions
- `GET /api/prescriptions/:id` - Get single prescription
- `PUT /api/prescriptions/:id/approve` - Approve prescription (Admin)

### Admin
- `GET /api/admin/analytics` - Get analytics data
- `GET /api/admin/orders` - Get all orders
- `PUT /api/admin/orders/:id` - Update order status
- `GET /api/admin/users` - Get all users

## 🧪 Testing

```bash
# Backend tests
cd backend
npm test

# Frontend tests
cd frontend
npm test
```

## 🚀 Deployment

### Frontend (Vercel)
```bash
cd frontend
vercel --prod
```

### Backend (Render/Railway)
- Connect GitHub repository
- Set environment variables
- Deploy from main branch

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)

## 🙏 Acknowledgments

- Inspired by 1mg, NetMeds, and Apollo Pharmacy
- Icons from React Icons
- UI inspiration from various design systems

## 📞 Support

For support, email support@medimart.com or join our Slack channel.

---

**Built with ❤️ for healthcare accessibility**
