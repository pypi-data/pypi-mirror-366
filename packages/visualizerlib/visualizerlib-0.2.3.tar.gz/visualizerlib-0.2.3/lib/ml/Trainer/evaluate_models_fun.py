from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)

from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score
)

from sklearn.model_selection import train_test_split, GridSearchCV
from tqdm import tqdm
import joblib
import os
import numpy as np
import pandas as pd


def evaluate_classification(true, predicted, average='binary'):
    acc = accuracy_score(true, predicted)
    precision = precision_score(true, predicted, average=average, zero_division=0)
    recall = recall_score(true, predicted, average=average, zero_division=0)
    f1 = f1_score(true, predicted, average=average, zero_division=0)
    return acc, precision, recall, f1



def evaluate_classification_models(X, y, models, param_grids=None, model_dir='saved_models', average='binary', tune=False):
    os.makedirs(model_dir, exist_ok=True)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    results = []
    best_score = -np.inf
    best_model = None
    best_model_name = ""

    for name, model in tqdm(models.items()):
        try:
            if tune and param_grids and name in param_grids:
                print(f"\n🔍 Performing hyperparameter tuning for {name}")
                grid = GridSearchCV(model, param_grids[name], 
                                    cv=5, scoring='f1_macro' if average != 'binary' else 'f1', 
                                    verbose=2)
                grid.fit(X_train, y_train)
                model = grid.best_estimator_
                print(f"✔ Best Params for {name}: {grid.best_params_}")
            else:
                model.fit(X_train, y_train)

            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)

            train_acc, train_prec, train_rec, train_f1 = evaluate_classification(y_train, y_train_pred, average)
            test_acc, test_prec, test_rec, test_f1 = evaluate_classification(y_test, y_test_pred, average)

            results.append({
                'Model': name,
                'Train Accuracy': train_acc,
                'Train Precision': train_prec,
                'Train Recall': train_rec,
                'Train F1': train_f1,
                'Test Accuracy': test_acc,
                'Test Precision': test_prec,
                'Test Recall': test_rec,
                'Test F1': test_f1
            })

            if test_f1 > best_score:
                best_score = test_f1
                best_model = model
                best_model_name = name

            print(f"\n{name}")
            print("="*len(name))
            print("Training Performance:")
            print(f"- Accuracy: {train_acc:.4f}, Precision: {train_prec:.4f}, Recall: {train_rec:.4f}, F1: {train_f1:.4f}")

            print("\nTest Performance:")
            print(f"- Accuracy: {test_acc:.4f}, Precision: {test_prec:.4f}, Recall: {test_rec:.4f}, F1: {test_f1:.4f}")
            print("\nClassification Report:")
            print(classification_report(y_test, y_test_pred, zero_division=0))
            print("="*50)

        except Exception as e:
            print(f"❌ Error with {name}: {str(e)}")
            continue

    if best_model is not None:
        model_path = os.path.join(model_dir, f"best_model_{best_model_name}.pkl")
        joblib.dump(best_model, model_path)
        print(f"\n💾 Saved best model ({best_model_name}) to {model_path}")
    else:
        print("\n⚠️ No models were successfully trained.")

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(by='Test F1', ascending=False)

    print("\n📊 Summary:")
    print(results_df[['Model', 'Test Accuracy', 'Test F1']])
    print(f"\n🏆 Best model: {type(best_model).__name__}")

    return results_df, best_model




def evaluate_reg(true, predicted):
    mse = mean_squared_error(true, predicted)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(true, predicted)
    r2 = r2_score(true, predicted)
    return mse, rmse, mae, r2


def evaluate_regression_models(X, y, models, param_grids=None, model_dir='saved_models', tune=False):
    os.makedirs(model_dir, exist_ok=True)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    results = []
    best_score = -np.inf
    best_model = None
    best_model_name = ""

    for name, model in tqdm(models.items()):
        try:
            if tune and param_grids and name in param_grids:
                print(f"\n🔍 Performing hyperparameter tuning for {name}")
                grid = GridSearchCV(model, param_grids[name], 
                                    cv=5, scoring='r2',
                                    verbose=2
                                    )
                grid.fit(X_train, y_train)
                model = grid.best_estimator_
                print(f"✔ Best Params for {name}: {grid.best_params_}")
            else:
                model.fit(X_train, y_train)

            # Make predictions
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)

            # Evaluate both train and test data
            train_mse, train_rmse, train_mae, train_r2 = evaluate_reg(y_train, y_train_pred)
            test_mse, test_rmse, test_mae, test_r2 = evaluate_reg(y_test, y_test_pred)

            # Store results
            results.append({
                'Model': name,
                'Train MSE': train_mse,
                'Train RMSE': train_rmse,
                'Train MAE': train_mae,
                'Train R2': train_r2,
                'Test MSE': test_mse,
                'Test RMSE': test_rmse,
                'Test MAE': test_mae,
                'Test R2': test_r2
            })

            # Check if current model is the best so far
            if test_r2 > best_score:
                best_score = test_r2
                best_model = model
                best_model_name = name

            # Print results
            print(f"\n{name}")
            print("="*len(name))
            print("Training Performance:")
            print(f"- MSE: {train_mse:.4f}, RMSE: {train_rmse:.4f}")
            print(f"- MAE: {train_mae:.4f}, R2: {train_r2:.4f}")

            print("\nTest Performance:")
            print(f"- MSE: {test_mse:.4f}, RMSE: {test_rmse:.4f}")
            print(f"- MAE: {test_mae:.4f}, R2: {test_r2:.4f}")
            print("="*50)

        except Exception as e:
            print(f"❌ Error with {name}: {str(e)}")
            continue

    # Save the best model
    if best_model is not None:
        model_path = os.path.join(model_dir, f"best_model_{best_model_name}.pkl")
        joblib.dump(best_model, model_path)
        print(f"\n💾 Saved best model ({best_model_name}) to {model_path}")
    else:
        print("\n⚠️ No models were successfully trained.")

    # Create results dataframe
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(by='Test R2', ascending=False)

    print("\n📊 Summary:")
    print(results_df[['Model', 'Test R2', 'Test RMSE']])
    print(f"\n🏆 Best model: {type(best_model).__name__}")

    return results_df, best_model
