from flask import Flask, render_template_string
import requests
import folium

app = Flask(__name__)

# Constants for the map center (example: San Francisco)
MAP_CENTER_LAT = 37.7749
MAP_CENTER_LON = -122.4194
WILDFIRE_API_URL = 'https://eonet.gsfc.nasa.gov/api/v2.1/events?status=open&category=wildfires'
AQI_API_URL = 'https://api.waqi.info/feed/here/?token=03fb00810b1773ffd525c9a786d71aed176d4201'

# Function to fetch AQI data
def fetch_aqi_data():
    response = requests.get(AQI_API_URL)
    if response.status_code == 200:
        data = response.json().get('data', {})
        return data.get('aqi', 0)  # Return AQI value or 0 if not available
    return 0

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
    
    # Fetch AQI data
    aqi = fetch_aqi_data()

    # Render the HTML page with the map and AQI progress bar
    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Wildfire Map and AQI</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4; /* Background for AQI section */
                color: #333;
                text-align: center;
                margin: 0;
                padding: 0;
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
            .container {{
                width: 150px;
                height: 150px;
                position: relative;
                margin-bottom: 20px;
            }}
            .progress-circle {{
                position: relative;
                width: 100%;
                height: 100%;
            }}
            .circle {{
                position: relative;
                width: 100%;
                height: 100%;
                border-radius: 50%;
                background-color: #e6e6e6;
            }}
            .mask {{
                position: absolute;
                width: 100%;
                height: 100%;
                clip: rect(0px, 75px, 150px, 0px);
            }}
            .fill {{
                position: absolute;
                clip: rect(0px, 75px, 150px, 0px);
                background-color: #4caf50;
                width: 100%;
                height: 100%;
                border-radius: 50%;
                transform: rotate(0deg);
            }}
            .inside-circle {{
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                font-size: 24px;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <h1>Wildfire Map and Air Quality Index (AQI)</h1>

        <div class="container">
            <div class="progress-circle" id="progress-circle">
                <div class="circle">
                    <div class="mask full" id="mask-full"></div>
                    <div class="mask half">
                        <div class="fill" id="fill"></div>
                    </div>
                </div>
                <div class="inside-circle" id="aqi-value">{{ aqi }}</div>
            </div>
        </div>

        <iframe src="/map" title="Wildfire Map"></iframe>

        <script>
            document.addEventListener("DOMContentLoaded", function () {{
                const aqi = {aqi};
                const fillElement = document.getElementById('fill');
                const angle = Math.min((aqi / 500) * 360, 360);

                if (angle <= 180) {{
                    fillElement.style.transform = `rotate(${angle}deg)`;
                    document.getElementById('mask-full').style.backgroundColor = 'transparent';
                }} else {{
                    fillElement.style.transform = 'rotate(180deg)';
                    document.getElementById('mask-full').style.backgroundColor = '#4caf50';
                    document.querySelector('.mask.half .fill').style.transform = `rotate(${angle - 180}deg)`;
                }}

                // Change color based on AQI value
                if (aqi <= 50) {{
                    fillElement.style.backgroundColor = '#4caf50'; // Good
                }} else if (aqi <= 100) {{
                    fillElement.style.backgroundColor = '#ffeb3b'; // Moderate
                }} else if (aqi <= 150) {{
                    fillElement.style.backgroundColor = '#ff9800'; // Unhealthy for sensitive groups
                }} else if (aqi <= 200) {{
                    fillElement.style.backgroundColor = '#f44336'; // Unhealthy
                }} else if (aqi <= 300) {{
                    fillElement.style.backgroundColor = '#9c27b0'; // Very Unhealthy
                }} else {{
                    fillElement.style.backgroundColor = '#673ab7'; // Hazardous
                }}
            }});
        </script>
    </body>
    </html>
    """, aqi=aqi)

# Flask route to serve the map HTML file
@app.route('/map')
def serve_map():
    with open('wildfire_map.html', 'r') as f:
        return f.read()

if __name__ == '__main__':
    app.run(debug=True)
