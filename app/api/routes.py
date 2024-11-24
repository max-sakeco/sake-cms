from flask import jsonify, request
from app.api import bp
from app.models import Article, Category, Tag
from app.auth.utils import verify_token
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        token = token.split(' ')[1] if len(token.split(' ')) > 1 else token
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        return f(*args, **kwargs)
    return decorated

@bp.route('/articles', methods=['GET'])
@token_required
def get_articles():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category = request.args.get('category')
    tag = request.args.get('tag')
    search = request.args.get('search')
    
    query = Article.query.filter(Article.status == 'published')
    
    if category:
        query = query.filter(Article.category_id == category)
    
    if tag:
        query = query.join(Article.tags).filter(Tag.id == tag)
    
    if search:
        query = query.filter(
            db.or_(
                Article.title.ilike(f'%{search}%'),
                Article.content.ilike(f'%{search}%'),
                Article.summary.ilike(f'%{search}%')
            )
        )
    
    articles = query.order_by(Article.published_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'items': [{
            'id': article.id,
            'title': article.title,
            'summary': article.summary,
            'content': article.content,
            'featured_image': article.featured_image,
            'author': article.author.username,
            'published_at': article.published_at.isoformat(),
            'category': {
                'id': article.category.id,
                'name': article.category.name
            } if article.category else None,
            'tags': [{
                'id': tag.id,
                'name': tag.name
            } for tag in article.tags]
        } for article in articles.items],
        'total': articles.total,
        'pages': articles.pages,
        'current_page': articles.page
    })

@bp.route('/articles/<int:id>', methods=['GET'])
@token_required
def get_article(id):
    article = Article.query.filter_by(id=id, status='published').first_or_404()
    
    return jsonify({
        'id': article.id,
        'title': article.title,
        'summary': article.summary,
        'content': article.content,
        'featured_image': article.featured_image,
        'author': article.author.username,
        'published_at': article.published_at.isoformat(),
        'category': {
            'id': article.category.id,
            'name': article.category.name
        } if article.category else None,
        'tags': [{
            'id': tag.id,
            'name': tag.name
        } for tag in article.tags]
    })

@bp.route('/categories', methods=['GET'])
@token_required
def get_categories():
    categories = Category.query.all()
    return jsonify([{
        'id': category.id,
        'name': category.name,
        'description': category.description
    } for category in categories])

@bp.route('/tags', methods=['GET'])
@token_required
def get_tags():
    tags = Tag.query.all()
    return jsonify([{
        'id': tag.id,
        'name': tag.name
    } for tag in tags])
