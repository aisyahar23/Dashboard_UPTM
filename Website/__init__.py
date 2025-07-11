from flask import Flask

def createApp():
    app = Flask(__name__, static_folder='static')
    
    # Set up any necessary configuration for the Flask app
    app.config['SECRET_KEY'] = "SSSDWslddlvpSfdwpwcwxa"


    from .dashboard import dashboard


    # Register blueprints
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(dashboard, url_prefix='/dashboard')
    return app
