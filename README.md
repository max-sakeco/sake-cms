# Sake CMS

A modern Content Management System built with Flask, featuring article management with advanced capabilities.

## Features

- User Authentication and Authorization
- Article Management (Create, Read, Update, Delete)
- Rich Text Editing with TinyMCE
- Category and Tag Support
- File Upload Support
- Review System for Articles

## Requirements

- Python 3.10+
- Flask 2.3.3
- SQLAlchemy
- Flask-Login for authentication
- TinyMCE for rich text editing

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sake-cms.git
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
