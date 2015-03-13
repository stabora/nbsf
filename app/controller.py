from flask import render_template, redirect, url_for
from app import app


@app.route('/', endpoint='/')
def home():
    return render_template('home.html')


@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('/'), code=302)
