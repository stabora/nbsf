from flask import render_template, redirect, url_for
from app import app
import os


@app.route('/', endpoint='/')
def home():
    return render_template('home.html')


@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('/'), code=302)


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)

        if filename:
            file_path = os.path.join(app.root_path, endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)

    return url_for(endpoint, **values)
