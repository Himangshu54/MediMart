# 🏥 MediMart - Pharmacy E-Commerce Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Node.js Version](https://img.shields.io/badge/node-%3E%3D14.0.0-brightgreen)](https://nodejs.org/)

A modern and lightweight pharmacy e-commerce web application built with pure HTML, CSS, JavaScript, and Node.js. Perfect for small-scale demonstrations and learning purposes.

## ✨ Features

### � Customer Features
- **Product Browsing**: Search and filter products by category
- **Shopping Cart**: Add/remove items with quantity management
- **Prescription Upload**: Upload prescription images (JPG, PNG, PDF up to 5MB)
- **User Authentication**: Login and registration system
- **Order Management**: Place orders and view order history
- **Modern UI**: Animated gradients, glass morphism effects, and smooth transitions
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

### 🎨 Design Features
- **Animated Backgrounds**: Dynamic gradient animations
- **Glass Morphism**: Modern frosted-glass UI effects
- **Smooth Animations**: Hover effects, page transitions, and loading animations
- **Toast Notifications**: Real-time feedback for user actions
- **Professional Product Images**: Real medical product photos from Unsplash

## 🛠️ Tech Stack

### Frontend (Pure Vanilla)
- **HTML5**: Semantic markup
- **CSS3**: Custom animations, gradients, and glass morphism
- **JavaScript**: Vanilla JS (No frameworks)
- **Design**: Modern UI with responsive layout

### Backend
- **Runtime**: Node.js
- **Framework**: Express.js
- **Data Storage**: In-memory (No database)
- **Dependencies**: express, cors (only 2 packages!)

## 📁 Project Structure

```
MediMart/
├── simple-frontend/           # Frontend files
│   ├── index.html            # Single-page application
│   ├── style.css             # All styling with animations
│   └── app.js                # Client-side logic
│
├── simple-backend/           # Backend server
│   ├── server.js             # Express server with all APIs
│   ├── package.json          # Dependencies
│   └── package-lock.json
│
├── .github/
│   └── workflows/            # CI/CD configuration
├── .gitignore
├── LICENSE
├── README.md
└── README-SIMPLE.md          # Quick start guide
```

## 🚀 Getting Started

### Prerequisites
- Node.js (v14 or higher)
- npm (comes with Node.js)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Himangshu54/MediMart.git
cd MediMart
```

2. **Install Backend Dependencies**
```bash
cd simple-backend
npm install
```

3. **Run the Server**
```bash
node server.js
```

The server will start on `http://localhost:3000` and will serve both the API and frontend files.

4. **Access the Application**
Open your browser and navigate to:
```
http://localhost:3000
```

### Test Credentials
- **User Account**: `user@medimart.com` / `password123`
- **Admin Account**: `admin@medimart.com` / `admin123`

## 📱 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### Products
- `GET /api/products` - Get all products
- `GET /api/products/:id` - Get single product
- `GET /api/products/search?q=keyword` - Search products

### Cart
- `GET /api/cart` - Get user cart
- `POST /api/cart` - Add item to cart
- `PUT /api/cart/:productId` - Update cart item quantity
- `DELETE /api/cart/:productId` - Remove item from cart

### Orders
- `POST /api/orders` - Create new order
- `GET /api/orders` - Get user orders
- `GET /api/orders/:id` - Get single order details

## 🎨 Key Features Explained

### Prescription Upload
- Accepts: JPG, PNG, GIF, PDF
- Max file size: 5MB
- Real-time validation and feedback
- File information logged for review

### Mock Data
The application uses in-memory storage with:
- **8 Products**: Including medicines, vitamins, sanitizers, medical devices
- **2 Test Users**: One regular user, one admin
- **Session Management**: Token-based authentication
- **Cart System**: Per-user shopping cart
- **Orders**: Order history tracking

### UI/UX Features
- **Gradient Animations**: Smooth color transitions
- **Glass Morphism**: Frosted glass effect on cards
- **Hover Effects**: Interactive button and card animations
- **Loading States**: Animated loading overlay
- **Toast Notifications**: Success/error messages
- **Smooth Scrolling**: Enhanced page navigation

## 🚀 Deployment

This is a simple demonstration project. For deployment:

### Option 1: Deploy on Render/Railway
1. Push your code to GitHub
2. Connect your repository to Render or Railway
3. Set the start command: `node server.js`
4. Deploy!

### Option 2: Deploy on Heroku
```bash
heroku create medimart-app
git push heroku main
```

### Option 3: Deploy on Vercel/Netlify (with serverless functions)
Convert the Express server to serverless functions for deployment.

## 💡 Learning Outcomes

This project demonstrates:
- ✅ Clean HTML/CSS/JavaScript architecture
- ✅ RESTful API design with Express.js
- ✅ Client-server communication
- ✅ Session management without databases
- ✅ File upload handling
- ✅ Modern UI/UX design principles
- ✅ Responsive web design
- ✅ Form validation
- ✅ Error handling and user feedback

## 🤝 Contributing

Contributions are welcome! Feel free to:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Future Enhancements

Possible improvements:
- Add a real database (MongoDB/PostgreSQL)
- Implement payment gateway integration
- Add email notifications
- Create admin dashboard
- Add product reviews and ratings
- Implement real-time chat support
- Add inventory management
- Create mobile app version

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Himangshu Saikia**
- GitHub: [@Himangshu54](https://github.com/Himangshu54)

## 🙏 Acknowledgments

- Product images from [Unsplash](https://unsplash.com)
- Icons and emojis for UI enhancement
- Inspired by modern e-commerce platforms

## 📞 Support

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ for learning and demonstration purposes**
