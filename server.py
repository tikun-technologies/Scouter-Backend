from flask import Flask
from utils.helper import jwt
app = Flask(__name__)


app.secret_key = 'Dheeraj@2006'


app.config['JWT_SECRET_KEY'] = 'Dheeraj@2006'

jwt.init_app(app)
# Import and register blueprints
from routes.place_route import place_bp
from routes.city_route import city_bp
from routes.activity_route import activity_bp
from routes.auth_route import auth_bp

app.register_blueprint(place_bp, url_prefix="/place")
app.register_blueprint(city_bp, url_prefix="/city")
app.register_blueprint(activity_bp, url_prefix="/activity")
app.register_blueprint(auth_bp, url_prefix="/auth")

if __name__ == "__main__":
    app.run(debug=True)
