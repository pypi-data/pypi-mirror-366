import os, sys
from lib.ml.base import VlibBaseTransformer




class VlibSimpleImputer(VlibBaseTransformer):
    def __init__(self, columns=None, strategy="mean"):
        super().__init__(columns)
        self.strategy = strategy

    def fit(self, X, y=None):
        cols = self._get_columns(X)
        if self.strategy == "mean":
            self.statistics_ = X[cols].mean()
        elif self.strategy == "median":
            self.statistics_ = X[cols].median()
        elif self.strategy == "most_frequent":
            self.statistics_ = X[cols].mode().iloc[0]
        else:
            raise ValueError(f"Unsupported strategy: {self.strategy}")
        return self

    def transform(self, X):
        X = X.copy()
        for col in self._get_columns(X):
            X[col] = X[col].fillna(self.statistics_[col])
        return X