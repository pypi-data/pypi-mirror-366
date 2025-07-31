import pandas as pd
import numpy as np
import os, sys



class VlibColumnTransformer:
    def __init__(self, transformers, output="numpy"):
        self.transformers = transformers
        self.output = output
        self.fitted_transformers = []
        self.output_columns = []

    def fit(self, X, y=None):
        self.fitted_transformers = []
        self.output_columns = []
        for name, pipeline, cols in self.transformers:
            X_subset = X[cols]
            pipeline.fit(X_subset, y)
            self.output_columns.extend(pipeline.get_feature_names(cols))
            self.fitted_transformers.append((name, pipeline, cols))
        return self

    def transform(self, X):
        transformed_parts = []
        for name, pipeline, cols in self.fitted_transformers:
            part = pipeline.transform(X[cols].copy())
            part_np = part.values if isinstance(part, pd.DataFrame) else part
            transformed_parts.append(part_np)

        X_out = np.hstack(transformed_parts)
        if self.output == "pandas":
            return pd.DataFrame(X_out, columns=self.output_columns, index=X.index)
        return X_out

    def fit_transform(self, X, y=None):
        self.fit(X, y)
        return self.transform(X)

    def get_feature_names(self):
        return self.output_columns
