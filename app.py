#!/usr/bin/env python
"""
API Frontend for our mobile apps to use, served by one of our many devops teams.
Sends HASH to Backend secure API to verify the caller is one of the many UnicronRentals teams
Returns HASH that mobile apps use to verify the message AND server API version are legitimate
HASH changes when files in codebase change for security.
Wouldnt want competitors scraping our FULL backend API, or man in middle attacks against our apps
Probably better way to do this, but for now this will do.
"""

__author__ = 'Inigo Montoya (inigo.montoya@unicornrentals.click)'
__vcs_id__ = 'fa5820bed77873c372122b7f9a4c9177'
__version__ = '575252a6682bae904e032f2badc91408'

from flask import Flask, request
from flask_restful import Resource, Api
import os
import requests
import json
import logging

logging.basicConfig(level=logging.INFO)

#Secure Hash code
from secrethash import hasher

#Set Unicorn Rentals backend API URL to proxy too
BACKEND_API = os.getenv('BACKEND_API')
if BACKEND_API == None:
    print "BACKEND API environment variable not set."

#Make sure we can find unicorn files
CODE_DIR = os.getenv('CODE_DIR')
if not CODE_DIR:
    CODE_DIR = './'

app = Flask(__name__)
api = Api(app)
#Lets try to use AWS X-ray for metrics / logging if available to us
try:
    from aws_xray_sdk.core import xray_recorder
    from aws_xray_sdk.core import patch_all
    from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
    xray_recorder.configure(service='Unicorn API Proxy')
    plugins = ('EC2Plugin','ECSPlugin')
    xray_recorder.configure(plugins=plugins)
    patch_all()
except:
    logging.exception('Failed to import X-ray')

try:
    XRayMiddleware(app, xray_recorder)
except:
    logging.exception('Failed to load X-ray')

def get_secret():
    #Compute secure hash to use as shared secret with backend API
    secretmaker = hasher()
    secretmaker.generate(CODE_DIR+'unicorn_descriptions/*')
    secretmaker.generate(CODE_DIR+'secrethash.py')
    secretmaker.generate_text(__version__)
    secretmaker.generate_text(__vcs_id__)
    return secretmaker.hexdigest.strip()

class HealthCheck(Resource):
    def get(self):
        #Test Connectivity to Backend API
        return {'status': 'OK'}

class Unicorn(Resource):
    def get(self):
        #Return List of Unicorns - You may find some cool unicorns to check out
        #Unsecured API
        req = requests.get(BACKEND_API+'/unicorn')
        return json.loads(req.text), req.status_code

class Unicorns(Resource):
    def get(self, unicorn_id):
        #Get details of specific Unicorn, add cached random description
        #(doesnt matter too much, our unicorns are mainly the same, and MAGIC),
        #And compute a salt / Secure API
        shared_secret = get_secret()
        headers = {'x-unicorn-api-secret': shared_secret}
        req = requests.get(BACKEND_API+'/unicorn/'+unicorn_id, headers=headers)
        return json.loads(req.text), req.status_code, {'x-unicorn-api-secret': shared_secret}

    def post(self, unicorn_id):
        #Give a unicorn a treat by sending me a json 'snack'
        #API secured by secret bonus codes
        shared_secret = get_secret()
        data = request.get_json()
        headers = {'x-unicorn-api-secret': shared_secret}
        req = requests.post(BACKEND_API+'/unicorn/'+unicorn_id, data = json.dumps({'snack': data['snack']}), headers=headers)
        return req.json(), req.status_code, {'x-unicorn-api-secret': shared_secret}


api.add_resource(HealthCheck,'/healthcheck','/')
api.add_resource(Unicorn, '/unicorn')
api.add_resource(Unicorns, '/unicorn/<string:unicorn_id>')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
