from app import create_app
from app.models import User, Product, Order
from mongoengine import connect
from config import Config

app = create_app()

with app.app_context():
    # Connect to MongoDB
    connect(host=Config.MONGODB_SETTINGS['host'])

    # Create sample users
    customer = User(email="customer@example.com", name="Rahul Sharma", role="customer")
    customer.set_password("password123")
    customer.save()

    seller = User(email="seller@example.com", name="Priya Patel", role="seller")
    seller.set_password("password123")
    seller.save()

    admin = User(email="admin@example.com", name="Admin User", role="admin")
    admin.set_password("password123")
    admin.save()

    # Create sample products
    products = [
        Product(name="Tomatoes", description="Fresh, ripe tomatoes", price=40, stock=100, category="Vegetables", seller=seller, image="/static/uploads/tomato.jpg"),
        Product(name="Onions", description="Large, red onions", price=30, stock=150, category="Vegetables", seller=seller, image="/static/uploads/onion.jpg"),
        Product(name="Potatoes", description="Medium-sized potatoes", price=25, stock=200, category="Vegetables", seller=seller, image="/static/uploads/potato.jpg"),
        Product(name="Cauliflower", description="Fresh cauliflower", price=35, stock=75, category="Vegetables", seller=seller, image="/static/uploads/cauliflower.jpg"),
        Product(name="Green Beans", description="Tender green beans", price=50, stock=50, category="Vegetables", seller=seller, image="/static/uploads/green_beans.jpg"),
        Product(name="Apples", description="Kashmiri apples", price=120, stock=100, category="Fruits", seller=seller, image="/static/uploads/apple.jpg"),
        Product(name="Bananas", description="Ripe yellow bananas", price=40, stock=150, category="Fruits", seller=seller, image="/static/uploads/banana.jpg"),
        Product(name="Mangoes", description="Sweet Alphonso mangoes", price=200, stock=80, category="Fruits", seller=seller, image="/static/uploads/mango.jpg"),
        Product(name="Spinach", description="Fresh, leafy spinach", price=30, stock=100, category="Leafy Greens", seller=seller, image="/static/uploads/spinach.jpg"),
        Product(name="Coriander", description="Fresh coriander leaves", price=20, stock=100, category="Herbs", seller=seller, image="/static/uploads/coriander.jpg"),
    ]
    for product in products:
        product.save()

    print("Sample data loaded successfully!")

