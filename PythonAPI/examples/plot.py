import matplotlib.pyplot as plt 
import numpy as np 
import pydb2
import pandas as pd
import matplotlib

# dataset = pd.read_csv("new_burchinal.csv")
# x = dataset.difference
# y = dataset.windspeed
# plt.scatter(x,y)
# plt.show()



# plt.plot(dataset.difference, dataset.windspeed)
# plt.show()



# Clear =  dataset[dataset.conditions == 'Clear']
# Overcast = dataset[dataset.conditions == 'Overcast']
# plt.plot(Clear.difference, Clear.windspeed)
# plt.plot(Overcast.difference, Overcast.windspeed)
# plt.legend(['Clear', 'Overcast'])
# plt.xlabel('difference of temp and dew')
# plt.ylabel('windspeed')
# plt.show()

import numpy as np
import matplotlib.pyplot as plt

x = pydb2.get_dataset_difference()
y = pydb2.get_dataset_windspeed() 
z = pydb2.get_dataset_safefactor()

for i in range(0, len(x)):
    x[i] = float(x[i])

for i in range(0, len(y)):
    y[i] = float(y[i])

for i in range(0, len(z)):
    z[i] = float(z[i])




plt.scatter(x,y)
plt.show()



# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# colors = ["blue", "red", "green"]
# color_indices = y
# colormap = matplotlib.colors.ListedColormap(colors)
# ax.scatter(x, y, z, c=color_indices,cmap=colormap, marker = 'o')

# #ax.scatter(x, y, z, c='b', marker = 'o')
# ax.set_xlabel('Dew')
# ax.set_ylabel('Windspeed')
# ax.set_zlabel('Safe factor')
# plt.show()
