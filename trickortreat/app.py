import requests
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():
    return "home"


if __name__ == '__main__':
    app.run()
