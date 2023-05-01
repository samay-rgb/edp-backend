from flask import Flask
import os
from flask import request
import json
import random
from supabase import create_client, Client
from flask import jsonify
from flask_cors import CORS
from helpers.wpl import getLocation
from math import sin, cos, sqrt, atan2, radians
from helpers.pdr import estimate_location
import numpy as np
from filterpy.kalman import KalmanFilter

wifilocs = {
    'MAC1': [0, 0],
    'MAC2': [5,5],
    'MAC3': [5,10],
}


def final_estimation(zs, x0, P0, F, H, Q, R):
    kf = KalmanFilter(dim_x=2, dim_z=2)
    kf.x = np.array([x0[0, 0], x0[1, 0]])
    kf.P = P0
    kf.F = F
    kf.H = H
    kf.Q = Q
    kf.R = R
    estimated_states = []
    for z in zs:
        kf.predict()
        kf.update(z)
        estimated_states.append(kf.x)
    return np.array(estimated_states)


def hybridize(zs):

    # Initial state
    x0 = np.array([[45], [17.5]])

    # Initial covariance
    P0 = np.array([[0.1, 0.0], [0.0, 0.1]])

    # State transition matrix
    F = np.array([[1.0, 0.1], [0.0, 1.0]])

    # Measurement function
    H = np.array([[1.0, 0.0], [0.0, 1.0]])

    # Process noise covariance
    Q = np.array([[0.1, 0.0], [0.0, 0.1]])

    # Measurement noise covariance
    R = np.array([[0.1, 0.0], [0.0, 0.1]])

    # Call the position_estimation function
    estimated_states = final_estimation(zs, x0, P0, F, H, Q, R)
    return estimated_states[0][0], estimated_states[0][1]


app = Flask(__name__)
CORS(app)
url: str = 'https://dplltipzjdmwdgxbihor.supabase.co'
key: str = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRwbGx0aXB6amRtd2RneGJpaG9yIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY4MjUxMzM4NywiZXhwIjoxOTk4MDg5Mzg3fQ.GHDRfXRoOfsJsqGk-liZmnCCgfWGJofLBe1KzSJmVMc'
supabase: Client = create_client(url, key)


@app.route('/')
def hello_world():
    return 'Hello World'


@app.route('/sensor-reading', methods=['POST'])
def sensor_data():
    if request.method == 'POST':
        ax = request.json.get('ax')
        ay = request.json.get('ay')
        az = request.json.get('az')
        gx = request.json.get('gx')
        gy = request.json.get('gy')
        gz = request.json.get('gz')
        mx = request.json.get('mx')
        my = request.json.get('my')
        mz = request.json.get('mz')
        mac1 = request.json.get('mac1') if "mac1" in request.json else 0
        mac2 = request.json.get('mac2') if "mac2" in request.json else 0
        mac3 = request.json.get('mac3') if "mac3" in request.json else 0
        gas = request.json.get("gas")
        rssi = [mac1, mac2, mac3]
        diff1 = random.uniform(0, 0.788)
        diff2 = random.uniform(0, 0.95)
        x, y = getLocation(rssi, wifilocs)
        x2, y2 = estimate_location([ax, ay, az], [gx, gy, gz], [mx, my, mz])
        xf, yf = hybridize([[x, y], [x2, y2]])
        # print(x, y)
        # device_id = request.json.get('device_id')
        data, count = supabase.table('locations').insert(
            {"wplx": x, "wply": y, "pdrx": x2, "pdry": y2, "finalx": xf, "finaly": yf, "device_id": 798, "gas": gas}).execute()
        data2, count2= supabase.table('sensor-readings').insert({"ax": ax, "ay": ay,"az":az,"gx":gx,"gy":gy,"gz":gz,"mx":mx,"my":my,"mz":mz,"calcx":x2,"calcy":y2}).execute()
        data3,count3= supabase.table('wifi-readings').insert({"mac1": mac1, "mac2": mac2,"mac3":mac3,"calcx":x,"calcy":y}).execute()
        return jsonify({'message': 'Data stored successfully'}), 200


@app.route('/get-sensor-data', methods=['GET'])
def get_sensor_data():
    data, count = supabase.table('sensor-readings').select('*').execute()
    data2, count2 = supabase.table('wifi-readings').select('*').execute()
    data3, count3 = supabase.table('locations').select('*').execute()
    print(data[1])
    return jsonify({"sensordata": data[1], "wifidata": data2[1], "location": data3[1]}), 200


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
