import os,sys

class VlibPipeline:
    def __init__(self, steps, output="numpy"):
        self.steps = steps
        self.output = output

    def fit(self, X, y=None):
        self.input_columns = list(X.columns)
        for step in self.steps:
            X = step.fit_transform(X, y)
        self.output_columns = self.get_feature_names(self.input_columns)
        return self

    def transform(self, X):
        for step in self.steps:
            X = step.transform(X)
        if self.output == "pandas":
            return X
        return X.values

    def fit_transform(self, X, y=None):
        self.fit(X, y)
        return self.transform(X)

    def __or__(self, other):
        return VlibPipeline(self.steps + ([other] if not isinstance(other, VlibPipeline) else other.steps))

    def get_feature_names(self, input_cols):
        cols = input_cols
        for step in self.steps:
            cols = step.get_feature_names(cols)
        return cols
    