from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from . import mongo

auth = Blueprint('auth', __name__)

@auth.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

