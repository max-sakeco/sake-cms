from flask import jsonify, request, url_for, render_template, redirect, flash
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.auth import bp
from app.models import User, Role
from app.auth.forms import LoginForm, RegistrationForm, UserForm
from app.auth.utils import generate_token, verify_token

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        flash('Welcome back!', 'success')
        
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/settings/users')
@login_required
def user_list():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('main.index'))
    users = User.query.all()
    return render_template('auth/user_list.html', users=users)

@bp.route('/settings/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('main.index'))
    
    form = UserForm()
    form.role.choices = [(r.id, r.name) for r in Role.query.all()]
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role_id=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
            flash('User added successfully.')
            return redirect(url_for('auth.user_list'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding user. Email might already be registered.')
    
    return render_template('auth/user_form.html', form=form, title='Add User')

@bp.route('/settings/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    form.role.choices = [(r.id, r.name) for r in Role.query.all()]
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role_id = form.role.data
        if form.password.data:
            user.set_password(form.password.data)
        
        try:
            db.session.commit()
            flash('User updated successfully.')
            return redirect(url_for('auth.user_list'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating user. Email might already be registered.')
    
    return render_template('auth/user_form.html', form=form, title='Edit User')

@bp.route('/settings/users/<int:id>/delete', methods=['POST'])
@login_required
def delete_user(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('main.index'))
    
    if current_user.id == id:
        flash('You cannot delete your own account.')
        return redirect(url_for('auth.user_list'))
    
    user = User.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting user.')
