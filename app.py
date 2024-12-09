import re
from datetime import datetime
import logging

from flask import Flask, request, jsonify
from tinydb import TinyDB
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

db = TinyDB('db.json', storage=CachingMiddleware(JSONStorage)) #* Initializing TinyDB 

forms_table = db.table('forms') #* Get forms from DB 

# Initialize DB if form is empty
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
    app.logger.info("DB ia initialized with pre-intalled form.")

def is_date(value):
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"): #* validate form of date
        try:
            datetime.strptime(value, fmt)
            return True
        except ValueError:
            pass
    return False

def is_phone(value):
    pattern = r'^\+7\s\d{3}\s\d{3}\s\d{2}\s\d{2}$' #* validate phone number
    return re.match(pattern, value) is not None

def is_email(value):
    pattern = r'^[^@]+@[^@]+\.[^@]+$' #* Validate email
    return re.match(pattern, value) is not None

def detect_field_type(value): #* Determines the field type based on the rules
    if is_date(value):
        return "date"
    if is_phone(value):
        return "phone"
    if is_email(value):
        return "email"
    return "text"

@app.route('/', methods=['GET'])
def index():
    return "Hello, service is running", 200 #* route to root address

@app.route('/get_form', methods=['POST']) #* route for post req
def get_form():
    form_data = request.form.to_dict()
    app.logger.info(f"Получены данные формы: {form_data}")

    detected_types = {k: detect_field_type(v) for k, v in form_data.items()}
    app.logger.info(f"Определенные типы полей: {detected_types}")

    all_forms = forms_table.all()

    for form_template in all_forms:
        template_fields = form_template.get("fields", {})
        match = True
        for field_name, field_type in template_fields.items():
            if field_name not in detected_types or detected_types[field_name] != field_type:
                match = False
                break
        if match:
            app.logger.info(f"Matching pattern found: {form_template['name']}")
            return jsonify({"template_name": form_template["name"]})

    app.logger.info("No matching template found.")
    return jsonify(detected_types), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
