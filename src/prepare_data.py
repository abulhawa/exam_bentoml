from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_csv("data/raw/admission.csv")

# Remove whitespace from column names
df.columns = df.columns.str.strip()

# Remove the identifier
df = df.drop(columns=["Serial No."])

# Basic missing-value handling
df = df.dropna()
X = df.drop(columns=["Chance of Admit"])
y = df["Chance of Admit"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)


output_dir = Path("data/processed")
output_dir.mkdir(parents=True, exist_ok=True)

X_train.to_csv(output_dir / "X_train.csv", index=False)
X_test.to_csv(output_dir / "X_test.csv", index=False)
y_train.to_csv(output_dir / "y_train.csv", index=False)
y_test.to_csv(output_dir / "y_test.csv", index=False)
