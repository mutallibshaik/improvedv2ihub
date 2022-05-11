from itertools import count
from unittest import result
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

#import pydb2
#import TEST_ATMOSPHERE_DATA

# x_slip_factor = TEST_ATMOSPHERE_DATA.get_slip_factor()
# y_visibility_factor = TEST_ATMOSPHERE_DATA.get_visibility_factor()

def combined_fis(x,y):
    slip_factor = ctrl.Antecedent(np.arange(0,1.1,0.1), 'slip_factor')
    visibility_factor = ctrl.Antecedent(np.arange(0,1.1,0.1), 'visibility_factor')
    safety_factor = ctrl.Consequent(np.arange(0,1.1,0.1), 'safety_factor')
    

    # safety_factor['low'] = fuzz.trapmf(safety_factor.universe, [0, 0, 0.2, 0.3])
    # safety_factor['medium'] = fuzz.trimf(safety_factor.universe,[0.25,0.55, 0.6])
    # safety_factor['high'] = fuzz.trapmf(safety_factor.universe, [0.55, 0.7, 1, 1])

    slip_factor['low'] = fuzz.trapmf(slip_factor.universe, [0, 0, 0.2, 0.3])
    slip_factor['medium'] = fuzz.trimf(slip_factor.universe, [0.2, 0.4, 0.6])
    slip_factor['high'] = fuzz.trapmf(slip_factor.universe, [0.4, 0.6, 1, 1])

    visibility_factor['low'] = fuzz.trapmf(visibility_factor.universe, [0, 0, 0.2, 0.4])
    visibility_factor['medium'] = fuzz.trimf(visibility_factor.universe,[0.2,0.4,0.6])
    visibility_factor['high'] = fuzz.trapmf(visibility_factor.universe, [0.5,0.7, 1, 1])

    safety_factor.automf(3)

    #slip_factor.view()
    #visibility_factor.view()
    #safety_factor.view()


    rule1 = ctrl.Rule((slip_factor['high'] & visibility_factor['high']) , safety_factor['good'])
    rule2 = ctrl.Rule((slip_factor['high'] & visibility_factor['medium']) , safety_factor['good'])
    rule3 = ctrl.Rule((slip_factor['high'] & visibility_factor['low']) , safety_factor['average'])

    rule4 = ctrl.Rule((slip_factor['medium'] & visibility_factor['high']) , safety_factor['good'])
    rule5 = ctrl.Rule((slip_factor['medium'] & visibility_factor['medium']) , safety_factor['average'])
    rule6 = ctrl.Rule((slip_factor['medium'] & visibility_factor['low']) , safety_factor['poor'])

    rule7 = ctrl.Rule((slip_factor['low'] & visibility_factor['high']) , safety_factor['poor'])
    rule8 = ctrl.Rule((slip_factor['low'] & visibility_factor['medium']) , safety_factor['poor'])
    rule9 = ctrl.Rule((slip_factor['low'] & visibility_factor['low']) , safety_factor['poor'])

    rule_box = ctrl.ControlSystem([rule1,rule2,rule3,rule4,rule5,rule6,rule7,
                                rule8,rule9])
    safety_factor_result = ctrl.ControlSystemSimulation(rule_box)

    safety_factor_result.input['slip_factor'] = x
    safety_factor_result.input['visibility_factor'] = y

    safety_factor_result.compute()

    print(safety_factor_result.output['safety_factor'])

    #print(safety_factor_result.output)
    safety_factor.view(sim=safety_factor_result)
    #plt.show()


    return safety_factor_result.output['safety_factor']

combined_fis(0.75,0.70) # Normal, fast Precipi

def combined_message(combined_factor):
    if combined_factor <= 0.5:
        return "High Risk Accident Conditions"
    elif 0.5 < combined_factor <0.8:
        return "Medium Risk Accident Conditions"
    elif combined_factor >= 0.8:
        return "Low Risk Accident Conditions"
