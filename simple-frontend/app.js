const API_URL = 'http://localhost:5000';

const STORAGE_KEYS = {
    customerToken: 'mm_customer_token',
    customerUser: 'mm_customer_user',
    pharmacyToken: 'mm_pharmacy_token',
    pharmacyUser: 'mm_pharmacy_user',
    adminToken: 'mm_admin_token',
    adminUser: 'mm_admin_user',
    cart: 'mm_cart',
    prescription: 'mm_prescription_id'
};

let customerToken = localStorage.getItem(STORAGE_KEYS.customerToken);
let currentCustomer = safeJsonParse(localStorage.getItem(STORAGE_KEYS.customerUser));
let pharmacyToken = localStorage.getItem(STORAGE_KEYS.pharmacyToken);
let currentPharmacy = safeJsonParse(localStorage.getItem(STORAGE_KEYS.pharmacyUser));
let adminToken = localStorage.getItem(STORAGE_KEYS.adminToken);
let currentAdmin = safeJsonParse(localStorage.getItem(STORAGE_KEYS.adminUser));
let cart = safeJsonParse(localStorage.getItem(STORAGE_KEYS.cart)) || [];
let currentResults = [];
let lastPrescriptionId = localStorage.getItem(STORAGE_KEYS.prescription);
let adminPharmacies = [];
let adminStatus = 'PENDING';
const medicineCategories = [
    'Pain Relief',
    'Vitamins',
    'Hygiene',
    'Devices',
    'First Aid',
    'Supplements',
    'Safety'
];
let selectedCategory = '';
const categoryImages = {
    'Pain Relief': "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='90' viewBox='0 0 120 90'><rect width='120' height='90' rx='12' fill='%23e0f2fe'/><rect x='28' y='34' width='64' height='22' rx='11' fill='%230f766e'/><rect x='34' y='39' width='24' height='12' rx='6' fill='%23ffffff'/></svg>",
    'Vitamins': "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='90' viewBox='0 0 120 90'><rect width='120' height='90' rx='12' fill='%23fef9c3'/><rect x='46' y='18' width='28' height='54' rx='10' fill='%23f59e0b'/><rect x='50' y='14' width='20' height='10' rx='4' fill='%230f172a'/></svg>",
    'Hygiene': "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='90' viewBox='0 0 120 90'><rect width='120' height='90' rx='12' fill='%23dcfce7'/><path d='M60 18c10 14 16 24 16 34a16 16 0 1 1-32 0c0-10 6-20 16-34z' fill='%2316a34a'/></svg>",
    'Devices': "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='90' viewBox='0 0 120 90'><rect width='120' height='90' rx='12' fill='%23e2e8f0'/><circle cx='42' cy='50' r='14' stroke='%230f172a' stroke-width='6' fill='none'/><path d='M56 50h20c8 0 12-6 12-12' stroke='%230f172a' stroke-width='6' fill='none' stroke-linecap='round'/></svg>",
    'First Aid': "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='90' viewBox='0 0 120 90'><rect width='120' height='90' rx='12' fill='%23fee2e2'/><rect x='50' y='26' width='20' height='38' fill='%23ef4444'/><rect x='41' y='35' width='38' height='20' fill='%23ef4444'/></svg>",
    'Supplements': "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='90' viewBox='0 0 120 90'><rect width='120' height='90' rx='12' fill='%23ede9fe'/><rect x='34' y='36' width='28' height='18' rx='9' fill='%236366f1'/><rect x='58' y='36' width='28' height='18' rx='9' fill='%23a5b4fc'/></svg>",
    'Safety': "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='90' viewBox='0 0 120 90'><rect width='120' height='90' rx='12' fill='%23ffedd5'/><path d='M60 18l26 10v16c0 18-12 28-26 34-14-6-26-16-26-34V28l26-10z' fill='%23f97316'/></svg>"
};

function isCustomerActive() {
    return Boolean(customerToken);
}

function isPharmacyActive() {
    return Boolean(pharmacyToken);
}

function isAdminActive() {
    return Boolean(adminToken);
}

const placeholderImage = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='260'><rect width='100%' height='100%' fill='%23f3f4f6'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' fill='%236b7280' font-size='24' font-family='Arial'>Medicine</text></svg>";

function safeJsonParse(value) {
    try {
        return value ? JSON.parse(value) : null;
    } catch {
        return null;
    }
}

function saveCart() {
    localStorage.setItem(STORAGE_KEYS.cart, JSON.stringify(cart));
}

function setCustomer(user, newToken) {
    currentCustomer = user;
    customerToken = newToken;
    localStorage.setItem(STORAGE_KEYS.customerUser, JSON.stringify(user));
    localStorage.setItem(STORAGE_KEYS.customerToken, newToken);
}

function setPharmacy(user, newToken) {
    currentPharmacy = user;
    pharmacyToken = newToken;
    localStorage.setItem(STORAGE_KEYS.pharmacyUser, JSON.stringify(user));
    localStorage.setItem(STORAGE_KEYS.pharmacyToken, newToken);
}

function setAdmin(user, newToken) {
    currentAdmin = user;
    adminToken = newToken;
    localStorage.setItem(STORAGE_KEYS.adminUser, JSON.stringify(user));
    localStorage.setItem(STORAGE_KEYS.adminToken, newToken);
}

function clearCustomerAuth() {
    customerToken = null;
    currentCustomer = null;
    localStorage.removeItem(STORAGE_KEYS.customerToken);
    localStorage.removeItem(STORAGE_KEYS.customerUser);
}

function clearPharmacyAuth() {
    pharmacyToken = null;
    currentPharmacy = null;
    localStorage.removeItem(STORAGE_KEYS.pharmacyToken);
    localStorage.removeItem(STORAGE_KEYS.pharmacyUser);
}

function clearAdminAuth() {
    adminToken = null;
    currentAdmin = null;
    localStorage.removeItem(STORAGE_KEYS.adminToken);
    localStorage.removeItem(STORAGE_KEYS.adminUser);
}

function clearCustomerState() {
    cart = [];
    lastPrescriptionId = null;
    localStorage.removeItem(STORAGE_KEYS.cart);
    localStorage.removeItem(STORAGE_KEYS.prescription);
    updateCartCount();
}

function setExclusiveRole(role) {
    if (role !== 'customer' && isCustomerActive()) {
        clearCustomerAuth();
        clearCustomerState();
    }
    if (role !== 'pharmacy' && isPharmacyActive()) {
        clearPharmacyAuth();
    }
    if (role !== 'admin' && isAdminActive()) {
        clearAdminAuth();
    }
    updateRoleUI();
}

function getAuthHeaders(role) {
    if (role === 'pharmacy') {
        return pharmacyToken ? { 'Authorization': `Bearer ${pharmacyToken}` } : {};
    }
    if (role === 'admin') {
        return adminToken ? { 'Authorization': `Bearer ${adminToken}` } : {};
    }
    return customerToken ? { 'Authorization': `Bearer ${customerToken}` } : {};
}

// Loading overlay functions
function showLoading() {
    document.getElementById('loading-overlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    if (customerToken && currentCustomer) {
        checkAuth();
    } else {
        updateAuthUI(false);
    }

    updateRoleUI();

    loadProducts();
    renderCategoryCards();
    showPage('home');
    updateCartCount();

    document.documentElement.style.scrollBehavior = 'smooth';
});

// Show/Hide Pages
function showPage(pageName) {
    if (isAdminActive() && ['login', 'register', 'pharmacy-login', 'pharmacy-register', 'pharmacy-dashboard', 'products', 'cart', 'orders'].includes(pageName)) {
        showToast('Admin session active. Logout to switch roles.', 'error');
        return;
    }

    if (isPharmacyActive() && ['login', 'register', 'products', 'cart', 'orders', 'admin-login', 'admin-dashboard'].includes(pageName)) {
        showToast('Pharmacy session active. Logout to switch roles.', 'error');
        return;
    }

    if (isCustomerActive() && ['pharmacy-login', 'pharmacy-register', 'pharmacy-dashboard', 'admin-login', 'admin-dashboard'].includes(pageName)) {
        showToast('Customer session active. Logout to switch roles.', 'error');
        return;
    }

    applyCustomerNavVisibility(pageName);

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
        if (!customerToken) {
            showToast('Please login to view orders', 'error');
            showPage('login');
            return;
        }
        loadOrders();
    } else if (pageName === 'pharmacy-dashboard') {
        if (!pharmacyToken) {
            showPage('pharmacy-login');
            return;
        }
        loadPharmacyOrders();
        loadPharmacyStock();
    } else if (pageName === 'admin-dashboard') {
        if (!adminToken) {
            showPage('admin-login');
            return;
        }
        updateAdminHeader();
        loadAdminPharmacies();
    }
}

function applyCustomerNavVisibility(pageName) {
    const adminLink = document.getElementById('admin-link');
    const pharmacyLink = document.getElementById('pharmacy-link');
    const cartLink = document.getElementById('cart-link');
    const customerPages = ['login', 'register', 'products', 'cart', 'orders'];

    if (customerPages.includes(pageName)) {
        if (adminLink) adminLink.style.display = 'none';
        if (pharmacyLink) pharmacyLink.style.display = 'none';
        if (cartLink && !customerToken) cartLink.style.display = 'none';
    } else {
        updateRoleUI();
    }
}
function showPharmacyPortal() {
    if (isAdminActive()) {
        showToast('Admin session active. Logout to switch roles.', 'error');
        return;
    }
    if (isCustomerActive()) {
        const category = selectedCategory || document.getElementById('category-filter')?.value || '';
        showToast('Customer session active. Logout to switch roles.', 'error');
        return;
    }
    if (pharmacyToken) {
        showPage('pharmacy-dashboard');
    } else {
        showPage('pharmacy-login');
    }
}

function showAdminPortal() {
    if (isPharmacyActive()) {
        showToast('Pharmacy session active. Logout to switch roles.', 'error');
        return;
    }
    if (isCustomerActive()) {
        showToast('Customer session active. Logout to switch roles.', 'error');
        return;
    }
    if (adminToken) {
        showPage('admin-dashboard');
    } else {
        showPage('admin-login');
    }
}

function updateAdminHeader() {
    const pincodeEl = document.getElementById('admin-pincode');
    if (!pincodeEl) {
        return;
    }
    if (currentAdmin && currentAdmin.pincode) {
        pincodeEl.textContent = `Pincode: ${currentAdmin.pincode}`;
    } else {
        pincodeEl.textContent = '';
    }
}

function updateRoleUI() {
    const adminLink = document.getElementById('admin-link');
    const pharmacyLink = document.getElementById('pharmacy-link');
    const cartLink = document.getElementById('cart-link');
    const ordersLink = document.getElementById('orders-link');

    if (isAdminActive()) {
        if (adminLink) adminLink.style.display = 'block';
        if (pharmacyLink) pharmacyLink.style.display = 'none';
        if (cartLink) cartLink.style.display = 'none';
        if (ordersLink) ordersLink.style.display = 'none';
    } else if (isPharmacyActive()) {
        if (adminLink) adminLink.style.display = 'none';
        if (pharmacyLink) pharmacyLink.style.display = 'block';
        if (cartLink) cartLink.style.display = 'none';
        if (ordersLink) ordersLink.style.display = 'none';
    } else {
        if (adminLink) adminLink.style.display = 'block';
        if (pharmacyLink) pharmacyLink.style.display = 'block';
        if (cartLink) cartLink.style.display = 'block';
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
async function handlePrescriptionUpload(event) {
    const file = event.target.files[0];
    if (!file) {
        return;
    }

    if (!customerToken) {
        showToast('Please login to upload a prescription', 'error');
        showPage('login');
        event.target.value = '';
        return;
    }

    const doctorName = prompt('Enter doctor name');
    if (!doctorName) {
        showToast('Doctor name is required', 'error');
        event.target.value = '';
        return;
    }

    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'application/pdf'];
    if (!validTypes.includes(file.type)) {
        showToast('Please upload a valid image (JPG, PNG, GIF) or PDF file', 'error');
        event.target.value = '';
        return;
    }

    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
        showToast('File size must be less than 5MB', 'error');
        event.target.value = '';
        return;
    }

    try {
        const formData = new FormData();
        formData.append('doctor_name', doctorName);
        formData.append('file', file);

        const response = await fetch(`${API_URL}/prescriptions`, {
            method: 'POST',
            headers: {
                ...getAuthHeaders('customer')
            },
            body: formData
        });

        const data = await response.json();
        if (!response.ok) {
            showToast(data.error || 'Upload failed', 'error');
            return;
        }

        lastPrescriptionId = data.prescription_id;
        localStorage.setItem(STORAGE_KEYS.prescription, String(lastPrescriptionId));
        showToast('Prescription uploaded successfully');
    } catch (error) {
        showToast('Upload failed. Please try again.', 'error');
    } finally {
        event.target.value = '';
    }
}

// Check Authentication
async function checkAuth() {
    if (!currentCustomer) {
        updateAuthUI(false);
        return;
    }

    try {
        const response = await fetch(`${API_URL}/orders/customer/${currentCustomer.customer_id}`, {
            headers: {
                ...getAuthHeaders('customer')
            }
        });

        if (response.ok) {
            updateAuthUI(true);
        } else {
            logout();
        }
    } catch (error) {
        updateAuthUI(false);
    }
}

// Update UI based on auth status
function updateAuthUI(isLoggedIn) {
    if (isLoggedIn) {
        document.getElementById('login-link').style.display = 'none';
        document.getElementById('logout-link').style.display = 'block';
        document.getElementById('orders-link').style.display = 'block';
        document.getElementById('user-name').style.display = 'block';
        const displayName = currentCustomer ? `${currentCustomer.first_name} ${currentCustomer.last_name}` : 'User';
        document.getElementById('user-name').textContent = displayName.trim();
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

    setExclusiveRole('customer');

    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    try {
        const response = await fetch(`${API_URL}/auth/customer/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();
        if (!response.ok) {
            showToast(data.error || 'Login failed', 'error');
            return;
        }

        setCustomer(data.customer, data.token);
        updateAuthUI(true);
        updateRoleUI();
        showToast('Login successful');
            showPage('products');
    } catch (error) {
        showToast('Login failed. Please try again.', 'error');
    }
}

// Register
async function register(event) {
    event.preventDefault();

    setExclusiveRole('customer');

    const first_name = document.getElementById('register-first-name').value;
    const last_name = document.getElementById('register-last-name').value;
    const email = document.getElementById('register-email').value;
    const phone = document.getElementById('register-phone').value;
    const street = document.getElementById('register-street').value;
    const pincode = document.getElementById('register-pincode').value;
    const city_id = parseInt(document.getElementById('register-city-id').value, 10);
    const password = document.getElementById('register-password').value;

    if (Number.isNaN(city_id)) {
        showToast('City ID must be a number', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/auth/customer/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                first_name,
                last_name,
                email,
                phone,
                street,
                pincode,
                city_id,
                password
            })
        });

        const data = await response.json();
        if (!response.ok) {
            showToast(data.error || 'Registration failed', 'error');
            return;
        }

        setCustomer(
            { customer_id: data.customer_id, first_name, last_name, email },
            data.token
        );
        updateAuthUI(true);
        updateRoleUI();
        showToast('Registration successful');
            showPage('products');
    } catch (error) {
        showToast('Registration failed. Please try again.', 'error');
    }
}

// Logout
function logout() {
    clearCustomerAuth();
    clearCustomerState();
    updateAuthUI(false);
    updateRoleUI();
    updateCartCount();
    showToast('Logged out successfully');
    showPage('home');
}

// Load Products
async function loadProducts() {
    showLoading();
    try {
        const search = document.getElementById('search-input')?.value || '';
        const cityId = document.getElementById('city-filter')?.value || '';
        const pincode = document.getElementById('pincode-filter')?.value || '';
        const category = selectedCategory || document.getElementById('category-filter')?.value || '';

        const params = new URLSearchParams();
        if (search) params.append('name', search);
        if (category) params.append('category', category);
        if (cityId) params.append('city_id', cityId);
        if (pincode) params.append('pincode', pincode);

        const response = await fetch(`${API_URL}/medicines/search?${params.toString()}`);
        const data = await response.json();

        if (response.ok) {
            currentResults = data.results || [];
            displayProducts(currentResults);
        } else {
            showToast(data.error || 'Failed to load medicines', 'error');
        }
    } catch (error) {
        showToast('Failed to load medicines', 'error');
    } finally {
        hideLoading();
    }
}

// Display Products
function displayProducts(products) {
    const grid = document.getElementById('products-grid');

    if (!products || products.length === 0) {
        grid.innerHTML = '<p>No medicines found.</p>';
        return;
    }

    grid.innerHTML = `
        <div class="product-list">
            <div class="product-row product-head">
                <span>Medicine</span>
                <span>Category</span>
                <span>Pharmacy</span>
                <span>Pincode</span>
                <span>Price</span>
                <span>Stock</span>
                <span>Rx</span>
                <span>Action</span>
            </div>
            ${products.map(product => `
                <div class="product-row">
                    <div class="product-main">
                        <strong>${product.medicine_name}</strong>
                        <small>${product.description || 'No description available.'}</small>
                    </div>
                    <span>${product.category || 'Other'}</span>
                    <span>${product.pharmacy_name}</span>
                    <span>${product.pincode}</span>
                    <span>₹${product.price}</span>
                    <span>${product.stock_quantity}</span>
                    <span>${product.requires_prescription ? 'Yes' : 'No'}</span>
                    <button class="btn btn-primary" onclick="addToCart(${product.medicine_id})">Add</button>
                </div>
            `).join('')}
        </div>
    `;
}

// Search Products
function searchProducts() {
    loadProducts();
}

function renderCategoryCards() {
    const grid = document.getElementById('category-grid');
    if (!grid) {
        return;
    }

    grid.innerHTML = medicineCategories.map(category => `
        <button class="category-card" onclick="selectCategory('${category}')">
            <img src="${categoryImages[category] || placeholderImage}" alt="${category}">
            <span>${category}</span>
        </button>
    `).join('');
}

function selectCategory(category) {
    selectedCategory = category;
    const input = document.getElementById('category-filter');
    if (input) {
        input.value = category;
    }
    document.querySelectorAll('.category-card').forEach(card => {
        card.classList.toggle('active', card.textContent.trim() === category);
    });
    loadProducts();
}

// Add to Cart
function addToCart(medicineId) {
    if (!customerToken) {
        showToast('Please login to add items to cart', 'error');
        showPage('login');
        return;
    }

    const medicine = currentResults.find(item => item.medicine_id === medicineId);
    if (!medicine) {
        showToast('Medicine not found', 'error');
        return;
    }

    if (cart.length > 0 && cart[0].pharmacy_id !== medicine.pharmacy_id) {
        const confirmClear = window.confirm('Cart has items from another pharmacy. Clear cart to add this item?');
        if (!confirmClear) {
            return;
        }
        cart = [];
    }

    const existing = cart.find(item => item.medicine_id === medicine.medicine_id);
    if (existing) {
        existing.quantity += 1;
    } else {
        cart.push({
            medicine_id: medicine.medicine_id,
            medicine_name: medicine.medicine_name,
            price: Number(medicine.price),
            quantity: 1,
            pharmacy_id: medicine.pharmacy_id,
            pharmacy_name: medicine.pharmacy_name,
            requires_prescription: Boolean(medicine.requires_prescription)
        });
    }

    saveCart();
    updateCartCount();
    showToast('Added to cart');
}

// Load Cart
function loadCart() {
    if (!customerToken) {
        document.getElementById('empty-cart').style.display = 'block';
        document.getElementById('cart-items').innerHTML = '';
        document.getElementById('cart-summary').style.display = 'none';
        return;
    }

    displayCart(cart);
    updateCartCount();
}

// Display Cart
function displayCart(items) {
    const cartItems = document.getElementById('cart-items');
    const cartSummary = document.getElementById('cart-summary');
    const emptyCart = document.getElementById('empty-cart');

    if (!items || items.length === 0) {
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
                <img src="${placeholderImage}" alt="Medicine">
                <div class="cart-item-info">
                    <h3>${item.medicine_name}</h3>
                    <p>Pharmacy: ${item.pharmacy_name}</p>
                    <p>₹${item.price} each</p>
                    <div class="cart-item-controls">
                        <button onclick="updateCartQuantity(${item.medicine_id}, ${item.quantity - 1})">-</button>
                        <input type="number" value="${item.quantity}" min="1" readonly>
                        <button onclick="updateCartQuantity(${item.medicine_id}, ${item.quantity + 1})">+</button>
                        <button class="btn-danger" onclick="removeFromCart(${item.medicine_id})">Remove</button>
                    </div>
                </div>
                <div>
                    <strong>₹${itemTotal}</strong>
                </div>
            </div>
        `;
    }).join('');

    document.getElementById('cart-total').textContent = total.toFixed(2);
}

// Update Cart Quantity
function updateCartQuantity(medicineId, quantity) {
    const item = cart.find(entry => entry.medicine_id === medicineId);
    if (!item) {
        return;
    }

    if (quantity < 1) {
        removeFromCart(medicineId);
        return;
    }

    item.quantity = quantity;
    saveCart();
    displayCart(cart);
    updateCartCount();
}

// Remove from Cart
function removeFromCart(medicineId) {
    cart = cart.filter(entry => entry.medicine_id !== medicineId);
    saveCart();
    displayCart(cart);
    updateCartCount();
    showToast('Item removed from cart');
}

// Update Cart Count
function updateCartCount() {
    const count = cart.reduce((sum, item) => sum + item.quantity, 0);
    const cartCount = document.getElementById('cart-count');
    if (cartCount) {
        cartCount.textContent = String(count);
    }
}

// Checkout
async function checkout() {
    if (!customerToken) {
        showToast('Please login to place an order', 'error');
        showPage('login');
        return;
    }

    if (!cart.length) {
        showToast('Cart is empty', 'error');
        return;
    }

    const needsPrescription = cart.some(item => item.requires_prescription);
    if (needsPrescription && !lastPrescriptionId) {
        showToast('Prescription required for selected items', 'error');
        return;
    }

    const payload = {
        pharmacy_id: cart[0].pharmacy_id,
        items: cart.map(item => ({
            medicine_id: item.medicine_id,
            quantity: item.quantity
        })),
        prescription_id: needsPrescription ? Number(lastPrescriptionId) : null
    };

    try {
        const response = await fetch(`${API_URL}/orders`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders('customer')
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        if (!response.ok) {
            showToast(data.error || 'Checkout failed', 'error');
            return;
        }

        cart = [];
        lastPrescriptionId = null;
        localStorage.removeItem(STORAGE_KEYS.cart);
        localStorage.removeItem(STORAGE_KEYS.prescription);
        updateCartCount();
        showToast('Order placed successfully');
        showPage('orders');
    } catch (error) {
        showToast('Checkout failed. Please try again.', 'error');
    }
}

// Load Orders
async function loadOrders() {
    if (!currentCustomer) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/orders/customer/${currentCustomer.customer_id}`, {
            headers: {
                ...getAuthHeaders('customer')
            }
        });

        const data = await response.json();
        if (response.ok) {
            displayOrders(data.orders || []);
        } else {
            showToast(data.error || 'Failed to load orders', 'error');
        }
    } catch (error) {
        showToast('Failed to load orders', 'error');
    }
}

// Display Orders
function displayOrders(orders) {
    const ordersList = document.getElementById('orders-list');

    if (!orders || orders.length === 0) {
        ordersList.innerHTML = '<p>No orders yet. <a href="#" onclick="showPage(\'products\')">Start shopping</a></p>';
        return;
    }

    ordersList.innerHTML = orders.map(order => `
        <div class="order-card" onclick="toggleOrderDetails(${order.order_id})">
            <div class="order-header">
                <div>
                    <h3>Order #${order.order_id}</h3>
                    <p>${new Date(order.order_date).toLocaleDateString()}</p>
                    <p>${order.pharmacy_name}</p>
                </div>
                <span class="order-status ${String(order.order_status).toLowerCase()}">${order.order_status}</span>
            </div>
            <div id="order-details-${order.order_id}" class="order-details" style="display:none;"></div>
        </div>
    `).join('');
}

async function toggleOrderDetails(orderId) {
    const container = document.getElementById(`order-details-${orderId}`);
    if (!container) {
        return;
    }

    if (container.dataset.loaded === 'true') {
        container.style.display = container.style.display === 'none' ? 'block' : 'none';
        return;
    }

    try {
        const response = await fetch(`${API_URL}/orders/${orderId}`, {
            headers: {
                ...getAuthHeaders('customer')
            }
        });
        const data = await response.json();
        if (!response.ok) {
            showToast(data.error || 'Failed to load order details', 'error');
            return;
        }

        const items = data.items || [];
        const order = data.order || {};
        const total = items.reduce((sum, item) => sum + Number(item.subtotal || 0), 0);
        container.innerHTML = `
            <div class="order-items">
                ${items.map(item => `
                    <div class="order-item">
                        <strong>${item.medicine_name}</strong>
                        <span>Qty: ${item.quantity}</span>
                        <span>Unit: ₹${Number(item.unit_price || 0).toFixed(2)}</span>
                        <span>Subtotal: ₹${Number(item.subtotal || 0).toFixed(2)}</span>
                    </div>
                `).join('')}
            </div>
            <div class="order-meta">
                <span>Pharmacy: ${order.pharmacy_name || ''}</span>
                <span>Status: ${order.order_status || ''}</span>
            </div>
            <div class="order-total">Total: ₹${total.toFixed(2)}</div>
        `;
        container.dataset.loaded = 'true';
        container.style.display = 'block';
    } catch (error) {
        showToast('Failed to load order details', 'error');
    }
}

// Initialize cart count
updateCartCount();

// -----------------------------
// Pharmacy UI
// -----------------------------

async function pharmacyLogin(event) {
    event.preventDefault();

    setExclusiveRole('pharmacy');

    const email = document.getElementById('pharmacy-login-email').value;
    const password = document.getElementById('pharmacy-login-password').value;

    try {
        const response = await fetch(`${API_URL}/auth/pharmacy/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();
        if (!response.ok) {
            showToast(data.error || 'Login failed', 'error');
            return;
        }

        setPharmacy(data.pharmacy, data.token);
        showToast('Pharmacy login successful');
        updateRoleUI();
        showPage('pharmacy-dashboard');
    } catch (error) {
        showToast('Login failed. Please try again.', 'error');
    }
}

async function pharmacyRegister(event) {
    event.preventDefault();

    setExclusiveRole('pharmacy');

    const pharmacy_name = document.getElementById('pharmacy-name').value;
    const license_number = document.getElementById('pharmacy-license').value;
    const email = document.getElementById('pharmacy-email').value;
    const phone = document.getElementById('pharmacy-phone').value;
    const street = document.getElementById('pharmacy-street').value;
    const pincode = document.getElementById('pharmacy-pincode').value;
    const city_id = parseInt(document.getElementById('pharmacy-city-id').value, 10);
    const password = document.getElementById('pharmacy-password').value;

    if (Number.isNaN(city_id)) {
        showToast('City ID must be a number', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/auth/pharmacy/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                pharmacy_name,
                license_number,
                email,
                phone,
                street,
                pincode,
                city_id,
                password
            })
        });

        const data = await response.json();
        if (!response.ok) {
            showToast(data.error || 'Registration failed', 'error');
            return;
        }

        showToast('Registration submitted. Wait for admin approval.');
        updateRoleUI();
        showPage('pharmacy-login');
    } catch (error) {
        showToast('Registration failed. Please try again.', 'error');
    }
}

function pharmacyLogout() {
    clearPharmacyAuth();
    showToast('Pharmacy logged out');
    updateRoleUI();
    showPage('pharmacy-login');
}

async function loadPharmacyOrders() {
    if (!pharmacyToken) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/pharmacy/orders`, {
            headers: {
                ...getAuthHeaders('pharmacy')
            }
        });

        const data = await response.json();
        if (!response.ok) {
            showToast(data.error || 'Failed to load orders', 'error');
            return;
        }

        displayPharmacyOrders(data.orders || []);
    } catch (error) {
        showToast('Failed to load orders', 'error');
    }
}

function displayPharmacyOrders(orders) {
    const container = document.getElementById('pharmacy-orders');
    if (!orders.length) {
        container.innerHTML = '<p>No orders yet.</p>';
        return;
    }

    container.innerHTML = orders.map(order => `
        <div class="order-card">
            <div class="order-header">
                <div>
                    <h3>Order #${order.order_id}</h3>
                    <p>${new Date(order.order_date).toLocaleString()}</p>
                    <p>${order.first_name} ${order.last_name}</p>
                </div>
                <span class="order-status ${String(order.order_status).toLowerCase()}">${order.order_status}</span>
            </div>
            <div class="order-actions">
                <button class="btn btn-primary" onclick="updateOrderStatus(${order.order_id}, 'ACCEPTED')">Accept</button>
                <button class="btn btn-danger" onclick="updateOrderStatus(${order.order_id}, 'REJECTED')">Reject</button>
            </div>
        </div>
    `).join('');
}

async function updateOrderStatus(orderId, status) {
    try {
        const response = await fetch(`${API_URL}/orders/${orderId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders('pharmacy')
            },
            body: JSON.stringify({ order_status: status })
        });

        const data = await response.json();
        if (!response.ok) {
            showToast(data.error || 'Failed to update order', 'error');
            return;
        }

        showToast(`Order ${status.toLowerCase()}`);
        loadPharmacyOrders();
    } catch (error) {
        showToast('Failed to update order', 'error');
    }
}

async function loadPharmacyStock() {
    if (!pharmacyToken) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/pharmacy/stock`, {
            headers: {
                ...getAuthHeaders('pharmacy')
            }
        });

        const data = await response.json();
        if (!response.ok) {
            showToast(data.error || 'Failed to load stock', 'error');
            return;
        }

        displayPharmacyStock(data.medicines || []);
    } catch (error) {
        showToast('Failed to load stock', 'error');
    }
}

function displayPharmacyStock(medicines) {
    const container = document.getElementById('pharmacy-stock');
    if (!medicines.length) {
        container.innerHTML = '<p>No medicines added yet.</p>';
        return;
    }

    container.innerHTML = `
        <div class="stock-table">
            <div class="stock-row stock-head">
                <span>Name</span>
                <span>Batch</span>
                <span>MFG</span>
                <span>Price</span>
                <span>Stock</span>
                <span>Expiry</span>
                <span>Action</span>
            </div>
            ${medicines.map(med => `
                <div class="stock-row">
                    <span>${med.medicine_name}</span>
                    <input type="text" value="${med.batch_no || ''}" id="batch-${med.medicine_id}">
                    <input type="date" value="${formatDateInput(med.mfg_date)}" id="mfg-${med.medicine_id}">
                    <input type="number" step="0.01" value="${med.price}" id="price-${med.medicine_id}">
                    <input type="number" value="${med.stock_quantity}" id="stock-${med.medicine_id}">
                    <input type="date" value="${formatDateInput(med.expiry_date)}" id="expiry-${med.medicine_id}">
                    <button class="btn btn-primary" onclick="updateMedicine(${med.medicine_id})">Update</button>
                </div>
            `).join('')}
        </div>
    `;
}

function formatDateInput(dateValue) {
    if (!dateValue) {
        return '';
    }
    const date = new Date(dateValue);
    if (Number.isNaN(date.getTime())) {
        return '';
    }
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function formatDateLabel(dateValue) {
    if (!dateValue) {
        return 'N/A';
    }
    const date = new Date(dateValue);
    if (Number.isNaN(date.getTime())) {
        return 'N/A';
    }
    return date.toLocaleDateString();
}

async function addMedicine(event) {
    event.preventDefault();

    const payload = {
        medicine_name: document.getElementById('medicine-name').value,
        category: document.getElementById('medicine-category').value,
        manufacturer: document.getElementById('medicine-manufacturer').value,
        batch_no: document.getElementById('medicine-batch').value,
        mfg_date: document.getElementById('medicine-mfg').value,
        price: Number(document.getElementById('medicine-price').value),
        stock_quantity: Number(document.getElementById('medicine-stock').value),
        expiry_date: document.getElementById('medicine-expiry').value,
        requires_prescription: document.getElementById('medicine-rx').value === 'true',
        description: document.getElementById('medicine-description').value
    };

    try {
        const response = await fetch(`${API_URL}/pharmacy/stock`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders('pharmacy')
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        if (!response.ok) {
            showToast(data.error || 'Failed to add medicine', 'error');
            return;
        }

        showToast('Medicine added');
        event.target.reset();
        loadPharmacyStock();
    } catch (error) {
        showToast('Failed to add medicine', 'error');
    }
}

async function updateMedicine(medicineId) {
    const payload = {
        batch_no: document.getElementById(`batch-${medicineId}`).value,
        mfg_date: document.getElementById(`mfg-${medicineId}`).value,
        price: Number(document.getElementById(`price-${medicineId}`).value),
        stock_quantity: Number(document.getElementById(`stock-${medicineId}`).value),
        expiry_date: document.getElementById(`expiry-${medicineId}`).value
    };

    try {
        const response = await fetch(`${API_URL}/pharmacy/stock/${medicineId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders('pharmacy')
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        if (!response.ok) {
            showToast(data.error || 'Failed to update medicine', 'error');
            return;
        }

        showToast('Stock updated');
        loadPharmacyStock();
    } catch (error) {
        showToast('Failed to update medicine', 'error');
    }
}

// -----------------------------
// Admin UI
// -----------------------------

async function adminLogin(event) {
    event.preventDefault();

    setExclusiveRole('admin');

    const email = document.getElementById('admin-login-email').value;
    const password = document.getElementById('admin-login-password').value;

    try {
        const response = await fetch(`${API_URL}/auth/admin/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();
        if (!response.ok) {
            showToast(data.error || 'Login failed', 'error');
            return;
        }

        setAdmin(data.admin, data.token);
        showToast('Admin login successful');
        updateAdminHeader();
        updateRoleUI();
        showPage('admin-dashboard');
    } catch (error) {
        showToast('Login failed. Please try again.', 'error');
    }
}

function adminLogout() {
    clearAdminAuth();
    showToast('Admin logged out');
    updateRoleUI();
    showPage('admin-login');
}

async function loadAdminPharmacies() {
    if (!adminToken) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/admin/pharmacies?status=${adminStatus}`, {
            headers: {
                ...getAuthHeaders('admin')
            }
        });

        const data = await response.json();
        if (!response.ok) {
            showToast(data.error || 'Failed to load pharmacies', 'error');
            return;
        }

        adminPharmacies = data.pharmacies || [];
        renderPendingPharmacies(adminPharmacies);
    } catch (error) {
        showToast('Failed to load pharmacies', 'error');
    }
}

function setAdminStatus(status) {
    adminStatus = status;
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.toggle('active', button.dataset.status === status);
    });
    loadAdminPharmacies();
}

function filterAdminPharmacies() {
    const query = document.getElementById('admin-search').value.trim().toLowerCase();
    if (!query) {
        renderPendingPharmacies(adminPharmacies);
        return;
    }

    const filtered = adminPharmacies.filter(pharmacy => {
        const fields = [
            pharmacy.pharmacy_name,
            pharmacy.email,
            pharmacy.phone,
            pharmacy.license_number,
            pharmacy.pincode,
            pharmacy.street
        ];
        return fields.some(value => String(value || '').toLowerCase().includes(query));
    });
    renderPendingPharmacies(filtered);
}

function renderPendingPharmacies(pharmacies) {
    const container = document.getElementById('admin-pharmacies');
    if (!pharmacies.length) {
        container.innerHTML = '<p>No pending pharmacies.</p>';
        return;
    }

    container.innerHTML = pharmacies.map(pharmacy => `
        <div class="approval-card">
            <div>
                <h3>${pharmacy.pharmacy_name}</h3>
                <p>${pharmacy.email} | ${pharmacy.phone}</p>
                <p>${pharmacy.street}, ${pharmacy.pincode}</p>
                <p>License: ${pharmacy.license_number}</p>
            </div>
            <div class="approval-actions">
                ${adminStatus === 'PENDING' ? `
                    <button class="btn btn-primary" onclick="approvePharmacy(${pharmacy.pharmacy_id}, 'APPROVED')">Approve</button>
                    <button class="btn btn-danger" onclick="approvePharmacy(${pharmacy.pharmacy_id}, 'REJECTED')">Reject</button>
                ` : ''}
            </div>
        </div>
    `).join('');
}

async function approvePharmacy(pharmacyId, status) {
    try {
        const response = await fetch(`${API_URL}/admin/pharmacies/${pharmacyId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders('admin')
            },
            body: JSON.stringify({ approval_status: status })
        });

        const data = await response.json();
        if (!response.ok) {
            showToast(data.error || 'Failed to update pharmacy', 'error');
            return;
        }

        showToast(`Pharmacy ${status.toLowerCase()}`);
        loadAdminPharmacies();
    } catch (error) {
        showToast('Failed to update pharmacy', 'error');
    }
}

function goBrowseMedicines() {
    if (customerToken) {
        showPage('products');
    } else {
        showPage('login');
    }
}