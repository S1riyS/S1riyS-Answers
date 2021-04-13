import datetime

from flask import Flask
from flask_moment import Moment
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import render_template, redirect, request, url_for, session

from data import db_session
from data.users import User
from data.questions import Question, Answer

from forms.user import RegisterForm, LoginForm
from forms.questions import QuestionForm, AnswerForm

app = Flask(__name__)
moment = Moment(app)
manager = LoginManager(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

@app.route('/main', methods=['GET', 'POST'])
def main_page():
    db_sess = db_session.create_session()
    questions = db_sess.query(Question).all()
    current_time = datetime.datetime.now()
    return render_template(
        'main.html',
        title='Ответы S1RIYS.RU',
        questions=questions,
        user=current_user,
        current_time=current_time
    )

@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            age=form.age.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация', form=form, user=current_user)

@manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    return user

@manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    db_sess = db_session.create_session()
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        if email and password:
            user = db_sess.query(User).filter(User.email == form.email.data).first()
            if not user:
                return render_template('login.html', title='Вход', form=form, message='Неверный логин или пароль!', user=current_user)
            elif user.check_password(password):
                login_user(user)
                session['user_id'] = user.id
                return redirect(url_for('main_page'))
            else:
                return render_template('login.html', title='Вход', form=form, message='Неверный логин или пароль!', user=current_user)

    return render_template('login.html', title='Вход', form=form, user=current_user)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main_page'))

@app.route('/question/<int:question_id>', methods=['GET', 'POST'])
def question_page(question_id):
    form = AnswerForm()
    db_sess = db_session.create_session()
    question = db_sess.query(Question).filter(Question.id == question_id).first()
    answers = db_sess.query(Answer).filter(Answer.question_id == question_id).all()
    if form.validate_on_submit():
        print('Submit!')
        answer = Answer(
            text=form.text.data,
            user_id=current_user.id,
            question_id=question_id
        )
        db_sess.add(answer)
        db_sess.commit()
        return redirect(url_for('question_page', question_id=question_id))
    return render_template(
                        'question.html',
                        id=question_id,
                        title='Вопрос',
                        question=question,
                        answers=answers,
                        form=form,
                        user=current_user,
                    )

@app.route('/ask', methods=['GET', 'POST'])
@login_required
def ask_question_page():
    db_sess = db_session.create_session()
    form = QuestionForm()
    if form.validate_on_submit():
        title = form.title.data
        text = form.text.data
        print(title, text)
        if title and text:
            question = Question(
                title=title,
                text=text,
                user_id=current_user.id
            )
            db_sess.add(question)
            db_sess.commit()
            return redirect(url_for('main_page'))
        else:
            return render_template('ask_question.html', form=form, message='Оба поля должны быть заполены', user=current_user)
    return render_template('ask_question.html', form=form, user=current_user)

def main():
    db_session.global_init("db/messenger.db")
    app.run(port=8080, host='127.0.0.1')

if __name__ == '__main__':
    main()
