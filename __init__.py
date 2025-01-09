from flask import Flask
from mongoengine import connect
from flask_login import LoginManager
from config import Config
from flask import render_template
import os
from PIL import Image

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Connect to MongoDB
    connect(host=app.config['MONGODB_SETTINGS']['host'])

    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Ensure the images folder exists
    images_folder = os.path.join(app.static_folder, 'images')
    os.makedirs(images_folder, exist_ok=True)

    # Ensure the placeholder image exists
    placeholder_path = os.path.join(images_folder, 'placeholder.png')
    if not os.path.exists(placeholder_path):
        # If the default placeholder doesn't exist, create a simple one
        img = Image.new('RGB', (200, 200), color = (73, 109, 137))
        img.save(placeholder_path)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    with app.app_context():
        from app.routes import admin, auth, customer, seller
        app.register_blueprint(admin.bp)
        app.register_blueprint(auth.bp)
        app.register_blueprint(customer.bp)
        app.register_blueprint(seller.bp)

    @app.context_processor
    def inject_globals():
        return {
            "app_name": "GrocerEase"
        }

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500

    return app

