def vstop(price, multiplier, atr, prev):
    """
    Calculates the volatility stop indicator
    
    :param price: the current price used to determine the vstop 
    :param multiplier: the multiplier used for the vstop
    :param atr: the current average true range for the vstop
    :param prev: the previous state of the vstop function
    
    :return: the current state of the vstop function
    :return type: dictionary with keys: trend, vstop, max_price, min_price
    """
    max_price = max(price, prev['max_price'])
    min_price = min(price, prev['min_price'])

    had_up_trend = (prev['trend'] == 'up')

    stop = (max_price - multiplier * atr) if had_up_trend else (min_price + multiplier * atr)
    vstop = max(prev['vstop'], stop) if had_up_trend else min(prev['vstop'], stop)
    
    trend = 'up' if price >= vstop else 'down'    
    is_trend_changed = trend != prev['trend']
    
    if is_trend_changed:
        max_price = price
        min_price = price
        vstop = max_price - multiplier * atr if trend == 'up' else (min_price + multiplier * atr)
    
    return {'trend': trend,
            'vstop': vstop,
            'max_price': max_price,
            'min_price': min_price}