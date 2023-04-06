# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long

import os
import base64
import datetime

import requests
from flask import session

from dotenv import load_dotenv

load_dotenv()


class PrimeTrust:
    _username = os.getenv('PT_USERNAME')
    _password = os.getenv('PT_PASSWORD')

    _pt_url_base = os.getenv('PT_URL_BASE')

    def __init__(self):

        if 'ptjwt' in session:
            print('Using cached JWT')
            self._jwt = session['ptjwt']
        else:
            print('requesting JWT')
            self._jwt = self._request_jwt()
            session['ptjwt'] = self._jwt

        if 'ptjwt' in session and 'ptjwt_expires' in session:
            now = datetime.datetime.now(datetime.timezone.utc)
            expiry = datetime.datetime.strptime(session['ptjwt_expires'], '%Y-%m-%dT%H:%M:%S%z')

            if expiry >= now:
                print('Using cached JWT')
                return

            session.pop('ptjwt')
            session.pop('ptjwt_expires')

        print('requesting JWT')
        response = self._request_jwt()

        session['ptjwt'] = response['jwt']
        session['ptjwt_expires'] = response['expires']


    def _request_jwt(self):
        url = f'{self._pt_url_base}/auth/jwts'

        jwt_expires_at = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%S%z')

        body = {
            'expires_at': jwt_expires_at
        }

        if 'ptjwt' in session:
            session.pop('ptjwt')
        if 'ptjwt_expires' in session:
            session.pop('ptjwt_expires')

        response = self._send_request('POST', url, body)

        jwt = response.json()['token']
        return {'jwt': jwt, 'expires': jwt_expires_at}


    def _send_request(self, method, url, body = None):
        headers = {
            "ACCEPT": "application/json",
            "CONTENT-TYPE": "application/json"
        }

        if 'ptjwt' in session:
            headers['AUTHORIZATION'] = f'Bearer {session["ptjwt"]}'
        else:
            token = f'{self._username}:{self._password}'
            auth = base64.b64encode(token.encode()).decode('utf-8')
            headers['AUTHORIZATION'] = f'Basic {auth}'

        if method == "GET":
            response = requests.get(url=url, headers=headers)
        elif method == "POST":
            response = requests.post(url=url, headers=headers, json=body)
        elif method == "PATCH":
            response = requests.patch(url=url, headers=headers, json=body)

        print("==================")
        print(f"{response.request.method} {response.request.url}")
        # print(response.request.params)
        print(response.request.headers)
        print(response.request.body)
        print(f"status: {response}")
        print(response.json())
        print("==================")

        print(response.raise_for_status())

        return response


    def get_current_user(self):
        url = f"{self._pt_url_base}/v2/users/current"

        response = self._send_request("GET", url)

        user_info = {"id": response.json()["data"]["id"], "name": response.json()["data"]["attributes"]["name"], "email": response.json()["data"]["attributes"]["email"]}
        return user_info


# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
    def create_account_with_socure(
        self,
        _, # reference_id
        document_uuid,
        device_id,
        firstname,
        middlename,
        lastname,
        email,
        phone,
        dob,
        tax_id_number,
        street1,
        street2,
        city,
        state,
        postal
    ):
        url = f"{self._pt_url_base}/v2/accounts"

        body = {
            "data": {
                "type": "accounts",
                "attributes": {
                    "account-type": "custodial",
                    "name": f"{firstname} {lastname}'s Account",
                    "authorized-signature": f"{firstname} {lastname}",
                    "webhook-config": {
                        "url": "https://webhook.site/11af2ce0-d8de-48d7-8d04-254cdee1ca1a",
                        "contact-email": "malexander+webhook@primetrust.com",
                        "shared-secret": "5558675309",
                        "enabled": True
                    },
                    "owner": {
                        "contact-type": "natural_person",
                        "first_name": firstname,
                        "middle_name": middlename,
                        "last_name": lastname,
                        "email": email,
                        "date-of-birth": dob,
                        "tax-id-number": tax_id_number,
                        "tax-country": "US",
                        "primary-phone-number": {
                            "country": "US",
                            "number": phone,
                            "sms": True
                        },
                        "primary-address": {
                            "street-1": street1,
                            "street-2": street2,
                            "postal-code": postal,
                            "city": city,
                            "region": state,
                            "country": "US"
                        },
                        "socure_document_id": document_uuid,
                        "socure_device_id": device_id
                    }
                }
            }
        }

        response = self._send_request("POST", url, body)
        return response.json()["data"]["id"]
# pylint: enable=too-many-arguments
# pylint: enable=too-many-locals
