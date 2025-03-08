from flask import Flask

app = Flask(__name__)

# Import and register blueprints
from routes.place_route import place_bp
# from routes.city_routes import city_bp
# from routes.activity_routes import activity_bp

app.register_blueprint(place_bp, url_prefix="/place")
# app.register_blueprint(city_bp, url_prefix="/cities")
# app.register_blueprint(activity_bp, url_prefix="/activities")

if __name__ == "__main__":
    app.run(debug=True)
