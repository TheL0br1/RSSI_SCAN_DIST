import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
def connect_to_RTDB():
    cred = credentials.Certificate('AIzaSyAely9-ilJNLL47cagehLw6oQEkgZ4kZBk')
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://esp-test-6caf4-default-rtdb.firebaseio.com/'
    })
def write_position(node, x, y):
    ref = db.reference(node)
    new_user_ref = ref.push()
    new_user_ref.set({
        'x': x,
        'y': y
    })