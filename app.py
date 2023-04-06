# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long

"""Prime Trust testing"""

from flask import Flask, request, render_template, session
from ptapi import PrimeTrust

import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

socure_key = os.getenv('SOCURE_SDK_KEY')

@app.route('/')
def home():
    """home page"""
    return render_template('home.html')


@app.route('/currentuser')
def current_user():
    """return current user information"""
    pt = PrimeTrust()
    user_info = pt.get_current_user()

    data = {
        'name': user_info["name"],
        'email': user_info["email"]
    }
    return render_template('currentuser.html', **data)


@app.route('/socurePII')
def socure_pii():
    data = {
        'socureKey': socure_key
    }
    return render_template('socurePII.html', **data)


@app.route('/socure', methods=['POST'])
def socure():
    data = {}
    for fieldname, value in request.form.items():
        data[fieldname] = value
    data['socureKey'] = socure_key
    return render_template('socure.html', **data)


@app.route('/socureOnSuccess', methods=['POST'])
def socure_on_success():
    data = {}
    for fieldname, value in request.form.items():
        data[fieldname] = value

    return render_template('socureOnSuccess.html', **data)


@app.route('/createAccount', methods=['POST'])
def create_account():
    data = {}
    for fieldname, value in request.form.items():
        data[fieldname] = value

    pt = PrimeTrust()
    acct_id = pt.create_account_with_socure(
        data["referenceId"],
        data["documentUuid"],
        data["deviceId"],
        data["firstName"],
        data["middleName"],
        data["lastName"],
        data["email"],
        data["phone"],
        data["dob"],
        data["taxIdNumber"],
        data["street1"],
        data["street2"],
        data["city"],
        data["state"],
        data["postal"]
    )

    data["accountId"] = acct_id

    return render_template('accountCreated.html', **data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
