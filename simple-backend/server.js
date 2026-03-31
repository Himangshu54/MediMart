const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../simple-frontend')));

// Mock Data
const products = [
  { id: 1, name: 'Paracetamol 500mg', price: 50, category: 'Medicine', image: 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400&h=300&fit=crop', description: 'Effective pain and fever relief', stock: 100 },
  { id: 2, name: 'Vitamin C Tablets', price: 120, category: 'Medicine', image: 'https://images.unsplash.com/photo-1607619056574-7b8d3ee536b2?w=400&h=300&fit=crop', description: 'Boosts immunity', stock: 80 },
  { id: 3, name: 'Hand Sanitizer 500ml', price: 80, category: 'Hygiene', image: 'https://images.unsplash.com/photo-1584744982491-665216d95f8b?w=400&h=300&fit=crop', description: 'Kills 99.9% germs', stock: 150 },
  { id: 4, name: 'Blood Pressure Monitor', price: 2500, category: 'Devices', image: 'https://images.unsplash.com/photo-1615486511484-92e172cc4fe0?w=400&h=300&fit=crop', description: 'Digital BP monitor', stock: 25 },
  { id: 5, name: 'First Aid Kit', price: 450, category: 'First Aid', image: 'https://images.unsplash.com/photo-1603398938378-e54eab446dde?w=400&h=300&fit=crop', description: 'Complete first aid kit', stock: 60 },
  { id: 6, name: 'Omega-3 Capsules', price: 350, category: 'Supplements', image: 'https://images.unsplash.com/photo-1471864190281-a93a3070b6de?w=400&h=300&fit=crop', description: 'Heart health supplement', stock: 90 },
  { id: 7, name: 'N95 Face Masks (Pack of 10)', price: 250, category: 'Safety', image: 'https://images.unsplash.com/photo-1584634731339-252c581abfc5?w=400&h=300&fit=crop', description: 'Premium quality N95 masks', stock: 200 },
  { id: 8, name: 'Thermometer Digital', price: 180, category: 'Devices', image: 'https://images.unsplash.com/photo-1615461066841-6116e61058f4?w=400&h=300&fit=crop', description: 'Fast and accurate', stock: 75 }
];

let users = [
  { id: 1, email: 'user@medimart.com', password: 'password123', name: 'John Doe', role: 'user' },
  { id: 2, email: 'admin@medimart.com', password: 'admin123', name: 'Admin User', role: 'admin' }
];

let orders = [];
let carts = {}; // userId: [{productId, quantity}]
let sessions = {}; // token: userId

// Helper Functions
function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

function generateToken() {
  return 'token_' + generateId();
}

function getUserFromToken(token) {
  const userId = sessions[token];
  return users.find(u => u.id === userId);
}

// ========== API ROUTES ==========

// Health Check
app.get('/api/health', (req, res) => {
  res.json({ success: true, message: 'MediMart Simple API is running!' });
});

// Auth - Register
app.post('/api/auth/register', (req, res) => {
  const { name, email, password } = req.body;
  
  if (users.find(u => u.email === email)) {
    return res.status(400).json({ success: false, message: 'Email already exists' });
  }
  
  const newUser = {
    id: users.length + 1,
    name,
    email,
    password,
    role: 'user'
  };
  
  users.push(newUser);
  const token = generateToken();
  sessions[token] = newUser.id;
  
  res.json({ 
    success: true, 
    token, 
    user: { id: newUser.id, name: newUser.name, email: newUser.email, role: newUser.role } 
  });
});

// Auth - Login
app.post('/api/auth/login', (req, res) => {
  const { email, password } = req.body;
  
  const user = users.find(u => u.email === email && u.password === password);
  
  if (!user) {
    return res.status(401).json({ success: false, message: 'Invalid credentials' });
  }
  
  const token = generateToken();
  sessions[token] = user.id;
  
  res.json({ 
    success: true, 
    token, 
    user: { id: user.id, name: user.name, email: user.email, role: user.role } 
  });
});

// Products - Get All
app.get('/api/products', (req, res) => {
  const { search, category } = req.query;
  
  let filtered = products;
  
  if (search) {
    filtered = filtered.filter(p => 
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.description.toLowerCase().includes(search.toLowerCase())
    );
  }
  
  if (category && category !== 'all') {
    filtered = filtered.filter(p => p.category === category);
  }
  
  res.json({ success: true, data: filtered });
});

// Products - Get One
app.get('/api/products/:id', (req, res) => {
  const product = products.find(p => p.id === parseInt(req.params.id));
  
  if (!product) {
    return res.status(404).json({ success: false, message: 'Product not found' });
  }
  
  res.json({ success: true, data: product });
});

// Cart - Get
app.get('/api/cart', (req, res) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  const user = getUserFromToken(token);
  
  if (!user) {
    return res.status(401).json({ success: false, message: 'Not authenticated' });
  }
  
  const userCart = carts[user.id] || [];
  const cartWithProducts = userCart.map(item => {
    const product = products.find(p => p.id === item.productId);
    return { ...product, quantity: item.quantity };
  });
  
  res.json({ success: true, data: cartWithProducts });
});

// Cart - Add Item
app.post('/api/cart/add', (req, res) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  const user = getUserFromToken(token);
  
  if (!user) {
    return res.status(401).json({ success: false, message: 'Not authenticated' });
  }
  
  const { productId, quantity } = req.body;
  
  if (!carts[user.id]) {
    carts[user.id] = [];
  }
  
  const existingItem = carts[user.id].find(item => item.productId === productId);
  
  if (existingItem) {
    existingItem.quantity += quantity;
  } else {
    carts[user.id].push({ productId, quantity });
  }
  
  res.json({ success: true, message: 'Added to cart' });
});

// Cart - Update Item
app.put('/api/cart/:productId', (req, res) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  const user = getUserFromToken(token);
  
  if (!user) {
    return res.status(401).json({ success: false, message: 'Not authenticated' });
  }
  
  const { quantity } = req.body;
  const productId = parseInt(req.params.productId);
  
  if (!carts[user.id]) {
    return res.status(404).json({ success: false, message: 'Cart not found' });
  }
  
  const item = carts[user.id].find(item => item.productId === productId);
  
  if (item) {
    item.quantity = quantity;
    res.json({ success: true, message: 'Cart updated' });
  } else {
    res.status(404).json({ success: false, message: 'Item not found' });
  }
});

// Cart - Remove Item
app.delete('/api/cart/:productId', (req, res) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  const user = getUserFromToken(token);
  
  if (!user) {
    return res.status(401).json({ success: false, message: 'Not authenticated' });
  }
  
  const productId = parseInt(req.params.productId);
  
  if (carts[user.id]) {
    carts[user.id] = carts[user.id].filter(item => item.productId !== productId);
    res.json({ success: true, message: 'Item removed' });
  } else {
    res.status(404).json({ success: false, message: 'Cart not found' });
  }
});

// Orders - Create
app.post('/api/orders', (req, res) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  const user = getUserFromToken(token);
  
  if (!user) {
    return res.status(401).json({ success: false, message: 'Not authenticated' });
  }
  
  const userCart = carts[user.id] || [];
  
  if (userCart.length === 0) {
    return res.status(400).json({ success: false, message: 'Cart is empty' });
  }
  
  const orderItems = userCart.map(item => {
    const product = products.find(p => p.id === item.productId);
    return {
      productId: item.productId,
      name: product.name,
      price: product.price,
      quantity: item.quantity
    };
  });
  
  const total = orderItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  
  const order = {
    id: orders.length + 1,
    userId: user.id,
    items: orderItems,
    total,
    status: 'Pending',
    date: new Date().toISOString()
  };
  
  orders.push(order);
  carts[user.id] = []; // Clear cart
  
  res.json({ success: true, data: order, message: 'Order placed successfully!' });
});

// Orders - Get User Orders
app.get('/api/orders', (req, res) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  const user = getUserFromToken(token);
  
  if (!user) {
    return res.status(401).json({ success: false, message: 'Not authenticated' });
  }
  
  const userOrders = orders.filter(o => o.userId === user.id);
  res.json({ success: true, data: userOrders });
});

// Serve HTML files
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../simple-frontend/index.html'));
});

// Start Server
app.listen(PORT, () => {
  console.log(`\n🚀 MediMart Simple Server running on http://localhost:${PORT}`);
  console.log(`📦 Mode: Pure HTML/CSS/JS + Node.js (No Database)`);
  console.log(`\n✨ Test credentials:`);
  console.log(`   User: user@medimart.com / password123`);
  console.log(`   Admin: admin@medimart.com / admin123\n`);
});
