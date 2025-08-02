import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
import joblib
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image

class MlModelGenerator():
    def __init__(self, input_data_csv_path, feature_columns, target_column):
        self.input_data_csv_path = input_data_csv_path
        self.feature_columns = feature_columns
        self.target_column = target_column

    def train(self, pkl_model_path):
        # --- Step 1: Load CSV ---
        df = pd.read_csv(self.input_data_csv_path)

        # --- Step 2: Use only specified columns ---
        x = df[self.feature_columns]
        y = df[self.target_column]

        # --- Step 3: Identify types ---
        numeric_features = x.select_dtypes(include=["int64", "float64"]).columns
        categorical_features = x.select_dtypes(include=["object", "category"]).columns

        # --- Step 4: Preprocessing pipelines ---
        numeric_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="mean")),
            ("scaler", StandardScaler())
        ])

        categorical_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore"))
        ])

        preprocessor = ColumnTransformer(transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features)
        ])

        # --- Step 6: Split data ---
        X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

        # --- Step 7: Train the model ---
        
        if(os.path.exists(pkl_model_path)):
            with open(pkl_model_path, "rb") as f:
                model = joblib.load(f)
                model.fit(X_train, y_train)

                joblib.dump(model, pkl_model_path)
        
                return pkl_model_path
            
        model = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(n_estimators=100, random_state=42))
        ])
        
        model.fit(X_train, y_train)

        # --- Step 8: Evaluate ---
        y_pred = model.predict(X_test)
        print("Accuracy:", accuracy_score(y_test, y_pred))
        print("\nClassification Report:\n", classification_report(y_test, y_pred))

        #--- Step 9 (Optional): Save model ---
        joblib.dump(model, pkl_model_path)

        # screenshot_path = os.path.join(os.path.dirname(pkl_model_path), f"{os.path.basename(pkl_model_path)}_matrix_screenshot.png")
        # self.take_screenshot(model, y_test, y_pred, screenshot_path)

    def take_screenshot(self, model, y_test, y_pred, screenshot_path):
        try:
            cm = confusion_matrix(y_test, y_pred, labels=model.classes_)
            disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=model.classes_)
            disp.plot()
            
            plt.tight_layout()
            plt.savefig(screenshot_path)
            plt.close()
            print(f"Confusion matrix saved to: {screenshot_path}")
        except Exception as e:
            print(e)

    @staticmethod
    def predict(model_path, input_dict):
        model = joblib.load(model_path)
        df_input = pd.DataFrame([input_dict])
        prediction = model.predict(df_input)
        return prediction[0]