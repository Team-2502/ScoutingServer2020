import pyrebase
import os
import ast

firebase = pyrebase.initialize_app(ast.literal_eval(os.environ['firebase_info']))
database = firebase.database()

database.child('config').child('currentMatch').set(1)
