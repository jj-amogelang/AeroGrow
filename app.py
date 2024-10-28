from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

# Your OpenWeatherMap API key
OPENWEATHER_API_KEY = ''

# Load course content from JSON file
with open('course_content.json') as f:
    course_content = json.load(f)

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

    # Retrieve courses and recommendations based on user selections
    courses = course_content['crops'].get(crop_type, {}).get('courses', [])
    recommendations = course_content['farm_sizes'].get(farm_size, {}).get('recommendations', [])

    return render_template('dashboard.html', cropType=crop_type, farmSize=farm_size, farmLocation=farm_location, courses=courses, recommendations=recommendations)

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

@app.route('/dashboard', methods=['GET'])
def dashboard():
    crop_type = request.args.get('cropType')
    farm_size = request.args.get('farmSize')
    farm_location = request.args.get('farmLocation')

    # Retrieve courses based on user selections
    courses = course_content['crops'].get(crop_type, {}).get('courses', [])
    
    # Retrieve recommendations based on farm size and location
    farm_size_recommendations = course_content['farm_sizes'].get(farm_size, {}).get('recommendations', [])
    location_recommendations = course_content['locations'].get(farm_location, {}).get('recommendations', [])

    return render_template('dashboard.html', 
                           cropType=crop_type, 
                           farmSize=farm_size, 
                           farmLocation=farm_location, 
                           courses=courses, 
                           farm_size_recommendations=farm_size_recommendations, 
                           location_recommendations=location_recommendations)

if __name__ == '__main__':
    app.run(debug=True)
