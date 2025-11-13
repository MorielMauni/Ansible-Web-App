from flask import Blueprint

def create_api_blueprint():
    from app.api import routes
    return routes.api
