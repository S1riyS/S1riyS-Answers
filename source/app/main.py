########## FLASK И ДОПОЛНИТЕЛЬНЫЕ МОДУЛИ ##########
from flask import Flask
from flask_moment import Moment
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import render_template, redirect, request, url_for, session, flash
########## КЛАССЫ ##########
from data import db_session
from data.users import User
from data.questions import Question, Answer
########## ФОРМЫ ##########
from forms.user import RegisterForm, LoginForm, UpdateProfileForm
from forms.questions import QuestionForm, AnswerForm

########## ИНИЦИАЛИЗАЦИЯ ПРИЛОЖЕНИЯ ##########
app = Flask(__name__)
moment = Moment(app)
manager = LoginManager(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

########## ГЛАВНАЯ СТРАНИЦА ##########
@app.route('/main', methods=['GET', 'POST'])
def main_page():
    db_sess = db_session.create_session()
    questions = db_sess.query(Question).all()
    return render_template(
        'main.html',
        title='Ответы S1RIYS.RU',
        questions=questions,
    )
########## СТРАНИЦА РЕГИСТРАЦИИ ##########
@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            flash("Пароли не совпадают")
            return render_template('register.html', title='Регистрация',
                                   form=form)
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            flash("Такой пользователь уже есть")
            return render_template('register.html', title='Регистрация',
                                   form=form)
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
########## ЗАГРУЗКА ПОЛЬЗОВАТЕЛЯ ##########
@manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    return user
########## ПЕРЕНАПРАВЛЕНИЕ, ЕСЛИ ПОЛЬЗОВАТЕЛЬ НЕ АВТОРИЗОВАН ##########
@manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')
########## СТРАНИЦА ВХОДА ##########
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
                flash('Неверный логин или пароль!')
                return render_template('login.html', title='Вход', form=form)
            elif user.check_password(password):
                login_user(user)
                return redirect(url_for('main_page'))
            else:
                flash('Неверный логин или пароль!')
                return render_template('login.html', title='Вход', form=form)

    return render_template('login.html', title='Вход', form=form)
########## ВЫХОД ИЗ АККАУНТА ##########
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main_page'))
########## СТРАНИЦА ПРОФИЛЯ ##########
@app.route('/profile/<int:profile_id>', methods=['GET', 'POST'])
def profile_page(profile_id):
    form = UpdateProfileForm()
    db_sess = db_session.create_session()

    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.surname = form.surname.data
        current_user.age = form.age.data
        current_user.email = form.email.data

        local_current_user = db_sess.merge(current_user)
        db_sess.add(local_current_user)
        db_sess.commit()

    return render_template(
        'profile.html',
        user=load_user(profile_id),
        form=form
    )
########## СТРАНИЦА ВОПРОСА ##########
@app.route('/question/<int:question_id>', methods=['GET', 'POST'])
def question_page(question_id):
    form = AnswerForm()
    db_sess = db_session.create_session()
    question = db_sess.query(Question).filter(Question.id == question_id).first()
    if form.validate_on_submit():
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
                        question=question,
                        form=form
                    )
########## СТРАНИЦА С СОЗДАНИЕМ ВОПРОСА ##########
@app.route('/ask', methods=['GET', 'POST'])
@login_required
def ask_question_page():
    db_sess = db_session.create_session()
    form = QuestionForm()
    if form.validate_on_submit():
        title = form.title.data
        text = form.text.data
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
########## ОБРАБОТЧИК ОШИБКИ 404 ##########
@app.errorhandler(404)
def error_404_page(error):
    print(error)
    return redirect(url_for('main_page'))

def main():
    db_session.global_init("db/messenger.db")
    app.run(port=8080, host='127.0.0.1')

if __name__ == '__main__':
    main()
