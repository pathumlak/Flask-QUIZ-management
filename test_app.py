import unittest
import json
from app import app, mongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/test'
        self.app = app.test_client()
        self.app.testing = True
        
        
    def register(self, username, password):
        return self.app.post('/register', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def create_admin_user(self):
        password_hash = generate_password_hash('adminpass', method='pbkdf2:sha256')
        mongo.db.users.insert_one({'username': 'admin', 'password': password_hash, 'isadmin': True})

    def test_register(self):
        response = self.register('testuser', 'testpassword')
        self.assertEqual(response.status_code, 200)
        user = mongo.db.users.find_one({'username': 'testuser'})
        self.assertIsNotNone(user)
        self.assertTrue(check_password_hash(user['password'], 'testpassword'))

  
    def test_admin_dashboard_access(self):
        self.create_admin_user()
        self.login('admin', 'adminpass')
        response = self.app.get('/dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'admin', response.data)

    def test_student_dashboard_access(self):
        self.register('testuser', 'testpassword')
        self.login('testuser', 'testpassword')
        response = self.app.get('/dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'student', response.data)

    def test_manage_quiz_as_admin(self):
        self.create_admin_user()
        self.login('admin', 'adminpass')
        response = self.app.post('/admin/quiz', data=dict(
            question='What is 2+2?',
            option1='3',
            option2='4',
            option3='5',
            option4='6',
            correct_answer='4'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        quiz = mongo.db.quizzes.find_one({'question': 'What is 2+2?'})
        self.assertIsNotNone(quiz)
        self.assertEqual(quiz['correct_answer'], '4')

    def test_edit_quiz(self):
        self.create_admin_user()
        self.login('admin', 'adminpass')
        quiz_id = mongo.db.quizzes.insert_one({
            'question': 'What is 2+2?',
            'options': ['3', '4', '5', '6'],
            'correct_answer': '4'
        }).inserted_id
        response = self.app.post(f'/admin/quiz/edit/{quiz_id}', data=dict(
            question='What is 3+3?',
            option1='5',
            option2='6',
            option3='7',
            option4='8',
            correct_answer='6'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        quiz = mongo.db.quizzes.find_one({'_id': ObjectId(quiz_id)})
        self.assertEqual(quiz['question'], 'What is 3+3?')
        self.assertEqual(quiz['correct_answer'], '6')

    def test_delete_quiz(self):
        self.create_admin_user()
        self.login('admin', 'adminpass')
        quiz_id = mongo.db.quizzes.insert_one({
            'question': 'What is 2+2?',
            'options': ['3', '4', '5', '6'],
            'correct_answer': '4'
        }).inserted_id
        response = self.app.get(f'/admin/quiz/delete/{quiz_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        quiz = mongo.db.quizzes.find_one({'_id': ObjectId(quiz_id)})
        self.assertIsNone(quiz)

    def test_manage_students_access(self):
        self.create_admin_user()
        self.register('teststudent', 'studentpassword')
        self.login('admin', 'adminpass')
        response = self.app.get('/admin/manage_students', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'teststudent', response.data)

    def test_toggle_student_access(self):
        self.create_admin_user()
        self.register('teststudent', 'studentpassword')
        student = mongo.db.users.find_one({'username': 'teststudent'})
        self.login('admin', 'adminpass')
        response = self.app.get(f'/admin/toggle_access/{student["_id"]}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        student = mongo.db.users.find_one({'username': 'teststudent'})
        self.assertTrue(student['can_access_exam'])

    
    def test_view_results(self):
        self.create_admin_user()
        self.register('teststudent', 'studentpassword')
        student = mongo.db.users.find_one({'username': 'teststudent'})
        mongo.db.results.insert_one({'student_id': student['_id'], 'score': 5, 'total_questions': 10})
        self.login('admin', 'adminpass')
        response = self.app.get('/admin/results', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'teststudent', response.data)

    def test_download_results(self):
        self.create_admin_user()
        self.register('teststudent', 'studentpassword')
        student = mongo.db.users.find_one({'username': 'teststudent'})
        mongo.db.results.insert_one({'student_id': student['_id'], 'score': 5, 'total_questions': 10})
        self.login('admin', 'adminpass')
        response = self.app.get('/admin/download_results', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'teststudent', response.data)
        self.assertIn(b'Mean', response.data)
        self.assertIn(b'Average', response.data)

  
    
if __name__ == '__main__':
    unittest.main()
