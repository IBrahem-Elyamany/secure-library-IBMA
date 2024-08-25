import os
import re
import hashlib
import hmac
from werkzeug.security import generate_password_hash, check_password_hash


def allowed_ex(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in {'png','jpg','jpeg','gif'}
def allowed_size(file):
    file.seek(0,os.SEEK_END)
    file_size=file.tell()
    file.seek(0,os.SEEK_SET)
    return file_size <= 5*1024*1024

def is_strong_password(password):
    if len(password) > 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def hash_password(password):
    return generate_password_hash(password)

def is_password_correct(password, hashed_password):
    return check_password_hash(hashed_password, password)



def create_mac(price):
    secret_password = b"#%$2341dw/123\\*+d2merti231war4"
    price = str(price).encode('utf-8')
    mac = hmac.new(secret_password, price, hashlib.sha256).hexdigest()

    return mac

def get_product_by_id(products_list, product_id):
    for product in products_list:
        if product['id'] == int(product_id):
            return product
    return None