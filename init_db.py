from app import create_app, db
from app.models import User, Category, Tag, Article, Role
from slugify import slugify

def init_db():
    app = create_app()
    with app.app_context():
        # Create tables
        db.drop_all()
        db.create_all()

        # Create roles
        admin_role = Role(name='admin')
        editor_role = Role(name='editor')
        writer_role = Role(name='writer')
        db.session.add_all([admin_role, editor_role, writer_role])
        db.session.commit()

        # Create admin user
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                role=admin_role
            )
            admin.set_password('admin123')
            db.session.add(admin)

        # Create sample categories
        categories = [
            Category(name='Technology'),
            Category(name='Business'),
            Category(name='Lifestyle')
        ]
        for category in categories:
            category.slug = slugify(category.name)
        db.session.add_all(categories)

        # Create sample tags
        tags = [
            Tag(name='Python'),
            Tag(name='JavaScript'),
            Tag(name='Web Development'),
            Tag(name='AI'),
            Tag(name='Machine Learning')
        ]
        for tag in tags:
            tag.slug = slugify(tag.name)
        db.session.add_all(tags)

        # Create sample articles
        articles = [
            Article(
                title='Getting Started with Flask',
                content='Flask is a lightweight WSGI web application framework...',
                summary='Learn the basics of Flask framework',
                author=admin,
                category=categories[0],
                tags=[tags[0], tags[2]],
                status='published'
            ),
            Article(
                title='Python Best Practices',
                content='Writing clean and maintainable Python code...',
                summary='Essential Python coding practices',
                author=admin,
                category=categories[0],
                tags=[tags[0]],
                status='published'
            )
        ]
        for article in articles:
            article.slug = slugify(article.title)
        db.session.add_all(articles)

        db.session.commit()

if __name__ == '__main__':
    init_db()
