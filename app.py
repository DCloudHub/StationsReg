# app.py
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import sqlite3
import json
import math

app = Flask(__name__)
app.secret_key = 'your-secret-key'
CORS(app)

# Database setup
def init_db():
    conn = sqlite3.connect('stations.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  owner TEXT NOT NULL,
                  email TEXT NOT NULL,
                  phone TEXT NOT NULL,
                  address TEXT NOT NULL,
                  latitude REAL NOT NULL,
                  longitude REAL NOT NULL,
                  fuel_types TEXT NOT NULL,
                  photos TEXT,
                  status TEXT DEFAULT 'pending',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')  # Your HTML file

@app.route('/api/register', methods=['POST'])
def register_station():
    data = request.json
    
    # Check for duplicates within 50m radius
    conn = sqlite3.connect('stations.db')
    c = conn.cursor()
    
    # Calculate distance using Haversine formula
    c.execute('SELECT id, latitude, longitude FROM stations WHERE status="approved"')
    existing_stations = c.fetchall()
    
    for station in existing_stations:
        dist = haversine_distance(
            data['latitude'], data['longitude'],
            station[1], station[2]
        )
        if dist < 0.05:  # 50 meters = 0.05 km
            return jsonify({
                'success': False,
                'error': 'Station already exists within 50m radius'
            }), 400
    
    # Save to database
    c.execute('''INSERT INTO stations 
                 (name, owner, email, phone, address, latitude, longitude, fuel_types, photos)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (data['name'], data['owner'], data['email'], data['phone'],
               data['address'], data['latitude'], data['longitude'],
               json.dumps(data['fuel_types']), json.dumps(data['photos'])))
    
    conn.commit()
    station_id = c.lastrowid
    conn.close()
    
    return jsonify({'success': True, 'station_id': station_id})

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in kilometers"""
    R = 6371  # Earth's radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

@app.route('/api/stations')
def get_stations():
    conn = sqlite3.connect('stations.db')
    c = conn.cursor()
    c.execute('SELECT * FROM stations')
    stations = c.fetchall()
    conn.close()
    return jsonify({'stations': stations})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    # Add your authentication logic here
    return jsonify({'success': True, 'token': 'fake-jwt-token'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
