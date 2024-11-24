from app import create_app, db
from app.models import User, Category, Tag, Article
from slugify import slugify

app = create_app()

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Create some initial categories
            categories = [
                Category(name='Technology'),
                Category(name='Business'),
                Category(name='Science'),
                Category(name='Arts')
            ]
            for category in categories:
                category.slug = slugify(category.name)
            db.session.add_all(categories)
            
            # Create some initial tags
            tags = [
                Tag(name='Web Development'),
                Tag(name='AI'),
                Tag(name='Data Science'),
                Tag(name='Design')
            ]
            for tag in tags:
                tag.slug = slugify(tag.name)
            db.session.add_all(tags)
            
            db.session.commit()
            print("Database initialized with admin user and initial categories/tags.")
        else:
            print("Admin user already exists.")

if __name__ == '__main__':
    init_db()
