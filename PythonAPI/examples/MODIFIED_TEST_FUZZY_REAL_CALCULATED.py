# FINAL LOGIG FOR FUZZY WIND DEW DATA
from itertools import count
from unittest import result
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import pydb2
import matplotlib.pyplot as plt


def SafetyFactor(x,y): # (dewfactor, windspped)
    # Antecedent and Consequent Objects
    dewfactor = ctrl.Antecedent(np.arange(0,10,1), 'dewfactor') #http://tornado.sfsu.edu/geosciences/classes/m356/Dewpoint.htm
    windspeed = ctrl.Antecedent(np.arange(0,110,1), 'windspeed')
    safefactor = ctrl.Consequent(np.arange(0,1.1,0.01), 'safefactor')


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

    # safefactor['low'] = fuzz.trapmf(safefactor.universe, [0, 0, 0.2, 0.5])
    # safefactor['medium'] = fuzz.trapmf(safefactor.universe,[0.2,0.3,0.6, 0.7])
    # #safefactor['medium'] = fuzz.trimf(safefactor.universe,[0.2,0.45, 0.7])
    # safefactor['high'] = fuzz.trapmf(safefactor.universe, [0.5, 0.7, 1, 1])
    # safefactor.view()
    



    # dewfactor['snow'] = fuzz.trimf(dewfactor.universe,[0,4,5])
    # dewfactor['snow overcast'] = fuzz.trimf(dewfactor.universe,[1,4,5])
    # dewfactor['rain overcast'] = fuzz.trimf(dewfactor.universe,[1,5,8])    
    # dewfactor['snow partially cloudy'] = fuzz.trimf(dewfactor.universe,[2,8,9])
    # dewfactor['overcast'] = fuzz.trimf(dewfactor.universe,[2,9,16])
    # dewfactor['rain partially cloudy'] = fuzz.trimf(dewfactor.universe,[3,16,20])
    # dewfactor['partially cloudy'] = fuzz.trimf(dewfactor.universe,[3,20,22])
    # dewfactor['rain'] = fuzz.trimf(dewfactor.universe,[7,14,22])
    # dewfactor['clear'] = fuzz.trimf(dewfactor.universe,[5,22,25])
    
    dewfactor['snow'] = fuzz.trimf(dewfactor.universe,[0,5,10])
    dewfactor['snow_overcast'] = fuzz.trimf(dewfactor.universe,[10,15,20])
    dewfactor['rain_overcast'] = fuzz.trimf(dewfactor.universe,[20,25,30])    
    dewfactor['snow_partially_cloudy'] = fuzz.trimf(dewfactor.universe,[30,35,40])
    dewfactor['overcast'] = fuzz.trimf(dewfactor.universe,[40,45,50])
    dewfactor['rain_partially_cloudy'] = fuzz.trimf(dewfactor.universe,[50,55,60])
    dewfactor['partially_cloudy'] = fuzz.trimf(dewfactor.universe,[60,65,70])
    dewfactor['rain'] = fuzz.trimf(dewfactor.universe,[70,75,80])
    dewfactor['clear'] = fuzz.trimf(dewfactor.universe,[80,85,90])


    # https://www.canada.ca/en/environment-climate-change/services/general-marine-weather-information/understanding-forecasts/beaufort-wind-scale-table.html
    #windspeed['calm'] = fuzz.trapmf(windspeed.universe,[0,0,10,10])
    windspeed['light_breeze'] = fuzz.trimf(windspeed.universe,[0,5,10])
    windspeed['gentle_breeze'] = fuzz.trimf(windspeed.universe,[10,15,20]) 
    windspeed['moderate_breeze'] = fuzz.trimf(windspeed.universe,[20,25,30])
    windspeed['fresh_breeze'] = fuzz.trimf(windspeed.universe,[30,35,40])
    windspeed['strong_breeze'] = fuzz.trimf(windspeed.universe,[40,45,50])
    windspeed['near_gale'] = fuzz.trimf(windspeed.universe,[50,55,60])
    windspeed['gale'] = fuzz.trimf(windspeed.universe,[60,67.5,75])
    windspeed['strong_gale'] = fuzz.trimf(windspeed.universe,[75,82.5,90]) 
    windspeed['storm'] = fuzz.trimf(windspeed.universe,[90,95,100])
    #windspeed['storm'] = fuzz.trapmf(windspeed.universe,[90,90,100,120])
    
    

    #dewfactor.automf(3)
    #dewfactor.view()
    #windspeed.automf(7)
    #windspeed.view()


    
    safefactor['low'] = fuzz.trapmf(safefactor.universe, [0,0, 0.2, 0.4])
    safefactor['medium'] = fuzz.trapmf(safefactor.universe,[0,0.4,0.49,1])
    #safefactor['medium'] = fuzz.trimf(safefactor.universe,[0.4,0.45, 0.49])
    safefactor['high'] = fuzz.trapmf(safefactor.universe, [0.49, 0.8 ,1.0,1.0])

    #safefactor.view()




    # rule1 = ctrl.Rule((dewfactor['snow'] & windspeed['light breeze']) , safefactor['low'])   #storm          = excellent
    # rule2 = ctrl.Rule((dewfactor['snow'] & windspeed['gentle breeze']) , safefactor['low'])        #strong gale    = good
    # rule3 = ctrl.Rule((dewfactor['snow'] & windspeed['moderate breeze']) , safefactor['low'])   #gale           = decent
    # rule4 = ctrl.Rule((dewfactor['snow'] & windspeed['fresh breeze']) , safefactor['low'])
    # rule5 = ctrl.Rule((dewfactor['snow'] & windspeed['strong breeze']) , safefactor['low'])  #near gale      = average
    # rule6 = ctrl.Rule((dewfactor['snow'] & windspeed['near gale']) , safefactor['high'])   #strong breeze  = mediocre
    # rule7 = ctrl.Rule((dewfactor['snow'] & windspeed['gale']) , safefactor['low'])       #moderate breeze= poor
    # rule8 = ctrl.Rule((dewfactor['snow'] & windspeed['strong gale']) , safefactor['low'])     #gentle breeze  = dismal
    # rule9 = ctrl.Rule((dewfactor['snow'] & windspeed['storm']) , safefactor['low'])


    rule1 = ctrl.Rule((dewfactor['snow'] & windspeed['light_breeze']) |
                      (dewfactor['snow'] & windspeed['gentle_breeze']) |
                      (dewfactor['snow'] & windspeed['moderate_breeze']) |
                      (dewfactor['snow'] & windspeed['fresh_breeze']) |
                      (dewfactor['snow'] & windspeed['strong_breeze']) |
                      (dewfactor['snow'] & windspeed['near_gale']) |
                      (dewfactor['snow'] & windspeed['gale']) |
                      (dewfactor['snow'] & windspeed['strong_gale']) |
                      (dewfactor['snow'] & windspeed['storm']), safefactor['low'])

    rule2 = ctrl.Rule((dewfactor['snow_overcast'] & windspeed['light_breeze']) |
                      (dewfactor['snow_overcast'] & windspeed['gentle_breeze']) |
                      (dewfactor['snow_overcast'] & windspeed['moderate_breeze']) |
                      (dewfactor['snow_overcast'] & windspeed['fresh_breeze']) |
                      (dewfactor['snow_overcast'] & windspeed['strong_breeze']) |
                      (dewfactor['snow_overcast'] & windspeed['near_gale']) |
                      (dewfactor['snow_overcast'] & windspeed['gale']) |
                      (dewfactor['snow_overcast'] & windspeed['strong_gale']) |
                      (dewfactor['snow_overcast'] & windspeed['storm']), safefactor['low'])

    # rule10 = ctrl.Rule((dewfactor['snow overcast'] & windspeed['light breeze']) , safefactor['low'])   #storm          = excellent
    # rule11 = ctrl.Rule((dewfactor['snow overcast'] & windspeed['gentle breeze']) , safefactor['low'])        #strong gale    = good
    # rule12 = ctrl.Rule((dewfactor['snow overcast'] & windspeed['moderate breeze']) , safefactor['low'])   #gale           = decent
    # rule13 = ctrl.Rule((dewfactor['snow overcast'] & windspeed['fresh breeze']) , safefactor['low'])   #gale           = decent
    # rule14 = ctrl.Rule((dewfactor['snow overcast'] & windspeed['strong breeze']) , safefactor['low'])  #near gale      = average
    # rule15 = ctrl.Rule((dewfactor['snow overcast'] & windspeed['near gale']) , safefactor['low'])   #strong breeze  = mediocre
    # rule16 = ctrl.Rule((dewfactor['snow overcast'] & windspeed['gale']) , safefactor['low'])       #moderate breeze= poor
    # rule17 = ctrl.Rule((dewfactor['snow overcast'] & windspeed['strong gale']) , safefactor['low'])     #gentle breeze  = dismal
    # rule18 = ctrl.Rule((dewfactor['snow overcast'] & windspeed['storm']) , safefactor['low'])
    
    # rule19 = ctrl.Rule((dewfactor['rain overcast'] & windspeed['light breeze']) , safefactor['low'])   #storm          = excellent
    # rule20 = ctrl.Rule((dewfactor['rain overcast'] & windspeed['gentle breeze']) , safefactor['low'])        #strong gale    = good
    # rule21 = ctrl.Rule((dewfactor['rain overcast'] & windspeed['moderate breeze']) , safefactor['low'])   #gale           = decent
    # rule22 = ctrl.Rule((dewfactor['rain overcast'] & windspeed['fresh breeze']) , safefactor['low'])   #gale           = decent
    # rule23 = ctrl.Rule((dewfactor['rain overcast'] & windspeed['strong breeze']) , safefactor['low'])  #near gale      = average
    # rule24 = ctrl.Rule((dewfactor['rain overcast'] & windspeed['near gale']) , safefactor['low'])   #strong breeze  = mediocre
    # rule25 = ctrl.Rule((dewfactor['rain overcast'] & windspeed['gale']) , safefactor['low'])       #moderate breeze= poor
    # rule26 = ctrl.Rule((dewfactor['rain overcast'] & windspeed['strong gale']) , safefactor['low'])     #gentle breeze  = dismal
    # rule27 = ctrl.Rule((dewfactor['rain overcast'] & windspeed['storm']) , safefactor['low'])

    # rule28 = ctrl.Rule((dewfactor['snow partially cloudy'] & windspeed['light breeze']) , safefactor['low'])   #storm          = excellent
    # rule29 = ctrl.Rule((dewfactor['snow partially cloudy'] & windspeed['gentle breeze']) , safefactor['low'])        #strong gale    = good
    # rule30 = ctrl.Rule((dewfactor['snow partially cloudy'] & windspeed['moderate breeze']) , safefactor['low'])   #gale           = decent
    # rule31 = ctrl.Rule((dewfactor['snow partially cloudy'] & windspeed['fresh breeze']) , safefactor['low'])
    # rule32 = ctrl.Rule((dewfactor['snow partially cloudy'] & windspeed['strong breeze']) , safefactor['low'])  #near gale      = average
    # rule33 = ctrl.Rule((dewfactor['snow partially cloudy'] & windspeed['near gale']) , safefactor['low'])   #strong breeze  = mediocre
    # rule34 = ctrl.Rule((dewfactor['snow partially cloudy'] & windspeed['gale']) , safefactor['low'])       #moderate breeze= poor
    # rule35 = ctrl.Rule((dewfactor['snow partially cloudy'] & windspeed['strong gale']) , safefactor['low'])     #gentle breeze  = dismal
    # rule36 = ctrl.Rule((dewfactor['snow partially cloudy'] & windspeed['storm']) , safefactor['low'])
    
    # rule37 = ctrl.Rule((dewfactor['overcast'] & windspeed['light breeze']) , safefactor['medium'])   #storm          = excellent
    # rule38 = ctrl.Rule((dewfactor['overcast'] & windspeed['gentle breeze']) , safefactor['medium'])        #strong gale    = good
    # rule39 = ctrl.Rule((dewfactor['overcast'] & windspeed['moderate breeze']) , safefactor['medium'])   #gale           = decent
    # rule40 = ctrl.Rule((dewfactor['overcast'] & windspeed['fresh breeze']) , safefactor['medium'])   #gale           = decent
    # rule41 = ctrl.Rule((dewfactor['overcast'] & windspeed['strong breeze']) , safefactor['low'])  #near gale      = average
    # rule42 = ctrl.Rule((dewfactor['overcast'] & windspeed['near gale']) , safefactor['low'])   #strong breeze  = mediocre
    # rule43 = ctrl.Rule((dewfactor['overcast'] & windspeed['gale']) , safefactor['low'])       #moderate breeze= poor
    # rule44 = ctrl.Rule((dewfactor['overcast'] & windspeed['strong gale']) , safefactor['low'])     #gentle breeze  = dismal
    # rule45 = ctrl.Rule((dewfactor['overcast'] & windspeed['storm']) , safefactor['low'])
    
    # rule46 = ctrl.Rule((dewfactor['rain partially cloudy'] & windspeed['light breeze']) , safefactor['medium'])   #storm          = excellent
    # rule47 = ctrl.Rule((dewfactor['rain partially cloudy'] & windspeed['gentle breeze']) , safefactor['medium'])        #strong gale    = good
    # rule48 = ctrl.Rule((dewfactor['rain partially cloudy'] & windspeed['moderate breeze']) , safefactor['medium'])   #gale           = decent
    # rule49 = ctrl.Rule((dewfactor['rain partially cloudy'] & windspeed['fresh breeze']) , safefactor['medium'])   #gale           = decent
    # rule50 = ctrl.Rule((dewfactor['rain partially cloudy'] & windspeed['strong breeze']) , safefactor['medium'])  #near gale      = average
    # rule51 = ctrl.Rule((dewfactor['rain partially cloudy'] & windspeed['near gale']) , safefactor['medium'])   #strong breeze  = mediocre
    # rule52 = ctrl.Rule((dewfactor['rain partially cloudy'] & windspeed['gale']) , safefactor['low'])       #moderate breeze= poor
    # rule53 = ctrl.Rule((dewfactor['rain partially cloudy'] & windspeed['strong gale']) , safefactor['low'])     #gentle breeze  = dismal
    # rule54 = ctrl.Rule((dewfactor['rain partially cloudy'] & windspeed['storm']) , safefactor['low'])
    
    # rule55 = ctrl.Rule((dewfactor['partially cloudy'] & windspeed['light breeze']) , safefactor['medium'])   #storm          = excellent
    # rule56 = ctrl.Rule((dewfactor['partially cloudy'] & windspeed['gentle breeze']) , safefactor['medium'])        #strong gale    = good
    # rule57 = ctrl.Rule((dewfactor['partially cloudy'] & windspeed['moderate breeze']) , safefactor['medium'])   #gale           = decent
    # rule58 = ctrl.Rule((dewfactor['partially cloudy'] & windspeed['fresh breeze']) , safefactor['medium'])   #gale           = decent
    # rule59 = ctrl.Rule((dewfactor['partially cloudy'] & windspeed['strong breeze']) , safefactor['medium'])  #near gale      = average
    # rule60 = ctrl.Rule((dewfactor['partially cloudy'] & windspeed['near gale']) , safefactor['medium'])   #strong breeze  = mediocre
    # rule61 = ctrl.Rule((dewfactor['partially cloudy'] & windspeed['gale']) , safefactor['low'])       #moderate breeze= poor
    # rule62 = ctrl.Rule((dewfactor['partially cloudy'] & windspeed['strong gale']) , safefactor['low'])     #gentle breeze  = dismal
    # rule63 = ctrl.Rule((dewfactor['partially cloudy'] & windspeed['storm']) , safefactor['low'])
    
    # rule64 = ctrl.Rule((dewfactor['rain'] & windspeed['light breeze']) , safefactor['medium'])   #storm          = excellent
    # rule65 = ctrl.Rule((dewfactor['rain'] & windspeed['gentle breeze']) , safefactor['medium'])        #strong gale    = good
    # rule66 = ctrl.Rule((dewfactor['rain'] & windspeed['moderate breeze']) , safefactor['medium'])   #gale           = decent
    # rule67 = ctrl.Rule((dewfactor['rain'] & windspeed['fresh breeze']) , safefactor['medium'])   #gale           = decent
    # rule68 = ctrl.Rule((dewfactor['rain'] & windspeed['strong breeze']) , safefactor['medium'])  #near gale      = average
    # rule69 = ctrl.Rule((dewfactor['rain'] & windspeed['near gale']) , safefactor['medium'])   #strong breeze  = mediocre
    # rule70 = ctrl.Rule((dewfactor['rain'] & windspeed['gale']) , safefactor['low'])       #moderate breeze= poor
    # rule71 = ctrl.Rule((dewfactor['rain'] & windspeed['strong gale']) , safefactor['low'])     #gentle breeze  = dismal
    # rule72 = ctrl.Rule((dewfactor['rain'] & windspeed['storm']) , safefactor['low'])
    
    # rule73 = ctrl.Rule((dewfactor['clear'] & windspeed['light breeze']) , safefactor['high'])   #storm          = excellent
    # rule74 = ctrl.Rule((dewfactor['clear'] & windspeed['gentle breeze']) , safefactor['high'])        #strong gale    = good
    # rule75 = ctrl.Rule((dewfactor['clear'] & windspeed['moderate breeze']) , safefactor['high'])   #gale           = decent
    # rule76 = ctrl.Rule((dewfactor['clear'] & windspeed['fresh breeze']) , safefactor['high'])   #gale           = decent
    # rule77 = ctrl.Rule((dewfactor['clear'] & windspeed['strong breeze']) , safefactor['medium'])  #near gale      = average
    # rule78 = ctrl.Rule((dewfactor['clear'] & windspeed['near gale']) , safefactor['medium'])   #strong breeze  = mediocre
    # rule79 = ctrl.Rule((dewfactor['clear'] & windspeed['gale']) , safefactor['low'])       #moderate breeze= poor
    # rule80 = ctrl.Rule((dewfactor['clear'] & windspeed['strong gale']) , safefactor['low'])     #gentle breeze  = dismal
    # rule81 = ctrl.Rule((dewfactor['clear'] & windspeed['storm']) , safefactor['low'])

    safety = ctrl.ControlSystem([rule1,rule2])

    # safety = ctrl.ControlSystem([rule1,rule2,rule3,rule4,rule5,rule6,rule7,rule8,rule9,rule10,rule11,rule12,rule13,rule14,rule15,rule16,rule17,rule18,rule19,rule20,rule21,rule22,rule23,rule24,rule25,rule26,rule27,rule28,rule29,rule30,
    #                              rule31,rule32,rule33,rule34,rule35,rule36,rule37,rule38,rule39,rule40, rule41,rule42,rule43,rule44,rule45,rule46,rule47,rule48,rule49,rule50,
    #                              rule51,rule52,rule53,rule54,rule55,rule56,rule57,rule58,rule59,rule60, rule61,rule62,rule63,rule64,rule65,rule66,rule67,rule68,rule69,rule70,
    #                              rule71,rule72,rule73,rule74,rule75,rule76,rule77,rule78,rule79,rule80, rule81])  

    safety_result = ctrl.ControlSystemSimulation(safety)

    safety_result.input['dewfactor'] = float(x)
    safety_result.input['windspeed'] = float(y)

    safety_result.compute()
    #print(safety_result.output['safefactor'])
    print(safety_result.output)
    safefactor.view(sim=safety_result)
    plt.show()
    
    
    return safety_result.output['safefactor']


SafetyFactor(1.0,20.0)


def safety_message(safe_factor):
    if safe_factor < 0.5:
        return "Fast Precipitation"
    elif 0.3 <= safe_factor <= 0.7:
        return "Normal Precipitation"
    elif safe_factor > 0.7:
        return "Slow Precipitation"






