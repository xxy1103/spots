from flask import Flask, render_template
from app.map import map

app = Flask(__name__)


app.register_blueprint(map, url_prefix='/map')

