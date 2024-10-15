from flask import Flask, render_template_string
import requests
import folium

app = Flask(__name__)

# Constants for the map center (example: San Francisco)
MAP_CENTER_LAT = 37.7749
MAP_CENTER_LON = -122.4194
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

    # Load the map HTML
    with open(map_html_path, 'r') as f:
        map_html = f.read()

    # Render the minimal HTML page with the map
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
                background-color: red; /* Set background color to red */
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
            .map-container {{
                width: 800px;
                height: 600px;
                border-radius: 10px;
                overflow: hidden;
                background-color: #222;
            }}
        </style>
    </head>
    <body>
        <h1>Wildfire Map</h1>
        <div class="map-container">
            {map_html}  <!-- Load the actual map HTML here -->
        </div>
    </body>
    </html>
    """)

if __name__ == '__main__':
    app.run(debug=True)
