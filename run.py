from app import create_app, db
from app.models import User, Article, Category, Tag, Comment

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Article': Article,
        'Category': Category,
        'Tag': Tag,
        'Comment': Comment
    }

if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.run(port=5001, use_reloader=False)
