from flask import Flask, render_template, request
from content_database import content_database  # Import the content database

app = Flask(__name__)

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

@app.route('/community')
def community():
    return render_template('community.html')  # Ensure you have a community.html template

if __name__ == '__main__':
    app.run(debug=True)
