from flask import Flask, render_template, request
import requests
import configparser
from datetime import datetime
from app.models import db

app = Flask(__name__)
app.debug = True
app.config.from_object('config')

db.init_app(app)

db.create_all()

@app.route('/')
def weather_dashboard():
    return render_template('home.html')


@app.route('/results', methods=['POST'])
def render_results():
    zip_code = request.form['zipCode']
    temp_unit = request.form['temp_unit']
    print(temp_unit)
    api_key = get_api_key()
    if temp_unit == "F":
        data = get_weather_results_imperial(zip_code, api_key)
        temp = "{0:.2f}".format(data["main"]["temp"])
    else:
        data = get_weather_results_metric(zip_code, api_key)
        temp = "{0:.2f}".format(data["main"]["temp"])
    # tempc = "{0:.2f}".format((float(tempf) - 32) * 5 / 9)
    feels_like = "{0:.2f}".format(data["main"]["feels_like"])
    weather = data["weather"][0]["main"]
    location = data["name"]
    icon = data["weather"][0]["icon"]
    icon_url = "http://openweathermap.org/img/w/" + icon + ".png"
    timestamp = 1661261478
    dt_obj = datetime.datetime.fromtimestamp(timestamp)
    print(dt_obj)
    now = datetime.datetime.now()
    print(now)
    # utc_time = datetime.now(timezone.utc)
    return render_template('results.html',
                           location=location, temp=temp, dt_obj=dt_obj, now=now,
                           feels_like=feels_like, weather=weather, icon_url=icon_url)


def get_api_key():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['openweathermap']['api']


def get_weather_results_metric(zip_code, api_key):
    api_url = "https://api.openweathermap.org/data/2.5/weather?zip={}&units=metric&appid={}".format(zip_code, api_key)
    r = requests.get(api_url)
    return r.json()


def get_weather_results_imperial(zip_code, api_key):
    api_url = "https://api.openweathermap.org/data/2.5/weather?zip={}&units=imperial&appid={}".format(zip_code, api_key)
    r = requests.get(api_url)
    return r.json()


print(get_weather_results_imperial("95129", "6d5e9ce85b27e3228611e45c197387ba"))
print(get_weather_results_metric("95129", "6d5e9ce85b27e3228611e45c197387ba"))


if __name__ == '__main__':
    app.run()
