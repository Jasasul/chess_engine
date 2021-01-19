from flask import render_template, url_for, redirect, Blueprint

routes = Blueprint('routes', __name__)

@routes.route('/')
@routes.route('/home')
def home():
    return render_template('home.html')