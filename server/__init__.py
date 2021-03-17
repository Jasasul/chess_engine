from flask import Flask

def create_app():
    app = Flask(__name__)
    # setting up routes from blueprint
    from server.routes import routes
    app.register_blueprint(routes)
    # returns flask app
    return app