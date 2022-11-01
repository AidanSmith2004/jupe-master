from flask import Blueprint, render_template, request, redirect
from app.models import db, Results
import configparser
import requests
from datetime import datetime


ui_bp = Blueprint(
   'ui_bp', __name__,
   template_folder='templates',
   static_folder='static'
)


@ui_bp.route('/')
def home():
    return render_template('home.html')


@ui_bp.route('/upload', methods=['POST'])
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
    temp_min = data['main']['temp_min']
    temp_max = data['main']['temp_max']
    created = datetime.now()
    created = datetime.timestamp(created)
    created = '<a href="/result/'+str(created)+'">'+str(created)+'</a'
    dt_obj = datetime.fromtimestamp(timestamp)
    print(dt_obj)
    now = datetime.now()
    print(now)
    pressure = data["main"]["pressure"]
    # utc_time = datetime.now(timezone.utc)
    result = Results(location=location, feels_like=feels_like, temp=temp, dt_obj=dt_obj, icon_url=icon_url,
                     weather=weather, pressure=pressure, temp_min=temp_min, temp_max=temp_max, created=created)
    db.session.add(result)
    db.session.commit()
    return redirect("/results")


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


@ui_bp.route('/results')
def list_results():
    results = Results.query
    return render_template('results.html', title='results', results=results)


@ui_bp.route('/api/results')
def results_all():
    return {'data': [result.to_dict() for result in Results.query]}


@ui_bp.route('/result/<created>', methods=['POST', 'GET'])
def list_result(created):
    result = Results.query.filter_by(created=created).first()
    return render_template('result.html', result=result)

