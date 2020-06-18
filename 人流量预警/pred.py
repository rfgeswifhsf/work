from sklearn.linear_model import LinearRegression
from MongoUtils import slide_windows
import numpy as np
data = slide_windows()
X_train,y_train = data[0],data[1]
X_train=np.reshape(X_train,(-1,1))


model = LinearRegression()
model.fit(X_train, y_train)
print (model.coef_)
print (model.intercept_)
y_pre = model.predict(X_train)



from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
# MSE
mse_predict = mean_squared_error(y_train, y_pre)
# MAE
mae_predict = mean_absolute_error(y_train, y_pre)

print(mse_predict)
print(mae_predict)
