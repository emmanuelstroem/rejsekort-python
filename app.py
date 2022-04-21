from flask import Flask, Response
import os # to get env variables 

port = os.getenv('PORT', 3000)
env = os.getenv('ENV', "development")

app = Flask(__name__)


@app.route('/')
def health_check():
    return {"status": "Healthy"}, 200, {"Content-Type": "application/json"}


# run app in debug mode if env is development 
if __name__ == '__main__':
    if env == "development":
        app.run(host="0.0.0.0", debug=True, port=port)
    else:
        app.run(port=port)
