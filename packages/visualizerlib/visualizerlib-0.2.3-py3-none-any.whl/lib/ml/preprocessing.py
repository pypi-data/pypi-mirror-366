import pandas as pd
import numpy as np
import os, sys
from lib.ml.base import VlibBaseTransformer



class VlibStandardScaler(VlibBaseTransformer):
    def fit(self, X, y=None):
        cols = self._get_columns(X)
        self.mean_ = X[cols].mean()
        self.std_ = X[cols].std()
        return self

    def transform(self, X):
        X = X.copy()
        cols = self._get_columns(X)
        X[cols] = (X[cols] - self.mean_) / self.std_
        return X


class VlibMinMaxScaler(VlibBaseTransformer):
    def fit(self, X, y=None):
        cols = self._get_columns(X)
        self.min_ = X[cols].min()
        self.max_ = X[cols].max()
        return self

    def transform(self, X):
        X = X.copy()
        cols = self._get_columns(X)
        X[cols] = (X[cols] - self.min_) / (self.max_ - self.min_)
        return X

class VlibOrdinalEncoder(VlibBaseTransformer):
    def fit(self, X, y=None):
        self.mapping_ = {}
        for col in self._get_columns(X):
            self.mapping_[col] = {cat: i for i, cat in enumerate(X[col].astype(str).unique())}
        return self

    def transform(self, X):
        X = X.copy()
        for col in self._get_columns(X):
            X[col] = X[col].astype(str).map(self.mapping_[col])
        return X


class VlibOneHotEncoder(VlibBaseTransformer):
    def fit(self, X, y=None):
        self.categories_ = {
            col: sorted(X[col].astype(str).unique()) for col in self._get_columns(X)
        }
        return self

    def transform(self, X):
        X = X.copy()
        for col in self._get_columns(X):
            dummies = pd.get_dummies(X[col].astype(str), prefix=col)
            X = X.drop(columns=col)
            X = pd.concat([X, dummies], axis=1)
        return X

    def get_feature_names(self, input_cols):
        output_cols = []
        for col in input_cols:
            for category in self.categories_.get(col, []):
                output_cols.append(f"{col}_{category}")
        return output_cols


class VlibLabelEncoder(VlibBaseTransformer):
    def __init__(self, column=None):
        super().__init__([column] if column else None)

    def fit(self, X, y=None):
        if isinstance(X, pd.Series):
            self.col = X.name or "target"
            values = X.astype(str)
        else:
            self.col = self._get_columns(X)[0]
            values = X[self.col].astype(str)

        self.mapping_ = {cat: i for i, cat in enumerate(values.unique())}
        self.inverse_mapping_ = {v: k for k, v in self.mapping_.items()}
        return self

    def transform(self, X):
        if isinstance(X, pd.Series):
            encoded = X.astype(str).map(self.mapping_)
            return encoded.to_numpy()
        else:
            X = X.copy()
            X[self.col] = X[self.col].astype(str).map(self.mapping_)
            return X

    def fit_transform(self, X, y=None):
        return self.fit(X).transform(X)

    def inverse_transform(self, X):
        if isinstance(X, np.ndarray):
            return np.vectorize(self.inverse_mapping_.get)(X)
        elif isinstance(X, pd.Series):
            return X.map(self.inverse_mapping_)
        else:
            X = X.copy()
            X[self.col] = X[self.col].map(self.inverse_mapping_)
            return X


class VlibFunctionalTransformer(VlibBaseTransformer):
    def __init__(self, func, columns=None):
        super().__init__(columns)
        self.func = func

    def transform(self, X):
        X = X.copy()
        cols = self._get_columns(X)
        X[cols] = self.func(X[cols])
        return X



def remove_outliers_IQR(col, df):

        
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)

    iqr = Q3 - Q1

    upper_limit = Q3 + 1.5 * iqr
    lower_limit = Q1 - 1.5 * iqr

    df.loc[(df[col]>upper_limit),col] = upper_limit
    df.loc[(df[col]<lower_limit),col] = lower_limit

    return df
