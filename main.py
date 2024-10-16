from flask import Flask, render_template_string
import requests
import folium

app = Flask(__name__)

# Constants for the map center (example: San Francisco)
MAP_CENTER_LAT =
MAP_CENTER_LON = 
WILDFIRE_API_URL = 'https://eonet.gsfc.nasa.gov/api/v2.1/events?status=open&category=wildfires'

# Function to fetch wildfire data from the NASA EONET API
def fetch_wildfire_data():
    response = requests.get(WILDFIRE_API_URL)
    if response.status_code != 200:
        return []
    return response.json().get('events', [])

# Function to create a Folium map with wildfire data
def create_map():
    wildfires = fetch_wildfire_data()
    fire_map = folium.Map(location=[MAP_CENTER_LAT, MAP_CENTER_LON], zoom_start=5)

    # Add wildfire markers to the map
    for fire in wildfires:
        for geometry in fire['geometries']:
            lat, lon = geometry['coordinates'][1], geometry['coordinates'][0]
            folium.Marker([lat, lon], popup=fire['title']).add_to(fire_map)

    # Save map to HTML and return the file path
    map_file = 'wildfire_map.html'
    fire_map.save(map_file)
    return map_file

# Flask route for the web interface
@app.route('/')
def index():
    # Use the Python function to create the map
    map_html_path = create_map()

    # Render the minimal HTML page with the map embedded in an iframe
    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Wildfire Map</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: red; /* Keep background red */
                color: #F5F5DC; /* Text color */
                text-align: center; /* Center the title */
                margin: 0;
                padding: 0;
                height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }}
            h1 {{
                margin-bottom: 20px;
            }}
            iframe {{
                width: 800px;
                height: 600px;
                border: none;
                border-radius: 10px;
            }}
        </style>
    </head>
    <body>
        <h1>Wildfire Map</h1>
        <iframe src="/map" title="Wildfire Map"></iframe>
    </body>
    </html>
    """)

# Flask route to serve the map HTML file
@app.route('/map')
def serve_map():
    with open('wildfire_map.html', 'r') as f:
        return f.read()

if __name__ == '__main__':
    app.run(debug=True)
