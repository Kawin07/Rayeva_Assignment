from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import uuid
from flask import g, request
from config import config, validate_runtime_config
from app.errors import register_error_handlers

db = SQLAlchemy()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('APP_ENV') or os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    validate_runtime_config(app.config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route('/')
    def root():
        return jsonify({
            'success': True,
            'message': 'Rayeva AI Systems for Sustainable Commerce',
            'api': 'Visit http://localhost:5000/api for API documentation'
        }), 200

    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.before_request
    def assign_request_id():
        incoming = request.headers.get('X-Request-Id', '').strip()
        g.request_id = incoming or str(uuid.uuid4())

    @app.after_request
    def attach_request_id(response):
        response.headers['X-Request-Id'] = getattr(g, 'request_id', 'unknown')
        return response

    register_error_handlers(app)

    return app
