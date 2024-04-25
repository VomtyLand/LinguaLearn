# Импорт класса Flask и нескольких функций из flask
from flask import Flask, request, render_template, redirect, url_for
# Импорт класса SQLAlchemy для работы с базой данных
from flask_sqlalchemy import SQLAlchemy
# Импорт класса Translator для перевода текста
from googletrans import Translator

# Создание экземпляра приложения Flask
app = Flask(__name__)

# Конфигурация базы данных, указание пути к файлу базы данных SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# Создание объекта SQLAlchemy для работы с базой данных
db = SQLAlchemy(app)

# Определение модели пользователя в базе данных с помощью SQLAlchemy
class User(db.Model):
    # Уникальный идентификатор пользователя, первичный ключ
    id = db.Column(db.Integer, primary_key=True)
    # Адрес электронной почты пользователя, должен быть уникальным
    email = db.Column(db.String(80), unique=True, nullable=False)
    # Пароль пользователя
    password = db.Column(db.String(80), nullable=False)

# Словарь с доступными заданиями для пользователей
tasks = {
    'grammar': 'Грамматические упражнения',
    'listening': 'Упражнения на аудирование'
}

# Создание объекта переводчика
translator = Translator()

# Маршрут к главной странице
@app.route('/main')
def index():
    # Возвращает главную страницу
    return render_template('index.html')

# Маршрут для регистрации пользователей
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Обработка данных формы регистрации
    if request.method == 'POST':
        # Получение данных из формы
        email = request.form['email']
        password = request.form['password']
        # Создание нового пользователя
        new_user = User(email=email, password=password)
        # Добавление пользователя в базу данных
        db.session.add(new_user)
        # Сохранение изменений в базе данных
        db.session.commit()
        # Сообщение об успешной регистрации
        return 'Регистрация прошла успешно!'
    # Возвращает страницу регистрации
    return render_template('register.html')

# Маршрут для входа пользователей
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Обработка данных формы входа
    if request.method == 'POST':
        # Получение данных из формы
        email = request.form['email']
        password = request.form['password']
        # Поиск пользователя в базе данных
        user = User.query.filter_by(email=email, password=password).first()
        # Проверка наличия пользователя в базе данных
        if user:
            # Перенаправление на страницу выбора заданий
            return redirect(url_for('choose'))
        else:
            # Сообщение о неверных данных
            return 'Неверный email или пароль!'
    # Возвращает страницу входа
    return render_template('login.html')

# Маршрут для выбора заданий
@app.route('/choose', methods=['GET', 'POST'])
def choose():
    # Обработка выбора задания
    if request.method == 'POST':
        # Получение текста для перевода
        original_text = request.form['text']
        # Перевод текста
        translated_text = translator.translate(original_text, src='ru', dest='en').text
        # Возвращает страницу с заданиями и переводом
        return render_template('tasks_index.html', tasks=tasks, original_text=original_text, translation=translated_text)
    # Возвращает страницу с заданиями без перевода
    return render_template('tasks_index.html', tasks=tasks, original_text='', translation='')

# Маршрут для выполнения задания
@app.route('/task', methods=['POST'])
def task():
    # Получение выбранного задания
    selected_task = request.form.get('task')
    # Проверка наличия задания в списке
    if selected_task in tasks:
        # Возвращает страницу с заданием
        return render_template(f'{selected_task}.html')
    else:
        # Возвращает ошибку, если задание не найдено
        return 'Task not found', 404

# Проверка, что файл запущен как основная программа
if __name__ == '__main__':
    # Создание таблиц в базе данных
    with app.app_context():
        db.create_all()
    # Запуск приложения в режиме отладки
    app.run(debug=True)
