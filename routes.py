from flask import Flask, render_template, json, request, jsonify
import numpy as np
import pandas as pd
import time,datetime
from GetCityWeather import GetCityWeather
# log to stderr
import logging
from logging import StreamHandler
file_handler = StreamHandler()



airport_data = pd.read_csv('./airports.csv',header=0,quotechar='"',sep=',',na_values = ['NA', '-', '.', ''])
discrete_encode_file='model/discrete_encode.txt'
imputer_file='model/imputer.npy'
scale_file='model/scaler.npy'
clf_file='model/clf.npy'
reg_file='model/reg.npy'

imputer = np.load(imputer_file)
scaler = np.load(scale_file)
clf = np.load(clf_file)
reg = np.load(reg_file)
cat_keys=[]
with open(discrete_encode_file) as f:
    for line in f:
        cat_keys.append(line.strip())
f.close()
    
app = Flask(__name__)
app.Debug = True
app.logger.setLevel(logging.DEBUG)  # set the desired logging level here
app.logger.addHandler(file_handler)
########### calculations
def makeFeatureVector(data):
    testVector = np.zeros(2)
    return testVector
    
def predictFlightStatus(depid,arrid,depdate,deptime,carrier):

    dateval = datetime.date(int(depdate.split('-')[0]),int(depdate.split('-')[1]),int(depdate.split('-')[2]))
    dep_disc_vector = []

    dep_disc_vector.append('MONTH='+str(int(depdate.split('-')[1])))
    dep_disc_vector.append('DAY_OF_WEEK='+str(dateval.weekday()+1))
    hour = float(deptime.split(':')[0])
    #if deptime.split(' ')[1]:
    #    hour = hour + 12
    dep_disc_vector.append('CRS_DEP_TIME='+str(hour)) 
    dep_disc_vector.append('CARRIER='+carrier) 
    
    daysfromNow = int(depdate.split('-')[2]) - int(time.strftime("%d"))
    depforetext,dep_disc_we,dep_cont_we=GetCityWeather(airport_data.ix[depid]["city"],airport_data.ix[depid]["state"],daysfromNow)
    arrforetext,arr_disc_we,arr_cont_we=GetCityWeather(airport_data.ix[arrid]["city"],airport_data.ix[arrid]["state"],daysfromNow)
    
    dep_disc_vector.append('WindDirDegrees='+str(dep_disc_we))
    dep_disc_vector.append('WindDirDegrees_DEST='+str(arr_disc_we))
    
    # first encode categorical variables
    disc_features = np.zeros(len(cat_keys))
    for entry in dep_disc_vector:
        found_ind = [e for e,x in enumerate(cat_keys) if entry==x]
        disc_features[found_ind[0]]=1
    
    all_features=np.concatenate((dep_cont_we, arr_cont_we, disc_features), axis=1)
    # then inpute
    for e,entry in enumerate(all_features):
        if np.isnan(entry):
            all_features[e] = imputer[e]
            
    # now scale
    for e,entry in enumerate(all_features):
        all_features[e] = all_features[e] - scaler[e] # demean
        all_features[e] = 1.0*all_features[e]/scaler[e+all_features.shape[0]] # scale

    #now predict
    prediction = np.dot(all_features,clf[0:all_features.shape[0]]) + clf[-1]
    prediction = np.exp(-1.0*prediction)
    cancellation=int(100/(1+prediction))
    
    #
    prediction = np.dot(all_features,reg[0:all_features.shape[0]]) + reg[-1]
    delay=int(prediction)
    return depforetext,arrforetext,cancellation,delay


########## App related

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/query', methods=['POST'])
def query():
    data = json.loads(request.data)
    data['departure'] = data['departure'].upper()
    data['arrival'] = data['arrival'].upper()    
    departure_id = np.where(airport_data["iata"]==data['departure'])[0][0]
    arrival_id = np.where(airport_data["iata"]==data['arrival'])[0][0]    
    depwe,arrwe,cancellation,delay = predictFlightStatus(departure_id,arrival_id,data['depdate'],data['deptime'],data['carrier'])
    return jsonify(deplat=airport_data.ix[departure_id]["lat"],deplong=airport_data.ix[departure_id]["long"],
                   arrlat=airport_data.ix[arrival_id]["lat"],arrlong=airport_data.ix[arrival_id]["long"],
                    depwe="Weather at departure: "+depwe,arrwe="Weather at arrival: "+arrwe,
                    cancellation="Chance of cancellation: "+str(cancellation)+'%',delay="Expected delay: "+str(delay)+'min')
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
