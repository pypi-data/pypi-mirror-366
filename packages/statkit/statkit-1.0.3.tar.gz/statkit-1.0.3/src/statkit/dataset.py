"""Various methods for partitioning the dataset, such as downsampling and splitting."""

from functools import partial

import numpy as np
from numpy.typing import NDArray
from pandas import DataFrame, Series
from sklearn.linear_model import LogisticRegression  # type: ignore
from sklearn.preprocessing import LabelBinarizer  # type: ignore


def _as_categories(x_multinomial):
    """Convert multinomial sample to long vector of categorical draws."""
    #  Line up all draws in one long vector (of size `n_samples`), indicating which
    # feature was drawn.
    # Use Numpy instead of JAX implementation because it is faster.
    return np.repeat(np.arange(len(x_multinomial)), x_multinomial)  # type: ignore


def _as_multinomial(x_categorical, n_features: int):
    """Convert string of categorical draws to multinomial representation."""
    x_test = np.zeros(n_features, dtype=int)
    np.add.at(x_test, x_categorical, 1)  # In place change.
    return x_test  # type: ignore


def _single_multinomial_train_test_split(
    random_state, x_i, test_size: float = 0.2
) -> tuple:
    """Make train-test split for a single multinomial draw.

    Args:
        random_state: Instance of NumPy pseudo random number state.
        x_i: A single multinomial observation.
        test_size: Proportion of draws for test set.
    """
    x_i = x_i.astype(int)
    x_draws = _as_categories(x_i)
    # Take, on average, `n_test` draws from test set (i.e., without replacement).
    u = random_state.uniform(size=len(x_draws))
    selected = u <= test_size
    x_test_draws = x_draws[selected]
    # Go back to multinomial representation.
    x_test = _as_multinomial(x_test_draws, n_features=len(x_i))  # type: ignore
    # Remainder is train set.
    x_train = x_i - x_test
    return x_train, x_test


def split_multinomial_dataset(
    X: NDArray[np.int_] | DataFrame, test_size: float = 0.5, random_state=None
) -> tuple[NDArray[np.int_] | DataFrame, NDArray[np.int_] | DataFrame]:
    """Partition dataset, with number of observations per row, in a train-test split.

    Each row in `X` counts the number of observations per category (columns). This
    function equally divides, for each row, the observations in a train and test set
    (with the test set getting a proportion of `test_size`).

    Example:
        Let's say you have a dataset with questionnaire fields, with the total number of
        product ratings:
        ```python
        import pandas as pd
        product_names = ["a", "b"]
        rating_names = ["🙁", "😐", "😃"]
        product_ratings = pd.DataFrame(
            [[0, 1, 0], [2, 3, 7]], product_names, rating_names,
        )
        ```

        The total ratings of each product is multinomially distributed.

        >>> product_ratings
        🙁  😐  😃
        a  0  1  0
        b  2  3  7

        Here is how you make a train test split, equaly partitioning the ratings per
        product:

        >>> from statkit.dataset import split_multinomial_dataset
        >>> x_train, x_test = split_multinomial_dataset(
            product_ratings, test_size=0.5,
        )
        >>> x_train
           🙁  😐  😃
            a  0  1  0
            b  1  2  4
        >>> x_test
        🙁  😐  😃
        a  0  0  0
        b  1  1  3

    Args:
        X: A dataset where each row counts the number of observations per category
            (columns). That is, each row is a multinomial draw.
        test_size: Proportion of draws to reserve for the test set.
        random_state: Seed for numpy pseudo random number generator state.

    Returns:
        A pair `X_train`, `X_test` both shaped like `X`.
    """
    random_state = np.random.default_rng(random_state)

    _single_split = partial(_single_multinomial_train_test_split, test_size=test_size)

    X_np = X
    if isinstance(X, DataFrame):
        X_np = X.to_numpy()

    x_as = []
    x_bs = []
    for x_i in X_np:
        x_a, x_b = _single_split(random_state, x_i)
        x_as.append(x_a)
        x_bs.append(x_b)
    X_train = np.stack(x_as)
    X_test = np.stack(x_bs)

    if isinstance(X, DataFrame):
        df_train = DataFrame(X_train, index=X.index, columns=X.columns)
        df_test = DataFrame(X_test, index=X.index, columns=X.columns)
        return df_train, df_test
    return X_train, X_test


def balanced_downsample(
    X: DataFrame | NDArray,
    y: Series | NDArray,
    ratio: int = 1,
    replace: bool = False,
    verbose: bool = False,
) -> NDArray:
    r"""Downsample majority class while stratifying for variables `X`.

    This method uses propensity score matching to subsample the majority class so that
    covariates `X` of both groups are balanced [1]. The logits from a logistic
    regression model, [i.e., \( \ln \frac{p}{1-p} \) where \( p(\pmb{y}|\pmb{X}) \)] are
    used to match the cases (`y=1`) to the closest controls (`y=0`). This ensures that
    after downsampling both groups are equally likely to be in both classes (according
    to the features `X`).

    Warning: In the worst case scenario, this method has a time complexity of
    \( O(m^2) \), where \( m \) is the number of samples.

    Example:
        Let's say you have two groups with systematic group differences in sex.
        ```python
        import numpy as np
        import pandas as pd

        names = ["eve", "alice", "carol", "dian", "bob", "frank"]
        group_label = pd.Series([1, 1, 0, 0, 0, 0], index=names)
        # Notice, no men in the case group (systematic bias).
        x_gender = np.array([0, 0, 0, 0, 1, 1])  # Female: 0; Male: 1.
        x_age = np.array([55, 75, 50, 60, 70, 80])
        demographics = pd.DataFrame(
            data={"gender": x_gender, "age": x_age}, index=names,
        )
        ```
        Make a subselection of the majority class matching on age and gender. After
        down sampling, the control group has similar age and gender distributions (
        namely, no men).

        >>> from statkit.dataset import balanced_downsample
        >>> controls = balanced_downsample(X=demographics, y=group_label)
        >>> controls
        Index(["carol", "dian"], dtype='object')

    Args:
        X: Downsample while balancing (stratifying) the classes based on these
            features/covariates/exogeneous variables.
        y: Binary classes to match (e.g., `y=1` case, `y=0` is control).
        ratio: Downsample majority class to achieve this `majority:minority` ratio.
        replace: By default, subsample without replacement.
        verbose: If True, print progress.

    Returns:
        Index of the matched majority class (control group): integer indices if `X` is a
        NumPy array, or index labels if `X` is a DataFrame.

    References:
        [1]: Rosenbaum-Ruben, Biometrika 70, 1, pp. 41-55 (1983).
    """
    if replace:
        raise NotImplementedError("Downsampling with replacement is not implemented.")

    if ratio != 1:
        raise NotImplementedError("Downsampling with ratio != 1 is not implemented.")

    y_ = LabelBinarizer().fit_transform(y)
    y_ = np.squeeze(y_)
    # Swap classes if y=1 is the majority class.
    if sum(y_) > sum(1 - y_):
        y_ = 1 - y_

    # 1) Compute logits.
    model = LogisticRegression(penalty=None).fit(X, y_)
    logits = model.decision_function(X)

    # 2) Match the case with controls using propensity scores.
    control_indices = _find_nearest_matches_greedily(logits, y_, verbose)

    if isinstance(X, DataFrame):
        return X.index[control_indices]
    return control_indices


def _find_nearest_matches_greedily(logits, y, verbose):
    # Split cases and controls.
    case = y == 1
    control = y == 0

    # Select without replacement: we keep track of previously selected controls.
    not_selected = np.ones_like(y, dtype=bool)
    for idx_case in np.nonzero(case)[0]:
        idx_controls = np.nonzero(control & not_selected)[0]
        k = np.argmin(np.abs(logits[idx_controls] - logits[idx_case]))
        idx_match = idx_controls[k]
        not_selected[idx_match] = False
        if verbose:
            print(".", end="")

    if verbose:
        print()

    return np.nonzero(control & (~not_selected))[0]
