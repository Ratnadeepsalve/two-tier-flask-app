import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
from contextlib import closing

app = Flask(__name__)

# Configure MySQL from environment variables
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'default_user')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'default_password')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'default_db')

# Initialize MySQL
mysql = MySQL(app)

def init_db():
    try:
        with app.app_context():
            with closing(mysql.connection.cursor()) as cur:
                cur.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    message TEXT NOT NULL
                );
                ''')
                mysql.connection.commit()
    except Exception as e:
        logging.error(f"Error initializing database: {e}")

@app.route('/')
def hello():
    try:
        with closing(mysql.connection.cursor()) as cur:
            cur.execute('SELECT message FROM messages')
            messages = cur.fetchall()
        return render_template('index.html', messages=messages)
    except Exception as e:
        logging.error(f"Error fetching messages: {e}")
        return "An error occurred while fetching messages.", 500

@app.route('/submit', methods=['POST'])
def submit():
    new_message = request.form.get('new_message')
    if not new_message:
        return jsonify({'error': 'Message cannot be empty'}), 400
    try:
        with closing(mysql.connection.cursor()) as cur:
            cur.execute('INSERT INTO messages (message) VALUES (%s)', [new_message])
            mysql.connection.commit()
        return jsonify({'message': new_message})
    except Exception as e:
        logging.error(f"Error inserting message: {e}")
        return "An error occurred while inserting the message.", 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
