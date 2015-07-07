from flask import Flask, render_template, json, request, jsonify
import numpy as np
import pandas as pd
import time

from GetCityWeather import GetCityWeather


airport_data = pd.read_csv('./airports.csv',header=0,quotechar='"',sep=',',na_values = ['NA', '-', '.', ''])

app = Flask(__name__)
app.Debug = True

########### calculations
def makeFeatureVector(data):
    testVector = np.zeros(2)
    return testVector
    
def predictFlightStatus(depid,arrid,depdate,deptime):
    daysfromNow = int(depdate.split('-')[1]) - int(time.strftime("%d"))
    depforetext=GetCityWeather(airport_data.ix[depid]["city"],airport_data.ix[depid]["state"],daysfromNow)
    arrforetext=GetCityWeather(airport_data.ix[arrid]["city"],airport_data.ix[arrid]["state"],daysfromNow)
   # testVector = makeFeatureVector(data)
    #depwe="Sunny"
    #arrwe="Rain"
    cancellation=50
    delay=60
    return depforetext,arrforetext,cancellation,delay


########## App related

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
    data['departure'] = data['departure'].upper()
    data['arrival'] = data['arrival'].upper()    
    departure_id = np.where(airport_data["iata"]==data['departure'])[0][0]
    arrival_id = np.where(airport_data["iata"]==data['arrival'])[0][0]    
    depwe,arrwe,cancellation,delay = predictFlightStatus(departure_id,arrival_id,data['depdate'],data['deptime'])
    return jsonify(deplat=airport_data.ix[departure_id]["lat"],deplong=airport_data.ix[departure_id]["long"],
                   arrlat=airport_data.ix[arrival_id]["lat"],arrlong=airport_data.ix[arrival_id]["long"],
                    depwe="Weather at departure: "+depwe,arrwe="Weather at arrival: "+arrwe,
                    cancellation="Chance of cancellation: "+str(cancellation)+'%',delay="Expected delay: "+str(delay)+'min')
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
