from flask import Flask, render_template, send_file, request, jsonify
import requests
import json
from datetime import datetime, timedelta
import pdfkit  # You'll need to install this: pip install pdfkit
import os

app = Flask(__name__)

# Your OpenWeatherMap API key
OPENWEATHER_API_KEY = 'd2c3bebe233beec28447108d23b4661b'

# Load course content from JSON file
with open('course_content.json') as f:
    course_content = json.load(f)

# Temporary storage for events (replace with database in production)
events = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommendations')
def home():
    return render_template('dashboard.html')

@app.route('/generate_certificate')
def generate_certificate():
    # Get current date for the certificate
    date = datetime.now().strftime("%B %d, %Y")
    
    # Render certificate template
    return render_template('certificate.html', 
                         date=date,
                         name="Student Name")  # You can pass the actual user's name here

@app.route('/recommendations', methods=['POST'])
def recommendations():
    crop_type = request.form.get('cropType')
    farm_size = request.form.get('farmSize')
    farm_location = request.form.get('farmLocation')

    # Convert farm_size to readable format
    farm_size_display = {
        'small-scale': 'Small Scale (0.5 - 5 hectares)',
        'medium-scale': 'Medium Scale (5 - 20 hectares)',
        'large-scale': 'Large Scale (20 - 50 hectares)',
        'commercial': 'Commercial Scale (50+ hectares)'
    }.get(farm_size, farm_size)

    # Simplified location advice
    location_advice = {
        'Limpopo': 'With Limpopo\'s warm climate and long growing season, you\'re in an ideal position for tropical and subtropical crops. Focus on heat-tolerant varieties and efficient irrigation systems.',
        'Eastern Cape': 'The Eastern Cape\'s diverse climate zones allow for various farming approaches. Consider implementing drought-resistant techniques and focus on seasonal crop rotation.',
        'Western Cape': 'The Mediterranean climate of the Western Cape is perfect for winter rainfall crops. Plan your irrigation carefully during summer months and consider wind protection measures.',
        'KwaZulu-Natal': 'KwaZulu-Natal\'s high rainfall and fertile soils are great assets. Focus on proper drainage systems and pest management due to the humid conditions.'
    }

    # Simplified size tips
    size_tips = {
        'small-scale': 'Maximize your yield through intensive farming methods. Consider intercropping and vertical farming techniques to make the most of your space.',
        'medium-scale': 'Implement precision farming techniques and consider investing in basic machinery. Focus on efficient resource management and crop rotation.',
        'large-scale': 'Invest in mechanization and automated systems. Consider implementing GPS-guided farming and advanced irrigation systems.',
        'commercial': 'Look into advanced agricultural technologies and consider diversifying your crop portfolio. Focus on supply chain optimization and market integration.'
    }

    # Get the specific advice and tip
    specific_location_advice = location_advice.get(farm_location, '')
    specific_size_tip = size_tips.get(farm_size, '')

    # Get courses from course content
    courses = course_content['crops'].get(crop_type, {}).get('courses', [])

    print(f"Debug - Crop Type: {crop_type}")
    print(f"Debug - Farm Size: {farm_size_display}")
    print(f"Debug - Location: {farm_location}")
    print(f"Debug - Location Advice: {specific_location_advice}")
    print(f"Debug - Size Tip: {specific_size_tip}")

    return render_template('dashboard.html',
                         crop_type=crop_type,
                         farm_size=farm_size_display,
                         farm_location=farm_location,
                         location_advice=specific_location_advice,
                         size_tip=specific_size_tip,
                         courses=courses)

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
    return render_template('community.html')  

@app.route('/aerogrow_ai')
def aerogrow_ai():
    return render_template('aerogrow_ai.html')  

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

@app.route('/test')
def test():
    return render_template('test.html')  # Ensure this points to your test.html file

@app.route('/get_events')
def get_events():
    # Add some default events
    default_events = [
        {
            'title': 'Planting Season',
            'start': datetime.now().strftime('%Y-%m-%d'),
            'description': 'Start planting spring crops'
        },
        {
            'title': 'Harvest Time',
            'start': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'description': 'Begin harvesting winter crops'
        }
    ]
    return jsonify(events + default_events)

@app.route('/add_event', methods=['POST'])
def add_event():
    event_data = request.json
    events.append({
        'title': event_data['title'],
        'start': event_data['date'],
        'description': event_data['description']
    })
    return jsonify({'success': True})

@app.route('/learning_path')
def learning_path():
    # Get parameters from query string
    crop_type = request.args.get('cropType')
    farm_size = request.args.get('farmSize')
    farm_location = request.args.get('farmLocation')
    
    # Get courses from course content
    courses = course_content['crops'].get(crop_type, {}).get('courses', [])
    
    return render_template('learning_path.html',
                         crop_type=crop_type,
                         farm_size=farm_size,
                         farm_location=farm_location,
                         courses=courses)

if __name__ == '__main__':
    app.run(debug=True)
