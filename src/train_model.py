import bentoml
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

X_train = pd.read_csv("data/processed/X_train.csv")
X_test = pd.read_csv("data/processed/X_test.csv")

y_train = pd.read_csv("data/processed/y_train.csv").squeeze("columns")
y_test = pd.read_csv("data/processed/y_test.csv").squeeze("columns")


model = LinearRegression()
model.fit(X_train, y_train)

predictions = model.predict(X_test)


rmse = mean_squared_error(y_test, predictions) ** 0.5
mae = mean_absolute_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print(f"RMSE: {rmse:.4f}")
print(f"MAE: {mae:.4f}")
print(f"R²: {r2:.4f}")


model_ref = bentoml.sklearn.save_model("admission_lr", model)

print(f"Saved model: {model_ref}")
