from flask import Flask
from utils.helper import jwt
app = Flask(__name__)


app.secret_key = 'Dheeraj@2006'


app.config['JWT_SECRET_KEY'] = 'Dheeraj@2006'

jwt.init_app(app)
# Import and register blueprints
from routes.core_route.place_route import place_bp
from routes.core_route.city_route import city_bp
from routes.core_route.activity_route import activity_bp
from routes.core_route.auth_route import auth_bp
from routes.app_route.home_route import home_bp

app.register_blueprint(place_bp, url_prefix="/api/v1/Place")
app.register_blueprint(city_bp, url_prefix="/city")
app.register_blueprint(activity_bp, url_prefix="/activity")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(home_bp, url_prefix="/api/v1/Mobile")

if __name__ == "__main__":
    app.run(debug=True)
