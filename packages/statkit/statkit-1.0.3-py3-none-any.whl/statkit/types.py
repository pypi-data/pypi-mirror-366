import re
import numpy as np


def _parse_scientific_notation(input: float) -> tuple[float, int]:
    """Convert number 0.00001234 into 1.234 and -6"""
    input_str = "{:e}".format(input)
    scientific_number = r"([-+]?[\d]+\.?[\d]*)[Ee]((?:[-+]?[\d]+)?)"
    match = re.search(string=input_str, pattern=scientific_number)
    if match is None:
        raise ValueError(
            f"Could not extract base ten exponent from {input} in standard form."
        )
    mantissa = float(match.group(1))
    exponent = int(match.group(2))
    return mantissa, exponent


def _get_number_of_significant_digits(value: float, error: float) -> int:
    """Determine how many significant digits to use."""
    _, estimate_exponent = _parse_scientific_notation(value)
    _, error_exponent = _parse_scientific_notation(error)
    return max(estimate_exponent - error_exponent + 1, 2)


def _format_float(value: float, n_digits: int):
    """Format string upto given number of digits."""
    mantissa, exponent = _parse_scientific_notation(value)
    # No need to add the e+00 part.
    if exponent == 0:
        format_template = "{:." + str(n_digits - 1) + "f}"
        return format_template.format(mantissa)
    elif exponent == -1:
        format_template = "{:." + str(n_digits) + "f}"
        return format_template.format(value)

    # Use scientific notation, e.g., 1.23 e-02 for `n_digits = 3`.
    format_template = "{:." + str(n_digits - 1) + "e}"
    return format_template.format(value)


class Estimate:
    """Estimate with range of uncertainty (95% confidence interval).

    Example:
        ```python
        mean = 1.0
        standard_deviation = 0.2
        estimate = Estimate(
            point=mean,
            lower=mean - 1.96*standard_deviation,
            upper=mean + 1.96*standard_deviation,
            )
        # Print estimate in LaTeX format.
        print(estimate.latex())
        ```
    """

    def __init__(self, point: float, lower: float, upper: float):
        """
        Args:
            point: Point estimate.
            lower: Lower limit of 95% confidence interval (CI).
            upper: Upper limit of 95% CI.
        """
        self.point = point
        self.lower = lower
        self.upper = upper

    def _significant_digits(self) -> int:
        """Number of significant digits"""
        upper_error = self.upper - self.point
        lower_error = self.point - self.lower
        error = max(upper_error, lower_error)
        return _get_number_of_significant_digits(self.point, error)

    def latex(self) -> str:
        """Format 95% confidence interval as LaTeX."""
        if any(np.isnan([self.point, self.lower, self.upper])):
            return r"\verb|<nan>|"

        n_digits = self._significant_digits()
        number, exponent = _parse_scientific_notation(self.point)

        if exponent == 0:
            fargs = (number, (self.upper - self.point), (self.lower - self.point))
            return (
                "{:."
                + str(n_digits - 1)
                + "f}$^{{+{:."
                + str(n_digits - 1)
                + "f}}}_{{{:."
                + str(n_digits - 1)
                + "f}}}$"
            ).format(*fargs)

        elif exponent == -1:
            fargs = (self.point, (self.upper - self.point), (self.lower - self.point))
            return (
                "{:."
                + str(n_digits)
                + "f}$^{{+{:."
                + str(n_digits)
                + "f}}}_{{{:."
                + str(n_digits)
                + "f}}}$"
            ).format(*fargs)

        fargs_with_exp = (
            number,
            (self.upper - self.point) / 10**exponent,
            (self.lower - self.point) / 10**exponent,
            exponent,
        )

        return (
            "{:."
            + str(n_digits - 1)
            + r"f}$^{{+{:."
            + str(n_digits - 1)
            + r"f}}}_{{{:."
            + str(n_digits - 1)
            + r"f}}} \cdot 10^{{{:}}}$"
        ).format(*fargs_with_exp)

    def __str__(self) -> str:
        """String representation of estimate with 95% confidence interval."""
        if any(np.isnan([self.point, self.lower, self.upper])):
            return "<nan>"

        n_digits = self._significant_digits()
        point_str = _format_float(self.point, n_digits)
        lower_str = _format_float(self.lower, n_digits)
        upper_str = _format_float(self.upper, n_digits)
        return f"{point_str} (95% CI: {lower_str}–{upper_str})"

    def __eq__(self, other) -> bool:
        """Estimates are equal if all their values are equal."""
        # Perhaps we should make a more lenient definition, that estimate is not
        # significantly different?
        return (
            (self.point == other.point)
            and (self.upper == other.upper)
            and (self.lower == other.lower)
        )

    def __repr__(self) -> str:
        """Machine friendly representation."""
        return f"Estimate({self.point}, lower={self.lower}, upper={self.upper})"

    def __iter__(self):
        """Make function representable as a dict."""
        yield "point", self.point
        yield "lower", self.lower
        yield "upper", self.upper
