class Config:
    SECRET_KEY = 'your_secret_key'
    MONGO_URI = 'mongodb://127.0.0.1:27017/QMA'

class TestConfig(Config):
    TESTING = True
    MONGO_URI = 'mongodb://127.0.0.1:27017/test_QMA'
