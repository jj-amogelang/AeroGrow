from flask import Flask, render_template, request, jsonify
import requests
from content_database import content_database  # Import the content database

app = Flask(__name__)

# Your OpenWeatherMap API key
OPENWEATHER_API_KEY = 'd2c3bebe233beec28447108d23b4661b'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommendations', methods=['POST'])
def recommendations():
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    print(f"User's Location: Latitude: {latitude}, Longitude: {longitude}")

    # Get user input from the form
    crop_type = request.form.get('cropType')  # Crop type based on the selected service icon
    farm_size = request.form.get('farmSize')  # Farm size as a string
    farm_location = request.form.get('farmLocation')  # Farm location as a string

    # Generate recommendations based on crop type, farm size, and location
    recommendations, videos = get_relevant_content(crop_type, farm_size, farm_location)

    # Render the dashboard with recommendations and videos
    return render_template('dashboard.html', recommendations=recommendations, videos=videos)

def get_relevant_content(crop_type, farm_size, farm_location):
    # Retrieve content based on crop type, location, and size
    relevant_recommendations = []
    relevant_videos = []
    
    if crop_type in content_database:
        if farm_location in content_database[crop_type]:
            size_data = content_database[crop_type][farm_location].get(farm_size, {})
            relevant_recommendations.extend(size_data.get("recommendations", []))
            relevant_videos.extend(size_data.get("videos", []))

    return relevant_recommendations, relevant_videos

@app.route('/get_weather', methods=['POST'])
def get_weather():
    city = request.json.get('city')
    country = request.json.get('country')

    # Fetch current weather data from OpenWeatherMap
    weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={city},{country}&units=metric&appid={OPENWEATHER_API_KEY}'
    response = requests.get(weather_url)

    if response.status_code == 200:
        weather_data = response.json()
        temperature = weather_data['main']['temp']
        return jsonify({'temperature': temperature})
    else:
        return jsonify({'error': 'Unable to fetch weather data'}), response.status_code

@app.route('/get_forecast', methods=['POST'])
def get_forecast():
    city = request.json.get('city')
    country = request.json.get('country')

    # Fetch 5-day weather forecast from OpenWeatherMap
    forecast_url = f'https://api.openweathermap.org/data/2.5/forecast?q={city},{country}&units=metric&appid={OPENWEATHER_API_KEY}'
    response = requests.get(forecast_url)

    if response.status_code == 200:
        forecast_data = response.json()
        # Extract relevant forecast data
        forecast_list = []
        for item in forecast_data['list']:
            date = item['dt_txt'].split(" ")[0]  # Get the date part
            temp = item['main']['temp']
            forecast_list.append({'date': date, 'temp': temp})

        # Group by date and take the average temperature for each day
        daily_forecast = {}
        for entry in forecast_list:
            date = entry['date']
            temp = entry['temp']
            if date not in daily_forecast:
                daily_forecast[date] = []
            daily_forecast[date].append(temp)

        # Calculate average temperatures
        average_forecast = [{'date': date, 'temp': sum(temps) / len(temps)} for date, temps in daily_forecast.items()]

        return jsonify(average_forecast)
    else:
        return jsonify({'error': 'Unable to fetch forecast data'}), response.status_code

@app.route('/community')
def community():
    return render_template('community.html')  # Ensure you have a community.html template

if __name__ == '__main__':
    app.run(debug=True)
