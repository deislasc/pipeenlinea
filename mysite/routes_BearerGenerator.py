from flask import session, current_app, Flask, request
import requests # Needed for making HTTP requests
import time #Needed to generate the OAuth timestamp
import urllib.parse #Needed to URLencode the parameter string
from base64 import b64encode  #Needed for create_signature function
import hmac  #Needed for create_signature function
import hashlib #Needed for create_signature functionx
import binascii#Needed for create_signature function
import datetime
import jwt

app = current_app
def encode_auth_token(user):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=3600),
            'iat': datetime.datetime.utcnow(),
            'sub': user["ownerID"]
        }
        return jwt.encode(
            payload,
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return e

def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """
    try:
        #payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
        payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'),algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return False #'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return False #'Invalid token. Please log in again.'


