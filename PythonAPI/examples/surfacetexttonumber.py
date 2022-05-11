import numpy as np


def convertsurfacetonumber(SURFACE_CONDITION,SURFACE_TEMP):
    if (SURFACE_CONDITION == "Dry") & (SURFACE_TEMP >= 60):
        SURFACE_COND_NO = np.random.uniform(9.2, 10)
    elif (SURFACE_CONDITION == "Dry") & (SURFACE_TEMP < 60):
        SURFACE_COND_NO = np.random.uniform(8.4, 9.1)
    elif (SURFACE_CONDITION == "Trace Moisture") & (SURFACE_TEMP >= 60):
        SURFACE_COND_NO = np.random.uniform(7.5, 8.3)
    elif (SURFACE_CONDITION == "Trace Moisture") & (SURFACE_TEMP < 60):
        SURFACE_COND_NO = np.random.uniform(6.7, 7.4)
    elif (SURFACE_CONDITION == "Wet") & (SURFACE_TEMP >= 60):
        SURFACE_COND_NO = np.random.uniform(5.8, 6.6)
    elif (SURFACE_CONDITION == "Wet") & (SURFACE_TEMP < 60):
        SURFACE_COND_NO = np.random.uniform(5, 5.7)
    elif (SURFACE_CONDITION == "Chemically Wet") & (SURFACE_TEMP >= 15):
        SURFACE_COND_NO = np.random.uniform(4.1, 4.9)
    elif (SURFACE_CONDITION == "Chemically Wet") & (SURFACE_TEMP < 15):
        SURFACE_COND_NO = np.random.uniform(3.3, 4)
    elif (SURFACE_CONDITION == "Ice Watch") & (SURFACE_TEMP >= 15):
        SURFACE_COND_NO = np.random.uniform(2.4, 3.2)
    elif (SURFACE_CONDITION == "Ice Watch") & (SURFACE_TEMP < 15):
        SURFACE_COND_NO = np.random.uniform(1.6, 2.3)
    elif (SURFACE_CONDITION == "Ice Warning") & (SURFACE_TEMP >= 15):
        SURFACE_COND_NO = np.random.uniform(0.75, 1.5)
    elif (SURFACE_CONDITION == "Ice Warning") & (SURFACE_TEMP < 15):
        SURFACE_COND_NO = np.random.uniform(0, 0.74)
    else:
        SURFACE_COND_NO = 'NaN'
    
    return SURFACE_COND_NO

def slip_message(slip_factor):
    if (slip_factor < 0.3):
        return "Very Slippery"
    elif (0.3 <= slip_factor < 0.5):
        return "Slippery"
    elif (slip_factor >= 0.5):
        return "Normal"