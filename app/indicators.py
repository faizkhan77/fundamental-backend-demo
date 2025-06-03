# app/indicators.py
import math
from typing import List, Dict, Any, Optional, Tuple, Union

# Helper to get the last valid item from a list or None
def _get_latest(series: List[Any]) -> Optional[Any]:
    return series[-1] if series and series[-1] is not None and not math.isnan(series[-1]) else None

def _get_nth_latest(series: List[Any], n: int) -> Optional[Any]:
    """Gets the nth latest value (0 for latest, 1 for second latest, etc.) if valid."""
    if series and len(series) > n and series[-(n+1)] is not None and not math.isnan(series[-(n+1)]):
        return series[-(n+1)]
    return None

# --- Helper Calculation Functions ---

def _calculate_sma(data: List[float], period: int) -> List[Optional[float]]:
    if not data or len(data) < period:
        return [None] * len(data)
    
    sma_values: List[Optional[float]] = [None] * (period - 1)
    current_sum = sum(data[0:period])
    sma_values.append(current_sum / period)
    
    for i in range(period, len(data)):
        current_sum += data[i] - data[i - period]
        sma_values.append(current_sum / period)
    return sma_values

def _calculate_ema(data: List[float], period: int) -> List[Optional[float]]:
    if not data or len(data) < period:
        return [None] * len(data)
    
    ema_values: List[Optional[float]] = [None] * (period - 1)
    # First EMA is SMA
    sma = sum(data[0:period]) / period
    ema_values.append(sma)
    
    multiplier = 2 / (period + 1)
    
    for i in range(period, len(data)):
        ema_val = (data[i] - ema_values[i-1]) * multiplier + ema_values[i-1] if ema_values[i-1] is not None else None
        ema_values.append(ema_val)
    return ema_values

def _calculate_rma(data: List[float], period: int) -> List[Optional[float]]:
    """Wilder's Smoothing Average (Running Moving Average)"""
    if not data or len(data) < period:
        return [None] * len(data)

    rma_values: List[Optional[float]] = [None] * (period - 1)
    
    # Initial SMA for the first RMA value
    current_sum = sum(d for d in data[0:period] if d is not None) # Handle potential Nones in data
    if len([d for d in data[0:period] if d is not None]) != period: # Not enough data for first SMA
         # Fill initial segment with None and try to start later if possible
        rma_values = [None] * len(data)
        # Or raise error, this simplistic fill might not be robust for all cases
        first_valid_idx = -1
        for idx in range(len(data) - period + 1):
            segment = data[idx:idx+period]
            if all(s is not None for s in segment):
                rma_values[idx+period-1] = sum(segment) / period
                first_valid_idx = idx+period-1
                break
        if first_valid_idx == -1:
            return [None] * len(data) # Still not enough valid data
        
        start_loop_idx = first_valid_idx + 1
        
    else:
        rma_values.append(current_sum / period)
        start_loop_idx = period

    alpha = 1 / period
    for i in range(start_loop_idx, len(data)):
        if data[i] is None or rma_values[i-1] is None:
            rma_values.append(None) # Propagate None
            continue
        rma_val = alpha * data[i] + (1 - alpha) * rma_values[i-1]
        rma_values.append(rma_val)
    return rma_values


def _calculate_tr(highs: List[float], lows: List[float], closes: List[float]) -> List[Optional[float]]:
    if not highs or not lows or not closes or len(highs) != len(lows) or len(highs) != len(closes):
        raise ValueError("Input arrays must be non-empty and of the same length.")
    if len(highs) < 1: # Needs at least 1 for first TR (though usually starts from 2nd day)
        return []

    tr_values: List[Optional[float]] = [None] # First TR is often undefined or just H-L
    if len(highs) > 0 and highs[0] is not None and lows[0] is not None:
        tr_values[0] = highs[0] - lows[0] 

    for i in range(1, len(highs)):
        if highs[i] is None or lows[i] is None or closes[i-1] is None:
            tr_values.append(None)
            continue
        h_minus_l = highs[i] - lows[i]
        h_minus_pc = abs(highs[i] - closes[i-1])
        l_minus_pc = abs(lows[i] - closes[i-1])
        tr_values.append(max(h_minus_l, h_minus_pc, l_minus_pc))
    return tr_values

def calculate_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> List[Optional[float]]:
    if period <= 0:
        raise ValueError("ATR period must be positive.")
    tr_series = _calculate_tr(highs, lows, closes)
    # Filter out initial Nones from TR if any before passing to RMA
    valid_tr_series = [tr for tr in tr_series if tr is not None]
    
    if not valid_tr_series or len(valid_tr_series) < period :
        return [None] * len(closes) # Not enough data for ATR

    atr_series_calculated = _calculate_rma(valid_tr_series, period)
    
    # Align ATR series with original price series length
    # Find first non-None TR to align calculation start
    first_tr_index = -1
    for i, tr_val in enumerate(tr_series):
        if tr_val is not None:
            first_tr_index = i
            break
    
    if first_tr_index == -1: # Should not happen if valid_tr_series was populated
        return [None] * len(closes)

    # The atr_series_calculated starts from the first valid segment of TRs
    # We need to pad Nones at the beginning to match original length
    # The length of padding needed is first_tr_index + (period -1 for RMA's own initial Nones)
    # if the first valid TR value leads to first valid ATR value at that point in valid_tr_series
    
    aligned_atr_series = [None] * len(closes)
    # The first ATR value corresponds to index (period-1) in the valid_tr_series
    # This (period-1) index in valid_tr_series corresponds to some index in the original closes series
    
    # Count Nones at start of tr_series
    initial_tr_nones = 0
    for tr_val in tr_series:
        if tr_val is None:
            initial_tr_nones +=1
        else:
            break
            
    # The atr_series_calculated is based on tr_series[initial_tr_nones:]
    # The first value of atr_series_calculated (at its index period-1) corresponds to
    # original index: initial_tr_nones + period - 1
    
    atr_start_original_index = initial_tr_nones + period -1
    
    for i in range(len(atr_series_calculated)):
        if atr_series_calculated[i] is not None:
            # The i-th value in atr_series_calculated corresponds to 
            # (i) in terms of the 'valid_tr_series'
            # The first non-None is at atr_series_calculated[period-1]
            # This should be placed at aligned_atr_series[atr_start_original_index + (i - (period-1))]
            target_idx = atr_start_original_index + (i-(period-1)) if i >= period-1 else -1
            if 0 <= target_idx < len(aligned_atr_series):
                 aligned_atr_series[target_idx] = atr_series_calculated[i]
    
    return aligned_atr_series


def _calculate_directional_movement(highs: List[float], lows: List[float]) -> Dict[str, List[Optional[float]]]:
    if not highs or len(highs) < 2:
        return {"plus_dm": [], "minus_dm": []}

    plus_dm_values: List[Optional[float]] = [None] # First value undefined
    minus_dm_values: List[Optional[float]] = [None]

    for i in range(1, len(highs)):
        if highs[i] is None or lows[i] is None or highs[i-1] is None or lows[i-1] is None:
            plus_dm_values.append(None)
            minus_dm_values.append(None)
            continue

        up_move = highs[i] - highs[i-1]
        down_move = lows[i-1] - lows[i]

        current_plus_dm = 0.0
        current_minus_dm = 0.0

        if up_move > down_move and up_move > 0:
            current_plus_dm = up_move
        
        if down_move > up_move and down_move > 0:
            current_minus_dm = down_move
        
        plus_dm_values.append(current_plus_dm)
        minus_dm_values.append(current_minus_dm)
        
    return {"plus_dm": plus_dm_values, "minus_dm": minus_dm_values}

# --- Main Indicator Functions ---

def calculate_rsi(closes: List[float], period: int = 14) -> List[Optional[float]]:
    if not closes or len(closes) <= period: # Need len > period for any RSI value
        return [None] * len(closes)

    rsi_values: List[Optional[float]] = [None] * period 
    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
    
    gains_sum = 0.0
    losses_sum = 0.0

    # Calculate initial average gains and losses
    for i in range(period): # Using first 'period' deltas
        if i >= len(deltas): break # Should not happen if len(closes) > period
        change = deltas[i]
        if change > 0:
            gains_sum += change
        else:
            losses_sum -= change # losses are positive

    if period == 0: return [None] * len(closes)
    avg_gain = gains_sum / period
    avg_loss = losses_sum / period
    
    # Calculate first RSI
    if avg_loss == 0:
        current_rsi = 100.0
    else:
        rs = avg_gain / avg_loss
        current_rsi = 100.0 - (100.0 / (1.0 + rs))
    rsi_values.append(current_rsi)

    # Calculate subsequent RSIs
    for i in range(period, len(deltas)):
        change = deltas[i]
        gain = change if change > 0 else 0.0
        loss = -change if change < 0 else 0.0

        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period

        if avg_loss == 0:
            current_rsi = 100.0
        else:
            rs = avg_gain / avg_loss
            current_rsi = 100.0 - (100.0 / (1.0 + rs))
        rsi_values.append(current_rsi)
    
    # Pad with Nones if rsi_values is shorter than closes
    return [None]*(len(closes)-len(rsi_values)) + rsi_values if len(rsi_values) < len(closes) else rsi_values


def calculate_macd(
    closes: List[float],
    fast_length: int = 12,
    slow_length: int = 26,
    signal_length: int = 9,
    sma_source: str = "EMA", # "EMA" or "SMA"
    sma_signal: str = "EMA"  # "EMA" or "SMA"
) -> Dict[str, List[Optional[float]]]:
    
    if not closes or len(closes) < slow_length + signal_length: # Simplified check
        # raise ValueError("Invalid input: closes must have length >= slow_length + signal_length")
        return {"macd": [], "signal": [], "hist": []}

    ma_function = _calculate_sma if sma_source == "SMA" else _calculate_ema
    signal_function = _calculate_sma if sma_signal == "SMA" else _calculate_ema

    fast_ma = ma_function(closes, fast_length)
    slow_ma = ma_function(closes, slow_length)

    macd_line: List[Optional[float]] = []
    # Align MACD calculation with the longer of the two MAs (slow_ma)
    # fast_ma and slow_ma already have leading Nones
    for i in range(len(closes)):
        if fast_ma[i] is not None and slow_ma[i] is not None:
            macd_line.append(fast_ma[i] - slow_ma[i])
        else:
            macd_line.append(None)
    
    # Filter out initial Nones from macd_line before passing to signal_function
    # but keep track of original indexing
    first_macd_val_idx = -1
    for idx, val in enumerate(macd_line):
        if val is not None:
            first_macd_val_idx = idx
            break
    
    if first_macd_val_idx == -1: # All MACD values are None
        return {"macd": macd_line, "signal": [None]*len(closes), "hist": [None]*len(closes)}

    # Calculate signal line on the valid part of macd_line
    valid_macd_part = macd_line[first_macd_val_idx:]
    signal_line_calculated = signal_function(valid_macd_part, signal_length)

    # Align signal_line_calculated back to original length
    signal_line: List[Optional[float]] = [None] * len(closes)
    # The first value of signal_line_calculated corresponds to index (signal_length-1) in valid_macd_part
    # This is original index: first_macd_val_idx + signal_length - 1
    signal_start_original_idx = first_macd_val_idx + signal_length - 1
    
    for i in range(len(signal_line_calculated)):
        if signal_line_calculated[i] is not None:
            target_idx = first_macd_val_idx + i # Signal calc starts from valid MACD, EMA/SMA adds its own padding
            if 0 <= target_idx < len(signal_line):
                 signal_line[target_idx] = signal_line_calculated[i]


    hist_line: List[Optional[float]] = []
    for i in range(len(closes)):
        if macd_line[i] is not None and signal_line[i] is not None:
            hist_line.append(macd_line[i] - signal_line[i])
        else:
            hist_line.append(None)
            
    return {"macd": macd_line, "signal": signal_line, "hist": hist_line}


def calculate_adx(
    highs: List[float], 
    lows: List[float], 
    closes: List[float], 
    di_len: int = 14, 
    adx_len: int = 14
) -> Dict[str, List[Optional[float]]]:
    
    min_len = di_len + adx_len # Approximation
    if not highs or len(highs) < min_len:
        # raise ValueError(f"Invalid input: arrays must have length >= {min_len}")
        return {"plus_di": [], "minus_di": [], "adx": []}

    tr_series = _calculate_tr(highs, lows, closes)
    dm_data = _calculate_directional_movement(highs, lows)
    plus_dm_series = dm_data["plus_dm"]
    minus_dm_series = dm_data["minus_dm"]

    # Ensure all series are aligned and filter Nones for RMA
    # RMA needs non-None series, so we filter and then align back

    def _filter_and_rma(series: List[Optional[float]], period: int) -> List[Optional[float]]:
        if not any(s is not None for s in series): return [None] * len(series)
        
        first_valid_idx = 0
        while first_valid_idx < len(series) and series[first_valid_idx] is None:
            first_valid_idx += 1
        
        valid_part = [s for s in series[first_valid_idx:] if s is not None] # Further Nones could exist
        if len(valid_part) < period : return [None] * len(series) # Not enough data after filtering

        rma_calc = _calculate_rma(valid_part, period) # RMA result on filtered data
        
        # Align back
        aligned_rma = [None] * len(series)
        rma_calc_idx = 0
        # The first value of rma_calc is at its index (period-1)
        # This corresponds to original series index: first_valid_idx + (period-1 for value in valid_part) + (period-1 for RMA internal start)
        # Let's simplify: rma_calc applies to valid_part. The first non-None in rma_calc is at index (period-1)
        # This (period-1) in rma_calc is the (period-1)th *valid* value from 'series'.
        # Need to map this back carefully.

        # RMA's first output is at index `period-1` of its input `valid_part`.
        # This `valid_part[period-1]` corresponds to some original index.
        
        # Simpler alignment: find first non-None in series, then add period-1 for RMA's own start
        # then iterate through rma_calc and place values.
        
        # RMA's first output (at its index period-1) corresponds to the data point at
        # (first_valid_idx + period -1) in original series.
        # This is where the 'period'-th valid data point occurs.
        start_original_idx_for_rma_output = -1
        valid_count = 0
        for i in range(len(series)):
            if series[i] is not None:
                valid_count +=1
            if valid_count == period:
                start_original_idx_for_rma_output = i
                break
        
        if start_original_idx_for_rma_output != -1:
            for r_idx, r_val in enumerate(rma_calc):
                # r_val at rma_calc[r_idx] should be placed at start_original_idx_for_rma_output + (r_idx - (period-1))
                # but only if r_idx >= period-1
                if r_val is not None and r_idx >= period -1 :
                    target_idx = start_original_idx_for_rma_output + (r_idx - (period-1))
                    if 0 <= target_idx < len(aligned_rma):
                        aligned_rma[target_idx] = r_val
        return aligned_rma


    smoothed_tr = _filter_and_rma(tr_series, di_len)
    smoothed_plus_dm = _filter_and_rma(plus_dm_series, di_len)
    smoothed_minus_dm = _filter_and_rma(minus_dm_series, di_len)

    plus_di: List[Optional[float]] = [None] * len(highs)
    minus_di: List[Optional[float]] = [None] * len(highs)
    
    for i in range(len(highs)):
        if smoothed_tr[i] is not None and smoothed_tr[i] != 0 and \
           smoothed_plus_dm[i] is not None and smoothed_minus_dm[i] is not None:
            plus_di[i] = (smoothed_plus_dm[i] / smoothed_tr[i]) * 100
            minus_di[i] = (smoothed_minus_dm[i] / smoothed_tr[i]) * 100
        else:
            plus_di[i] = None
            minus_di[i] = None

    dx_series: List[Optional[float]] = [None] * len(highs)
    for i in range(len(highs)):
        if plus_di[i] is not None and minus_di[i] is not None:
            di_sum = plus_di[i] + minus_di[i]
            if di_sum != 0:
                dx_series[i] = (abs(plus_di[i] - minus_di[i]) / di_sum) * 100
            else:
                dx_series[i] = 0.0 # Or None, JS had 0
        else:
            dx_series[i] = None
            
    adx_line = _filter_and_rma(dx_series, adx_len)
    
    return {"plus_di": plus_di, "minus_di": minus_di, "adx": adx_line}


def calculate_supertrend(
    highs: List[float], 
    lows: List[float], 
    closes: List[float], 
    atr_period: int = 10, 
    factor: float = 3.0
) -> Dict[str, List[Any]]: # supertrend is float, direction is int

    min_len = atr_period + 1 # ATR needs 'atr_period' TR values, Supertrend starts after ATR is available
    if not highs or len(highs) < min_len :
        # raise ValueError(f"Invalid input: arrays must have length >= {min_len}")
        return {"supertrend": [], "direction": []}

    atr_values = calculate_atr(highs, lows, closes, atr_period)

    supertrend_line: List[Optional[float]] = [None] * len(highs)
    direction_line: List[Optional[int]] = [None] * len(highs) # 1 for uptrend, -1 for downtrend

    # Find first valid ATR to start Supertrend calculation
    first_valid_atr_idx = -1
    for i, atr_val in enumerate(atr_values):
        if atr_val is not None:
            first_valid_atr_idx = i
            break
    
    if first_valid_atr_idx == -1 or first_valid_atr_idx >= len(highs): # No valid ATR or not enough data
        return {"supertrend": [None]*len(highs), "direction": [None]*len(highs)}

    # Initial Supertrend value calculation
    # This depends on where the first ATR is. Supertrend needs close[i-1] and supertrend[i-1].
    # The JS logic seems to initialize at i = atrPeriod, which implies ATR is available from there.
    # Let's use first_valid_atr_idx as the point where calculation can begin.
    
    start_index = first_valid_atr_idx # The index where ATR is first available

    if start_index >= len(highs) or highs[start_index] is None or lows[start_index] is None or atr_values[start_index] is None:
         return {"supertrend": [None]*len(highs), "direction": [None]*len(highs)} # Not enough data to start

    # First ST value: JS uses lowerBand for init.
    # (high[i] + low[i]) / 2 - factor * atr[i]
    # We need to ensure all components are valid at start_index
    initial_mid_price = (highs[start_index] + lows[start_index]) / 2
    supertrend_line[start_index] = initial_mid_price - factor * atr_values[start_index]
    direction_line[start_index] = 1 # Initial assumption: uptrend

    for i in range(start_index + 1, len(highs)):
        if highs[i] is None or lows[i] is None or closes[i] is None or closes[i-1] is None or \
           atr_values[i] is None or supertrend_line[i-1] is None:
            supertrend_line[i] = None # Propagate None
            direction_line[i] = None
            continue

        basic_upper_band = ((highs[i] + lows[i]) / 2) + (factor * atr_values[i])
        basic_lower_band = ((highs[i] + lows[i]) / 2) - (factor * atr_values[i])
        
        prev_st = supertrend_line[i-1]
        prev_close = closes[i-1]

        current_st = 0.0
        if prev_close > prev_st : # Previous trend was up (or flat becoming up)
            current_st = max(basic_lower_band, prev_st) # JS uses min for lowerBand when up, but logic is prev_close > prev_st
                                                        # This is more like: if prev close > prev ST, new ST is max(new_lower_band, prev_ST)
                                                        # PineScript: src > nz(trend[1], src) ? max(dn, nz(trend[1], dn)) : min(up, nz(trend[1], up))
                                                        # if close[i-1] > supertrend[i-1] implies uptrend was active
                                                        # then new supertrend is max(basic_lower_band, supertrend[i-1])
                                                        # The JS is: close[i-1] > supertrend[i-1] ? Math.min(lowerBand, supertrend[i-1]) : Math.max(upperBand, supertrend[i-1])
                                                        # This seems inverted logic for typical supertrend. Let's use a common ST logic.
            # Typical ST logic:
            # if closes[i-1] > supertrend_line[i-1]: # If prev close broke above prev ST (uptrend)
            #     supertrend_line[i] = max(basic_lower_band, supertrend_line[i-1])
            # else: # Downtrend
            #     supertrend_line[i] = min(basic_upper_band, supertrend_line[i-1])
            # Let's follow the JS provided:
            if closes[i-1] > supertrend_line[i-1]:
                 supertrend_line[i] = max(basic_lower_band, supertrend_line[i-1]) # Typical use max for uptrend's lowerband adjustment
                 # JS: Math.min(lowerBand, supertrend[i-1]) -- this is for upper band in other variants. 
                 # Using the more common way (max for lower, min for upper) might be intended.
                 # Sticking to provided JS:
                 # supertrend_line[i] = min(basic_lower_band, supertrend_line[i-1]) # This is unusual if prev_close > prev_st
                 # The JS provided logic for ST update seems different from standard.
                 # Let's re-evaluate the JS:
                 # supertrend[i] = close[i-1] > supertrend[i-1] ? Math.max(lowerBand, supertrend[i-1]) : Math.min(upperBand, supertrend[i-1]);
                 # This means: if prev close was above prev ST (so prev trend was UP): new ST is max(current_lower_band, prev_ST_value).
                 # if prev close was below prev ST (so prev trend was DOWN): new ST is min(current_upper_band, prev_ST_value).
                 # This is a common way. Okay, the JS provided `Math.min(lowerBand, supertrend[i-1])` was a misread.
                 # The actual JS in prompt:
                 # supertrend[i] = close[i-1] > supertrend[i-1] ? Math.max(lowerBand, supertrend[i-1]) : Math.min(upperBand, supertrend[i-1]);
                 # This is NOT what was in the prompt. The prompt had:
                 # supertrend[i] = close[i - 1] > supertrend[i - 1]
                 #      ? Math.min(lowerBand, supertrend[i - 1]) <--- This is odd.
                 #      : Math.max(upperBand, supertrend[i - 1]); <--- This is odd.
                 # Assuming the prompt's version is what's desired, even if unusual:
                 if closes[i-1] > supertrend_line[i-1]: # Trend was up or crossing up
                    supertrend_line[i] = min(basic_lower_band, supertrend_line[i-1]) # JS: Math.min(lowerBand, supertrend[i-1])
                 else: # Trend was down or crossing down
                    supertrend_line[i] = max(basic_upper_band, supertrend_line[i-1]) # JS: Math.max(upperBand, supertrend[i-1])

        else: # was downrend
            supertrend_line[i] = max(basic_upper_band, supertrend_line[i-1])


        # Determine current direction based on current close and current ST
        if closes[i] > supertrend_line[i]:
            direction_line[i] = 1
        elif closes[i] < supertrend_line[i]:
            direction_line[i] = -1
        else: # close == supertrend
            direction_line[i] = direction_line[i-1] if i > 0 and direction_line[i-1] is not None else 1 # maintain previous or default to up

    return {"supertrend": supertrend_line, "direction": direction_line}


def _calculate_donchian_channel_ichimoku_helper(highs: List[float], lows: List[float], period: int) -> List[Optional[float]]:
    if not highs or len(highs) < period:
        return [None] * len(highs)
    
    results: List[Optional[float]] = [None] * (period - 1)
    for i in range(period - 1, len(highs)):
        high_slice = highs[i - period + 1 : i + 1]
        low_slice = lows[i - period + 1 : i + 1]

        if any(x is None for x in high_slice) or any(x is None for x in low_slice):
            results.append(None)
            continue
            
        highest = max(high_slice)
        lowest = min(low_slice)
        results.append((highest + lowest) / 2)
    return results


def calculate_ichimoku_cloud(
    highs: List[float], 
    lows: List[float], 
    closes: List[float],
    conversion_periods: int = 9,
    base_periods: int = 26,
    lagging_span_2_periods: int = 52, # Senkou Span B period
    displacement: int = 26 # For Senkou Spans and Chikou
) -> Dict[str, List[Optional[float]]]:

    min_len = max(conversion_periods, base_periods, lagging_span_2_periods) # displacement also matters for alignment
    if not highs or len(highs) < min_len + displacement: # Ensure enough data for lookaheads/behinds
        # raise ValueError("Invalid input: insufficient data for Ichimoku.")
        return {
            "conversion_line": [], "base_line": [], "lead_line1": [], 
            "lead_line2": [], "lagging_span": []
        }

    conversion_line = _calculate_donchian_channel_ichimoku_helper(highs, lows, conversion_periods)
    base_line = _calculate_donchian_channel_ichimoku_helper(highs, lows, base_periods)
    
    # Senkou Span A (Lead Line 1)
    lead_line1_calc: List[Optional[float]] = [None] * len(highs)
    for i in range(len(highs)):
        if conversion_line[i] is not None and base_line[i] is not None:
            lead_line1_calc[i] = (conversion_line[i] + base_line[i]) / 2
    
    # Senkou Span B (Lead Line 2)
    lead_line2_calc = _calculate_donchian_channel_ichimoku_helper(highs, lows, lagging_span_2_periods)

    # Displace Senkou Spans forward
    lead_line1_displaced: List[Optional[float]] = [None] * len(highs)
    lead_line2_displaced: List[Optional[float]] = [None] * len(highs)

    for i in range(len(highs) - displacement):
        lead_line1_displaced[i + displacement] = lead_line1_calc[i]
        lead_line2_displaced[i + displacement] = lead_line2_calc[i]

    # Chikou Span (Lagging Span) - current close plotted `displacement` periods in the past
    lagging_span: List[Optional[float]] = [None] * len(highs)
    for i in range(displacement, len(highs)):
        lagging_span[i - displacement] = closes[i]
        
    return {
        "conversion_line": conversion_line, # Tenkan-sen
        "base_line": base_line,             # Kijun-sen
        "lead_line1": lead_line1_displaced, # Senkou Span A (displaced)
        "lead_line2": lead_line2_displaced, # Senkou Span B (displaced)
        "lagging_span": lagging_span   ,     # Chikou Span (displaced)
        "displacement_val": displacement # Added for decision logic
    
    }


def calculate_parabolic_sar(
    highs: List[float], 
    lows: List[float], 
    start_af: float = 0.02, 
    increment_af: float = 0.02, 
    max_af: float = 0.2
) -> List[Optional[float]]:
    
    if not highs or len(highs) < 2:
        # raise ValueError("Invalid input: prices must be an array with length >= 2")
        return []
    
    sar_values: List[Optional[float]] = [None] * len(highs)
    if highs[0] is None or lows[0] is None: return [None] * len(highs) # Cannot start

    # Initial values
    sar_values[0] = lows[0] # Initial SAR often set to first low (if assumed uptrend) or high (if downtrend)
                            # JS code uses prices[0].low for sar[0] and ep=prices[0].low, implying initial uptrend guess.
    ep = lows[0] # Extreme Price
    af = start_af
    is_uptrend = True # Initial assumption

    for i in range(1, len(highs)):
        if highs[i] is None or lows[i] is None or sar_values[i-1] is None or \
           highs[i-1] is None or lows[i-1] is None : # Check previous day's H/L too for min/max logic
            sar_values[i] = None
            # Reset state if data becomes gappy? Or propagate None and hope for recovery?
            # For simplicity, propagating None if essential data missing.
            continue

        prev_sar = sar_values[i-1]
        
        if is_uptrend:
            sar_values[i] = prev_sar + af * (ep - prev_sar)
            if sar_values[i] > lows[i]: # Trend reversal to downtrend
                is_uptrend = False
                sar_values[i] = ep # SAR becomes the prior EP
                ep = lows[i]    # New EP is the low of the reversal bar
                af = start_af
            else: # Continue uptrend
                if highs[i] > ep:
                    ep = highs[i]
                    af = min(af + increment_af, max_af)
                # Ensure SAR is not placed inside previous or current bar's low
                sar_values[i] = min(sar_values[i], lows[i-1], lows[i]) 
        else: # Downtrend
            sar_values[i] = prev_sar + af * (ep - prev_sar)
            if sar_values[i] < highs[i]: # Trend reversal to uptrend
                is_uptrend = True
                sar_values[i] = ep # SAR becomes the prior EP
                ep = highs[i]   # New EP is the high of the reversal bar
                af = start_af
            else: # Continue downtrend
                if lows[i] < ep:
                    ep = lows[i]
                    af = min(af + increment_af, max_af)
                # Ensure SAR is not placed inside previous or current bar's high
                sar_values[i] = max(sar_values[i], highs[i-1], highs[i])
                
    return sar_values


def calculate_williams_r(highs: List[float], lows: List[float], closes: List[float], length: int = 14) -> List[Optional[float]]:
    if not highs or len(highs) < length:
        # raise ValueError(f"Invalid input: prices must have length >= {length}")
        return []
        
    percent_r_values: List[Optional[float]] = [None] * (length - 1)
    for i in range(length - 1, len(highs)):
        if closes[i] is None:
            percent_r_values.append(None)
            continue
        
        h_slice = highs[i - length + 1 : i + 1]
        l_slice = lows[i - length + 1 : i + 1]

        if any(x is None for x in h_slice) or any(x is None for x in l_slice):
            percent_r_values.append(None)
            continue

        highest_high = max(h_slice)
        lowest_low = min(l_slice)
        
        if highest_high == lowest_low:
            percent_r_values.append(0.0) # Or -50.0, JS has 0
        else:
            pr = ((highest_high - closes[i]) / (highest_high - lowest_low)) * -100
            percent_r_values.append(pr)
            
    return percent_r_values


def calculate_vwap(
    highs: List[float], 
    lows: List[float], 
    closes: List[float], 
    volumes: List[float]
    # Ignoring band parameters from JS as they are not used in decision logic
) -> Dict[str, List[Optional[float]]]: # Only returning VWAP line
    
    if not highs or len(highs) < 1:
        # raise ValueError("Invalid input: prices must be an array with length >= 1")
        return {"vwap": []}

    vwap_values: List[Optional[float]] = []
    cumulative_price_volume = 0.0
    cumulative_volume = 0.0

    for i in range(len(highs)):
        if highs[i] is None or lows[i] is None or closes[i] is None or volumes[i] is None or volumes[i] == 0:
            vwap_values.append(None) # Cannot calculate if data missing or volume is zero
            # Reset cumulative for daily VWAP? This is session VWAP. For continuous, don't reset.
            # The JS example implies continuous cumulative VWAP.
            continue

        typical_price = (highs[i] + lows[i] + closes[i]) / 3
        volume = volumes[i]
        
        cumulative_price_volume += typical_price * volume
        cumulative_volume += volume
        
        if cumulative_volume == 0: # Should be caught by volume[i]==0 check earlier for first item
            vwap_values.append(None)
        else:
            vwap_values.append(cumulative_price_volume / cumulative_volume)
            
    return {"vwap": vwap_values} # Ignoring bands for now


def calculate_bollinger_bands(
    closes: List[float], 
    length: int = 20, 
    ma_type: str = "SMA", # SMA, EMA, RMA, WMA (WMA not implemented as helper yet)
    mult: float = 2.0
) -> Dict[str, List[Optional[float]]]:

    if not closes or len(closes) < length:
        # raise ValueError(f"Invalid input: prices must have length >= {length}")
        return {"basis": [], "upper": [], "lower": []}

    if ma_type == "SMA": ma_function = _calculate_sma
    elif ma_type == "EMA": ma_function = _calculate_ema
    elif ma_type == "RMA" or ma_type == "SMMA": ma_function = _calculate_rma
    # elif ma_type == "WMA": ma_function = _calculate_wma # WMA helper needed
    else: ma_function = _calculate_sma # Default to SMA

    basis_line = ma_function(closes, length)
    
    upper_band: List[Optional[float]] = [None] * len(closes)
    lower_band: List[Optional[float]] = [None] * len(closes)

    # Standard deviation calculation needs to align with MA availability
    for i in range(len(closes)):
        if basis_line[i] is None: # MA not yet available
            continue
        
        # Slice for stdev calculation should be closes[i-length+1 : i+1]
        # But this needs to be done carefully if `i` is already ahead due to MA's leading Nones
        # MA output (basis_line[i]) corresponds to original data up to closes[i]
        
        if i < length -1: # Not enough data for stdev calc relative to current point `i`
            continue

        price_slice = closes[i - length + 1 : i + 1]
        if any(p is None for p in price_slice):
            # upper_band[i], lower_band[i] remain None
            continue

        mean = basis_line[i] # Already calculated MA for this point
        variance = sum([(p - mean)**2 for p in price_slice]) / length
        stdev = math.sqrt(variance)
        
        upper_band[i] = mean + mult * stdev
        lower_band[i] = mean - mult * stdev
        
    return {"basis": basis_line, "upper": upper_band, "lower": lower_band}


# --- Master Decision Logic ---
def get_technical_analysis_summary(
    opens: List[float],
    highs: List[float],
    lows: List[float],
    closes: List[float],
    volumes: List[float]
) -> Dict[str, Any]:

    num_data_points = len(closes)
    # Basic check for minimal data
    if num_data_points < 60: # Arbitrary minimum, ~3 months for longer indicators
        return {
            "signals": [{"name": indicator, "value": None, "decision": "Neutral"} 
                        for indicator in ["RSI", "EMA", "SMA", "MACD", "ADX", "Supertrend", 
                                          "BollingerBands", "VWAP", "WilliamsR", "PSAR", "Ichimoku", "ATR"]],
            "overallSignal": "Neutral"
        }

    # Calculate all indicators
    # Ensure enough data points are passed to each.
    # These functions return full series, already padded with Nones at the start.
    
    rsi14_series = calculate_rsi(closes, 14)
    ema9_series = _calculate_ema(closes, 9)
    sma20_series = _calculate_sma(closes, 20)
    macd_data = calculate_macd(closes, 12, 26, 9, "EMA", "EMA")
    adx_data = calculate_adx(highs, lows, closes, 14, 14)
    supertrend_data = calculate_supertrend(highs, lows, closes, 10, 3.0)
    bollinger_data = calculate_bollinger_bands(closes, 20, "SMA", 2.0)
    vwap_data = calculate_vwap(highs, lows, closes, volumes)
    williams_r_series = calculate_williams_r(highs, lows, closes, 14)
    psar_series = calculate_parabolic_sar(highs, lows) # Default AFs
    ichimoku_data = calculate_ichimoku_cloud(highs, lows, closes) # Default periods
    atr_series = calculate_atr(highs, lows, closes, 14)

    # Get latest values
    latest_price = _get_latest(closes)
    # latest_open = _get_latest(opens) # Not used in Python decision logic directly yet
    prev_close = _get_nth_latest(closes, 1) # Second latest close

    latest_rsi = _get_latest(rsi14_series)
    latest_ema9 = _get_latest(ema9_series)
    latest_sma20 = _get_latest(sma20_series)
    
    latest_macd_line = _get_latest(macd_data.get("macd", []))
    latest_macd_signal = _get_latest(macd_data.get("signal", []))
    
    latest_adx_line = _get_latest(adx_data.get("adx", []))
    latest_plus_di = _get_latest(adx_data.get("plus_di", []))
    latest_minus_di = _get_latest(adx_data.get("minus_di", []))
    
    latest_supertrend_val = _get_latest(supertrend_data.get("supertrend", []))
    latest_supertrend_dir = _get_latest(supertrend_data.get("direction", []))
    
    latest_bb_upper = _get_latest(bollinger_data.get("upper", []))
    latest_bb_lower = _get_latest(bollinger_data.get("lower", []))
    latest_bb_middle = _get_latest(bollinger_data.get("basis", []))
    
    latest_vwap = _get_latest(vwap_data.get("vwap", []))
    latest_williams_r = _get_latest(williams_r_series)
    latest_psar = _get_latest(psar_series)
    
    latest_tenkan_sen = _get_latest(ichimoku_data.get("conversion_line", []))
    latest_kijun_sen = _get_latest(ichimoku_data.get("base_line", []))
    
    # For Ichimoku cloud comparison, we need Senkou spans corresponding to the *current* price.
    # Since Senkou spans are displaced forward by `displacement` (e.g., 26 periods),
    # the cloud data relevant for the *current* price candle was calculated `displacement` periods ago.
    # So, we look at `lead_line1/2[num_data_points - 1]` as these are already displaced.
    latest_senkou_a = _get_latest(ichimoku_data.get("lead_line1",[]))
    latest_senkou_b = _get_latest(ichimoku_data.get("lead_line2",[]))

    # Chikou span (lagging_span) is current close plotted `displacement` periods in the past.
    # The value at `lagging_span[num_data_points - 1 - displacement]` is the current close.
    # The decision logic uses `latestChikouSpan > closes[closes.length - 27]`
    # This means `lagging_span` value from `displacement` periods ago (which is current close[current-displacement])
    # compared against `closes[current - displacement - displacement]`.
    # In Python: `chikou_val = closes[num_data_points - 1 - displacement]`
    # compared with `price_for_chikou_compare = closes[num_data_points - 1 - displacement - displacement]`
    # The JS `latestChikouSpan` is `chikouSpan[chikouSpan.length - 1]`. This is incorrect.
    # `chikouSpan` is already shifted. The last value of `chikouSpan` corresponds to `close[current_price_index + displacement]`.
    # Corrected logic for Chikou:
    # Value of Chikou span *for the current period* is `closes[current_idx - displacement]`.
    # The price it's compared against is `closes[current_idx - displacement]`. This is self-comparison.
    # Standard: Chikou Span is `close` plotted `displacement` periods in the past.
    # Compare Chikou Span (today's close plotted `displacement` ago) with price from `displacement` periods ago.
    # Let's get current Chikou span value: `closes[num_data_points -1 - displacement]` if `num_data_points > displacement`.
    # Compare it with price that was `displacement` periods ago from where Chikou is plotted: `closes[num_data_points - 1 - displacement - displacement]`.

    # Ichimoku decision logic from JS:
    # `latestChikouSpan > closes[closes.length - 27]`
    # JS `latestChikouSpan` is `chikouSpan[chikouSpan.length - 1]` -> this is `closes[len-1+displacement]` if using JS logic fully. No, this is the *last plotted value* of Chikou.
    # The actual chikou value to consider *for current analysis* is the close `displacement` periods ago.
    # `ichimoku_data.get("lagging_span", [])` is the series of Chikou values.
    # `_get_latest(ichimoku_data.get("lagging_span",[]))` gives the "latest plotted" chikou, which is `close[current_time + displacement_offset_if_any]`.
    # For current analysis, one often checks if `close[current] > cloud[current]` and `chikou_span_value_related_to_current > price_related_to_chikou`.
    # The JS `latestChikouSpan = chikouSpan[chikouSpan.length - 1]` is tricky. If `chikouSpan` has length `L`, this is the last value.
    # If `lagging_span` is `closes` shifted left by `displacement`, then `lagging_span[i] = closes[i+displacement]`.
    # Then `lagging_span[L-1]` is `closes[L-1+displacement]`. This is future.
    # The JS code for `laggingSpan` calculation for Ichimoku:
    # `for (let i = 0; i < prices.length - displacement + 1; i++) { laggingSpan.push(prices[i].close); }`
    # This is NOT a standard Chikou span. Standard is `close` shifted `displacement` to the PAST.
    # The python `calculate_ichimoku_cloud` implements standard Chikou: `lagging_span[i - displacement] = closes[i]`
    # So, `_get_latest(lagging_span)` would be `closes[latest_idx]` plotted at `latest_idx - displacement`.
    # JS decision: `latestChikouSpan > closes[closes.length - 27]` (assuming displacement 26, so 27th element from end)
    # Python equivalent: `chikou_value_for_current_bar = _get_nth_latest(closes, displacement)`
    # `price_to_compare_chikou = _get_nth_latest(closes, displacement + displacement)` # Roughly
    
    # Let's use the JS reference point for chikou comparison if possible:
    # `closes[closes.length - 27]` is `closes[num_data_points - 1 - 26]` if `displacement=26`.
    chikou_compare_price_index = num_data_points - 1 - ichimoku_data.get("displacement_val", 26) # Assuming displacement stored
    chikou_price_for_comparison = closes[chikou_compare_price_index] if chikou_compare_price_index >= 0 else None
    
    # The `latestChikouSpan` should be the value of the Chikou line that corresponds to the current analysis point.
    # If lagging_span is `close` shifted left by `displacement`, then `lagging_span[current_idx]` is `closes[current_idx + displacement]`.
    # My python code for lagging_span: `lagging_span[i-displacement] = closes[i]`.
    # So, for current index `curr = num_data_points-1`, the relevant Chikou is `lagging_span[curr-displacement]`, which is `closes[curr]`.
    # This is not right. Chikou is `close` plotted `displacement` in the past.
    # So `lagging_span` series. `_get_latest(lagging_span)` is `close[latest_idx]` plotted at `latest_idx-displacement`.
    # We need to compare *this* `_get_latest(lagging_span)` with `price[latest_idx - displacement]`.
    
    # Let's simplify: `latest_chikou_val` is today's close. We are comparing it to cloud and price from `displacement` periods ago.
    # JS: `latestChikouSpan > closes[closes.length - 27]` (if displacement is 26). This means `close_today_plotted_26_days_ago > price_26_days_ago`.
    # My `lagging_span` has `lagging_span[i-displacement] = closes[i]`.
    # So `lagging_span` value at index `k` is `closes[k+displacement]`.
    # The `latest_chikou_span` is the value of Chikou on the chart for *today's position*.
    # This is `closes[today_idx - displacement]`.
    # The price it's compared to is `price_at_chikou_position` which is `closes[today_idx - displacement]`.
    # This logic needs care. Using the JS `latestChikouSpan` as a reference.
    # `latestChikouSpan = chikouSpan.length > 0 ? chikouSpan[chikouSpan.length - 1] : null;`
    # `chikouSpan` from JS is: `for (let i = 0; i < prices.length - displacement + 1; i++) { laggingSpan.push(prices[i].close); }`
    # This JS `chikouSpan` is a list of closes, from `close[0]` to `close[L-displacement]`. So `latestChikouSpan` is `close[L-displacement]`.
    # And `closes[closes.length - 27]` (for displacement=26) is `close[L - 1 - 26]`.
    # So it compares `close[L-displacement]` with `close[L-1-displacement]`. This is effectively `close_today_shifted_back` vs `close_yesterday_shifted_back`.

    # Python `lagging_span` created is `closes` shifted to the left.
    # `lagging_span[i] = closes[i+displacement]` where `i` goes up to `L-displacement-1`.
    # `_get_latest(lagging_span)` would be `closes[L-1]`. This is not what the JS decision logic seems to use.
    # Given my Python Ichimoku code: `lagging_span[i - displacement] = closes[i]`.
    # The `lagging_span` list has length `len(closes)`.
    # Its last non-None value is `lagging_span[len(closes)-1-displacement] = closes[len(closes)-1]`.
    # So `_get_latest(ichimoku_data.get("lagging_span",[]))` is `closes[latest_idx]`.
    # This is used for comparison.
    # The price it's compared against in JS is `closes[L-1-displacement]`.
    js_chikou_val_ref = _get_nth_latest(closes, ichimoku_data.get("displacement_val", 26)) if num_data_points > ichimoku_data.get("displacement_val", 26) else None

    latest_atr = _get_latest(atr_series)

    # --- Indicator Decisions ---
    indicator_decisions_map = {
        "RSI": "Neutral", "EMA": "Neutral", "SMA": "Neutral", "MACD": "Neutral",
        "ADX": "Neutral", "Supertrend": "Neutral", "BollingerBands": "Neutral",
        "VWAP": "Neutral", "WilliamsR": "Neutral", "PSAR": "Neutral",
        "Ichimoku": "Neutral", "ATR": "Neutral"
    }
    indicator_values_map = {k: None for k in indicator_decisions_map}


    if latest_price is None: # Cannot make decisions if no current price
        # Package results
        signals_list = []
        for name, decision in indicator_decisions_map.items():
            signals_list.append({"name": name, "value": indicator_values_map.get(name), "decision": decision})
        return {"signals": signals_list, "overallSignal": "Neutral"}

    # RSI
    indicator_values_map["RSI"] = latest_rsi
    if latest_rsi is not None:
        if latest_rsi < 20: indicator_decisions_map["RSI"] = "Strong Buy"
        elif latest_rsi < 30: indicator_decisions_map["RSI"] = "Buy"
        elif latest_rsi > 80: indicator_decisions_map["RSI"] = "Strong Sell"
        elif latest_rsi > 70: indicator_decisions_map["RSI"] = "Sell"

    # EMA
    indicator_values_map["EMA"] = latest_ema9
    if latest_ema9 is not None:
        if latest_price > latest_ema9 * 1.05: indicator_decisions_map["EMA"] = "Strong Buy"
        elif latest_price > latest_ema9: indicator_decisions_map["EMA"] = "Buy"
        elif latest_price < latest_ema9 * 0.95: indicator_decisions_map["EMA"] = "Strong Sell"
        elif latest_price < latest_ema9: indicator_decisions_map["EMA"] = "Sell"

    # SMA
    indicator_values_map["SMA"] = latest_sma20
    if latest_sma20 is not None:
        if latest_price > latest_sma20 * 1.05: indicator_decisions_map["SMA"] = "Strong Buy"
        elif latest_price > latest_sma20: indicator_decisions_map["SMA"] = "Buy"
        elif latest_price < latest_sma20 * 0.95: indicator_decisions_map["SMA"] = "Strong Sell"
        elif latest_price < latest_sma20: indicator_decisions_map["SMA"] = "Sell"
    
    # MACD
    indicator_values_map["MACD"] = latest_macd_line # Or a dict {"macd": val, "signal": val}
    if latest_macd_line is not None and latest_macd_signal is not None:
        macd_diff = latest_macd_line - latest_macd_signal
        if latest_macd_line > latest_macd_signal and latest_macd_line > 0 and macd_diff > abs(latest_macd_line) * 0.1:
            indicator_decisions_map["MACD"] = "Strong Buy"
        elif latest_macd_line > latest_macd_signal:
            indicator_decisions_map["MACD"] = "Buy"
        elif latest_macd_line < latest_macd_signal and latest_macd_line < 0 and abs(macd_diff) > abs(latest_macd_line) * 0.1:
            indicator_decisions_map["MACD"] = "Strong Sell"
        elif latest_macd_line < latest_macd_signal:
            indicator_decisions_map["MACD"] = "Sell"

    # ADX
    indicator_values_map["ADX"] = latest_adx_line
    if latest_adx_line is not None and latest_plus_di is not None and latest_minus_di is not None:
        if latest_adx_line > 40 and latest_plus_di > latest_minus_di: indicator_decisions_map["ADX"] = "Strong Buy"
        elif latest_adx_line > 25 and latest_plus_di > latest_minus_di: indicator_decisions_map["ADX"] = "Buy"
        elif latest_adx_line > 40 and latest_minus_di > latest_plus_di: indicator_decisions_map["ADX"] = "Strong Sell"
        elif latest_adx_line > 25 and latest_minus_di > latest_plus_di: indicator_decisions_map["ADX"] = "Sell"

    # Supertrend
    indicator_values_map["Supertrend"] = latest_supertrend_val
    if latest_supertrend_dir is not None and latest_supertrend_val is not None:
        if latest_supertrend_dir == 1 and latest_price > latest_supertrend_val:
            indicator_decisions_map["Supertrend"] = "Buy"
        elif latest_supertrend_dir == -1 and latest_price < latest_supertrend_val:
            indicator_decisions_map["Supertrend"] = "Sell"
    
    # Bollinger Bands
    indicator_values_map["BollingerBands"] = latest_bb_middle # Or a dict
    if latest_bb_upper is not None and latest_bb_lower is not None and latest_bb_middle is not None:
        if latest_price < latest_bb_lower: indicator_decisions_map["BollingerBands"] = "Strong Buy"
        elif latest_price > latest_bb_upper: indicator_decisions_map["BollingerBands"] = "Strong Sell"
        elif latest_price < latest_bb_middle: indicator_decisions_map["BollingerBands"] = "Sell"
        elif latest_price > latest_bb_middle: indicator_decisions_map["BollingerBands"] = "Buy"

    # VWAP
    indicator_values_map["VWAP"] = latest_vwap
    if latest_vwap is not None:
        if latest_price > latest_vwap * 1.03: indicator_decisions_map["VWAP"] = "Strong Buy"
        elif latest_price > latest_vwap: indicator_decisions_map["VWAP"] = "Buy"
        elif latest_price < latest_vwap * 0.97: indicator_decisions_map["VWAP"] = "Strong Sell"
        elif latest_price < latest_vwap: indicator_decisions_map["VWAP"] = "Sell"
    
    # Williams %R
    indicator_values_map["WilliamsR"] = latest_williams_r
    if latest_williams_r is not None:
        if latest_williams_r > -20: indicator_decisions_map["WilliamsR"] = "Strong Sell" # Overbought
        elif latest_williams_r > -30: indicator_decisions_map["WilliamsR"] = "Sell"
        elif latest_williams_r < -80: indicator_decisions_map["WilliamsR"] = "Strong Buy" # Oversold
        elif latest_williams_r < -70: indicator_decisions_map["WilliamsR"] = "Buy"

    # Parabolic SAR
    indicator_values_map["PSAR"] = latest_psar
    if latest_psar is not None and prev_close is not None: # Needs prev_close for trend context
        if latest_price > latest_psar and latest_psar < prev_close : # PSAR flipped below price
             indicator_decisions_map["PSAR"] = "Buy"
        elif latest_price < latest_psar and latest_psar > prev_close: # PSAR flipped above price
             indicator_decisions_map["PSAR"] = "Sell"
    
    # Ichimoku Cloud
    indicator_values_map["Ichimoku"] = None # It's a composite
    if latest_senkou_a is not None and latest_senkou_b is not None and \
       latest_tenkan_sen is not None and latest_kijun_sen is not None and \
       js_chikou_val_ref is not None and _get_latest(ichimoku_data.get("lagging_span",[])) is not None: # _get_latest(lagging_span) is approx. current close for this logic context
        
        cloud_top = max(latest_senkou_a, latest_senkou_b)
        cloud_bottom = min(latest_senkou_a, latest_senkou_b)
        
        # JS compared `latestChikouSpan` (close[L-displacement]) with `closes[L-1-displacement]`
        # Python: `js_chikou_val_ref` (close[L-1-displacement])
        # `latest_chikou_span_from_series = _get_latest(ichimoku_data.get("lagging_span",[]))` (this is current close `C[L-1]`)
        # The Ichimoku decision logic regarding Chikou Span in JS seems to compare C[t-displacement] with C[t-displacement-1].
        # Standard Chikou is: C[t] plotted at t-displacement, compared with Price[t-displacement].
        # Using the JS direct logic: chikou_cond_buy = _get_latest(lagging_span) > js_chikou_val_ref
        # chikou_cond_sell = _get_latest(lagging_span) < js_chikou_val_ref
        # Let's assume `_get_latest(ichimoku_data.get("lagging_span",[]))` refers to the value of chikou span plotted at current time's past.
        # This is `closes[current_idx - displacement]`.
        # And `js_chikou_val_ref` is `closes[current_idx - displacement -1]`.
        # So the condition means: is `close[today-disp]` > `close[yesterday-disp]`? (a momentum check on past price)
        # This is what the JS logic implies for its `latestChikouSpan` vs `closes[L-27]`.

        chikou_proxy_val = _get_nth_latest(closes, ichimoku_data.get("displacement_val", 26)) # Close from `displacement` days ago
        
        if chikou_proxy_val is not None and js_chikou_val_ref is not None: # js_chikou_val_ref is close from `displacement+1` days ago
            chikou_bullish_confirmation = chikou_proxy_val > js_chikou_val_ref
            chikou_bearish_confirmation = chikou_proxy_val < js_chikou_val_ref
            
            if latest_price > cloud_top and latest_tenkan_sen > latest_kijun_sen and chikou_bullish_confirmation:
                indicator_decisions_map["Ichimoku"] = "Strong Buy"
            elif latest_price > cloud_top and latest_tenkan_sen > latest_kijun_sen:
                indicator_decisions_map["Ichimoku"] = "Buy"
            elif latest_price < cloud_bottom and latest_tenkan_sen < latest_kijun_sen and chikou_bearish_confirmation:
                indicator_decisions_map["Ichimoku"] = "Strong Sell"
            elif latest_price < cloud_bottom and latest_tenkan_sen < latest_kijun_sen:
                indicator_decisions_map["Ichimoku"] = "Sell"
    
    # ATR
    indicator_values_map["ATR"] = latest_atr
    if latest_atr is not None and latest_ema9 is not None: # Depends on EMA9
        if latest_atr < latest_price * 0.01: # Low volatility relative to price
            indicator_decisions_map["ATR"] = "Neutral"
        elif latest_price > latest_ema9 and latest_atr > latest_price * 0.02: # Uptrend context, high vol
            indicator_decisions_map["ATR"] = "Buy"
        elif latest_price < latest_ema9 and latest_atr > latest_price * 0.02: # Downtrend context, high vol
            indicator_decisions_map["ATR"] = "Sell"

    # --- Overall Decision ---
    decision_scores = {"Strong Buy": 2, "Buy": 1, "Neutral": 0, "Sell": -1, "Strong Sell": -2}
    weights = {
        "RSI": 1.0, "EMA": 1.5, "SMA": 1.5, "MACD": 1.0, "ADX": 1.0, "Supertrend": 1.5,
        "BollingerBands": 1.0, "VWAP": 1.0, "WilliamsR": 1.0, "PSAR": 1.0, "Ichimoku": 1.5, "ATR": 1.0
    }
    
    selected_indicators = list(weights.keys()) # Assume all are selected by default
    
    total_score = 0.0
    total_weight = 0.0

    for indicator_name in selected_indicators:
        decision = indicator_decisions_map.get(indicator_name, "Neutral")
        score = decision_scores.get(decision, 0)
        weight = weights.get(indicator_name, 0)
        
        total_score += score * weight
        total_weight += weight # Sum of weights of indicators that gave a non-neutral signal or all selected indicators
                               # JS logic implies sum over all *selected* indicators, not just non-neutral ones.

    # Normalize score? The JS logic doesn't explicitly normalize by total_weight.
    # The thresholds (1.5, 0.5, -0.5, -1.5) are absolute.
    # Max possible score if all are Strong Buy: 2 * sum(weights)
    # sum(weights) = 1 + 1.5*3 + 1*7 = 1 + 4.5 + 7 = 12.5. Max score = 25. Min score = -25.

    overall_signal = "Neutral"
    if not selected_indicators: # Should not happen with default
        overall_signal = "Neutral"
    elif total_score >= 1.5 * (total_weight / sum(weights.values()) if total_weight > 0 else 1) : # Threshold adjusted by proportion of active weights. Or use fixed threshold.
                                                                     # The JS code uses fixed thresholds.
        if total_score >= 3.0 : overall_signal = "Strong Buy" # Adjusted thresholds slightly higher for weighted sum
        elif total_score >= 1.0 : overall_signal = "Buy"
        elif total_score <= -3.0 : overall_signal = "Strong Sell"
        elif total_score <= -1.0 : overall_signal = "Sell"
    # Using JS direct thresholds:
    if total_score >= 1.5 : overall_signal = "Strong Buy"
    elif total_score >= 0.5 : overall_signal = "Buy"
    elif total_score <= -1.5 : overall_signal = "Strong Sell"
    elif total_score <= -0.5 : overall_signal = "Sell"


    # Package results
    signals_list = []
    for name, decision in indicator_decisions_map.items():
        signals_list.append({"name": name, "value": indicator_values_map.get(name), "decision": decision})
        
    return {"signals": signals_list, "overallSignal": overall_signal, "raw_score_debug": total_score}

# Add ichimoku_data.get("displacement_val", 26) to ichimoku_data dict if needed
# In calculate_ichimoku_cloud, add: "displacement_val": displacement to the returned dict