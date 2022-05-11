import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import random


def road_condition(sur_cond, sur_temp):

    # Antecedent/Consequent objects
    surface_cond = ctrl.Antecedent(np.arange(0, 11, 1), 'surface condition')
    surface_temp = ctrl.Antecedent(np.arange(-25, 145, 5), 'surface temperature [F]')
    slipperiness = ctrl.Consequent(np.arange(0, 1.2, 0.2), 'slipperiness')

    # Custom membership functions
    surface_cond['ice_warning'] = fuzz.trapmf(surface_cond.universe, [0, 0, 1, 2])
    surface_cond['ice_watch'] = fuzz.trapmf(surface_cond.universe, [1, 2, 3, 4])
    surface_cond['chemical_wet'] = fuzz.trimf(surface_cond.universe, [3, 4, 5])
    surface_cond['wet'] = fuzz.trimf(surface_cond.universe, [4, 5, 6])
    surface_cond['trace_moisture'] = fuzz.trapmf(surface_cond.universe, [5, 6, 7, 8])
    surface_cond['dry'] = fuzz.trapmf(surface_cond.universe, [7, 8, 10, 10])
 #   surface_cond.view()

    surface_temp['very_low'] = fuzz.trapmf(surface_temp.universe, [-25, -25, 0, 30])
    surface_temp['low'] = fuzz.trimf(surface_temp.universe, [0, 30, 60])
    surface_temp['moderate'] = fuzz.trimf(surface_temp.universe, [30, 60, 90])
    surface_temp['high'] = fuzz.trimf(surface_temp.universe, [60, 90, 110])
    surface_temp['very high'] = fuzz.trapmf(surface_temp.universe, [90, 110, 140, 140])


#    surface_cond.view()
#    surface_temp.view()

    slipperiness['very_slippery'] = fuzz.trapmf(slipperiness.universe, [0, 0, 0.2, 0.3])
    slipperiness['slippery'] = fuzz.trimf(slipperiness.universe, [0.2, 0.4, 0.6])
    slipperiness['normal'] = fuzz.trapmf(slipperiness.universe, [0.4, 0.6, 1, 1])

    # Fuzzy rules
    rule1 = ctrl.Rule((surface_cond['dry'] & surface_temp['very high']) |
                      (surface_cond['dry'] & surface_temp['high']) |
                      (surface_cond['dry'] & surface_temp['moderate']) |
                      (surface_cond['dry'] & surface_temp['low']) |
                      (surface_cond['dry'] & surface_temp['very_low']), slipperiness['normal'])
    rule2 = ctrl.Rule((surface_cond['trace_moisture'] & surface_temp['very high']) |
                      (surface_cond['trace_moisture'] & surface_temp['high']) |
                      (surface_cond['trace_moisture'] & surface_temp['moderate']) |
                      (surface_cond['trace_moisture'] & surface_temp['low']), slipperiness['normal'])
    rule3 = ctrl.Rule((surface_cond['wet'] & surface_temp['high']) |
                      (surface_cond['wet'] & surface_temp['moderate']), slipperiness['normal'])
    rule4 = ctrl.Rule(surface_cond['wet'] & surface_temp['low'], slipperiness['slippery'])
    rule5 = ctrl.Rule(surface_cond['chemical_wet'] & surface_temp['moderate'], slipperiness['normal'])
    rule6 = ctrl.Rule((surface_cond['chemical_wet'] & surface_temp['low']) |
                      (surface_cond['chemical_wet'] & surface_temp['very_low']), slipperiness['slippery'])
    rule7 = ctrl.Rule((surface_cond['ice_watch'] & surface_temp['moderate']) |
                      (surface_cond['ice_watch'] & surface_temp['low']), slipperiness['slippery'])
    rule8 = ctrl.Rule(surface_cond['ice_watch'] & surface_temp['very_low'], slipperiness['very_slippery'])
    rule9 = ctrl.Rule(surface_cond['ice_warning'] & surface_temp['moderate'], slipperiness['slippery'])
    rule10 = ctrl.Rule((surface_cond['ice_warning'] & surface_temp['low']) |
                       (surface_cond['ice_warning'] & surface_temp['very_low']), slipperiness['very_slippery'])

    # Control System Creation and Simulation
    slip = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10])
    slip_result = ctrl.ControlSystemSimulation(slip)

    slip_result.input['surface condition'] = float(sur_cond)
    slip_result.input['surface temperature [F]'] = float(sur_temp)

    slip_result.compute()

    #slipperiness.view(slip_result)
    #print(slip_result)
    print(slip_result.output['slipperiness'])
    return slip_result.output['slipperiness']

#ABDUL added
#road_condition(9.5,60)