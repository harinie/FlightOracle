import urllib2
import json

def GetCityWeather(city,state,date):

    city = city.replace(' ','_')
    if date>3:
        date=0
        
    f = urllib2.urlopen('http://api.wunderground.com/api/acab7566950fd543/forecast/q/'+state+'/'+city+'.json')
    json_string = f.read()
    parsed_json = json.loads(json_string)
    qpf_allday = parsed_json['forecast']['simpleforecast']['forecastday'][date]['qpf_allday']['mm']
    forecasttext = parsed_json['forecast']['txt_forecast']['forecastday'][date]['fcttext_metric']
    #print "Current temperature is: %s" % (qpf_allday)
    f.close()
    
    return forecasttext