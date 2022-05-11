# TESTING WITH DATASET
from re import M
import pydb2
import MODIFIED_TEST_FUZZY

x = pydb2.get_dataset_difference()
y = pydb2.get_dataset_windspeed()

print(len(x))
print(len(y))

try:
    count = 0
    while count <= len(y):
        precipitation_factor = MODIFIED_TEST_FUZZY.precipitationFactor(x[count],y[count])
        precipitation_factor = round(precipitation_factor,2)
        print("Count is "+str(count) +" " +str(precipitation_factor))
        pydb2.runsqlquery(f'update dataset set precipitation_factor = "{precipitation_factor}"  where id = {count+1};')
        count = count+1

except IndexError:
    print("error handled")

