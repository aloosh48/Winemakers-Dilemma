import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as imbpipeline
import mlflow
import dagshub

# Initialize DagsHub and MLflow for tracking
dagshub.init(repo_owner='alaa.hussein401', repo_name='Winemakers-Dilemma', mlflow=True)
mlflow.set_tracking_uri('https://dagshub.com/alaa.hussein401/Winemakers-Dilemma.mlflow')

# Start an MLflow run
with mlflow.start_run():
    # Load the dataset
    df = pd.read_csv('vineyard_weather_1948-2017.csv')

    # Preprocess and feature engineering
    df['DATE'] = pd.to_datetime(df['DATE'], format='%Y-%m-%d')
    df['year'] = df['DATE'].dt.year
    df['week_of_year'] = df['DATE'].dt.isocalendar().week

    # Filter data for weeks 35 to 40
    df_filtered = df[(df['week_of_year'] >= 35) & (df['week_of_year'] <= 40)]

    # Aggregate data by year and week number
    weekly_data = df_filtered.groupby(['year', 'week_of_year']).agg({
        'PRCP': 'sum',
        'TMAX': 'mean',
        'TMIN': 'mean',
    }).reset_index()

    # Feature engineering
    weekly_data['PRCP_lag1'] = weekly_data['PRCP'].shift(1)
    weekly_data['PRCP_lag2'] = weekly_data['PRCP'].shift(2)
    weekly_data['PRCP_MA3'] = weekly_data['PRCP'].rolling(window=3).mean()

    # Drop rows with NaN values that were created by shifts and rolling means
    weekly_data.dropna(inplace=True)

    # Select features for training
    features = ['TMAX', 'TMIN', 'PRCP_lag1', 'PRCP_lag2', 'PRCP_MA3']
    X = weekly_data[features]
    y = (weekly_data['PRCP'] >= 0.35).astype(int)

    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create a pipeline that first standardizes the data, then applies SMOTE, and finally fits the model
    pipeline = imbpipeline([
        ('scaler', StandardScaler()),
        ('smote', SMOTE(random_state=42)),
        ('classifier', RandomForestClassifier(n_estimators=200, random_state=42))
    ])

    # Fit the pipeline
    pipeline.fit(X_train, y_train)

    # Make predictions
    y_pred = pipeline.predict(X_test)

    # Log parameters, metrics, and artifacts
    mlflow.log_params(pipeline.named_steps['classifier'].get_params())
    mlflow.log_metric('accuracy', pipeline.score(X_test, y_test))
    
    # Generate and log classification report
    report = classification_report(y_test, y_pred)
    mlflow.log_text(report, 'classification_report_3.txt')

    # Generate and log confusion matrix
    conf_matrix = confusion_matrix(y_test, y_pred)
    mlflow.log_text(str(conf_matrix), 'confusion_matrix_3.txt')

    # Print the classification report and confusion matrix
    print(report)
    print(conf_matrix)
