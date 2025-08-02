r"""Statistics for machine learning.

Brings traditional (frequentistic) statistical concepts to your sci-kit learn models.
Examples:
    - Hypothesis testing of model scores with \(p\)-values (see, e.g.,
        `statkit.non_parametric.unpaired_permutation_test`),
    - Estimate 95% confidence intervals around test scores (see, e.g.,
        `statkit.non_parametric.bootstrap_score`).
    - Decision curve analysis to compare models in terms of consequences of actions
        (see, e.g., `statkit.decision.NetBenefitDisplay`).
    - Downsample a dataset while matching/stratifying on continuous/discrete variables
      to balance the groups (see, e.g., `statkit.dataset.balanced_downsample`).
    - Univariate feature selection with multiple hypothesis testing correction (see,
      e.g.,
        `statkit.feature_selection.StatisticalTestFilter`),

Installation:
  You can install `statkit` via pip from [PyPI](https://pypi.org/project/statkit/):
  ```bash
  pip3 install statkit
  ```
"""

__version__ = "1.0.0"
