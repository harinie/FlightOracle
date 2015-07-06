from flask import Flask, render_template, json, request, jsonify
import numpy as np
import pandas as pd

#from GetCityWeather import GetCityWeather

# Setting up matplotlib sytles using BMH
s = json.load(open("./static/bmh_matplotlibrc.json"))

airport_data = pd.read_csv('./airports.csv',header=0,quotechar='"',sep=',',na_values = ['NA', '-', '.', ''])

app = Flask(__name__)
app.Debug = True

# log to stderr
import logging
from logging import StreamHandler
file_handler = StreamHandler()
app.logger.setLevel(logging.DEBUG)  # set the desired logging level here
app.logger.addHandler(file_handler)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/query', methods=['POST'])
def query():
    data = json.loads(request.data)
    app.logger.debug(data['depdate'])
    departure_id = np.where(airport_data["iata"]==data['departure'])[0][0]
    arrival_id = np.where(airport_data["iata"]==data['arrival'])[0][0]    
    return jsonify(deplat=airport_data.ix[departure_id]["lat"],deplong=airport_data.ix[departure_id]["long"],arrlat=airport_data.ix[arrival_id]["lat"],arrlong=airport_data.ix[arrival_id]["long"])
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
