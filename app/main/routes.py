from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.main import bp
from app.models import Article, Category, Tag, Comment
from app.main.utils import save_image, allowed_file
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from app.main.forms import ArticleForm, CategoryForm
from slugify import slugify

@bp.route('/')
@login_required
def index():
    return redirect(url_for('main.article_list'))

@bp.route('/articles')
@login_required
def article_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    category = request.args.get('category')
    search = request.args.get('search')
    
    query = Article.query
    
    if current_user.role != 'admin':
        query = query.filter(Article.author == current_user)
    
    if status:
        query = query.filter(Article.status == status)
    
    if category:
        query = query.filter(Article.category_id == category)
    
    if search:
        query = query.filter(
            db.or_(
                Article.title.ilike(f'%{search}%'),
                Article.content.ilike(f'%{search}%'),
                Article.summary.ilike(f'%{search}%')
            )
        )
    
    articles = query.order_by(Article.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    categories = Category.query.all()
    status_colors = {
        'in_progress': 'warning',
        'ready_for_review': 'info',
        'rejected': 'danger',
        'accepted': 'success',
        'published': 'primary'
    }
    
    return render_template('main/article_list.html',
                         articles=articles,
                         categories=categories,
                         status_colors=status_colors)

@bp.route('/articles/new', methods=['GET', 'POST'])
@login_required
def create_article_view():
    print("Method:", request.method)
    print("Form Data:", request.form)
    
    form = ArticleForm()
    print("Form Validation:", form.validate_on_submit())
    if form.errors:
        print("Form Errors:", form.errors)
    
    if form.validate_on_submit():
        try:
            article = Article(
                title=form.title.data,
                content=form.content.data,
                summary=form.summary.data,
                author=current_user
            )
            
            if form.category.data and form.category.data != 0:
                article.category_id = form.category.data
            
            if form.featured_image.data:
                file = form.featured_image.data
                if file and allowed_file(file.filename):
                    filename = save_image(file, file.filename)
                    article.featured_image = filename
            
            for tag_id in form.tags.data:
                tag = Tag.query.get(tag_id)
                if tag:
                    article.tags.append(tag)
            
            db.session.add(article)
            db.session.commit()
            
            flash('Article created successfully!', 'success')
            return redirect(url_for('main.article_list'))
        except Exception as e:
            print("Error creating article:", str(e))
            db.session.rollback()
            flash(f'Error creating article: {str(e)}', 'error')
            return render_template('main/article_form.html', form=form)
    
    if form.errors:
        flash('Please correct the errors below.', 'error')
    
    return render_template('main/article_form.html', form=form)

@bp.route('/articles/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_article_view(id):
    article = Article.query.get_or_404(id)
    
    if article.author != current_user and current_user.role != 'admin':
        flash('You do not have permission to edit this article.', 'danger')
        return redirect(url_for('main.article_list'))
    
    form = ArticleForm(obj=article)
    
    if form.validate_on_submit():
        article.title = form.title.data
        article.content = form.content.data
        article.summary = form.summary.data
        
        if form.category.data:
            article.category_id = form.category.data
        
        if form.featured_image.data:
            file = form.featured_image.data
            if file and allowed_file(file.filename):
                filename = save_image(file, file.filename)
                article.featured_image = filename
        
        article.tags = []
        for tag_id in form.tags.data:
            tag = Tag.query.get(tag_id)
            if tag:
                article.tags.append(tag)
        
        db.session.commit()
        flash('Article updated successfully!', 'success')
        return redirect(url_for('main.article_list'))
    
    return render_template('main/article_form.html', form=form, article=article)

@bp.route('/articles/<int:id>/status', methods=['PUT'])
@login_required
def update_article_status(id):
    article = Article.query.get_or_404(id)
    data = request.get_json()
    
    if current_user.role != 'admin' and data['status'] in ['accepted', 'published']:
        return jsonify({'error': 'Only admins can accept or publish articles'}), 403
    
    article.status = data['status']
    if data['status'] == 'published':
        article.published_at = datetime.utcnow()
    
    if 'comment' in data:
        comment = Comment(
            content=data['comment'],
            article=article,
            author=current_user,
            is_review_comment=True
        )
        db.session.add(comment)
    
    db.session.commit()
    return jsonify({'message': 'Article status updated successfully'})

@bp.route('/articles/<int:id>/image', methods=['POST'])
@login_required
def upload_article_image(id):
    article = Article.query.get_or_404(id)
    
    if article.author != current_user and current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = save_image(file, file.filename)
        article.featured_image = filename
        db.session.commit()
        return jsonify({'message': 'Image uploaded successfully', 'path': filename})
    
    return jsonify({'error': 'Invalid file type'}), 400

@bp.route('/review')
@login_required
def review_articles():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.article_list'))
    
    articles = Article.query.filter_by(status='ready_for_review').order_by(Article.created_at.desc()).all()
    return render_template('main/review_articles.html', articles=articles)

@bp.route('/categories')
@login_required
def category_list():
    categories = Category.query.order_by(Category.name).all()
    return render_template('main/category_list.html', categories=categories)

@bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data,
            slug=slugify(form.name.data)
        )
        db.session.add(category)
        db.session.commit()
        flash('Category created successfully.', 'success')
        return redirect(url_for('main.category_list'))
    return render_template('main/category_form.html', form=form, title='Add Category')

@bp.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    form = CategoryForm(obj=category)
    form._category_id = id
    
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        category.slug = slugify(form.name.data)
        db.session.commit()
        flash('Category updated successfully.', 'success')
        return redirect(url_for('main.category_list'))
    return render_template('main/category_form.html', form=form, title='Edit Category')

@bp.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    if category.articles:
        flash('Cannot delete category that has articles.', 'danger')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully.', 'success')
    return redirect(url_for('main.category_list'))

@bp.route('/settings/categories')
@login_required
def settings_category_list():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.index'))
    categories = Category.query.order_by(Category.name).all()
    return render_template('main/category_list.html', categories=categories)

@bp.route('/settings/categories/add', methods=['GET', 'POST'])
@login_required
def settings_add_category():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.index'))
    
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        category.description = form.description.data
        db.session.add(category)
        try:
            db.session.commit()
            flash('Category added successfully.', 'success')
            return redirect(url_for('main.settings_category_list'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding category.', 'danger')
    
    return render_template('main/category_form.html', form=form, title='Add Category')

@bp.route('/settings/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def settings_edit_category(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.index'))
    
    category = Category.query.get_or_404(id)
    form = CategoryForm(obj=category)
    form._category_id = category.id
    
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        category.slug = slugify(form.name.data)
        try:
            db.session.commit()
            flash('Category updated successfully.', 'success')
            return redirect(url_for('main.settings_category_list'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating category.', 'danger')
    
    return render_template('main/category_form.html', form=form, title='Edit Category')

@bp.route('/settings/categories/<int:id>/delete', methods=['POST'])
@login_required
def settings_delete_category(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.index'))
    
    category = Category.query.get_or_404(id)
    if category.articles.count() > 0:
        flash('Cannot delete category. It still has articles associated with it.', 'danger')
        return redirect(url_for('main.settings_category_list'))
    
    try:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting category.', 'danger')
    
    return redirect(url_for('main.settings_category_list'))
