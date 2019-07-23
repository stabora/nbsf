from flask import current_app, render_template, redirect, request, url_for
from flask_user import current_user
from app import app
import os


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


@app.route('/', endpoint='/')
def home():
    return render_template('home.html')


@app.route('/user/profile', methods=['POST', 'GET'])
def user_profile():
    user_manager = current_app.user_manager
    form = user_manager.register_form(request.form)
    form.username.data = current_user.username
    form.password.data = current_user.password
    form.retype_password.data = current_user.password

    if request.method == 'POST' and form.validate():
        db_adapter = user_manager.db_adapter
        db_adapter.update_object(current_user, first_name=form.first_name.data, last_name=form.last_name.data)
        db_adapter.commit()
        return redirect(url_for('/'))

    print form.errors

    form.first_name.default = current_user.first_name
    form.last_name.default = current_user.last_name
    form.process()

    return render_template(user_manager.user_profile_template, form=form)
