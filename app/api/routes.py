from flask import jsonify, request, current_app
from app.api import bp
from app.models import Article, Category, Tag
from flask_login import login_required
from sqlalchemy import desc

@bp.route('/articles', methods=['GET'])
def get_articles():
    """
    Get a list of published articles.
    Query parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 10)
    - category: Filter by category slug
    - tag: Filter by tag slug
    - search: Search in title and content
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category_slug = request.args.get('category')
    tag_slug = request.args.get('tag')
    search = request.args.get('search')

    # Start with base query
    query = Article.query.filter_by(status='published')

    # Apply filters
    if category_slug:
        query = query.join(Article.category).filter(Category.slug == category_slug)
    
    if tag_slug:
        query = query.join(Article.tags).filter(Tag.slug == tag_slug)
    
    if search:
        query = query.filter(
            db.or_(
                Article.title.ilike(f'%{search}%'),
                Article.content.ilike(f'%{search}%')
            )
        )

    # Order by publication date
    query = query.order_by(desc(Article.published_at))

    # Paginate results
    articles = query.paginate(page=page, per_page=per_page, error_out=False)

    # Format response
    response = {
        'items': [{
            'id': article.id,
            'title': article.title,
            'slug': article.slug,
            'summary': article.summary,
            'content': article.content,
            'featured_image': article.featured_image,
            'published_at': article.published_at.isoformat() if article.published_at else None,
            'category': {
                'id': article.category.id,
                'name': article.category.name,
                'slug': article.category.slug
            } if article.category else None,
            'tags': [{
                'id': tag.id,
                'name': tag.name,
                'slug': tag.slug
            } for tag in article.tags],
            'author': {
                'id': article.author.id,
                'username': article.author.username
            }
        } for article in articles.items],
        'meta': {
            'page': articles.page,
            'per_page': articles.per_page,
            'total_pages': articles.pages,
            'total_items': articles.total
        }
    }
    
    return jsonify(response)

@bp.route('/articles/<string:slug>', methods=['GET'])
def get_article(slug):
    """Get a specific article by its slug"""
    article = Article.query.filter_by(slug=slug, status='published').first_or_404()
    
    response = {
        'id': article.id,
        'title': article.title,
        'slug': article.slug,
        'summary': article.summary,
        'content': article.content,
        'featured_image': article.featured_image,
        'published_at': article.published_at.isoformat() if article.published_at else None,
        'category': {
            'id': article.category.id,
            'name': article.category.name,
            'slug': article.category.slug
        } if article.category else None,
        'tags': [{
            'id': tag.id,
            'name': tag.name,
            'slug': tag.slug
        } for tag in article.tags],
        'author': {
            'id': article.author.id,
            'username': article.author.username
        }
    }
    
    return jsonify(response)

@bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    categories = Category.query.all()
    return jsonify([{
        'id': category.id,
        'name': category.name,
        'slug': category.slug,
        'article_count': len(category.articles)
    } for category in categories])

@bp.route('/tags', methods=['GET'])
def get_tags():
    """Get all tags"""
    tags = Tag.query.all()
    return jsonify([{
        'id': tag.id,
        'name': tag.name,
        'slug': tag.slug,
        'article_count': len(tag.articles)
    } for tag in tags])
