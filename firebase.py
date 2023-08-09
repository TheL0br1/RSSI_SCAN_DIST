import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from config import accessPoints

def connect_to_RTDB():
    cred = credentials.Certificate('bau-navi-firebase-adminsdk-6x14o-ad79afa928.json')
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://bau-navi-default-rtdb.europe-west1.firebasedatabase.app/'
    })


def write_position(node, x, y):
    ref = db.reference(node)
    ref.set({
        'x': float(x),
        'y': float(y)
    })
def get_model_id(main_module_id):
    ref = db.reference("modelSensors/" + main_module_id + "modelId")
    data = ref.get()
    print(data.items())
def get_modules_id(main_module_id):
    ref = db.reference("modelSensors/"+main_module_id+"/floors/"+main_module_id+"/modules/")
    data = ref.get()
    signalAttenuation = 2.2
    distance = 1
    signal = -50
    ssids =[]
    locations=[]
    if data:
        for user_id, user_info in data.items():
            serial_id = user_info.get('serialId', 'Unknown Serial ID')
            coordinates = user_info.get('coordinates')
            # Дополнительные поля, которые могут быть присутствовать
            if coordinates is not None:
                ssids.append(user_id)
                locations.append(coordinates)

        for ssid, location in zip(ssids, locations):
            access_point = {
                'signalAttenuation': signalAttenuation,
                'location': location,
                'reference': {
                    'distance': distance,
                    'signal': signal
                },
                'ssid': ssid
            }
            accessPoints.append(access_point)

        # Вывод полученного массива accessPoints
        print(accessPoints)
        return ssid
    else:
        print("No user data found.")
