document.addEventListener('DOMContentLoaded', (event) => {
    console.log('DOM fully loaded and parsed');

    // Add to cart functionality
    const addToCartForms = document.querySelectorAll('form[action^="/add_to_cart/"]');
    addToCartForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            fetch(this.action, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Product added to cart!');
                } else {
                    alert('Error adding product to cart');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            });
        });
    });

    // Form validation for checkout
    const checkoutForm = document.getElementById('checkout-form');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', function(e) {
            e.preventDefault();
            if (validateCheckoutForm()) {
                this.submit();
            }
        });
    }

    // Form validation for login
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            if (validateLoginForm()) {
                this.submit();
            }
        });
    }

    // Form validation for registration
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            if (validateRegisterForm()) {
                this.submit();
            }
        });
    }
});

function validateCheckoutForm() {
    // Add your checkout form validation logic here
    return true;
}

function validateLoginForm() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    if (!email || !password) {
        alert('Please fill in all fields');
        return false;
    }
    
    if (!isValidEmail(email)) {
        alert('Please enter a valid email address');
        return false;
    }
    
    return true;
}

function validateRegisterForm() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const name = document.getElementById('name').value;
    
    if (!email || !password || !name) {
        alert('Please fill in all fields');
        return false;
    }
    
    if (!isValidEmail(email)) {
        alert('Please enter a valid email address');
        return false;
    }
    
    if (password.length < 8) {
        alert('Password must be at least 8 characters long');
        return false;
    }
    
    return true;
}

function isValidEmail(email) {
    const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

