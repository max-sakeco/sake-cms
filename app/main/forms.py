from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SelectMultipleField, FileField, SubmitField
from wtforms.validators import DataRequired, Length
from app.models import Category, Tag

class ArticleForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    summary = TextAreaField('Summary', validators=[Length(max=500)])
    category = SelectField('Category', coerce=int, choices=[], validators=[])
    tags = SelectMultipleField('Tags', coerce=int, choices=[], validators=[])
    featured_image = FileField('Featured Image')
    submit = SubmitField('Save Article')
    
    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.category.choices = [(0, 'No Category')] + [
            (c.id, c.name) for c in Category.query.order_by('name').all()
        ]
        self.tags.choices = [(t.id, t.name) for t in Tag.query.order_by('name').all()]
