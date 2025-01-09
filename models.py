from mongoengine import Document, StringField, FloatField, IntField, ReferenceField, ListField, EmbeddedDocument, EmbeddedDocumentField, DateTimeField, DictField
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, Document):
    email = StringField(required=True, unique=True)
    password_hash = StringField(required=True)
    name = StringField(required=True)
    role = StringField(required=True, choices=['customer', 'seller', 'admin'])
    phone_number = StringField()
    address = StringField()
    city = StringField()
    state = StringField()
    pincode = StringField()
    created_at = DateTimeField(default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(Document):
    name = StringField(required=True)
    description = StringField()
    price = FloatField(required=True)
    stock = IntField(required=True, min_value=0)
    category = StringField()
    seller = ReferenceField(User)
    image = StringField(default="/static/images/placeholder.png")
    created_at = DateTimeField(default=datetime.utcnow)

class CartItem(EmbeddedDocument):
    product = ReferenceField(Product)
    quantity = IntField(min_value=1, default=1)

class Cart(Document):
    user = ReferenceField(User)
    items = ListField(EmbeddedDocumentField(CartItem))
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    def add_item(self, product, quantity=1):
        cart_item = next((item for item in self.items if item.product == product), None)
        if cart_item:
            cart_item.quantity += quantity
        else:
            self.items.append(CartItem(product=product, quantity=quantity))
        self.updated_at = datetime.utcnow()
        self.save()

    def remove_item(self, product):
        self.items = [item for item in self.items if item.product != product]
        self.updated_at = datetime.utcnow()
        self.save()

    def get_total(self):
        return sum(item.product.price * item.quantity for item in self.items)

class Order(Document):
    customer = ReferenceField(User)
    products = ListField(EmbeddedDocumentField(CartItem))
    total_price = FloatField(required=True)
    status = StringField(required=True, choices=['pending', 'paid', 'dispatched', 'out_for_delivery', 'delivered', 'cancelled'])
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    delivery_address = DictField()

