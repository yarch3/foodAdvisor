from datetime import datetime
import os

from flask import Flask, render_template, send_file, url_for, send_from_directory, request, session, redirect, g, \
    jsonify
from sqlalchemy.sql import text
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, login_manager

# Import for Migrations
from flask_migrate import Migrate, migrate
from jinja2 import FileSystemLoader, Environment

import model
from model import db, Question

# Settings for migrations

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
login_mg = LoginManager(app)
login_mg.login_view = 'login'
app.app_context().push()
environment = Environment(loader=FileSystemLoader("templates/"))


SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'site.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
app.config['SECRET_KEY'] = 'supa dupa mega secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'youmail@gmail.com'
app.config['MAIL_DEFAULT_SENDER'] = 'youmail@gmail.com'
app.config['MAIL_PASSWORD'] = 'password'
db.init_app(app)

with app.app_context():
    db.create_all()
migrate = Migrate(app, db)
def fill_answers():
    from model import Answer
    ar = [["Суши", "Паста", "Гуляш", "Паэлья", "Кимчи"], ["Грибы", "Ананас", "Сыр", "Креветки", "Авокадо"],["Франция", "Италия", "Россия", "Япония", "США"], ["Суши", "Карри", "Пельмени", "Тапас", "Стейк"], ["Тирамису", "Баба гануш", "Чизкейк", "Макаруны", "Панакота"]]
    ans = ["Паста", "Сыр", "США", "Тапас", "Баба гануш"]
    index = 0
    for one in ar:
        for a in one:
            existing_answer = Answer.query.filter_by(text=a).first()
            if not existing_answer:
                if a == ans[index]:
                    new_answer = Answer(question_id=index+1, text=a, is_correct=True)
                else:
                    new_answer = Answer(question_id=index+1, text=a)
                db.session.add(new_answer)
        db.session.commit()
        index += 1
    return
#fill_answers()




@login_mg.user_loader
def load_user(user_id):
    from model import UserData
    return UserData.query.get(user_id)


@app.route('/')
def hello():
    return render_template("askaneli.html")

@app.route('/agreement')
def bop():
    return render_template('agreement.html')




@app.route('/login', methods=['post', 'get'])
def login():
    return render_template('login.html')

@app.route('/submit', methods=['post', 'get'])
def login_confirm():
    if request.method == 'POST':
        from model import UserData
        user = UserData.query.filter_by(email=request.form.get('email')).first()
        if user is None:
            message = "Wrong email or password"
        else:
            if user.check_password(request.form.get("password")):
                login_user(user, remember=True)
                return jsonify({'redirect': '/'})
            else:
                return jsonify({'error': 'Неправильный email или пароль'})


@app.route('/registration', methods=['post', 'get'])
def check():
    if request.method == 'POST':
        from model import UserData
        user = UserData(
            username = request.form.get('username'),
            email = request.form.get('email'),
        )
        user.set_password(request.form.get('password'))
        if user.check_password(request.form.get('confirmpswd')):
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
    return render_template('registration.html')

@app.route('/profile')
def show_profile():
    return render_template('profile.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect('/')

@app.route('/poll', methods=['GET', 'POST'])
@login_required
def polling():
    return render_template("poll.html")



@app.route('/static/<path:path>')
def send_report(path):
    return send_from_directory('static', path)


def get_next_question_id(current_question_id):
    # Реализуйте логику для получения ID следующего вопроса здесь
    # Например, можно вернуть следующий ID после текущего или использовать другую логику
    return current_question_id + 1 if current_question_id < 5 else 0


@app.route('/json', methods=['GET', 'POST'])
def get_json():
    if request.method == 'POST':
        from model import Question, Answer
        json_data = []
        questions = Question.query.all()
        correct_answer = ""
        for q in questions:
            answers_for_q = Answer.query.filter_by(question_id=q.id)
            answers = []
            for a in answers_for_q:
                answers.append(a.text)
                if a.is_correct:
                    correct_answer = a.text
            dict = {
                'question': q.text,
                'answers': answers,
                'answer': correct_answer
            }
            json_data.append(dict)
        return jsonify(json_data)


@app.route('/pollresult', methods=['GET', 'POST'])
def pollresult():
    from model import UserAnswer, Answer
    if request.method == 'POST':
        data = request.get_json() # Получаем JSON данные из тела запроса
        userAnswers = []
        for i, answer in data.items():
            ans_id = Answer.query.filter_by(text=answer).first().id
            userAnswers.append(model.UserAnswer(question_id=int(i), answer_id=ans_id, user_id=current_user.id))
        for userAnswer in userAnswers:
            db.session.add(userAnswer)
        db.session.commit()
    return jsonify({'result': 'ok'})


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)

