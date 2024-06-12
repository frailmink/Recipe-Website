from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, ValidationError
from flask_wtf.file import FileField, FileRequired, FileAllowed
from .models import Users

class LoginForm(FlaskForm):
    username = StringField('Enter Username', validators=[DataRequired(), Length(10, 40)])
    password = PasswordField('Enter Password', validators=[DataRequired(), Length(10, 40)])
    submit1 = SubmitField('Log In')

class SignUpForm(FlaskForm):
    username = StringField('Enter Username', validators=[DataRequired(), Length(10, 40)])
    password1 = PasswordField('Enter Password', validators=[DataRequired(), Length(10, 40)])
    password2 = PasswordField('Enter Password', validators=[DataRequired(), Length(10, 40)])
    submit2 = SubmitField('Sign Up')

    def validate_username(self, username):
        existingUsernames = Users.query.filter_by(username=username.data).first()
        if existingUsernames:
            raise ValidationError("this username alreagy exists")

class RecipeForm(FlaskForm):
    image = FileField(u'Image File', validators=[FileAllowed(['jpeg', 'jpg', 'png'], message='Images only'), FileRequired()])
    title = StringField('Enter Title', validators=[DataRequired(), Length(1, 40)])
    text = TextAreaField('Enter Recipe', validators=[DataRequired(), Length(1, 9999)])
    submit3 = SubmitField('Post')

class RecipeOpenForm(FlaskForm):
    id = IntegerField()
    submit7 = SubmitField()

class FollowRecipeForm(FlaskForm):
    userId = IntegerField()
    recipeId = IntegerField()
    submit4 = SubmitField('Follow Recipe')

class SearchForm(FlaskForm):
    searchbar = StringField('Search...')
    submit5 = SubmitField('search')


    # def validate_image(form, field):
    #     if field.data:
    #         field.data = re.sub(r'[^a-z0-9_.-]', '_', field.data)
