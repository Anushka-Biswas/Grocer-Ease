import unittest
from app import create_app
from app.models import User, Product

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)

    def test_register_page(self):
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)

    def test_add_to_cart(self):
        # Create a test user and product
        user = User(email='test@example.com', name='Test User')
        user.set_password('password123')
        user.save()

        product = Product(name='Test Product', price=10.0, stock=100)
        product.save()

        # Log in the test user
        self.client.post('/login', data=dict(
            email='test@example.com',
            password='password123'
        ), follow_redirects=True)

        # Add the product to the cart
        response = self.client.post(f'/add_to_cart/{product.id}', data=dict(
            quantity=1
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Product', response.data)

if __name__ == '__main__':
    unittest.main()

