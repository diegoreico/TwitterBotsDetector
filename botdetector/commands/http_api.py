def create_http_api():
    
    from flask import Flask
    from flask_apispec import FlaskApiSpec

    app = Flask(__name__)

    @app.route("/")
    def hello():
        return "Hello World!"

    docs = FlaskApiSpec(app)
    docs.register(hello)
