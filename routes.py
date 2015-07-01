from flask import Flask, render_template, json, request
import numpy as np

import matplotlib
import json
import random

matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.ioff()

from threading import Lock
lock = Lock()
import datetime
import mpld3
from mpld3 import plugins

from mpl_toolkits.basemap import Basemap
import pandas as pd

from GetCityWeather import GetCityWeather

# Setting up matplotlib sytles using BMH
s = json.load(open("./static/bmh_matplotlibrc.json"))
matplotlib.rcParams.update(s)

airport_data = pd.read_csv('./airports.csv',header=0,quotechar='"',sep=',',na_values = ['NA', '-', '.', ''])

def draw_fig(departure,arrival,depdate):
    """Returns html equivalent of matplotlib figure

    Parameters
    ----------
    fig_type: string, type of figure
            one of following:
                    * line
                    * bar

    Returns
    --------
    d3 representation of figure
    """
        

    departure_id = np.where(airport_data["iata"]==departure)[0][0]
    arrival_id = np.where(airport_data["iata"]==arrival)[0][0]
 
    fig, ax = plt.subplots()   
    m = Basemap(llcrnrlon=-119,llcrnrlat=22,urcrnrlon=-64,urcrnrlat=49,
            projection='lcc',lat_1=33,lat_2=45,lon_0=-95)
    m.drawcoastlines()   
    m.drawcountries()  
    m.drawstates()    
    dep_xdata, dep_ydata = m(airport_data.ix[departure_id]['long'],airport_data.ix[departure_id]['lat'])
    arr_xdata, arr_ydata = m(airport_data.ix[arrival_id]['long'],airport_data.ix[arrival_id]['lat'])
    ax.plot([dep_xdata,arr_xdata],[dep_ydata,arr_ydata], '-')
    
    #temp = GetCityWeather(airport_data.ix[departure_id]['city'],airport_data.ix[departure_id]['state'],depdate)
    #app.logger.debug(temp)
#    with lock:
#        
#        m = Basemap(llcrnrlon=-119,llcrnrlat=22,urcrnrlon=-64,urcrnrlat=49,
#            projection='lcc',lat_1=33,lat_2=45,lon_0=-95)
#        
#        m.drawcoastlines()
#        m.drawcountries()
#        m.drawstates()        
#        
#        
#    
#        if fig_type == "line":
#            
    
    return mpld3.fig_to_html(fig)

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
    return draw_fig(data["departure"],data["arrival"],data['depdate'])


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
