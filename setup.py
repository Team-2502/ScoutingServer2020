import pyrebase

import sensitiveInfo

firebase = pyrebase.initialize_app(sensitiveInfo.firebase_info_dev_2021())
database = firebase.database()

database.child('config').child('currentMatch').set(0)
