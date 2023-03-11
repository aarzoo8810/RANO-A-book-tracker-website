from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, DateField, EmailField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError
from flask_ckeditor import CKEditorField


def validate_number(form, field):
    field_data = field.data
    if len(field_data) > 0:
        if field_data.startswith("-") and field_data[1:].isdigit():
            raise ValidationError('Must be positive integer.')
        elif "." in field_data:
            field_data_list = field_data.split(".")
            print(field_data_list)
            for i in field_data_list:
                if i.isdigit():
                    pass
                else:
                    raise ValidationError('Must be a number')


def validate_float(form, field):
    """Validate if given string is decimal"""
    if len(field.data) > 0:
        if not field.data.isdigit():
            raise ValidationError('Must not be decimal')
            


    
class AddRecord(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    series = StringField("Series", validators=[DataRequired()])
    volume_number = StringField("Volume", validators=[validate_number])
    author_id = StringField("Author ID", validators=[DataRequired(), validate_number, validate_float])
    illustrator_id = StringField("Illustrator ID", validators=[validate_number, validate_float])
    release_date = DateField("Release Date", validators=[DataRequired()])
    cover = FileField("Cover:", validators=[FileRequired(), FileAllowed(['jpg', 'png'], "Images(jpg, png) Only")])
    description = CKEditorField("Description")
    submit_book = SubmitField("Submit")


class Register(FlaskForm):
    user_name = StringField("Username", validators=[DataRequired(), Length(max=50)])
    email = EmailField("email", validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    submit = SubmitField("Register")


class Login(FlaskForm):
    # user_name = StringField("Username", validators=[DataRequired(), Length(max=50)])
    email = EmailField("email", validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    submit = SubmitField("Login")


class AddPerson(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=50)])
    dob = DateField("Date of Birth", validators=[DataRequired()])
    job = SelectField("Profession", validators=[DataRequired()], choices=["Author", "Illustrator"])
    description = TextAreaField("About")
    submit = SubmitField("Submit")


class Comment(FlaskForm):
    comment = CKEditorField("Leave a Comment", validators=[DataRequired()])
    submit = SubmitField("Submit")