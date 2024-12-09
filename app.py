import re
from datetime import datetime
import logging

from flask import Flask, request, jsonify
from tinydb import TinyDB
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

# Создание экземпляра Flask приложения
app = Flask(__name__)

# Настройка логирования для отображения информационных сообщений
logging.basicConfig(level=logging.INFO)

# Инициализация TinyDB с использованием CachingMiddleware для улучшения производительности
# JSONStorage отвечает за хранение данных в формате JSON
db = TinyDB('db.json', storage=CachingMiddleware(JSONStorage))

# Получение таблицы 'forms' из базы данных TinyDB
forms_table = db.table('forms')

# Инициализируем базу данных, если таблица 'forms' пуста
if not forms_table.all():
    forms_table.insert_multiple([
        {
            "name": "MyForm",
            "fields": {
                "user_name": "text",       
                "lead_email": "email",    
                "order_date": "date"       
            }
        },
        {
            "name": "Order Form",
            "fields": {
                "contact_email": "email",  
                "contact_phone": "phone"   
            }
        }
    ])
    app.logger.info("База данных инициализирована с предустановленными шаблонами форм.")

def is_date(value):
    """
    Проверяет, соответствует ли значение одному из форматов даты.
    Поддерживаемые форматы: DD.MM.YYYY и YYYY-MM-DD
    """
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            datetime.strptime(value, fmt)
            return True
        except ValueError:
            pass
    return False

def is_phone(value):
    """
    Проверяет, соответствует ли значение формату телефона +7 xxx xxx xx xx.
    """
    pattern = r'^\+7\s\d{3}\s\d{3}\s\d{2}\s\d{2}$'
    return re.match(pattern, value) is not None

def is_email(value):
    """
    Проверяет, является ли значение корректным email-адресом.
    """
    pattern = r'^[^@]+@[^@]+\.[^@]+$'
    return re.match(pattern, value) is not None

def detect_field_type(value):
    """
    Определяет тип поля на основе заданных правил.
    Порядок проверки: дата, телефон, email, текст.
    """
    if is_date(value):
        return "date"
    if is_phone(value):
        return "phone"
    if is_email(value):
        return "email"
    return "text"

@app.route('/', methods=['GET'])
def index():
    """
    Маршрут по корневому адресу.
    Возвращает простое сообщение для проверки работы сервиса.
    """
    return "Hello, service is running", 200

@app.route('/get_form', methods=['POST'])
def get_form():
    """
    Маршрут для обработки POST-запросов на определение шаблона формы.
    Получает данные формы, определяет типы полей и ищет соответствующий шаблон.
    Возвращает имя шаблона или типы полей, если шаблон не найден.
    """
    # Преобразуем данные формы в словарь
    form_data = request.form.to_dict()
    app.logger.info(f"Получены данные формы: {form_data}")

    # Определяем типы каждого поля
    detected_types = {k: detect_field_type(v) for k, v in form_data.items()}
    app.logger.info(f"Определенные типы полей: {detected_types}")

    # Получаем все шаблоны форм из базы данных
    all_forms = forms_table.all()

    # Проходим по каждому шаблону и проверяем совпадение полей
    for form_template in all_forms:
        template_fields = form_template.get("fields", {})
        match = True
        for field_name, field_type in template_fields.items():
            # Проверяем наличие поля и соответствие типа
            if field_name not in detected_types or detected_types[field_name] != field_type:
                match = False
                break
        if match:
            app.logger.info(f"Найден совпадающий шаблон: {form_template['name']}")
            return jsonify({"template_name": form_template["name"]})

    # Если шаблон не найден, возвращаем типы полей с кодом 404
    app.logger.info("Совпадающий шаблон не найден.")
    return jsonify(detected_types), 404

if __name__ == '__main__':
    """
    Запуск Flask-приложения.
    Приложение будет доступно по всем адресам на порту 8080.
    """
    app.run(host='0.0.0.0', port=8080)
