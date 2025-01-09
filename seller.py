from mongoengine.errors import DoesNotExist
import os
import logging
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import Product, Order
from app.analytics import get_sales_data, generate_sales_chart, generate_top_products_chart
from app.forecasting import forecast_demand
from app.price_optimizer import optimize_price, get_market_prices, get_online_retail_prices
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = Blueprint('seller', __name__, url_prefix='/seller')

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'seller':
        abort(403)
    products = Product.objects(seller=current_user.id)
    all_orders = Order.objects().order_by('-created_at')
    recent_orders = [order for order in all_orders if any(item.product.seller == current_user.id for item in order.products)][:5]
    sales_data = get_sales_data(seller_id=current_user.id)
    sales_chart = generate_sales_chart(sales_data)
    top_products_chart = generate_top_products_chart(sales_data)
    
    total_revenue = sales_data['revenue'].sum() if not sales_data.empty else 0
    total_orders = sales_data['quantity'].sum() if not sales_data.empty else 0
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    return render_template('seller/dashboard.html', 
                           products=products, 
                           recent_orders=recent_orders,
                           sales_chart=sales_chart,
                           top_products_chart=top_products_chart,
                           total_revenue=total_revenue,
                           total_orders=total_orders,
                           avg_order_value=avg_order_value)

@bp.route('/inventory', methods=['GET', 'POST'])
@login_required
def inventory():
    if current_user.role != 'seller':
        abort(403)
    if request.method == 'POST':
        try:
            name = request.form['name']
            description = request.form['description']
            price = float(request.form['price'])
            stock = int(request.form['stock'])
            category = request.form['category']
            
            product = Product(name=name, description=description, price=price, stock=stock, category=category, seller=current_user.id)
            product.save()
            flash('Product added successfully.')
        except Exception as e:
            flash(f'Error adding product: {str(e)}', 'error')
    
    products = Product.objects(seller=current_user.id)
    return render_template('seller/inventory.html', products=products)

@bp.route('/update_stock/<product_id>', methods=['POST'])
@login_required
def update_stock(product_id):
    if current_user.role != 'seller':
        abort(403)
    try:
        product = Product.objects(id=product_id, seller=current_user.id).first()
        if not product:
            abort(404)
        new_stock = int(request.form.get('stock', 0))
        if new_stock >= 0:
            product.stock = new_stock
            product.save()
            flash(f'Stock updated for {product.name}')
        else:
            flash('Invalid stock value', 'error')
    except Exception as e:
        flash(f'Error updating stock: {str(e)}', 'error')
    return redirect(url_for('seller.inventory'))

@bp.route('/orders')
@login_required
def orders():
    if current_user.role != 'seller':
        abort(403)
    
    # First, get all the products of the current seller
    seller_products = Product.objects(seller=current_user.id)
    
    # Then, find all orders that contain any of these products
    orders = Order.objects(products__product__in=seller_products).order_by('-created_at')
    
    return render_template('seller/orders.html', orders=orders)

@bp.route('/forecast/<product_id>')
@login_required
def product_forecast(product_id):
    if current_user.role != 'seller':
        abort(403)
    try:
        product = Product.objects(id=product_id, seller=current_user.id).first()
        if not product:
            abort(404)
        forecast = forecast_demand(product)
        
        if forecast is None:
            flash('Not enough sales data for forecasting.')
            return redirect(url_for('seller.inventory'))
        
        return render_template('seller/forecast.html', product=product, forecast=forecast)
    except Exception as e:
        logger.error(f"Error generating forecast: {str(e)}")
        flash(f'Error generating forecast: {str(e)}', 'error')
        return redirect(url_for('seller.inventory'))

@bp.route('/optimize_price/<product_id>', methods=['GET', 'POST'])
@login_required
def optimize_price_route(product_id):
    if current_user.role != 'seller':
        abort(403)
    
    product = Product.objects(id=product_id, seller=current_user.id).first()
    if not product:
        abort(404)
    
    if request.method == 'POST':
        production_cost = float(request.form['production_cost'])
        min_price = float(request.form['min_price'])
        max_price = float(request.form['max_price'])

        logger.info(f"Optimizing price for product: {product.name}")
        logger.debug(f"Input parameters: production_cost={production_cost}, min_price={min_price}, max_price={max_price}")

        try:
            market_prices = get_market_prices(product.name)
            online_prices = get_online_retail_prices(product.name)
            
            logger.debug(f"Market prices: {market_prices}")
            logger.debug(f"Online prices: {online_prices}")

            if not market_prices and not online_prices:
                logger.warning(f"No market or online prices found for {product.name}")
                flash('Unable to find market or online prices for this product. Please try again later.', 'warning')
                return render_template('seller/optimize_price.html', product=product)

            optimized_price = optimize_price(product.name, production_cost, min_price, max_price, market_prices, online_prices)

            if optimized_price is not None:
                logger.info(f"Optimized price for {product.name}: ₹{optimized_price:.2f}")
                return render_template('seller/optimized_price.html', 
                                       product=product,
                                       optimized_price=optimized_price, 
                                       market_prices=market_prices, 
                                       online_prices=online_prices)
            else:
                logger.warning(f"Failed to optimize price for {product.name}")
                flash('Unable to optimize price due to insufficient market data.', 'warning')
        except Exception as e:
            logger.error(f"Unexpected error during price optimization: {str(e)}")
            flash('An unexpected error occurred during price optimization. Please try again later.', 'error')

    return render_template('seller/optimize_price.html', product=product)

@bp.route('/update_price/<product_id>', methods=['POST'])
@login_required
def update_price(product_id):
    if current_user.role != 'seller':
        abort(403)
    
    product = Product.objects(id=product_id, seller=current_user.id).first()
    if not product:
        abort(404)
    
    new_price = float(request.form['new_price'])
    
    if new_price <= 0:
        flash('Invalid price. Please enter a positive number.', 'error')
    else:
        product.price = new_price
        product.save()
        flash(f'Price updated for {product.name}')
    
    return redirect(url_for('seller.inventory'))

@bp.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if current_user.role != 'seller':
        abort(403)
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        category = request.form['category']
        
        product = Product(name=name, description=description, price=price, stock=stock, category=category, seller=current_user.id)
        
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and allowed_file(image_file.filename):
                product.set_image(image_file)
        
        product.save()
        flash('Product added successfully.')
        return redirect(url_for('seller.inventory'))
    
    return render_template('seller/add_product.html')

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/order/<order_id>')
@login_required
def order_details(order_id):
    if current_user.role != 'seller':
        abort(403)
    
    try:
        order = Order.objects.get(id=order_id)
        # Check if the seller has any products in this order
        if not any(item.product.seller.id == current_user.id for item in order.products):
            abort(404)
        return render_template('seller/order_details.html', order=order)
    except DoesNotExist:
        abort(404)

@bp.route('/order/<order_id>/update_status', methods=['POST'])
@login_required
def update_order_status(order_id):
    if current_user.role != 'seller':
        abort(403)
    
    order = Order.objects.get(id=order_id)
    if not order or not any(item.product.seller == current_user for item in order.products):
        abort(404)
    
    new_status = request.form.get('status')
    if new_status == 'dispatched' and order.status == 'paid':
        order.status = new_status
        order.updated_at = datetime.utcnow()
        order.save()
        flash('Order status updated successfully.')
    else:
        flash('Invalid status update.', 'error')
    
    return redirect(url_for('seller.order_details', order_id=order_id))

