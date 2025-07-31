import sympy
import math

def ratio_test(expr):
    try:
        n = sympy.Symbol('n')
        if isinstance(expr, str):
            expr = sympy.sympify(expr)

        # Ensure the expression is in terms of n
        if 'n' not in str(expr):
            return 'Inconclusive'

        # Compute the limit for the ratio test
        limit = sympy.limit(abs(expr.subs(n, n + 1) / expr), n, sympy.oo)

        if limit < 1:
            return 'Convergent'
        elif limit > 1:
            return 'Divergent'
        else:
            return 'Inconclusive'
    except (sympy.SympifyError, TypeError, ValueError):
        return 'Inconclusive'

def root_test(expr):
    try:
        n = sympy.Symbol('n')
        if isinstance(expr, str):
            expr = sympy.sympify(expr)

        # Ensure the expression is in terms of n
        if 'n' not in str(expr):
            return 'Inconclusive'

        # Compute the limit for the root test
        limit = sympy.limit(abs(expr)**(1/n), n, sympy.oo)

        if limit < 1:
            return 'Convergent'
        elif limit > 1:
            return 'Divergent'
        else:
            return 'Inconclusive'
    except (sympy.SympifyError, TypeError, ValueError):
        return 'Inconclusive'

def integral_test(expr):
    try:
        n = sympy.Symbol('n')
        if isinstance(expr, str):
            expr = sympy.sympify(expr)

        # Ensure the expression is in terms of n
        if 'n' not in str(expr):
            return 'Inconclusive'

        # Check if the function is positive and decreasing
        # Note: A full check for is_decreasing can be computationally expensive
        # and may not work for all functions. We'll rely on the integral's convergence.

        # Compute the integral
        integral = sympy.integrate(expr, (n, 1, sympy.oo))

        if integral.is_finite:
            return 'Convergent'
        else:
            return 'Divergent'
    except (sympy.SympifyError, TypeError, ValueError, NotImplementedError):
        return 'Inconclusive'

def nth_term_test(expr):
    try:
        n = sympy.Symbol('n')
        if isinstance(expr, str):
            expr = sympy.sympify(expr)

        # Ensure the expression is in terms of n
        if 'n' not in str(expr):
            return 'Inconclusive'

        # Compute the limit of the nth term
        limit = sympy.limit(abs(expr), n, sympy.oo)

        if limit != 0:
            return 'Divergent'
        else:
            # If the limit is 0, the test is inconclusive
            return 'Inconclusive'
    except (sympy.SympifyError, TypeError, ValueError):
        return 'Inconclusive'

def p_series_test(expr):
    try:
        n = sympy.Symbol('n')
        if isinstance(expr, str):
            expr = sympy.sympify(expr)

        # Check if the expression is a p-series of the form 1/n**p
        # This is a simplified check and may not cover all equivalent forms
        base, exp = expr.as_base_exp()
        if base == n and exp.is_constant():
            p = -exp
            if p > 1:
                return 'Convergent'
            else:
                return 'Divergent'
        elif expr.is_Pow and expr.base == n:
             p = -expr.exp
             if p > 1:
                return 'Convergent'
             else:
                return 'Divergent'

        # Attempt to match the structure 1/n**p
        p_val = sympy.Wild('p')
        match = expr.match(1/n**p_val)
        if match and match[p_val] > 1:
            return 'Convergent'
        elif match and match[p_val] <= 1:
            return 'Divergent'

        return 'Inconclusive'
    except (sympy.SympifyError, TypeError, ValueError):
        return 'Inconclusive'

def alternating_series_test(expr):
    try:
        n = sympy.Symbol('n')
        if isinstance(expr, str):
            expr = sympy.sympify(expr)

        # Check if the series is alternating
        # A simple check for (-1)**n or (-1)**(n+1)
        if not (expr.has(sympy.Pow(-1, n)) or expr.has(sympy.Pow(-1, n + 1))):
            return 'Inconclusive'

        # Remove the alternating part to get the absolute value of the terms
        b_n = expr.subs(sympy.Pow(-1, n), 1).subs(sympy.Pow(-1, n + 1), 1)

        # Condition 1: The limit of the terms must be 0
        if sympy.limit(b_n, n, sympy.oo) != 0:
            return 'Divergent'

        # Condition 2: The terms must be decreasing
        # This can be computationally expensive, so we check a few points
        # A more robust check would involve the derivative
        is_decreasing = all(b_n.subs(n, i) >= b_n.subs(n, i + 1) for i in range(1, 5))
        if not is_decreasing:
            return 'Inconclusive'

        return 'Convergent'
    except (sympy.SympifyError, TypeError, ValueError):
        return 'Inconclusive'

def check_convergence(expr_str):
    try:
        expr = sympy.sympify(expr_str)
        n = sympy.Symbol('n')

        # Nth Term Test for Divergence (quick check)
        if nth_term_test(expr) == 'Divergent':
            return 'Divergent by the Nth Term Test'

        # P-Series Test
        p_series_result = p_series_test(expr)
        if p_series_result != 'Inconclusive':
            return f'{p_series_result} by the P-Series Test'

        # Alternating Series Test
        alternating_result = alternating_series_test(expr)
        if alternating_result != 'Inconclusive':
            return f'{alternating_result} by the Alternating Series Test'

        # Ratio Test
        ratio_result = ratio_test(expr)
        if ratio_result != 'Inconclusive':
            return f'{ratio_result} by the Ratio Test'

        # Root Test
        root_result = root_test(expr)
        if root_result != 'Inconclusive':
            return f'{root_result} by the Root Test'

        # Integral Test
        integral_result = integral_test(expr)
        if integral_result != 'Inconclusive':
            return f'{integral_result} by the Integral Test'

        return 'Inconclusive: None of the tests could determine convergence or divergence.'

    except (sympy.SympifyError, TypeError, ValueError):
        return 'Error: Invalid expression'