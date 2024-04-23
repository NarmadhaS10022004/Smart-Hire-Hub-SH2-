from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask import session
from flask_socketio import SocketIO, emit
import sqlite3
import base64

app = Flask(__name__, template_folder='template')
app.secret_key = 'supersecretkey'
app.config['SECRET_KEY'] = 'your_secret_key_here'
socketio = SocketIO(app)

def create_connection():
    conn = sqlite3.connect('database.db')
    return conn

def connect_db():
    conn = sqlite3.connect('database.db')
    return conn

def create_user_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    email TEXT NOT NULL,
                    password TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_profile (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    profile_type TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS posts(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   post_text TEXT,
                   post_image BLOB,
                   post_link TEXT)''')
    conn.commit()
    conn.close()


def execute_query(query, args=()):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(query, args)
    conn.commit()
    conn.close()


def fetch_data(query, args=()):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(query, args)
    data = cursor.fetchall()
    conn.close()
    return data


def is_admin():
    return session.get('admin')

create_user_table()

connected_users = 0

create_connection()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

questions = [
    {
    "question": "What is the value of 2 + 2 * 2?",
    "options": ["4", "6", "8", "10"],
    "answer": "6"
  },
  {
    "question": "If a car travels 40 miles per hour, how long does it take to travel 120 miles?",
    "options": ["2 hours", "3 hours", "4 hours", "5 hours"],
    "answer": "3 hours"
  },
  {
    "question": "If a shirt costs $20 and is discounted by 25%, what is the discounted price?",
    "options": ["$5", "$10", "$15", "$20"],
    "answer": "$15"
  },
  {
    "question": "Solve: 3x - 7 = 11",
    "options": ["x = 4", "x = 6", "x = 8", "x = 10"],
    "answer": "x = 6"
  },
  {
    "question": "What is the next number in the sequence: 2, 4, 6, 8, ...?",
    "options": ["10", "12", "14", "16"],
    "answer": "10"
  },
  {
    "question": "If 5 apples cost $2.50, how much do 12 apples cost?",
    "options": ["$3.00", "$5.00", "$6.00", "$7.00"],
    "answer": "$6.00"
  },
  {
    "question": "What is the sum of the interior angles of a triangle?",
    "options": ["90 degrees", "180 degrees", "270 degrees", "360 degrees"],
    "answer": "180 degrees"
  },
  {
    "question": "If today is Monday, what day will it be in 5 days?",
    "options": ["Tuesday", "Saturday", "Thursday", "Friday"],
    "answer": "Saturday"
  },
  {
    "question": "What is the square root of 144?",
    "options": ["10", "12", "14", "16"],
    "answer": "12"
  },
  {
    "question": "How many sides does a hexagon have?",
    "options": ["4", "5", "6", "7"],
    "answer": "6"
  },
  {
    "question": "If a clock shows 3:15, what is the angle between the hour and minute hands?",
    "options": ["22.5 degrees", "45 degrees", "90 degrees", "180 degrees"],
    "answer": "7.5 degrees"
  },
  {
    "question": "A train travels at a speed of 60 miles per hour. How far will it travel in 2 hours?",
    "options": ["100 miles", "120 miles", "140 miles", "160 miles"],
    "answer": "120 miles"
  },
  {
    "question": "What is the smallest prime number greater than 20?",
    "options": ["21", "23", "25", "27"],
    "answer": "23"
  },
  {
    "question": "What is the next number in the sequence: 1, 4, 9, 16, ...?",
    "options": ["20", "24", "28", "32"],
    "answer": "25"
  },
  {
    "question": "How many degrees are there in a right angle?",
    "options": ["45 degrees", "90 degrees", "135 degrees", "180 degrees"],
    "answer": "90 degrees"
  },
  {
    "question": "What is 20% of 80?",
    "options": ["12", "16", "18", "20"],
    "answer": "16"
  },
  {
    "question": "If a box contains 12 chocolates and you take away 3, how many chocolates are left?",
    "options": ["6", "7", "8", "9"],
    "answer": "9"
  },
  {
    "question": "How many seconds are there in an hour?",
    "options": ["360", "600", "1800", "3600"],
    "answer": "3600"
  },
  {
    "question": "If x + 4 = 10, what is the value of x?",
    "options": ["2", "4", "6", "8"],
    "answer": "6"
  },
  {
    "question": "What is the perimeter of a rectangle with length 5 and width 3?",
    "options": ["10", "12", "14", "16"],
    "answer": "16"
  },
  {
    "question": "If a baker has 24 cookies and wants to package them in bags of 6, how many bags will he need?",
    "options": ["2", "3", "4", "5"],
    "answer": "4"
  },
  {
    "question": "What is the value of 2^3?",
    "options": ["4", "6", "8", "10"],
    "answer": "8"
  },
  {
    "question": "How many millimeters are in a meter?",
    "options": ["100", "1000", "10,000", "1,000,000"],
    "answer": "1000"
  },
  {
    "question": "If a circle has a radius of 5, what is its circumference?",
    "options": ["5π", "10π", "15π", "20π"],
    "answer": "10π"
  },
  {
    "question": "What is the missing number in the sequence: 2, 4, 8, 16, ...?",
    "options": ["24", "28", "32", "36"],
    "answer": "32"
  },
  {
    "question": "How many feet are there in a yard?",
    "options": ["2", "3", "4", "5"],
    "answer": "3"
  },
  {
    "question": "What is the next number in the sequence: 1, 3, 6, 10, ...?",
    "options": ["12", "14", "16", "18"],
    "answer": "15"
  },
  {
    "question": "If 7x = 35, what is the value of x?",
    "options": ["3", "4", "5", "6"],
    "answer": "5"
  },
  {
    "question": "What is the square of 9?",
    "options": ["72", "81", "90", "99"],
    "answer": "81"
  },
  {
    "question": "How many degrees are there in a circle?",
    "options": ["180", "270", "360", "450"],
    "answer": "360"
  },
  {
    "question": "What is the value of 3^2 + 4^2?",
    "options": ["5", "9", "25", "49"],
    "answer": "25"
  },
  {
    "question": "How many sides does a pentagon have?",
    "options": ["4", "5", "6", "7"],
    "answer": "5"
  },
  {
    "question": "What is the value of 2 * 3 * 4?",
    "options": ["12", "24", "36", "48"],
    "answer": "24"
  },
  {
    "question": "What is the next number in the sequence: 1, 1, 2, 3, 5, ...?",
    "options": ["8", "10", "12", "13"],
    "answer": "8"
  },
  {
    "question": "If 3x + 5 = 20, what is the value of x?",
    "options": ["5", "7", "9", "11"],
    "answer": "5"
  },
  {
    "question": "What is 30% of 200?",
    "options": ["40", "50", "60", "70"],
    "answer": "60"
  },
  {
    "question": "How many sides does a heptagon have?",
    "options": ["6", "7", "8", "9"],
    "answer": "7"
  },
  {
    "question": "What is the sum of the first 10 positive integers?",
    "options": ["45", "50", "55", "60"],
    "answer": "55"
  },
  {
    "question": "What is the value of 10 ÷ 2 * 5?",
    "options": ["5", "10", "15", "20"],
    "answer": "25"
  },
  {
    "question": "If a bag contains 6 red balls and 4 blue balls, what is the probability of drawing a red ball?",
    "options": ["30%", "40%", "50%", "60%"],
    "answer": "60%"
  },
  {
    "question": "What is the square root of 64?",
    "options": ["6", "7", "8", "9"],
    "answer": "8"
  },
  {
    "question": "How many seconds are there in a minute?",
    "options": ["30", "45", "60", "75"],
    "answer": "60"
  },
  {
    "question": "What is the value of 3^3?",
    "options": ["6", "9", "12", "27"],
    "answer": "27"
  },
  {
    "question": "If a rectangle has length 8 and width 6, what is its area?",
    "options": ["24", "32", "40", "48"],
    "answer": "48"
  },
  {
    "question": "What is the next number in the sequence: 2, 6, 12, 20, ...?",
    "options": ["26", "30", "36", "42"],
    "answer": "30"
  },
  {
    "question": "How many sides does a decagon have?",
    "options": ["8", "9", "10", "11"],
    "answer": "10"
  },
  {
    "question": "What is the sum of the first 20 positive integers?",
    "options": ["190", "200", "210", "220"],
    "answer": "210"
  },
  {
    "question": "What is the value of 5 + 3 * 2?",
    "options": ["11", "13", "15", "17"],
    "answer": "11"
  },
  {
    "question": "If a triangle has sides of lengths 3, 4, and 5, is it a right triangle?",
    "options": ["Yes", "No"],
    "answer": "Yes"
  },
  {
    "question": "How many faces does a cube have?",
    "options": ["4", "6", "8", "10"],
    "answer": "6"
  },
  {
    "question": "What is the sum of the angles in a quadrilateral?",
    "options": ["180 degrees", "270 degrees", "360 degrees", "450 degrees"],
    "answer": "360 degrees"
  },
  {
    "question": "What is the value of 2^4?",
    "options": ["8", "16", "32", "64"],
    "answer": "16"
  },
  {
    "question": "What is the value of 4! (4 factorial)?",
    "options": ["12", "24", "36", "48"],
    "answer": "24"
  },
  {
    "question": "What is the next number in the sequence: 1, 2, 4, 8, ...?",
    "options": ["10", "12", "14", "16"],
    "answer": "16"
  },
]

current_question_index = 0
score = 0

@app.route('/', methods=['GET', 'POST']) 
def index(): 
    if request.method == 'POST':
        session.pop('user-id', None)
        return redirect(url_for('index'))  
    else:
        return render_template('index.html')


@app.route('/index.html') 
def index_page(): 
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        print("Username:", username)  
        print("Password:", password)  
        
        conn = create_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?", [username, password])
            user = cursor.fetchone()
            conn.close()
            
            if user:
                session['user_id'] = user  
                return redirect(url_for('home'))
            else:
                error = 'Invalid username or password. Please try again.'
                return render_template('index.html', error=error)
        except Exception as e:
            print("Error executing SQL query:", e)  
            return render_template('index.html', error='An error occurred while processing your request.')
    return redirect(url_for('index'))


@app.route('/home', methods=['GET'])
def home():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id, post_text, post_link, post_image FROM posts ORDER BY id DESC")
    posts = c.fetchall()
    conn.close()

    formatted_posts = []
    for post in posts:
        post_id, post_text, post_link, post_image = post
        formatted_post = {
            'id': post_id,
            'text': post_text,
            'link': post_link,
            'image': base64.b64encode(post_image).decode() if post_image is not None else None
        }
        formatted_posts.append(formatted_post)

    return render_template('home.html', posts=formatted_posts)


@app.route('/home.html')
def home_page():
    return render_template('home.html')

@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    try:
        email = request.json['email']
        new_password = request.json['newPassword']
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Password updated successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/forgot_password.html')
def forgot_password_page():
    return render_template('forgot_password.html')

@app.route('/signup.html') 
def signup_page(): 
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    try:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? OR email=?", (username, email))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({'error': 'Username or email already exists.'}), 400
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
        conn.commit()
        conn.close()

        return redirect(url_for('profile_creating'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/profile_creating', methods=['GET', 'POST'])
def profile_creating():
    if request.method == 'POST':
        username = request.form.get('username')
        profile_type = request.form.get('profile_type')

        if not username or not profile_type:
            return jsonify({'error': 'Username and profile type are required fields.'}), 400

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user_profile (username, profile_type) VALUES (?, ?)", (username, profile_type))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))

    return render_template('profile_creating.html')

@app.route('/profile_creating.html')
def profile_creating_page():
    return render_template('profile_creating.html')


@app.route('/create_post', methods=['POST'])
def create_post():
    try:
        post_text = request.form.get('postText')
        post_image = request.files.get('postImage')
        post_link = request.form.get('postLink')

        if not post_text:
            return jsonify({'error': 'Post text is required.'}), 400

       
        if post_image:
            if post_image.mimetype.startswith('image'):
                image_data = post_image.read()
            else:
                return jsonify({'error': 'Uploaded file is not an image.'}), 400
        else:
            image_data = None

       
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO posts (post_text, post_image, post_link) VALUES (?, ?, ?)",
                       (post_text, image_data, post_link))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Post created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/create_post.html')
def create_post_page():
    return render_template('create_post.html')

@app.route('/chat_box.html')
def chat_box():
    return render_template('/chat_box.html')

@socketio.on('connect')
def handle_connect():
    global connected_users
    connected_users += 1
    emit('connected_users', {'count': connected_users}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    global connected_users
    connected_users -= 1
    emit('connected_users', {'count': connected_users}, broadcast=True)

@socketio.on('message')
def handle_message(message):
    emit('message', {'username': message['username'], 'message': message['message']}, broadcast=True)

@app.route('/logout', methods=['POST'])
def logout():
    return redirect(url_for('index'))

@app.route('/logout.html')
def logout_page():
    return render_template('logout.html')

@app.route('/get_user_info', methods=['POST'])
def get_user_info():
    try:
        username = request.json['username']
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE username = ?", (username,))
        user_info = cursor.fetchone()
        conn.close()

        if user_info:
            return jsonify({'success': True, 'email': user_info[0]}), 200
        else:
            return jsonify({'error': 'User not found.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/setting.html')
def setting():
    return render_template('/setting.html')

@app.route('/quiz.html')
def quiz():
    return render_template('/quiz.html')

@app.route('/question', methods=['GET'])
def get_question():
    global current_question_index
    if current_question_index < len(questions):
        question = questions[current_question_index]
        current_question_index += 1
        return jsonify(question)
    else:
        return jsonify({'error': 'No more questions'})

@app.route('/answer', methods=['POST'])
def check_answer():
    global score
    data = request.get_json()
    selected_answer = data['answer']
    correct_answer = questions[current_question_index - 1]['answer']
    if selected_answer == correct_answer:
        score += 1
    return jsonify({'score': score})

@app.route('/opportunity.html')
def opportunity_page():
    return render_template('/opportunity.html')

@app.route('/opportunity')
def opportunity():
    return render_template('/opportunity.html')

@app.route('/interview.html')
def interview_page():
    return render_template('/interview.html')

@app.route('/interview')
def interview():
    return render_template('/interview.html')
    
@app.route('/admin.html')
def admin_page():
    return render_template('/admin.html')

@app.route('/get_user_list')
def get_user_list():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, email FROM users")
    users = cursor.fetchall()
    conn.close()
    return jsonify(users)

@app.route('/admin_dashboard.html')
def admin_dashboard_page():
    return render_template('/admin_dashboard.html')

@app.route('/admin_login', methods=['POST'])
def admin_login():
    username = request.json.get('username')
    password = request.json.get('password')
    
    if username == 'admin' and password == 'admin2024':
        session['admin'] = True
        return jsonify({'success': True}), 200
    else:
        return jsonify({'error': 'Invalid username or password.'}), 401

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if not is_admin():
        return redirect(url_for('admin_login'))

    users = fetch_data("SELECT * FROM users")
    user_profile = fetch_data("SELECT * FROM user_profile")
    posts = fetch_data("SELECT * FROM posts")

    return render_template('admin_dashboard.html', users=users, user_profile=user_profile, posts=posts)


@app.route('/update_user', methods=['POST'])
def update_user():
    if not is_admin():
        return jsonify({'error': 'Unauthorized access.'}), 401

    user_id = request.json.get('user_id')
    new_username = request.json.get('new_username')
    new_email = request.json.get('new_email')

    execute_query("UPDATE users SET username=?, email=? WHERE user_id=?", (new_username, new_email, user_id))
    return jsonify({'success': True}), 200


@app.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if not is_admin():
        return jsonify({'error': 'Unauthorized access.'}), 401

    execute_query("DELETE FROM users WHERE user_id=?", (user_id,))
    return jsonify({'success': True}), 200

@app.route('/get_user_profiles')
def get_user_profiles():
    user_profiles = fetch_data("SELECT * FROM user_profile")
    return jsonify(user_profiles)


@app.route('/get_posts')
def get_posts():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, post_text, post_link, post_image FROM posts")
    posts = cursor.fetchall()
    conn.close()

    formatted_posts = []
    for post in posts:
        post_id, post_text, post_link, post_image = post
        formatted_post = {
            'id': post_id,
            'text': post_text,
            'link': post_link,
            'image': base64.b64encode(post_image).decode() if post_image is not None else None
        }
        formatted_posts.append(formatted_post)

    return jsonify(formatted_posts)


@app.route('/update_user_profile', methods=['POST'])
def update_user_profile():
    profile_id = request.json.get('profile_id')
    new_username = request.json.get('new_username')
    new_profile_type = request.json.get('new_profile_type')

    execute_query("UPDATE user_profile SET username=?, profile_type=? WHERE user_id=?", (new_username, new_profile_type, profile_id))
    return jsonify({'success': True}), 200


@app.route('/delete_user_profile/<int:profile_id>', methods=['DELETE'])
def delete_user_profile(profile_id):
    execute_query("DELETE FROM user_profile WHERE user_id=?", (profile_id,))
    return jsonify({'success': True}), 200


@app.route('/update_post', methods=['POST'])
def update_post():
    post_id = request.json.get('post_id')
    new_text = request.json.get('new_text')
    new_link = request.json.get('new_link')

    execute_query("UPDATE posts SET post_text=?, post_link=? WHERE id=?", (new_text, new_link, post_id))
    return jsonify({'success': True}), 200

@app.route('/delete_post/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    execute_query("DELETE FROM posts WHERE id=?", (post_id,))
    return jsonify({'success': True}), 200

if __name__ == '__main__':
    socketio.run(app, debug=True)
