"""
.. include:: ../readme.md
"""

from .auglinear.auglinear import AugLinearClassifier, AugLinearRegressor
from .augtree.augtree import AugTreeClassifier, AugTreeRegressor
from .linear_finetune import LinearFinetuneClassifier, LinearFinetuneRegressor
from .linear_ngram import LinearNgramClassifier, LinearNgramRegressor
from .d3.d3 import explain_dataset_d3
from .iprompt.api import explain_dataset_iprompt
from .iprompt.data import get_add_two_numbers_dataset
from .sasc.api import explain_module_sasc
from .treeprompt.treeprompt import TreePromptClassifier
from .kan.kan_sklearn import KANClassifier, KANGAMClassifier, KANRegressor, KANGAMRegressor
from .qaemb.qaemb import QAEmb
