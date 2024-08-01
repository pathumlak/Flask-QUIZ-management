from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import os
import csv
import io
from flask import make_response
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import pytz 

app = Flask(__name__)
if os.getenv('FLASK_ENV') == 'testing':
    app.config.from_object('config.TestConfig')
else:
    app.config.from_object('config.Config')
mongo = PyMongo(app)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            return redirect(url_for('login'))
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = mongo.db.users.find_one({'_id': ObjectId(data['user_id'])})
            if not current_user:
                return redirect(url_for('login'))
        except:
            return redirect(url_for('login'))
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        existing_user = mongo.db.users.find_one({'username': username})
        if existing_user is None:
            mongo.db.users.insert_one({'username': username, 'password': hashed_password, 'isadmin': False})
            return redirect(url_for('login'))
        else:
            return 'Username already exists!'
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = mongo.db.users.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            token = jwt.encode({
                'user_id': str(user['_id']),
                'exp': datetime.datetime.now(pytz.UTC) + datetime.timedelta(minutes=30)  # Updated line
            }, app.config['SECRET_KEY'])
            resp = redirect(url_for('dashboard'))
            resp.set_cookie('token', token)
            return resp
        else:
            return 'Invalid username or password!'
    return render_template('login.html')
@app.route('/logout')
def logout():
    resp = redirect(url_for('home'))
    resp.delete_cookie('token')
    return resp

@app.route('/dashboard')
@token_required
def dashboard(current_user):
    if 'isadmin' in current_user and current_user['isadmin']:
        return render_template('admin.html')
    else:
        return render_template('student.html')

@app.route('/admin/quiz', methods=['GET', 'POST'])
@token_required
def manage_quiz(current_user):
    if not current_user['isadmin']:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        question = request.form['question']
        options = [request.form['option1'], request.form['option2'], request.form['option3'], request.form['option4']]
        correct_answer = request.form['correct_answer']
        
        mongo.db.quizzes.insert_one({
            'question': question,
            'options': options,
            'correct_answer': correct_answer
        })
        return redirect(url_for('manage_quiz'))

    quizzes = mongo.db.quizzes.find()
    return render_template('manage_quiz.html', quizzes=quizzes)

@app.route('/admin/quiz/edit/<quiz_id>', methods=['GET', 'POST'])
@token_required
def edit_quiz(current_user, quiz_id):
    if not current_user['isadmin']:
        return redirect(url_for('dashboard'))
    
    quiz = mongo.db.quizzes.find_one({'_id': ObjectId(quiz_id)})

    if request.method == 'POST':
        question = request.form['question']
        options = [request.form['option1'], request.form['option2'], request.form['option3'], request.form['option4']]
        correct_answer = request.form['correct_answer']
        
        mongo.db.quizzes.update_one({'_id': ObjectId(quiz_id)}, {
            '$set': {
                'question': question,
                'options': options,
                'correct_answer': correct_answer
            }
        })
        return redirect(url_for('manage_quiz'))

    return render_template('edit_quiz.html', quiz=quiz)

@app.route('/admin/quiz/delete/<quiz_id>')
@token_required
def delete_quiz(current_user, quiz_id):
    if not current_user['isadmin']:
        return redirect(url_for('dashboard'))
    
    mongo.db.quizzes.delete_one({'_id': ObjectId(quiz_id)})
    return redirect(url_for('manage_quiz'))

@app.route('/admin/manage_students', methods=['GET', 'POST'])
@token_required
def manage_students(current_user):
    if not current_user['isadmin']:
        return redirect(url_for('dashboard'))

    students = mongo.db.users.find({'isadmin': False})
    return render_template('manage_students.html', students=students)

@app.route('/admin/toggle_access/<student_id>')
@token_required
def toggle_access(current_user, student_id):
    if not current_user['isadmin']:
        return redirect(url_for('dashboard'))
    
    student = mongo.db.users.find_one({'_id': ObjectId(student_id)})
    if student:
        mongo.db.users.update_one({'_id': ObjectId(student_id)}, {'$set': {'can_access_exam': not student.get('can_access_exam', False)}})
    return redirect(url_for('manage_students'))

@app.route('/exam', methods=['GET', 'POST'])
@token_required
def take_exam(current_user):
    if current_user['isadmin']:
        return redirect(url_for('dashboard'))
    
    if not current_user.get('can_access_exam', False):
        return render_template('not_allowed.html')
    
    quizzes = list(mongo.db.quizzes.find())
    if request.method == 'POST':
        score = 0
        total_questions = len(quizzes)
        answers = request.form
        for quiz in quizzes:
            if answers.get(str(quiz['_id'])) == quiz['correct_answer']:
                score += 1
        
        # Store the result in the database
        mongo.db.results.insert_one({
            'student_id': current_user['_id'],
            'score': score,
            'total_questions': total_questions
        })

        # Revoke access after the student submits the exam
        mongo.db.users.update_one({'_id': current_user['_id']}, {'$set': {'can_access_exam': False}})
        
        return render_template('result.html', score=score, total_questions=total_questions)
    
    return render_template('exam.html', quizzes=quizzes)

@app.route('/admin/results')
@token_required
def view_results(current_user):
    if not current_user['isadmin']:
        return redirect(url_for('dashboard'))
    
    students = mongo.db.users.find({'isadmin': False})
    results = []
    total_marks = []
    for student in students:
        student_results = mongo.db.results.find({'student_id': student['_id']})
        for result in student_results:
            results.append({
                'username': student['username'],
                'score': result['score'],
                'total_questions': result['total_questions']
            })
            total_marks.append(result['score'])
    
    mean = sum(total_marks) / len(total_marks) if total_marks else 0
    avg = sum(total_marks) / len(total_marks) if total_marks else 0
    
    return render_template('view_results.html', results=results, mean=mean, avg=avg)

@app.route('/admin/download_results')
@token_required
def download_results(current_user):
    if not current_user['isadmin']:
        return redirect(url_for('dashboard'))
    
    students = mongo.db.users.find({'isadmin': False})
    results = []
    total_marks = []
    for student in students:
        student_results = mongo.db.results.find({'student_id': student['_id']})
        for result in student_results:
            results.append({
                'username': student['username'],
                'score': result['score'],
                'total_questions': result['total_questions']
            })
            total_marks.append(result['score'])
    
    mean = sum(total_marks) / len(total_marks) if total_marks else 0
    avg = sum(total_marks) / len(total_marks) if total_marks else 0

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Username', 'Score', 'Total Questions'])
    for result in results:
        writer.writerow([result['username'], result['score'], result['total_questions']])
    writer.writerow([])
    writer.writerow(['Mean', mean])
    writer.writerow(['Average', avg])

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=student_results.csv'
    response.headers['Content-type'] = 'text/csv'
    return response

@app.route('/admin/grant_all_access', methods=['POST'])
@token_required
def grant_all_access(current_user):
    if not current_user['isadmin']:
        return redirect(url_for('dashboard'))
    
    mongo.db.users.update_many({'isadmin': False}, {'$set': {'can_access_exam': True}})
    return redirect(url_for('manage_students'))

@app.route('/admin/analyze')
@token_required
def analyze_results(current_user):
    if not current_user['isadmin']:
        return redirect(url_for('dashboard'))

    students = mongo.db.users.find({'isadmin': False})
    results = []
    for student in students:
        student_results = mongo.db.results.find({'student_id': student['_id']})
        for result in student_results:
            results.append({
                'username': student['username'],
                'score': result['score'],
                'total_questions': result['total_questions']
            })

    # Create the chart
    usernames = [result['username'] for result in results]
    scores = [result['score'] for result in results]

    plt.figure(figsize=(10, 5))
    bars = plt.bar(usernames, scores, color=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
    plt.xlabel('Students')
    plt.ylabel('Scores')
    plt.title('Students Scores Analysis')
    plt.xticks(rotation=45, ha="right")

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2 - 0.15, yval + 0.1, int(yval))

    # Save the plot to a PNG image
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template('analyze_results.html', plot_url=plot_url)
if __name__ == '__main__':
    app.run(debug=True)
