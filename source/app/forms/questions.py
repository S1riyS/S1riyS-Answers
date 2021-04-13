from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, IntegerField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class QuestionForm(FlaskForm):
    title = StringField('Тема вопроса ', validators=[DataRequired()],)
    text = TextAreaField('Текст вопроса ', validators=[DataRequired()])
    submit = SubmitField('Отправить')


class AnswerForm(FlaskForm):
    text = TextAreaField('Введите текст ответа', validators=[DataRequired()])
    submit = SubmitField('Отправить')