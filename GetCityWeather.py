import urllib2
import json
import numpy as np

   
def GetCityWeather(city,state,date):

    city = city.replace(' ','_')
    if date>3:
        date=0
        
    f = urllib2.urlopen('http://api.wunderground.com/api/acab7566950fd543/forecast/q/'+state+'/'+city+'.json')
    json_string = f.read()
    parsed_json = json.loads(json_string)
    
    forecasttext = parsed_json['forecast']['txt_forecast']['forecastday'][date]['fcttext_metric']
    
    # make the vector
    discrete_vals = []
    cont_vals = []

    #"Mean TemperatureF"
    high = float(parsed_json['forecast']['simpleforecast']['forecastday'][date]['high']['fahrenheit'])
    low = float(parsed_json['forecast']['simpleforecast']['forecastday'][date]['low']['fahrenheit'])
    cont_vals.append(0.5*(high + low))
    
    # mean humidity
    cont_vals.append(float(parsed_json['forecast']['simpleforecast']['forecastday'][date]['avehumidity']))
    cont_vals.append(float(parsed_json['forecast']['simpleforecast']['forecastday'][date]['maxwind']['mph']))
    cont_vals.append(float(parsed_json['forecast']['simpleforecast']['forecastday'][date]['avewind']['mph']))
    # precipitationIn
    cont_vals.append(float(parsed_json['forecast']['simpleforecast']['forecastday'][date]['qpf_allday']['in']))
    
        # wind dir degrees
    windDirDegrees = float(parsed_json['forecast']['simpleforecast']['forecastday'][date]['avewind']['degrees'])
    discrete_vals = np.floor(windDirDegrees/30 )
    
    f.close()

    return forecasttext,discrete_vals,cont_vals