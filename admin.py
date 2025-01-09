from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from app.models import User, Product, Order
from app.analytics import get_sales_data, generate_sales_chart, generate_top_products_chart
from datetime import datetime

bp = Blueprint('admin', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        abort(403)
    total_users = User.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    
    sales_data = get_sales_data()
    sales_chart = generate_sales_chart(sales_data)
    top_products_chart = generate_top_products_chart(sales_data)
    
    total_revenue = sales_data['revenue'].sum() if not sales_data.empty else 0
    
    return render_template('admin/dashboard.html', 
                           total_users=total_users,
                           total_products=total_products,
                           total_orders=total_orders,
                           total_revenue=total_revenue,
                           sales_chart=sales_chart,
                           top_products_chart=top_products_chart)

@bp.route('/users')
@login_required
def users():
    if current_user.role != 'admin':
        abort(403)
    users = User.objects.all()
    return render_template('admin/users.html', users=users)

@bp.route('/products')
@login_required
def products():
    if current_user.role != 'admin':
        abort(403)
    products = Product.objects.all()
    return render_template('admin/products.html', products=products)

@bp.route('/orders')
@login_required
def orders():
    if current_user.role != 'admin':
        abort(403)
    orders = Order.objects.all().order_by('-created_at')
    return render_template('admin/orders.html', orders=orders)

@bp.route('/analytics')
@login_required
def analytics():
    if current_user.role != 'admin':
        abort(403)
    sales_data = get_sales_data()
    sales_chart = generate_sales_chart(sales_data)
    top_products_chart = generate_top_products_chart(sales_data)
    
    total_revenue = sales_data['revenue'].sum() if not sales_data.empty else 0
    total_orders = sales_data['quantity'].sum() if not sales_data.empty else 0
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    top_sellers = sales_data.groupby('seller')['revenue'].sum().sort_values(ascending=False).head(5)
    
    return render_template('admin/analytics.html',
                           sales_chart=sales_chart,
                           top_products_chart=top_products_chart,
                           total_revenue=total_revenue,
                           total_orders=total_orders,
                           avg_order_value=avg_order_value,
                           top_sellers=top_sellers)

@bp.route('/order/<order_id>/update_status', methods=['POST'])
@login_required
def update_order_status(order_id):
    if current_user.role != 'admin':
        abort(403)
    
    order = Order.objects(id=order_id).first()
    if not order:
        abort(404)
    
    new_status = request.form.get('status')
    if new_status in ['out_for_delivery', 'delivered'] and order.status in ['dispatched', 'out_for_delivery']:
        order.status = new_status
        order.updated_at = datetime.utcnow()
        order.save()
        flash('Order status updated successfully.')
    else:
        flash('Invalid status update.', 'error')
    
    return redirect(url_for('admin.orders'))

