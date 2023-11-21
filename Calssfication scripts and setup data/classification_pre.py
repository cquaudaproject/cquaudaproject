import pandas as pd
import numpy as np

# import the collected features to the program
features = pd.read_excel("/home/pi/Desktop/prototype_features-rayshome3-21-01-2023.xlsx")
#print(features)
pd.set_option('display.max_columns', None)
# create the structure of new data frame with the pre processed features for classification
#print(features.dtypes)
device_ids = features["MAC Address"]
#print(device_ids)

important_features = features[["MAC Address", "Password Strength",
                               "Security Protocol", "Rouge AP",
                               "FC protected", "Port Vulnerability"]]
#print(important_features)

important_features.loc[:, "Other"] = "unknown"
important_features.loc[:, "Class_id"] = 0
print(important_features)

# Mapping the password strength
if important_features.iloc[0, 1] == "unknown":
    important_features.iloc[0, 1] = 1
elif important_features.iloc[0, 1] == "Weak Password":
    important_features.iloc[0, 1] = 2
elif important_features.iloc[0, 1] == "Medium Password":
    important_features.iloc[0, 1] = 3
elif important_features.iloc[0, 1] == "Strong Password":
    important_features.iloc[0, 1] = 4
    
important_features["Password Strength"] = np.where((important_features.loc[:,"MAC Address"].str.lower()
                                                    == important_features.iloc[0, 0].lower()) &
                                                   (important_features.loc[:,"Password Strength"] == "not applied"),
                                                   important_features.iloc[0, 1],
                                                   important_features["Password Strength"])

important_features["Password Strength"] = np.where((important_features.loc[:,"MAC Address"].str.lower()
                                                    != important_features.iloc[0, 0].lower()) &
                                                   (important_features.loc[:,"Password Strength"] == "not applied"),
                                                   0,important_features["Password Strength"])

# Mapping the Security Protocol

important_features.loc[important_features["Security Protocol"] == "unknown", "Security Protocol"] = 1
important_features.loc[important_features["Security Protocol"] == "Open Security", "Security Protocol"] = 2
important_features.loc[(important_features["Security Protocol"] == "WEP")|(important_features["Security Protocol"] == "No RSN layer"), "Security Protocol"] = 3
important_features.loc[important_features["Security Protocol"] == "WPA2/WPA", "Security Protocol"] = 4
important_features.loc[important_features["Security Protocol"] == "WPA3/WPA2", "Security Protocol"] = 5

# Mapping the Rouge AP
important_features.loc[important_features["Rouge AP"].isin([False, "not applied"]) , "Rouge AP"] = 0
important_features.loc[important_features["Rouge AP"].isin([True]) , "Rouge AP"] = 1

# Mapping FC protected

important_features.loc[important_features["FC protected"].isin([True, "not applied"]) , "FC protected"] = 1
important_features.loc[important_features["FC protected"].isin([False]) , "FC protected"] = 0

# Mapping Port Vulnerability
important_features.loc[important_features["Port Vulnerability"].isin([False, "not applied", "unknown"]) , "Port Vulnerability"] = 0
important_features.loc[important_features["Port Vulnerability"].isin([True]) , "Port Vulnerability"] = 1

#print(important_features)

#important_features.to_excel("traning_data.xlsx", index=False)

# Calculating the class_id

for i in range(important_features.shape[0]):
    score = 0
    passvul = 0
    securityvul = 0
    rougeapvul = 0
    fcvul = 0
    portvul = 0
    
    if (important_features.loc[i, "Password Strength"] in range(1,4)) or (
        important_features.loc[i, "Security Protocol"] == 2
        and important_features.loc[i, "FC protected"] == 0):
        passvul = 1
    if important_features.loc[i, "Security Protocol"] in range(1,5):
        securityvul = 1
    if important_features.loc[i, "Rouge AP"] == 1:
        rougeapvul = 1
    if important_features.loc[i, "FC protected"] == 0:
        fcvul = 1
    if important_features.loc[i, "Port Vulnerability"] == 1:
        portvul = 1
        
    score = passvul+securityvul+rougeapvul+fcvul+portvul
    
    if score >= 4:
        important_features.loc[i, "Class_id"] = 1
    elif score == 3:
        important_features.loc[i, "Class_id"] = 2
    elif score in range(1,3):
        important_features.loc[i, "Class_id"] = 3
    elif score == 0:
        important_features.loc[i, "Class_id"] = 4

print(important_features)

important_features.to_excel("traning_data5.xlsx", index=False)