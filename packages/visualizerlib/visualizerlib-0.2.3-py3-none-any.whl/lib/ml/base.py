import numpy as np
import pandas as pd
from lib.ml.chain.pipeline import VlibPipeline

class VlibBaseTransformer:
    def __init__(self, columns=None):
        self.columns = columns

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X

    def fit_transform(self, X, y=None):
        return self.fit(X, y).transform(X)

    def _get_columns(self, X):
        return self.columns if self.columns is not None else list(X.columns)

    def get_feature_names(self, input_cols):
        return input_cols

    def __or__(self, other):
        if isinstance(other, VlibPipeline):
            return VlibPipeline([self] + other.steps)
        return VlibPipeline([self, other])
