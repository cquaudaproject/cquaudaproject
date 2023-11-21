import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import confusion_matrix

# Load the training and testing data in to a data frame
df = pd.read_excel("/home/pi/traning_data_allv2.xlsx")

# set the maximum display of columns
pd.set_option('display.max_columns', None)

# Map the other feature to 0 value
df.loc[df['Other'] == 'unknown', 'Other'] = 0
#print(df)
#print("\n")
#print(df.dtypes)

#ML modeling where our data devide in to predictors (X) and target values (y)
x = df.copy().iloc[:, 1:8]
y = x.pop('Class_id')

#print(x)
#print(y)

# Training and testing model. The data set devided into 80% training and 20% testing
X_train, X_test, y_train, y_test = train_test_split(
    x,y, test_size=0.2, random_state=1, stratify = y)

'''
by stratifying on y we assure that the different classes are
represented proportionaly to the ammount in the total data
(this makes sure that all of class 1 is not in the test group only)
'''
#Calculating the Baseline Prediction
print('Baseline Prediction\n')
print(df.Class_id.value_counts(normalize= True))

# Create the Neural Network model instance
model = MLPClassifier(solver='lbfgs', alpha=1,
                      random_state=1, max_iter=1000)

# Fit the model on the training data
model.fit(X_train, y_train)

# Calculate the accuracy or score of the model
print('Accuracy: {}%'.format(model.score(X_test, y_test)* 100))

# Calculate the Cross Validation Score to determine model's strength
scores = cross_val_score(model, X_train, y_train)
print('Cross Validation score of the model: {}%\n'.format(np.mean(scores)* 100))

# Lets compare the model's predicted data with actual data
predictions = model.predict(X_test)

compare_df = pd.DataFrame({'actual': y_test, 'predicted': predictions})
compare_df = compare_df.reset_index(drop=True)
#compare_df.to_excel('predicted.xlsx', index=False)
print('Actual vs Predicted')
#print(compare_df)

# Generate the confusion matrix for predicted data
c_matrix = pd.DataFrame(confusion_matrix(y_test, predictions, labels=[4,3,2,1]),
                                         index=[4, 3, 2, 1], columns=[4,3,2,1])
print('\n')
print('Confusion Matrix')
print(c_matrix)

