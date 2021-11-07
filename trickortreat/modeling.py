import numpy as np


def safety_rating(community_info, w_murder=10, w_rape=7, w_theft=1):
    """
    Returns a value between 1 and 0 where 0 is the most dangerous and 1 is the safest. The national average is 0.5.
    """
    p_safety = (
            w_murder * community_info["crmcymurd"]
            + w_rape * community_info["crmcyrape"]
            + w_theft * community_info["crmcyproc"]
    )
    p_safe_n = safety_factor * (1.5 - p_safety / ((w_murd + w_rape + 1) * 100))
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


def p_dist(house_acre):
    dist = np.sqrt(house_acre * 4840 / 2)
    d_min = 20
    d_max = 200
    m = -1 / (d_max - d_min)
    p = m * (dist - d_max)
    return np.clip(p, 0, 1)


def p_bedroom(n_bed):
    p_bed = 0.5 * (n_bed - 1)
    return np.clip(p_bed, 0, 1)


def p_house(w_candy, w_dist, w_safe, w_bed, house_price, house_acre, community_info, n_bed):
    p_safe = safety_rating(community_info)
    p_dist = pDist(house_acre)
    p_candy = pCandy(house_price)
    p_bed = pBedroom(n_bed)
    return (w_candy * p_candy + w_dist * p_dist + w_safe * p_safe + w_bed * p_bed) / (w_candy + w_dist + w_safe + w_bed)
