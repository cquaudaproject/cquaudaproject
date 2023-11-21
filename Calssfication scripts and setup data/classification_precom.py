import pandas as pd
import numpy as np

# import the collected features to the program
td0 = pd.read_excel("/home/pi/traning_data0.xlsx")
td1 = pd.read_excel("/home/pi/traning_data1.xlsx")
td2 = pd.read_excel("/home/pi/traning_data2.xlsx")
td3 = pd.read_excel("/home/pi/traning_data3.xlsx")
td4 = pd.read_excel("/home/pi/traning_data4.xlsx")
#print(features)
pd.set_option('display.max_columns', None)

td = pd.concat([td0, td1, td2, td3, td4], axis=0)

print(td)

td.to_excel("traning_data_all.xlsx", index=False)