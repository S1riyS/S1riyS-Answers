import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash


class Question(SqlAlchemyBase):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    title = sqlalchemy.Column(sqlalchemy.String)
    text = sqlalchemy.Column(sqlalchemy.String)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                      default=datetime.datetime.utcnow)
    def get_answers(self):
        from data import db_session
        db_sess = db_session.create_session()
        answers= db_sess.query(Answer).filter(Answer.question_id == self.id).all()
        return answers

    @staticmethod
    def correct_form(number:int):
        if number % 10 == 1:
            return 'ответ'
        elif 2 <= number % 10 <= 4:
            return 'ответа'
        else:
            print('zxc')
            return 'ответов'

class Answer(SqlAlchemyBase):
    __tablename__ = 'answers'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    text = sqlalchemy.Column(sqlalchemy.String)
    likes = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    is_best = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')
    question_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("questions.id"))
    question = orm.relation('Question')
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                      default=datetime.datetime.utcnow)