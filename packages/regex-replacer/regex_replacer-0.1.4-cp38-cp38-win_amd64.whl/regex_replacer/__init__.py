from .regex_replacer import RegexReplacer
from sklearn.base import BaseEstimator, TransformerMixin
from typing import List, Tuple

__version__ = "0.1.4"

class RegexReplacerTransformer(TransformerMixin, BaseEstimator):
    def __init__(self, re_list: List[Tuple[str, str]], n_jobs: int = 0):
        super().__init__()
        self.transformer = RegexReplacer(re_list, n_jobs)
        self.n_jobs = n_jobs
        self.re_list = re_list

    def fit(self, X, y=None):
        return self

    def to_single_thread(self):
        self.n_jobs = 1
        self.transformer.to_single_thread()

    def transform(self, X: List[str]) -> List[str]:
        single_thread = self.n_jobs <= 0
        return self.transformer.transform(X)

    def __getstate__(self):
        return {
            're_list': self.re_list,
            'n_jobs': self.n_jobs
        }

    def __setstate__(self, state):
        self.n_jobs = state['n_jobs']
        self.re_list = state['re_list']
        self.transformer = RegexReplacer(self.re_list, self.n_jobs)
