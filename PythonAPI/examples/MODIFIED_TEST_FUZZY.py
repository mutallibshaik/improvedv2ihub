# FINAL LOGIG FOR FUZZY WIND DEW DATA
from itertools import count
from unittest import result
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import pydb2
import matplotlib.pyplot as plt



def visibilityFactor(x,y): # (dewfactor, windspped)
    # Antecedent and Consequent Objects
    dewfactor = ctrl.Antecedent(np.arange(0,22,0.1), 'dewfactor') #based on 6 years data
    windspeed = ctrl.Antecedent(np.arange(0,70,0.1), 'windspeed')
    visibility_factor = ctrl.Consequent(np.arange(0,1.1,0.01), 'visibility_factor')


    #Custom membership functions
    # dewfactor['poor'] = fuzz.trimf(dewfactor.universe,[0,3,5])
    # dewfactor['average'] = fuzz.trimf(dewfactor.universe,[4,8,10])
    # dewfactor['good'] = fuzz.trimf(dewfactor.universe,[9,15,20])

    # windspeed['dismal'] = fuzz.trimf(windspeed.universe,[0,10,20]) #gentle breeze 
    # windspeed['poor'] = fuzz.trimf(windspeed.universe,[15,27.5,40]) #moderate breeze
    # windspeed['mediocre'] = fuzz.trimf(windspeed.universe,[35,42.5,50]) #strong breeze
    # windspeed['average'] = fuzz.trimf(windspeed.universe,[45,52.5,60]) #near gale
    # windspeed['decent'] = fuzz.trimf(windspeed.universe,[55,65,75]) #gale
    # windspeed['good'] = fuzz.trimf(windspeed.universe,[70,80,90]) #strong gale 
    # windspeed['excellent'] = fuzz.trimf(windspeed.universe,[85,92.5,100]) #storm

    visibility_factor['low'] = fuzz.trapmf(visibility_factor.universe, [0, 0, 0.2, 0.4])
    visibility_factor['medium'] = fuzz.trimf(visibility_factor.universe,[0.2,0.4,0.6])
    #visibility_factor['medium'] = fuzz.trimf(visibility_factor.universe,[0,0.5,1])
    visibility_factor['high'] = fuzz.trapmf(visibility_factor.universe, [0.4,0.6, 1, 1])



    # https://www.canada.ca/en/environment-climate-change/services/general-marine-weather-information/understanding-forecasts/beaufort-wind-scale-table.html
    

    dewfactor.automf(3)
    windspeed.automf(7)

    #dewfactor.view()
    #windspeed.view()
    #visibility_factor.view()


#quality['average'].view()

    rule1 = ctrl.Rule((dewfactor['good'] & windspeed['excellent']) , visibility_factor['low'])   #storm          = excellent
    rule2 = ctrl.Rule((dewfactor['good'] & windspeed['good']) , visibility_factor['low'])        #strong gale    = good
    rule3 = ctrl.Rule((dewfactor['good'] & windspeed['decent']) , visibility_factor['medium'])   #gale           = decent
    rule4 = ctrl.Rule((dewfactor['good'] & windspeed['average']) , visibility_factor['medium'])  #near gale      = average
    rule5 = ctrl.Rule((dewfactor['good'] & windspeed['mediocre']) , visibility_factor['high'])   #strong breeze  = mediocre
    rule6 = ctrl.Rule((dewfactor['good'] & windspeed['poor']) , visibility_factor['high'])       #moderate breeze= poor
    rule7 = ctrl.Rule((dewfactor['good'] & windspeed['dismal']) , visibility_factor['high'])     #gentle breeze  = dismal
    
    rule8 = ctrl.Rule((dewfactor['average'] & windspeed['excellent']) , visibility_factor['low'])
    rule9 = ctrl.Rule((dewfactor['average'] & windspeed['good']) , visibility_factor['low'])
    rule10 = ctrl.Rule((dewfactor['average'] & windspeed['decent']) , visibility_factor['low'])
    rule11 = ctrl.Rule((dewfactor['average'] & windspeed['average']) , visibility_factor['medium'])
    rule12 = ctrl.Rule((dewfactor['average'] & windspeed['mediocre']) , visibility_factor['high'])
    rule13 = ctrl.Rule((dewfactor['average'] & windspeed['poor']) , visibility_factor['high'])
    rule14 = ctrl.Rule((dewfactor['average'] & windspeed['dismal']) , visibility_factor['high'])
    
    rule15 = ctrl.Rule((dewfactor['poor'] & windspeed['excellent']) , visibility_factor['low'])
    rule16 = ctrl.Rule((dewfactor['poor'] & windspeed['good']) , visibility_factor['low'])
    rule17 = ctrl.Rule((dewfactor['poor'] & windspeed['decent']) , visibility_factor['low'])
    rule18 = ctrl.Rule((dewfactor['poor'] & windspeed['average']) , visibility_factor['low'])
    rule19 = ctrl.Rule((dewfactor['poor'] & windspeed['mediocre']) , visibility_factor['low'])
    rule20 = ctrl.Rule((dewfactor['poor'] & windspeed['poor']) , visibility_factor['low'])
    rule21 = ctrl.Rule((dewfactor['poor'] & windspeed['dismal']) , visibility_factor['low'])\

    

    visibility = ctrl.ControlSystem([rule1,rule2,rule3,rule4,rule5,rule6,rule7,
                                rule8,rule9,rule10,rule11,rule12,rule13,rule14,
                                rule15,rule16,rule17,rule18,rule19,rule20,rule21])
    visibility_result = ctrl.ControlSystemSimulation(visibility)

    visibility_result.input['dewfactor'] = float(x)
    visibility_result.input['windspeed'] = float(y)

    visibility_result.compute()

    #print(visibility_result.output['visibility_factor'])
    #print(visibility_result.output)
    visibility_factor.view(sim=visibility_result)
    #plt.show()
    print(visibility_result.output['visibility_factor'])
    return visibility_result.output['visibility_factor']

#visibilityFactor(10,12)

#visibilityFactor(0,50)


def visibility_message(visibility_factor):
    if visibility_factor <= 0.3:
        return "Low Visibility"
    elif 0.3 < visibility_factor < 0.69:
        return "Moderate Visibility"
    elif visibility_factor > 0.69:
        return "High Visibility"