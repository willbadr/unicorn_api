# unicorn_api

This is our API Proxy code for use by trusted Unicorn Rentals partners, and less trusted DevOps teams.

## Getting Started

If you want to locally test etc:
* Have python 2.7

```
pip install -r requirements.txt
python app.py
```

## Tests
```
python tests_app.py
```

## Deployment
Deploy how suits you, but included is a Dockerfile if you want to use Docker, and an appspec.yml for CodeDeploy.

Make sure you set the BACKEND_API environment variable.

```
docker build -t unicorn_api .
docker run unicorn_api -p 5000:5000
```

## Built With
Python  
Flask  
flask_restful  
Requests  
# unicorn_api
