from flask import Flask
import os
from flask import request
import json
from supabase import create_client, Client
from flask import jsonify
from flask_cors import CORS
from helpers.wpl import getLocation
from math import sin, cos, sqrt, atan2, radians

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
        rssi = [mac1, mac2, mac3]
        lng = request.json.get('long')
        lat = request.json.get('lat')
        device_id = request.json.get('device_id')
        data, count = supabase.table('locations').insert({"wplx": lng, "wply": lat,"pdrx":lng,"pdry":lat,"finalx":lng,"finaly":lat,"device_id":798}).execute()
        data2, count2= supabase.table('sensor-readings').insert({"ax": ax, "ay": ay,"az":az,"gx":gx,"gy":gy,"gz":gz,"mx":mx,"my":my,"mz":mz,"calcx":lat,"calcy":lng}).execute()
        data3,count3= supabase.table('wifi-readings').insert({"mac1": mac1, "mac2": mac2,"mac3":mac3,"calcx":lat,"calcy":lng}).execute()
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
