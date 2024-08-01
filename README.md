# 🎓 Flask Quiz Management Application 🎓

Welcome to the **Flask Quiz Management Application**! This project allows admins to manage quizzes and students, while students can register, log in, and take quizzes.

## 🚀 Features

- **User Registration & Login**: Secure user authentication using hashed passwords.
- **Admin Dashboard**: Admins can manage quizzes and student access.
- **Student Dashboard**: Students can view their dashboard and take quizzes.
- **Quiz Management**: Admins can add, edit, and delete quizzes.
- **Student Management**: Admins can grant or revoke exam access for students.
- **Results Analysis**: Admins can view and download student results and analyze them with colorful charts.

## 🛠️ Installation

1. **Set up a virtual environment**:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

2. **Install the dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Set up environment variables**:
    Create a `.env` file in the root directory and add the following:
    ```plaintext
    SECRET_KEY=your_secret_key
    MONGO_URI=mongodb://127.0.0.1:27017/your_database
    ```

4. **Run the application**:
    ```sh
    flask run
    ```

## 🧪 Running Tests

Run the unit tests to ensure everything is working correctly:
```sh
python -m unittest discover
