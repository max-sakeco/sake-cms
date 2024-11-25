from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SelectMultipleField, FileField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from app.models import Category, Tag

class ArticleForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    summary = TextAreaField('Summary', validators=[Optional(), Length(max=500)])
    category = SelectField('Category', coerce=int)
    tags = SelectMultipleField('Tags', coerce=int)
    featured_image = FileField('Featured Image')
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.category.choices = [(0, 'No Category')] + [
            (c.id, c.name) for c in Category.query.order_by('name').all()
        ]
        self.tags.choices = [(t.id, t.name) for t in Tag.query.order_by('name').all()]

class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Save')

    def validate_name(self, field):
        category = Category.query.filter_by(name=field.data).first()
        if category and category.id != getattr(self, '_category_id', None):
            raise ValidationError('A category with this name already exists.')
