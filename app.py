from flask import Flask, render_template, request, redirect, session, flash
import sqlite3

app = Flask(__name__)

conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        password TEXT NOT NULL
    )
''')
conn.commit()
conn.close()

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS buses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bus_number TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL
        )
    ''')
    # Check if we have any buses, if not, add a dummy one
    cursor.execute("SELECT count(*) FROM buses")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO buses (bus_number, latitude, longitude) VALUES (?, ?, ?)", 
                       ('Bus 101', 12.9716, 77.5946)) # Example: Bangalore coordinates
        conn.commit()
    conn.commit()
    conn.close()

init_db()

# Home route (renders both forms)
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name']
    password = request.form['password']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, password) VALUES (?, ?)", (name, password))
    conn.commit()
    conn.close()
    return render_template('index.html', msg="Registration successfull")

@app.route('/signin', methods=['POST'])
def signin():
    name = request.form['name']
    password = request.form['password']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE name = ? AND password = ?", (name, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return render_template('logged.html')
    else:
        return render_template('index.html', msg="Entered wrong credantials")

@app.route('/api/buses')
def get_buses():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT bus_number, latitude, longitude FROM buses")
    rows = cursor.fetchall()
    conn.close()
    
    buses = []
    for row in rows:
        buses.append({
            'bus_number': row[0],
            'latitude': row[1],
            'longitude': row[2]
        })
    return {'buses': buses}

@app.route('/api/update_bus', methods=['POST'])
def update_bus():
    # Simple endpoint to simulate bus movement
    # Expects JSON: {"bus_number": "Bus 101", "lat": 12.xxx, "lng": 77.xxx}
    data = request.json
    if not data:
        return {'status': 'error', 'message': 'No data provided'}, 400
        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE buses SET latitude = ?, longitude = ? WHERE bus_number = ?", 
                   (data['lat'], data['lng'], data['bus_number']))
    conn.commit()
    conn.close()
    return {'status': 'success'}

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
