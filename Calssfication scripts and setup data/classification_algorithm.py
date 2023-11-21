import pandas as pd
import numpy as np
import time
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import confusion_matrix

# Get around the file opening error for modifing excel file
loading = True
firstround = True
timer_start = time.time()
while loading:
    while ((loading and (time.time() - timer_start >= 60)) or
    (loading and firstround)):
        timer_start = time.time()
        if firstround:
            firstround = False
        
        try:
            # import the collected features to the program
            features = pd.read_excel("/home/pi/prototype_features.xlsx", engine='openpyxl')
        except Exception as e:
            print(e)
        else:
            loading = False
            print('Data loaded successfully!')
            break
        
pd.set_option('display.max_columns', None)

# Extract the important features from features
important_features = features[["MAC Address", "Password Strength",
                               "Security Protocol", "Rouge AP",
                               "FC protected", "Port Vulnerability"]]
i_df = important_features.copy()

i_df.loc[:, "Other"] = "unknown"
i_df.loc[:, "Class_id"] = 0
#print(important_features)

# Mapping the password strength
if i_df.iloc[0, 1] == "unknown":
    i_df.iloc[0, 1] = 1
elif i_df.iloc[0, 1] == "Weak Password":
    i_df.iloc[0, 1] = 2
elif i_df.iloc[0, 1] == "Medium Password":
    i_df.iloc[0, 1] = 3
elif i_df.iloc[0, 1] == "Strong Password":
    i_df.iloc[0, 1] = 4

mask1 = ((i_df.loc[:,"MAC Address"].str.lower()
        == i_df.iloc[0, 0].lower()) &
        (i_df.loc[:,"Password Strength"] == "not applied"))
        
i_df.loc[mask1, "Password Strength"] = i_df.iloc[0, 1]

mask2 = ((i_df.loc[:,"MAC Address"].str.lower()
        != i_df.iloc[0, 0].lower()) &
        (i_df.loc[:,"Password Strength"] == "not applied"))
        
i_df.loc[mask2, "Password Strength"] = 0
# Mapping the Security Protocol

i_df.loc[i_df["Security Protocol"] == "unknown", "Security Protocol"] = 1
i_df.loc[i_df["Security Protocol"] == "Open Security", "Security Protocol"] = 2
i_df.loc[(i_df["Security Protocol"] == "WEP")|(i_df["Security Protocol"] == "No RSN layer"), "Security Protocol"] = 3
i_df.loc[i_df["Security Protocol"] == "WPA2/WPA", "Security Protocol"] = 4
i_df.loc[i_df["Security Protocol"] == "WPA3/WPA2", "Security Protocol"] = 5

# Mapping the Rouge AP
i_df.loc[i_df["Rouge AP"].isin([False, "not applied"]) , "Rouge AP"] = 0
i_df.loc[i_df["Rouge AP"].isin([True]) , "Rouge AP"] = 1

# Mapping FC protected

i_df.loc[i_df["FC protected"].isin([True, "not applied"]) , "FC protected"] = 1
i_df.loc[i_df["FC protected"].isin([False]) , "FC protected"] = 0

# Mapping Port Vulnerability
i_df.loc[i_df["Port Vulnerability"].isin([False, "not applied", "unknown"]) , "Port Vulnerability"] = 0
i_df.loc[i_df["Port Vulnerability"].isin([True]) , "Port Vulnerability"] = 1

#print(important_features)

i_df.to_csv("classification_result.csv", index=False)

# Load the training and testing data in to a data frame
df = pd.read_excel("/home/pi/traning_data_allv2.xlsx")

# Map the other feature to 0 value
df.loc[df['Other'] == 'unknown', 'Other'] = 0
i_df.loc[i_df['Other'] == 'unknown', 'Other'] = 0

#print(df)
#print(important_features)

#ML modeling where our data devide in to predictors (X) and target values (y)
x = df.copy().iloc[:, 1:8]
y = x.pop('Class_id')
x_current = i_df.copy().iloc[:, 1:7]
#print(x_current)
# Training and testing model. The data set devided into 80% training and 20% testing
X_train, X_test, y_train, y_test = train_test_split(
    x,y, test_size=0.2, random_state=1, stratify = y)
'''
by stratifying on y we assure that the different classes are
represented proportionaly to the ammount in the total data
(this makes sure that all of class 1 is not in the test group only)
'''
# Create the Neural Network model instance
model = MLPClassifier(solver='lbfgs', alpha=1,
                      random_state=1, max_iter=1000)

# Fit the model on the training data
model.fit(X_train, y_train)

# Calculate the accuracy or score of the model
#print('Accuracy: {}%'.format(model.score(X_test, y_test)* 100))

# Calculate the Cross Validation Score to determine model's strength
#scores = cross_val_score(model, X_train, y_train)
#print('Cross Validation score of the model: {}%\n'.format(np.mean(scores)* 100))

# Lets compare the model's predicted data with actual data
predictions = model.predict(x_current)
predictions_df = pd.DataFrame({'predictions': predictions})
predictions_df = predictions_df.reset_index(drop=True)


# Updating the classified class ids to the data set and save the results
i_df.loc[:,'Class_id'] = predictions_df.loc[:,'predictions']
i_df.to_csv("classification_result.csv", index=False)
print('Calssification Successful!')











