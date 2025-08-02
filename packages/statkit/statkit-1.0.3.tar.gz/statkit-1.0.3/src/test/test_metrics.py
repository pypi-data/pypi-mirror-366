from unittest import TestCase

import numpy as np
from numpy.testing import assert_almost_equal

from statkit.metrics import (
    false_positive_rate,
    perplexity,
    sensitivity,
    specificity,
    true_positive_rate,
    youden_j,
)


class TestMetrics(TestCase):
    def setUp(self):
        """Make up data where we know the answer."""
        # Lets construct data with:
        # - true positives: 2
        # - true negatives: 3
        # - false negatives: 4
        # - false positives: 5.
        self.y_true = [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        self.y_pred = [1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1]

    def test_sensitivity_specificity(self):
        """Test computation of sensitivity and specificity."""
        self.assertEqual(sensitivity(self.y_true, self.y_pred), 2 / (2 + 4))
        self.assertEqual(specificity(self.y_true, self.y_pred), 3 / (3 + 5))

    def test_youden_j(self):
        """Test expression with equivalent formulations."""
        # Youden J: true postives / (true positive + false negatives) +
        # true negatives / (true negatives + false positives) -1.

        assert_almost_equal(
            youden_j(self.y_true, self.y_pred),
            sensitivity(self.y_true, self.y_pred)
            + specificity(self.y_true, self.y_pred)
            - 1,
        )
        assert_almost_equal(
            youden_j(self.y_true, self.y_pred),
            true_positive_rate(self.y_true, self.y_pred)
            - false_positive_rate(self.y_true, self.y_pred),
        )

    def test_perplexity_no_observations(self):
        """Test edge case where there is a sample with no observations."""
        # Initialise with arbitrary probabilities.
        unnormed_probs = np.arange(1, 13).reshape(3, 4)
        probs = unnormed_probs / unnormed_probs.sum(axis=1, keepdims=True)
        # Compare that the perplexity with empty observations equals the dataset with
        # the sample removed.
        X_with_zeroes = np.array([[1, 2, 3, 4], [0, 0, 0, 0], [4, 5, 6, 7]])
        X_without_zeroes = np.array([[1, 2, 3, 4], [4, 5, 6, 7]])
        pp_no_zeroes = perplexity(X_without_zeroes, probs[[0, 2]])
        pp_with_zeroes = perplexity(X_with_zeroes, probs)
        assert_almost_equal(pp_no_zeroes, pp_with_zeroes)
