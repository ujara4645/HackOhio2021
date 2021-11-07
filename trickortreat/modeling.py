import numpy as np


def safety_rating(community_info, w_murder=10, w_rape=7, w_theft=1):
    """
    Returns a value between 1 and 0 where 1 is the most dangerous and 0 is the safest. The national average is 0.5.
    """
    p_safety = (
        w_murder * community_info["crmcymurd"]
        + w_rape * community_info["crmcyrape"]
        + w_theft * community_info["crmcyproc"]
    )
    p_safe_n = 0.5 * p_safety / ((w_murder + w_rape + w_theft) * 100) + 0.5
    return np.clip(p_safe_n, 0, 1)


def p_candy(price):
    p_max = 1000000
    p_min = 100000
    curve = 0.01
    p = (
        curve * np.exp(6.5 * np.log(2) / (p_max - p_min) * (price - p_min))
        - curve
    )
    return np.clip(p, 0, 1)
