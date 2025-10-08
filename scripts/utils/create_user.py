from flask import Flask
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import bcrypt
import os
import MySQLdb

load_dotenv()

# Database configuration
app = Flask(__name__)
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT'))
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

def create_user(username, password, role_id):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO recurso_operativo (recurso_operativo_cedula, recurso_operativo_password, id_roles) VALUES (%s, %s, %s)",
                    (username, hashed_password.decode('utf-8'), role_id))
        mysql.connection.commit()
        cur.close()
        print(f"User {username} created successfully.")
    except MySQLdb.Error as e:
        print(f"Error creating user: {e}")

if __name__ == '__main__':

    username = input("Enter username: ")
    password = input("Enter password: ")
    role_id = input("Enter role ID: ")
    create_user(username, password, role_id)