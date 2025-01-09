from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import login_manager

bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=user_id).first()

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('customer.browse'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.objects(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            if user.role == 'seller':
                return redirect(next_page or url_for('seller.dashboard'))
            else:
                return redirect(next_page or url_for('customer.browse'))
        flash('Invalid email or password', 'error')
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('customer.browse'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        role = request.form.get('role', 'customer')
        phone_number = request.form.get('phone_number')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        pincode = request.form.get('pincode')

        if User.objects(email=email).first():
            flash('Email already registered', 'error')
        else:
            user = User(email=email, name=name, role=role, phone_number=phone_number,
                        address=address, city=city, state=state, pincode=pincode)
            user.set_password(password)
            user.save()
            login_user(user)
            flash('Registration successful!', 'success')
            return redirect(url_for('customer.browse'))
    return render_template('auth/register.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

