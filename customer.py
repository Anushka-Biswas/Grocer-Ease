from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, jsonify
from flask_login import login_required, current_user
from app.models import Product, Cart, Order
import random
from mongoengine.errors import DoesNotExist, ValidationError

bp = Blueprint('customer', __name__)

@bp.route('/')
@bp.route('/browse')
def browse():
    products = Product.objects.all()
    categories = list(set(product.category for product in products))
    recommended_products = random.sample(list(products), min(3, len(products)))
    return render_template('customer/browse.html', products=products, categories=categories, recommended_products=recommended_products)

@bp.route('/product/<product_id>')
def product_details(product_id):
    try:
        product = Product.objects.get(id=product_id)
    except DoesNotExist:
        abort(404)
    return render_template('customer/product_details.html', product=product)

@bp.route('/search')
def search():
    query = request.args.get('q', '')
    products = Product.objects(name__icontains=query)
    return render_template('customer/search_results.html', products=products, query=query)

@bp.route('/add_to_cart/<product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    try:
        product = Product.objects.get(id=product_id)
        quantity = int(request.form.get('quantity', 1))
        
        cart = Cart.objects(user=current_user.id).first()
        if not cart:
            cart = Cart(user=current_user.id)
        
        cart.add_item(product, quantity)
        flash('Product added to cart successfully!')
        return redirect(url_for('customer.browse'))
    except DoesNotExist:
        flash('Product not found', 'error')
    except Exception as e:
        flash(f'Error adding product to cart: {str(e)}', 'error')
    return redirect(url_for('customer.browse'))

@bp.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    cart = Cart.objects(user=current_user.id).first()
    if request.method == 'POST':
        for item in cart.items:
            new_quantity = int(request.form.get(f'quantity_{item.product.id}', 0))
            if new_quantity == 0:
                cart.remove_item(item.product)
            elif new_quantity != item.quantity:
                cart.add_item(item.product, new_quantity - item.quantity)
        flash('Cart updated successfully!')
        return redirect(url_for('customer.cart'))
    return render_template('customer/cart.html', cart=cart)

@bp.route('/update_cart/<product_id>', methods=['POST'])
@login_required
def update_cart(product_id):
    cart = Cart.objects(user=current_user.id).first()
    if not cart:
        return jsonify({'success': False, 'error': 'Cart not found'}), 404

    try:
        product = Product.objects.get(id=product_id)
        quantity = int(request.json.get('quantity', 0))

        if quantity == 0:
            cart.remove_item(product)
        else:
            cart.add_item(product, quantity - next((item.quantity for item in cart.items if item.product == product), 0))

        cart.save()
        return jsonify({'success': True, 'total': cart.get_total()})
    except DoesNotExist:
        return jsonify({'success': False, 'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = Cart.objects(user=current_user.id).first()
    if not cart or not cart.items:
        flash('Your cart is empty.')
        return redirect(url_for('customer.browse'))
    
    if request.method == 'POST':
        # Update user's delivery information
        current_user.phone_number = request.form.get('phone_number')
        current_user.address = request.form.get('address')
        current_user.city = request.form.get('city')
        current_user.state = request.form.get('state')
        current_user.pincode = request.form.get('pincode')
        current_user.save()

        # Process payment information (in a real application, you would integrate with a payment gateway here)
        card_number = request.form.get('card_number')
        expiry_date = request.form.get('expiry_date')
        cvv = request.form.get('cvv')

        # Simulate payment process (replace this with actual payment processing in a production environment)
        payment_successful = True
        
        if payment_successful:
            try:
                order = Order(
                    customer=current_user.id,
                    products=cart.items,
                    total_price=cart.get_total(),
                    status='paid',
                    delivery_address={
                        'address': current_user.address,
                        'city': current_user.city,
                        'state': current_user.state,
                        'pincode': current_user.pincode,
                        'phone_number': current_user.phone_number
                    }
                )
                order.save()
                
                # Update product stock
                for item in cart.items:
                    product = item.product
                    product.stock -= item.quantity
                    product.save()
                
                # Clear the cart
                cart.delete()
                
                flash('Your order has been placed successfully!')
                return redirect(url_for('customer.order_confirmation', order_id=order.id))
            except ValidationError as e:
                flash(f'Error creating order: {str(e)}', 'error')
                return redirect(url_for('customer.checkout'))
        else:
            flash('Payment failed. Please try again.', 'error')
            return redirect(url_for('customer.checkout'))
    
    return render_template('customer/checkout.html', cart=cart)

@bp.route('/order_confirmation/<order_id>')
@login_required
def order_confirmation(order_id):
    try:
        order = Order.objects.get(id=order_id, customer=current_user.id)
    except DoesNotExist:
        abort(404)
    return render_template('customer/order_confirmation.html', order=order)

@bp.route('/order_history')
@login_required
def order_history():
    if current_user.role != 'customer':
        abort(403)  # Forbidden if not a customer
    orders = Order.objects(customer=current_user.id).order_by('-created_at')
    return render_template('customer/order_history.html', orders=orders)

# Remove the duplicate route
# @bp.route('/orders')
# @login_required
# def order_history():
#     orders = Order.objects(customer=current_user.id).order_by('-created_at')
#     return render_template('customer/order_history.html', orders=orders)

