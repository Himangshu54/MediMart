const API_URL = 'http://localhost:3000/api';
let currentUser = null;
let token = localStorage.getItem('token');
let cart = [];

// Loading overlay functions
function showLoading() {
    document.getElementById('loading-overlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    if (token) {
        checkAuth();
    }
    loadProducts();
    showPage('home');
    
    // Add smooth scroll behavior
    document.documentElement.style.scrollBehavior = 'smooth';
});

// Show/Hide Pages
function showPage(pageName) {
    // Smooth page transition
    document.querySelectorAll('.page').forEach(page => {
        page.style.opacity = '0';
        setTimeout(() => {
            page.classList.remove('active');
        }, 300);
    });
    
    setTimeout(() => {
        const targetPage = document.getElementById(`${pageName}-page`);
        targetPage.classList.add('active');
        targetPage.style.opacity = '1';
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 300);
    
    if (pageName === 'products') {
        loadProducts();
    } else if (pageName === 'cart') {
        loadCart();
    } else if (pageName === 'orders') {
        if (!token) {
            showToast('Please login to view orders', 'error');
            showPage('login');
            return;
        }
        loadOrders();
    }
}

// Toast Notification
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Handle Prescription Upload
function handlePrescriptionUpload(event) {
    const file = event.target.files[0];
    
    if (!file) {
        return;
    }
    
    // Validate file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'application/pdf'];
    if (!validTypes.includes(file.type)) {
        showToast('Please upload a valid image (JPG, PNG, GIF) or PDF file', 'error');
        event.target.value = ''; // Reset input
        return;
    }
    
    // Validate file size (max 5MB)
    const maxSize = 5 * 1024 * 1024; // 5MB in bytes
    if (file.size > maxSize) {
        showToast('File size must be less than 5MB', 'error');
        event.target.value = ''; // Reset input
        return;
    }
    
    // Show success message
    showToast(`Prescription "${file.name}" uploaded successfully! Our pharmacist will review it.`, 'success');
    
    // Log the file info (in a real app, you'd upload this to the server)
    console.log('Prescription uploaded:', {
        name: file.name,
        size: (file.size / 1024).toFixed(2) + ' KB',
        type: file.type,
        lastModified: new Date(file.lastModified).toLocaleDateString()
    });
    
    // Reset the input for next upload
    setTimeout(() => {
        event.target.value = '';
    }, 500);
}

// Check Authentication
async function checkAuth() {
    try {
        const response = await fetch(`${API_URL}/cart`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            updateAuthUI(true);
        } else {
            logout();
        }
    } catch (error) {
        console.error('Auth check failed:', error);
    }
}

// Update UI based on auth status
function updateAuthUI(isLoggedIn) {
    if (isLoggedIn) {
        document.getElementById('login-link').style.display = 'none';
        document.getElementById('logout-link').style.display = 'block';
        document.getElementById('orders-link').style.display = 'block';
        document.getElementById('user-name').style.display = 'block';
        document.getElementById('user-name').textContent = currentUser?.name || 'User';
    } else {
        document.getElementById('login-link').style.display = 'block';
        document.getElementById('logout-link').style.display = 'none';
        document.getElementById('orders-link').style.display = 'none';
        document.getElementById('user-name').style.display = 'none';
    }
}

// Login
async function login(event) {
    event.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            token = data.token;
            currentUser = data.user;
            localStorage.setItem('token', token);
            updateAuthUI(true);
            showToast('Login successful!');
            showPage('home');
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        showToast('Login failed. Please try again.', 'error');
    }
}

// Register
async function register(event) {
    event.preventDefault();
    
    const name = document.getElementById('register-name').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    
    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, email, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            token = data.token;
            currentUser = data.user;
            localStorage.setItem('token', token);
            updateAuthUI(true);
            showToast('Registration successful!');
            showPage('home');
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        showToast('Registration failed. Please try again.', 'error');
    }
}

// Logout
function logout() {
    token = null;
    currentUser = null;
    localStorage.removeItem('token');
    updateAuthUI(false);
    showToast('Logged out successfully');
    showPage('home');
}

// Load Products
async function loadProducts() {
    showLoading();
    try {
        const search = document.getElementById('search-input')?.value || '';
        const category = document.getElementById('category-filter')?.value || 'all';
        
        const response = await fetch(`${API_URL}/products?search=${search}&category=${category}`);
        const data = await response.json();
        
        if (data.success) {
            displayProducts(data.data);
        }
    } catch (error) {
        console.error('Failed to load products:', error);
        showToast('Failed to load products', 'error');
    } finally {
        hideLoading();
    }
}

// Display Products
function displayProducts(products) {
    const grid = document.getElementById('products-grid');
    
    if (products.length === 0) {
        grid.innerHTML = '<p>No products found.</p>';
        return;
    }
    
    grid.innerHTML = products.map(product => `
        <div class="product-card">
            <img src="${product.image}" alt="${product.name}">
            <div class="product-info">
                <span class="product-category">${product.category}</span>
                <h3>${product.name}</h3>
                <p class="product-description">${product.description}</p>
                <div class="product-price">₹${product.price}</div>
                <p class="product-stock">Stock: ${product.stock}</p>
                <button class="btn btn-primary" onclick="addToCart(${product.id})">
                    Add to Cart
                </button>
            </div>
        </div>
    `).join('');
}

// Search Products
function searchProducts() {
    loadProducts();
}

// Filter by Category
function filterByCategory() {
    loadProducts();
}

// Add to Cart
async function addToCart(productId) {
    if (!token) {
        showToast('Please login to add items to cart', 'error');
        showPage('login');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/cart/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ productId, quantity: 1 })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Added to cart!');
            updateCartCount();
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        showToast('Failed to add to cart', 'error');
    }
}

// Load Cart
async function loadCart() {
    if (!token) {
        document.getElementById('empty-cart').style.display = 'block';
        document.getElementById('cart-items').innerHTML = '';
        document.getElementById('cart-summary').style.display = 'none';
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/cart`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            cart = data.data;
            displayCart(cart);
            updateCartCount();
        }
    } catch (error) {
        console.error('Failed to load cart:', error);
    }
}

// Display Cart
function displayCart(items) {
    const cartItems = document.getElementById('cart-items');
    const cartSummary = document.getElementById('cart-summary');
    const emptyCart = document.getElementById('empty-cart');
    
    if (items.length === 0) {
        cartItems.innerHTML = '';
        cartSummary.style.display = 'none';
        emptyCart.style.display = 'block';
        return;
    }
    
    emptyCart.style.display = 'none';
    cartSummary.style.display = 'block';
    
    let total = 0;
    
    cartItems.innerHTML = items.map(item => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;
        
        return `
            <div class="cart-item">
                <img src="${item.image}" alt="${item.name}">
                <div class="cart-item-info">
                    <h3>${item.name}</h3>
                    <p>₹${item.price} each</p>
                    <div class="cart-item-controls">
                        <button onclick="updateCartQuantity(${item.id}, ${item.quantity - 1})">-</button>
                        <input type="number" value="${item.quantity}" min="1" 
                               onchange="updateCartQuantity(${item.id}, this.value)" readonly>
                        <button onclick="updateCartQuantity(${item.id}, ${item.quantity + 1})">+</button>
                        <button class="btn-danger" onclick="removeFromCart(${item.id})">Remove</button>
                    </div>
                </div>
                <div>
                    <strong>₹${itemTotal}</strong>
                </div>
            </div>
        `;
    }).join('');
    
    document.getElementById('cart-total').textContent = total;
}

// Update Cart Quantity
async function updateCartQuantity(productId, quantity) {
    if (quantity < 1) {
        removeFromCart(productId);
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/cart/${productId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ quantity: parseInt(quantity) })
        });
        
        const data = await response.json();
        
        if (data.success) {
            loadCart();
        }
    } catch (error) {
        showToast('Failed to update cart', 'error');
    }
}

// Remove from Cart
async function removeFromCart(productId) {
    try {
        const response = await fetch(`${API_URL}/cart/${productId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Item removed from cart');
            loadCart();
        }
    } catch (error) {
        showToast('Failed to remove item', 'error');
    }
}

// Update Cart Count
async function updateCartCount() {
    if (!token) {
        document.getElementById('cart-count').textContent = '0';
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/cart`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            const count = data.data.reduce((sum, item) => sum + item.quantity, 0);
            document.getElementById('cart-count').textContent = count;
        }
    } catch (error) {
        console.error('Failed to update cart count:', error);
    }
}

// Checkout
async function checkout() {
    try {
        const response = await fetch(`${API_URL}/orders`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Order placed successfully!');
            loadCart();
            showPage('orders');
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        showToast('Checkout failed. Please try again.', 'error');
    }
}

// Load Orders
async function loadOrders() {
    try {
        const response = await fetch(`${API_URL}/orders`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayOrders(data.data);
        }
    } catch (error) {
        console.error('Failed to load orders:', error);
    }
}

// Display Orders
function displayOrders(orders) {
    const ordersList = document.getElementById('orders-list');
    
    if (orders.length === 0) {
        ordersList.innerHTML = '<p>No orders yet. <a href="#" onclick="showPage(\'products\')">Start shopping</a></p>';
        return;
    }
    
    ordersList.innerHTML = orders.reverse().map(order => `
        <div class="order-card">
            <div class="order-header">
                <div>
                    <h3>Order #${order.id}</h3>
                    <p>${new Date(order.date).toLocaleDateString()}</p>
                </div>
                <span class="order-status ${order.status.toLowerCase()}">${order.status}</span>
            </div>
            <div class="order-items">
                ${order.items.map(item => `
                    <div class="order-item">
                        <strong>${item.name}</strong> - 
                        Qty: ${item.quantity} - 
                        ₹${item.price} x ${item.quantity} = ₹${item.price * item.quantity}
                    </div>
                `).join('')}
            </div>
            <div class="order-total">
                Total: ₹${order.total}
            </div>
        </div>
    `).join('');
}

// Initialize cart count
updateCartCount();
