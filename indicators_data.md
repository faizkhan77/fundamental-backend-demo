---

## **Indicator: Relative Strength Index (RSI)**

1.  **Description:**
    A momentum oscillator that measures the speed and change of price movements. RSI oscillates between 0 and 100. Traditionally, RSI is considered overbought when above 70 and oversold when below 30.

2.  **Data Needed & Source:**

    - `Closing Prices`: Series of closing prices from `BSEAdjustedPrice.close` (e.g., for the last N periods, typically 14).

3.  **Purpose of Data in Calculation:**

    - `Closing Prices`: Used to calculate price changes (gains and losses) from one period to the next.

4.  **Helper Calculations / Prerequisites:**

    - **Price Changes (Deltas):**
      - Why Needed: To identify upward (gains) and downward (losses) price movements.
      - Data for Helper: Current close and previous close.
    - **Average Gain / Average Loss (Smoothed):**
      - Why Needed: To calculate a smoothed average of gains and losses over the RSI period using a method similar to Wilder's Smoothing (RMA).
      - Data for Helper: Series of individual gains and losses.

5.  **Calculation Overview:**

    - Step 1: Calculate period-to-period price changes (close\[i] - close\[i-1]).
    - Step 2: Separate these changes into positive values (gains) and absolute negative values (losses).
    - Step 3: Calculate the initial average gain and average loss over the specified period (e.g., 14 days).
    - Step 4: For subsequent periods, calculate the smoothed average gain and average loss (e.g., `AvgGain = ((PrevAvgGain * (Period-1)) + CurrentGain) / Period`).
    - Step 5: Calculate Relative Strength (RS) = Average Gain / Average Loss.
    - Step 6: Calculate RSI = 100 - (100 / (1 + RS)). If Average Loss is 0, RSI is 100.

6.  **Action Decision Implication (General):**
    - **Buy Signal:** RSI crosses above the oversold level (e.g., 30 from below), or bullish divergence (price makes lower low, RSI makes higher low).
    - **Sell Signal:** RSI crosses below the overbought level (e.g., 70 from above), or bearish divergence (price makes higher high, RSI makes lower high).
    - **Hold/Neutral:** RSI is between oversold and overbought levels, or awaiting confirmation from divergences.

---

## **Indicator: Moving Average Convergence Divergence (MACD)**

1.  **Description:**
    A trend-following momentum indicator that shows the relationship between two Exponential Moving Averages (EMAs) of a security's price. The MACD line is the difference between these two EMAs. A signal line (an EMA of the MACD line) is then plotted to help generate buy/sell signals.

2.  **Data Needed & Source:**

    - `Closing Prices`: Series of closing prices from `BSEAdjustedPrice.close` (e.g., for at least `slow_length + signal_length` periods).

3.  **Purpose of Data in Calculation:**

    - `Closing Prices`: Used as the input for calculating the EMAs (or SMAs if configured).

4.  **Helper Calculations / Prerequisites:**

    - **Fast Exponential Moving Average (EMA):** (e.g., 12-period EMA)
      - Why Needed: To represent the shorter-term price trend.
      - Data for Helper: Closing prices.
    - **Slow Exponential Moving Average (EMA):** (e.g., 26-period EMA)
      - Why Needed: To represent the longer-term price trend.
      - Data for Helper: Closing prices.
    - **Signal Line (EMA of MACD Line):** (e.g., 9-period EMA of the MACD line)
      - Why Needed: Acts as a trigger for buy/sell signals based on its crossovers with the MACD line.
      - Data for Helper: The calculated MACD line values.

5.  **Calculation Overview:**

    - Step 1: Calculate the Fast EMA (e.g., 12-period) of closing prices.
    - Step 2: Calculate the Slow EMA (e.g., 26-period) of closing prices.
    - Step 3: Calculate the MACD Line = Fast EMA - Slow EMA.
    - Step 4: Calculate the Signal Line = EMA (e.g., 9-period) of the MACD Line.
    - Step 5: (Optional) Calculate the MACD Histogram = MACD Line - Signal Line.

6.  **Action Decision Implication (General):**
    - **Buy Signal:** MACD line crosses above the Signal line (bullish crossover). MACD line crosses above the zero line. Bullish divergence.
    - **Sell Signal:** MACD line crosses below the Signal line (bearish crossover). MACD line crosses below the zero line. Bearish divergence.
    - **Hold/Neutral:** MACD line is close to the signal line or zero line without clear crossovers, or awaiting confirmation.

---

## **Indicator: Average True Range (ATR)**

1.  **Description:**
    A technical analysis volatility indicator. It does not indicate price direction, but rather the degree of price volatility.

2.  **Data Needed & Source:**

    - `High Prices`: Series of high prices from `BSEAdjustedPrice.high`.
    - `Low Prices`: Series of low prices from `BSEAdjustedPrice.low`.
    - `Closing Prices`: Series of closing prices from `BSEAdjustedPrice.close` (specifically the previous period's close).

3.  **Purpose of Data in Calculation:**

    - `High Prices`, `Low Prices`, `Previous Closing Prices`: Used to calculate the "True Range" for each period.

4.  **Helper Calculations / Prerequisites:**

    - **True Range (TR):**
      - Why Needed: It's the fundamental building block of ATR, representing the maximum of:
        1.  Current High - Current Low
        2.  Absolute value of (Current High - Previous Close)
        3.  Absolute value of (Current Low - Previous Close)
      - Data for Helper: Current High, Current Low, Previous Close.
    - **Smoothed Average of TR (RMA or SMA):**
      - Why Needed: To average the True Range values over a specified period (typically 14) to get the ATR.
      - Data for Helper: Series of True Range values.

5.  **Calculation Overview:**

    - Step 1: For each period, calculate the True Range (TR).
    - Step 2: Calculate the Average True Range (ATR) by taking a smoothed moving average (typically an RMA or an SMA for the first value) of the TR values over a specified period (e.g., 14 days).

6.  **Action Decision Implication (General):**
    - ATR itself doesn't give direct buy/sell signals.
    - **Usage:** Used to set stop-loss levels (e.g., price - N \* ATR for long positions), gauge breakout strength (high ATR during breakout can confirm), or identify low volatility periods (low ATR) that might precede a significant move.
    - In your decision logic, it's used with EMA: "Buy" if price > EMA and ATR > price \* 0.02 (high volatility in uptrend context).

---

## **Indicator: Average Directional Index (ADX)**

1.  **Description:**
    A trend strength indicator, not trend direction. It quantifies the strength of a trend, whether up or down. Values range from 0 to 100. A high ADX (e.g., above 25) suggests a strong trend, while a low ADX (e.g., below 20) suggests a weak or non-trending market.

2.  **Data Needed & Source:**

    - `High Prices`: Series from `BSEAdjustedPrice.high`.
    - `Low Prices`: Series from `BSEAdjustedPrice.low`.
    - `Closing Prices`: Series from `BSEAdjustedPrice.close` (used for ATR calculation within ADX).

3.  **Purpose of Data in Calculation:**

    - `High Prices`, `Low Prices`: Used to calculate Directional Movement (+DM and -DM).
    - `High Prices`, `Low Prices`, `Closing Prices`: Used to calculate True Range (TR), which is then used for ATR, a component of ADX calculation.

4.  **Helper Calculations / Prerequisites:**

    - **True Range (TR) and Average True Range (ATR):**
      - Why Needed: ATR is used to normalize the +DM and -DM values, making them comparable across different securities and timeframes.
      - Data for Helper: High, Low, Close.
    - **Directional Movement (+DM, -DM):**
      - Why Needed: To measure the upward and downward price movement.
        - `+DM = Current High - Previous High` (if > `Previous Low - Current Low` and > 0, else 0)
        - `-DM = Previous Low - Current Low` (if > `Current High - Previous High` and > 0, else 0)
      - Data for Helper: Current High, Current Low, Previous High, Previous Low.
    - **Smoothed +DM, Smoothed -DM, Smoothed TR (or ATR):**
      - Why Needed: To get averaged values for calculating +DI and -DI.
      - Data for Helper: Series of +DM, -DM, TR values.
    - **Positive Directional Indicator (+DI):** `(Smoothed +DM / ATR) * 100`
    - **Negative Directional Indicator (-DI):** `(Smoothed -DM / ATR) * 100`
    - **Directional Index (DX):** `(ABS(+DI - -DI) / (+DI + -DI)) * 100`

5.  **Calculation Overview:**

    - Step 1: Calculate +DM, -DM, and TR for each period.
    - Step 2: Smooth these values over a specified period (e.g., 14 days) using RMA or similar. This gives Smoothed +DM, Smoothed -DM, and ATR (Smoothed TR).
    - Step 3: Calculate +DI and -DI.
    - Step 4: Calculate the Directional Index (DX).
    - Step 5: Calculate the ADX by taking a smoothed moving average (RMA) of the DX values over a specified period (e.g., 14 days).

6.  **Action Decision Implication (General):**
    - **Buy Signal:** When ADX is rising (e.g., > 25) AND +DI is above -DI. Stronger signal if ADX > 40.
    - **Sell Signal:** When ADX is rising (e.g., > 25) AND -DI is above +DI. Stronger signal if ADX > 40.
    - **Hold/Neutral:** ADX is low (e.g., < 20 or < 25), indicating a weak or ranging market. Avoid trend-following strategies.

---

## **Indicator: SuperTrend**

1.  **Description:**
    A trend-following indicator plotted on price. It indicates the current trend direction (uptrend or downtrend) and can be used for setting stop-loss levels or identifying entry/exit points.

2.  **Data Needed & Source:**

    - `High Prices`: Series from `BSEAdjustedPrice.high`.
    - `Low Prices`: Series from `BSEAdjustedPrice.low`.
    - `Closing Prices`: Series from `BSEAdjustedPrice.close`.

3.  **Purpose of Data in Calculation:**

    - `High Prices`, `Low Prices`: Used in the calculation of the basic upper and lower bands around a midpoint.
    - `Closing Prices`: Used to determine if the trend has reversed by comparing the close price to the SuperTrend line.
    - All three (H, L, C) are also needed for the prerequisite ATR calculation.

4.  **Helper Calculations / Prerequisites:**

    - **Average True Range (ATR):**
      - Why Needed: ATR is used as the volatility component to set the distance of the SuperTrend bands from the price.
      - Data for Helper: High, Low, Close.
    - **Basic Upper Band:** `((High + Low) / 2) + (Multiplier * ATR)`
    - **Basic Lower Band:** `((High + Low) / 2) - (Multiplier * ATR)`

5.  **Calculation Overview:**

    - Step 1: Calculate ATR over a specified period (e.g., 10).
    - Step 2: Calculate the Basic Upper Band and Basic Lower Band.
    - Step 3: Initialize the SuperTrend line.
    - Step 4: For subsequent periods:
      - If the previous closing price was above the previous SuperTrend line (uptrend):
        The current SuperTrend line is the maximum of the current Basic Lower Band and the previous SuperTrend value (or a variation like `min(BasicLowerBand, PrevSuperTrend)` as per your JS).
      - If the previous closing price was below the previous SuperTrend line (downtrend):
        The current SuperTrend line is the minimum of the current Basic Upper Band and the previous SuperTrend value (or a variation like `max(BasicUpperBand, PrevSuperTrend)` as per your JS).
      - If the current closing price crosses the newly calculated SuperTrend line, the trend "flips."

6.  **Action Decision Implication (General):**
    - **Buy Signal:** Price closes above the SuperTrend line (line flips from above price to below price). Or, maintain long if price stays above the SuperTrend line.
    - **Sell Signal:** Price closes below the SuperTrend line (line flips from below price to above price). Or, maintain short if price stays below the SuperTrend line.
    - The `direction` variable (1 for up, -1 for down) in your code explicitly tracks this.

---

## **Indicator: Ichimoku Cloud (Ichimoku Kinko Hyo)**

1.  **Description:**
    A comprehensive, versatile indicator that defines support and resistance, identifies trend direction, gauges momentum, and provides trading signals. It consists of five lines and a "cloud" (Kumo).

2.  **Data Needed & Source:**

    - `High Prices`: Series from `BSEAdjustedPrice.high`.
    - `Low Prices`: Series from `BSEAdjustedPrice.low`.
    - `Closing Prices`: Series from `BSEAdjustedPrice.close` (for Chikou Span).

3.  **Purpose of Data in Calculation:**

    - `High Prices`, `Low Prices`: Used to calculate the midpoints for Tenkan-sen, Kijun-sen, and Senkou Span B.
    - `Closing Prices`: Used for the Chikou Span.

4.  **Helper Calculations / Prerequisites:**

    - **Donchian Channel Midpoint (Helper):** This is what your `_calculate_donchian_channel_ichimoku_helper` does.
      - Why Needed: To find the midpoint of the highest high and lowest low over a specific period. This is the core of Tenkan-sen, Kijun-sen, and Senkou Span B.
      - Data for Helper: High and Low prices for the specified period.
    - **Tenkan-sen (Conversion Line):** Midpoint of (highest high + lowest low) / 2 over a short period (e.g., 9 periods).
    - **Kijun-sen (Base Line):** Midpoint of (highest high + lowest low) / 2 over a medium period (e.g., 26 periods).
    - **Senkou Span A (Leading Span A):** ((Tenkan-sen + Kijun-sen) / 2), plotted `displacement` periods (e.g., 26) ahead.
    - **Senkou Span B (Leading Span B):** Midpoint of (highest high + lowest low) / 2 over a long period (e.g., 52 periods), plotted `displacement` periods (e.g., 26) ahead.
    - **Chikou Span (Lagging Span):** Current closing price plotted `displacement` periods (e.g., 26) in the past.
    - **Kumo (Cloud):** The area between Senkou Span A and Senkou Span B.

5.  **Calculation Overview:**

    - Step 1: Calculate Tenkan-sen.
    - Step 2: Calculate Kijun-sen.
    - Step 3: Calculate Senkou Span A using Tenkan-sen and Kijun-sen, then shift it forward.
    - Step 4: Calculate Senkou Span B using H/L over its period, then shift it forward.
    - Step 5: Calculate Chikou Span by shifting current closing prices backward.

6.  **Action Decision Implication (General):**
    - **Strong Buy Signal (Example):** Price above Kumo, Tenkan-sen crosses Kijun-sen upwards (while both are above Kumo), Chikou Span above price action from `displacement` periods ago, and Kumo is bullish (Senkou A > Senkou B and ideally rising).
    - **Strong Sell Signal (Example):** Price below Kumo, Tenkan-sen crosses Kijun-sen downwards (while both are below Kumo), Chikou Span below price action from `displacement` periods ago, and Kumo is bearish (Senkou A < Senkou B and ideally falling).
    - Kumo acts as dynamic support/resistance. Trend direction is often inferred by price position relative to the Kumo.

---

## **Indicator: Parabolic SAR (Stop and Reverse)**

1.  **Description:**
    A trend-following indicator used to determine potential stop-loss levels and trend direction. SAR points are plotted on the chart, appearing below price during an uptrend and above price during a downtrend.

2.  **Data Needed & Source:**

    - `High Prices`: Series from `BSEAdjustedPrice.high`.
    - `Low Prices`: Series from `BSEAdjustedPrice.low`.

3.  **Purpose of Data in Calculation:**

    - `High Prices`, `Low Prices`: Used to determine the "Extreme Point (EP)" in the current trend and to check if the SAR has been hit, triggering a potential reversal.

4.  **Helper Calculations / Prerequisites:**

    - **Extreme Point (EP):** The highest high in an uptrend or the lowest low in a downtrend encountered so far in the current trend segment.
    - **Acceleration Factor (AF):** A factor that increases with each new EP, causing the SAR to accelerate towards the price. Starts at `start_af` (e.g., 0.02) and increases by `increment_af` (e.g., 0.02) up to `max_af` (e.g., 0.20).

5.  **Calculation Overview:**

    - Step 1: Initialize SAR, EP, AF, and trend direction (e.g., assume uptrend, SAR = initial low, EP = initial low).
    - Step 2: For each subsequent period:
      - If in an uptrend: Calculate SAR for today: `SAR_today = SAR_yesterday + AF_yesterday * (EP_yesterday - SAR_yesterday)`.
        - If `SAR_today` is above the current low, the trend reverses to downtrend. SAR for today is set to the previous EP. EP is reset to current low. AF resets.
        - Else (uptrend continues): If current high > previous EP, update EP to current high and increment AF (up to max_af). Ensure `SAR_today` is not above previous low or current low.
      - If in a downtrend: Calculate SAR for today using similar logic but inverted for lows/highs.

6.  **Action Decision Implication (General):**
    - **Buy Signal:** When SAR dots move from above the price to below the price, indicating a potential shift to an uptrend.
    - **Sell Signal:** When SAR dots move from below the price to above the price, indicating a potential shift to a downtrend.
    - Often used as a trailing stop-loss.

---

## **Indicator: Williams %R (Percent Range)**

1.  **Description:**
    A momentum oscillator that measures overbought and oversold levels. It's similar to the Stochastic Oscillator but is plotted on an inverted scale (-100 to 0). Readings from 0 to -20 are considered overbought, and readings from -80 to -100 are considered oversold.

2.  **Data Needed & Source:**

    - `High Prices`: Series from `BSEAdjustedPrice.high` over the lookback period (e.g., 14 days).
    - `Low Prices`: Series from `BSEAdjustedPrice.low` over the lookback period.
    - `Closing Prices`: The most recent closing price from `BSEAdjustedPrice.close`.

3.  **Purpose of Data in Calculation:**

    - `High Prices` (lookback period): To find the highest high in the period.
    - `Low Prices` (lookback period): To find the lowest low in the period.
    - `Closing Price` (current): To determine its position relative to the period's range.

4.  **Helper Calculations / Prerequisites:**

    - **Highest High (HH) over N periods.**
    - **Lowest Low (LL) over N periods.**

5.  **Calculation Overview:**

    - Step 1: For the lookback period (e.g., 14 days), find the Highest High (HH) and Lowest Low (LL).
    - Step 2: Calculate Williams %R = `((HH - Current Close) / (HH - LL)) * -100`.
    - (If HH equals LL, typically set to 0 or -50 to avoid division by zero).

6.  **Action Decision Implication (General):**
    - **Buy Signal:** Indicator moves out of the oversold zone (e.g., crosses above -80). Bullish divergence.
    - **Sell Signal:** Indicator moves out of the overbought zone (e.g., crosses below -20). Bearish divergence.

---

## **Indicator: Volume Weighted Average Price (VWAP)**

1.  **Description:**
    The average price a security has traded at throughout the period (typically a single day for intraday VWAP, or cumulative as in your implementation), weighted by volume at each price level. It's often used as a benchmark by institutional traders.

2.  **Data Needed & Source:**

    - `High Prices`: Series from `BSEAdjustedPrice.high`.
    - `Low Prices`: Series from `BSEAdjustedPrice.low`.
    - `Closing Prices`: Series from `BSEAdjustedPrice.close`.
    - `Volumes`: Series of trading volumes from `BSEAdjustedPrice.volume`.

3.  **Purpose of Data in Calculation:**

    - `High, Low, Close`: Used to calculate the Typical Price for each period: `(High + Low + Close) / 3`.
    - `Typical Price` and `Volume`: Multiplied together (`Typical Price * Volume`) for each period.

4.  **Helper Calculations / Prerequisites:**

    - **Typical Price:** `(High + Low + Close) / 3` for each bar.

5.  **Calculation Overview (Cumulative as per your code):**

    - Step 1: For each period, calculate Typical Price.
    - Step 2: Multiply Typical Price by Volume for that period.
    - Step 3: Sum these `(Typical Price * Volume)` values cumulatively.
    - Step 4: Sum the Volume values cumulatively.
    - Step 5: VWAP = Cumulative `(Typical Price * Volume)` / Cumulative Volume.
    - (For daily VWAP, these sums reset at the start of each new trading day).

6.  **Action Decision Implication (General):**
    - **Buy Signal (Intraday/Short-term):** Price crosses above VWAP, indicating potential bullish momentum, or price pulls back to and finds support at VWAP in an uptrend.
    - **Sell Signal (Intraday/Short-term):** Price crosses below VWAP, indicating potential bearish momentum, or price rallies to and finds resistance at VWAP in a downtrend.
    - Prices far above VWAP might be considered overextended short-term; prices far below might be considered oversold short-term.

---

## **Indicator: Bollinger Bands**

1.  **Description:**
    Volatility bands placed above and below a moving average. Volatility is based on the standard deviation of prices from the moving average. Bands widen when volatility increases and narrow when volatility decreases.

2.  **Data Needed & Source:**

    - `Closing Prices`: Series from `BSEAdjustedPrice.close`.

3.  **Purpose of Data in Calculation:**

    - `Closing Prices`: Used to calculate the central moving average and the standard deviation.

4.  **Helper Calculations / Prerequisites:**

    - **Middle Band (Moving Average):** Typically a Simple Moving Average (SMA) over N periods (e.g., 20-day SMA) of closing prices.
    - **Standard Deviation:** Calculated over the same N periods using closing prices around their N-period SMA.

5.  **Calculation Overview:**

    - Step 1: Calculate the Middle Band (e.g., 20-period SMA of closing prices).
    - Step 2: Calculate the Standard Deviation (StdDev) of closing prices over the same N periods.
    - Step 3: Upper Band = Middle Band + (Multiplier \* StdDev) (Multiplier is typically 2).
    - Step 4: Lower Band = Middle Band - (Multiplier \* StdDev).

6.  **Action Decision Implication (General):**
    - **Buy Signal:** Price touches or breaks below the Lower Band and then closes back inside (potential oversold bounce, often confirmed with other indicators). Price "walks up" the Upper Band in a strong uptrend. Breakout above Upper Band after a "squeeze" (narrow bands).
    - **Sell Signal:** Price touches or breaks above the Upper Band and then closes back inside (potential overbought reversal). Price "walks down" the Lower Band in a strong downtrend. Breakout below Lower Band after a "squeeze."
    - Your logic uses `price < LowerBand` as Strong Buy, `price > UpperBand` as Strong Sell, and relative to middle band for Buy/Sell.

---

## **Indicator: Dual Moving Average Crossover**

1.  **Description:**
    A classic trend-following strategy that uses two moving averages (one short-term, one long-term) to generate buy and sell signals when they cross.

2.  **Data Needed & Source:**

    - `Closing Prices`: Series from `BSEAdjustedPrice.close` (for a period sufficient to calculate the longer MA).

3.  **Purpose of Data in Calculation:**

    - `Closing Prices`: Used as input for both the short-term and long-term moving averages.

4.  **Helper Calculations / Prerequisites:**

    - **Short-Term Moving Average (SMA or EMA):** e.g., 20-period MA.
      - Why Needed: Represents recent price trend.
      - Data for Helper: Closing prices.
    - **Long-Term Moving Average (SMA or EMA):** e.g., 50-period MA.
      - Why Needed: Represents longer-term price trend.
      - Data for Helper: Closing prices.

5.  **Calculation Overview:**

    - Step 1: Calculate the Short-Term MA.
    - Step 2: Calculate the Long-Term MA.
    - Step 3: Monitor for crossovers between the two MAs.

6.  **Action Decision Implication (General):**
    - **Buy Signal ("Golden Cross"):** Short-Term MA crosses above the Long-Term MA.
    - **Sell Signal ("Death Cross"):** Short-Term MA crosses below the Long-Term MA.
    - **Hold/Neutral:** MAs are intertwined or moving parallel without a clear cross. Often confirmed by price action relative to the MAs (e.g., price above both MAs for stronger buy).

---

## **Indicator: RSI Failure-Swing Reversal**

1.  **Description:**
    A pattern in the RSI indicator that can signal a potential price reversal, considered more reliable than just overbought/oversold crossovers.

    - **Top Failure Swing (Bearish):** RSI moves into overbought (>70), pulls back, fails to make a new high on a subsequent rally (while price might make a new high - bearish divergence), and then breaks below its previous reaction low within the RSI.
    - **Bottom Failure Swing (Bullish):** RSI moves into oversold (<30), rallies, fails to make a new low on a subsequent decline (while price might make a new low - bullish divergence), and then breaks above its previous reaction high within the RSI.

2.  **Data Needed & Source:**

    - `Closing Prices`: Series from `BSEAdjustedPrice.close` (to calculate RSI).

3.  **Purpose of Data in Calculation:**

    - `Closing Prices`: Input for the RSI calculation.

4.  **Helper Calculations / Prerequisites:**

    - **Relative Strength Index (RSI):** (As detailed previously).
      - Why Needed: The failure swing pattern occurs on the RSI chart itself.
      - Data for Helper: Closing prices.

5.  **Calculation Overview:**

    - Step 1: Calculate RSI (e.g., 14-period).
    - Step 2: Identify overbought/oversold conditions.
    - Step 3: **For Top Failure Swing (Bearish):**
      - a. RSI peaks above 70.
      - b. RSI pulls back below 70, forming a trough (RSI_low1).
      - c. RSI rallies again but fails to exceed its previous peak (RSI_peak2 < RSI_peak1), even if price makes a new high.
      - d. RSI then declines and breaks below RSI_low1. This break is the confirmation.
    - Step 4: **For Bottom Failure Swing (Bullish):**
      - a. RSI troughs below 30.
      - b. RSI rallies above 30, forming a peak (RSI_high1).
      - c. RSI declines again but fails to break its previous trough (RSI_low2 > RSI_low1), even if price makes a new low.
      - d. RSI then rallies and breaks above RSI_high1. This break is the confirmation.

6.  **Action Decision Implication (General):**
    - **Buy Signal:** Confirmation of a Bottom Failure Swing (RSI breaks above its prior minor peak after failing to make a new low in oversold territory).
    - **Sell Signal:** Confirmation of a Top Failure Swing (RSI breaks below its prior minor trough after failing to make a new high in overbought territory).
    - These are often considered stronger signals than simple overbought/oversold exits.

---

## **Indicator: MACD Signal-Line Cross**

1.  **Description:**
    This is the primary trading signal generated by the MACD indicator, as detailed in the MACD section above. It occurs when the MACD line crosses above or below its signal line.

2.  **Data Needed & Source:** (Same as MACD)

    - `Closing Prices`: Series from `BSEAdjustedPrice.close`.

3.  **Purpose of Data in Calculation:** (Same as MACD)

    - `Closing Prices`: Input for EMAs that form the MACD and signal lines.

4.  **Helper Calculations / Prerequisites:** (Same as MACD)

    - Fast EMA, Slow EMA, MACD Line, Signal Line.

5.  **Calculation Overview:** (Same as MACD)

    - Calculate MACD line and Signal line. Monitor for crossovers.

6.  **Action Decision Implication (General):**
    - **Buy Signal:** MACD Line crosses above the Signal Line. Stronger if this occurs below the zero line and MACD then crosses above zero.
    - **Sell Signal:** MACD Line crosses below the Signal Line. Stronger if this occurs above the zero line and MACD then crosses below zero.

---

## **Indicator: Bollinger Band Squeeze Breakout**

1.  **Description:**
    A period of low volatility where the Bollinger Bands narrow significantly (a "squeeze"). This often precedes a period of high volatility and a significant price move. A "breakout" occurs when the price breaks out of these narrowed bands.

2.  **Data Needed & Source:** (Same as Bollinger Bands)

    - `Closing Prices`: Series from `BSEAdjustedPrice.close`.
    - (Optionally `High` and `Low` prices if the breakout is defined by candle body or full range rather than just close).

3.  **Purpose of Data in Calculation:**

    - `Closing Prices`: For calculating the Middle Band (SMA) and Standard Deviation, which define the Upper and Lower Bands.

4.  **Helper Calculations / Prerequisites:**

    - **Bollinger Bands (Upper, Middle, Lower):** (As detailed previously).
      - Why Needed: The squeeze is identified by the distance between the Upper and Lower bands.
      - Data for Helper: Closing prices.
    - **Bandwidth (Optional Metric):** `(Upper Band - Lower Band) / Middle Band`. A very low Bandwidth value indicates a squeeze. Or simply monitor the raw distance `Upper Band - Lower Band`.

5.  **Calculation Overview:**

    - Step 1: Calculate Bollinger Bands.
    - Step 2: Identify a "squeeze": The bands come unusually close together. This can be quantified by Bandwidth reaching a historical low or by comparing the current band distance to its own moving average.
    - Step 3: Monitor for a price "breakout": The price closes decisively outside either the Upper or Lower Band after a squeeze.

6.  **Action Decision Implication (General):**
    - **Buy Signal:** Price closes above the Upper Bollinger Band following a squeeze. Often confirmed by increased volume.
    - **Sell Signal:** Price closes below the Lower Bollinger Band following a squeeze. Often confirmed by increased volume.
    - The direction of the breakout indicates the likely direction of the subsequent high-volatility move.

---

## **Indicator: Fibonacci Retracement Bounce**

1.  **Description:**
    Fibonacci retracement levels are horizontal lines that indicate potential support or resistance levels where price might reverse or stall. A "bounce" refers to the price pulling back to one of these levels during a trend and then resuming the original trend direction. Key retracement levels are 23.6%, 38.2%, 50%, 61.8%, and 78.6%.

2.  **Data Needed & Source:**

    - `High Prices`: To identify significant swing highs from `BSEAdjustedPrice.high`.
    - `Low Prices`: To identify significant swing lows from `BSEAdjustedPrice.low`.
    - `Closing Prices`: Often used to confirm bounces or breaks from `BSEAdjustedPrice.close`.

3.  **Purpose of Data in Calculation:**

    - `Swing High and Swing Low`: These define the price range (Trend Move = Swing High - Swing Low, or vice-versa) over which the Fibonacci ratios are applied.

4.  **Helper Calculations / Prerequisites:**

    - **Identification of a Significant Prior Trend:** Requires identifying a clear recent uptrend or downtrend.
    - **Identification of a Swing High and Swing Low:** These are the start and end points of the identified trend move. This can be done manually or algorithmically (e.g., using Zig Zag indicator logic or simple N-period highest/lowest points).
    - **Calculation of Fibonacci Levels:**
      - For an uptrend (price moved from Swing Low to Swing High):
        - Level = Swing High - ((Swing High - Swing Low) \* Fibonacci Ratio)
      - For a downtrend (price moved from Swing High to Swing Low):
        - Level = Swing Low + ((Swing High - Swing Low) \* Fibonacci Ratio)

5.  **Calculation Overview:**

    - Step 1: Identify a significant prior price swing (e.g., a recent uptrend from point A (low) to point B (high)).
    - Step 2: Calculate the price difference between the swing high and swing low.
    - Step 3: Multiply this difference by the key Fibonacci ratios (0.236, 0.382, 0.500, 0.618, 0.786).
    - Step 4: For an uptrend, subtract these values from the swing high to get support levels. For a downtrend, add these values to the swing low to get resistance levels.
    - Step 5: Observe if price retraces to one of these levels and then "bounces" (reverses) back in the direction of the original trend.

6.  **Action Decision Implication (General):**
    - **Buy Signal:** In an existing uptrend, price retraces to a Fibonacci support level (e.g., 38.2%, 50%, or 61.8%) and then shows signs of bouncing up (e.g., bullish candlestick pattern, confirmation from other indicators).
    - **Sell Signal:** In an existing downtrend, price rallies to a Fibonacci resistance level and then shows signs of bouncing down.
    - The 50% and 61.8% levels are often considered particularly significant.

---

## **Indicator: Daily Pivot-Point Reversal**

1.  **Description:**
    Pivot points are significant price levels calculated using the previous day's high, low, and close. They are used to identify potential support and resistance levels for the current trading day. A "reversal" occurs when price approaches a pivot level (Central Pivot, Support 1/2/3, Resistance 1/2/3) and then reverses direction.

2.  **Data Needed & Source (Previous Day's Data):**

    - `Previous Day's High`: From `BSEAdjustedPrice.high` (for date = T-1).
    - `Previous Day's Low`: From `BSEAdjustedPrice.low` (for date = T-1).
    - `Previous Day's Close`: From `BSEAdjustedPrice.close` (for date = T-1).
    - `Current Day's Price Action (Open, High, Low, Close)`: From `BSEAdjustedPrice` (for date = T) to observe interactions with calculated pivot levels.

3.  **Purpose of Data in Calculation:**

    - `Previous Day's H, L, C`: Used as inputs to the pivot point formulas.

4.  **Helper Calculations / Prerequisites:**

    - **Central Pivot Point (PP):** `(Prev High + Prev Low + Prev Close) / 3`
    - **Support 1 (S1):** `(2 * PP) - Prev High`
    - **Resistance 1 (R1):** `(2 * PP) - Prev Low`
    - **Support 2 (S2):** `PP - (Prev High - Prev Low)`
    - **Resistance 2 (R2):** `PP + (Prev High - Prev Low)`
    - **Support 3 (S3):** `Prev Low - 2 * (Prev High - PP)`
    - **Resistance 3 (R3):** `Prev High + 2 * (PP - Prev Low)`
    - (Various other pivot formulas exist, e.g., Woodie's, Camarilla).

5.  **Calculation Overview:**

    - Step 1: At the start of the current trading day (or end of the previous), calculate the PP, S1, R1, S2, R2, etc., using the prior day's H, L, C.
    - Step 2: Plot these levels on the current day's chart.
    - Step 3: Observe if the current day's price action approaches these levels and shows signs of reversal (e.g., candlestick patterns, failure to break through).

6.  **Action Decision Implication (General):**
    - **Buy Signal:** Price falls to a support level (S1, S2, or PP if approached from above) and shows signs of reversing upwards (e.g., forms a bullish engulfing pattern, hammer).
    - **Sell Signal:** Price rallies to a resistance level (R1, R2, or PP if approached from below) and shows signs of reversing downwards.
    - Breakouts: If price decisively breaks through R1, it may target R2. If it breaks S1, it may target S2.
