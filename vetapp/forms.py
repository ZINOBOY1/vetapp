from flask_wtf import FlaskForm

from wtforms import StringField,TextAreaField,SubmitField,PasswordField,FileField,EmailField,DecimalField,SelectField
from wtforms.validators import DataRequired,Email,Length,EqualTo
from flask_wtf.file import FileField,FileAllowed,FileRequired
 

class SignForm(FlaskForm):
    name = StringField('Name',validators=[DataRequired(message='Please Input your name')])

    email = StringField('Email',validators=[DataRequired(message = 'Enter your email please'),Email(message='Input correct email')])

    password = PasswordField('Password',validators=[DataRequired(message= 'Enter your password'),Length(max=10)])

    conpass = PasswordField('Confirm Password',validators=[DataRequired(message= 'Password is required'),Length(max=10),EqualTo('password',message='Password does not match')])

    address = StringField('Address',validators=[DataRequired(message='Please type in current address')])

    submit = SubmitField('Send')

    class Meta:
        csrf = True
        csrf_time_limit = 7200

class AddProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    picture = FileField('Product Picture')
    category_id = SelectField('Category', coerce=int) 
    breed_id = SelectField('Breed', coerce=int) 
    submit = SubmitField('Add Product')

class AdminRegistrationForm(FlaskForm):
    admin_fullname = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=255)])
    admin_email = EmailField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    admin_password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('admin_password')])
    submit = SubmitField('Register')