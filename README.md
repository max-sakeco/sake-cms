# Sake CMS

A modern Content Management System built with Flask, featuring article management with advanced capabilities.

## Features

- User Authentication and Authorization
- Article Management (Create, Read, Update, Delete)
- Rich Text Editing with TinyMCE
- Category and Tag Support
- File Upload Support
- Review System for Articles
- RESTful API for Content Access

## Requirements

- Python 3.10+
- Flask 2.3.3
- SQLAlchemy
- Flask-Login for authentication
- TinyMCE for rich text editing

## Installation

1. Clone the repository:
```bash
git clone https://github.com/max-sakeco/sake-cms.git
cd sake-cms
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python init_db.py
```

5. Run the application:
```bash
python run.py
```

The application will be available at `http://localhost:5001`

## Default Admin Account

- Email: admin@example.com
- Password: admin123

## API Documentation

The CMS provides a RESTful API to access content:

### List Articles
```
GET /api/articles
```
Query parameters:
- page: Page number (default: 1)
- per_page: Items per page (default: 10)
- category: Filter by category slug
- tag: Filter by tag slug
- search: Search in title and content

### Get Single Article
```
GET /api/articles/<slug>
```

### List Categories
```
GET /api/categories
```

### List Tags
```
GET /api/tags
```

Example API response for articles:
```json
{
    "items": [
        {
            "id": 1,
            "title": "Article Title",
            "slug": "article-title",
            "summary": "Article summary",
            "content": "Full content",
            "featured_image": "image.jpg",
            "published_at": "2023-11-24T18:30:00",
            "category": {
                "id": 1,
                "name": "Technology",
                "slug": "technology"
            },
            "tags": [
                {
                    "id": 1,
                    "name": "Python",
                    "slug": "python"
                }
            ],
            "author": {
                "id": 1,
                "username": "admin"
            }
        }
    ],
    "meta": {
        "page": 1,
        "per_page": 10,
        "total_pages": 5,
        "total_items": 42
    }
}
```

## Configuration

The application can be configured through environment variables or the `config.py` file:

- `SECRET_KEY`: Flask secret key
- `SQLALCHEMY_DATABASE_URI`: Database connection string
- `TINYMCE_API_KEY`: Your TinyMCE API key

## Project Structure

```
sake-cms/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── auth/
│   │   └── routes.py
│   ├── main/
│   │   ├── forms.py
│   │   └── routes.py
│   └── templates/
├── config.py
├── init_db.py
└── run.py
```

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to your branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
