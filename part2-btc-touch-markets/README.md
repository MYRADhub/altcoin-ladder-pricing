# Part 2: Does the crowd know touching is twice as likely?

Part 1, pricing thin altcoin ladders, is in the [repository README](../README.md). Part 1 found that thin crowds lose to simple models; this part asks the same question of one of the busiest crypto prediction markets.

Polymarket runs daily, weekly and monthly BTC markets that pay if Bitcoin *touches* a price at any moment in a window: "Will Bitcoin reach $120,000 on August 15?" For a randomly moving price, touching a level is about twice as likely as finishing beyond it, and options desks price these "one-touch" bets every day. I checked whether the crowd prices them like the options market does, whether crowding and mood signals predict its mistakes, and whether its prices ever break a no-arbitrage bound against Kalshi's BTC ladders.

**Answer.**
- **Yes, the crowd knows.** Over 326 events and 1.87 million trades ($155M traded) from October 2024 to November 2026, Polymarket's touch prices were as accurate as a fair value built from Deribit's BTC options (Brier 0.1090 against 0.1101, difference not significant, p = 0.19) and close to perfectly calibrated. They price touching about 11 to 12 cents above finishing beyond the strike, so the crowd does not treat a touch bet like a closing-price bet.
- **No usable mispricing.** Against the planned fair value (twice the options-implied probability of finishing beyond the strike) the crowd sits 1.7 cents higher on both up and down markets (Holm p = 0.002), but against the textbook barrier formula it sits 1 to 3 cents lower. The two option models disagree with each other by more than the crowd disagrees with either. The only stable pattern is a small long-shot tilt (contracts near 6 cents touch about 4% of the time), smaller than the fee.
- **Mood and crowding do not move it.** The Fear & Greed regime and funding-crowding signals of the Q-7 model ([Babayev and Aliyev 2026, "Crypto Has Fundamentals: A Seven-Factor Model for Digital Asset Returns"](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6818558); see [part 1](../README.md#how-this-builds-on-the-q-7-model)) did not predict the crowd's premium (p from 0.07 to 0.94).
- **For risk forecasting, market prices beat history.** For "will BTC dip to $X today or this week", the crowd's price and the options value were each about 10% more accurate (Brier score) than the same calculation from BTC's past volatility (Holm p = 0.001 for both). The edge is in daily and weekly windows; for drops of 5% or more and for monthly windows, history did as well.
- **No arbitrage against Kalshi.** Polymarket priced a touch below Kalshi's "beyond K at 5 pm" for the same day in 262 of 129,997 paired trades, after fees. None of them survive a check that the two trades were close in time, BTC was flat between them, and the prints were on sides one could trade against: they are the two venues' bid-ask spreads.

![Calibration, premium against three fair values, premium by distance, and the Kalshi check](results/results.png)

The plan was written in `research.md` before any data was downloaded. One amendment (made while downloading, before any data was read) and the attempts log are dated there.

## Why it matters

Touch markets are among Polymarket's busiest crypto products: about $1.2 billion traded across these 336 events. They are barrier options sold to a retail crowd, and a crowd that confuses "touch" with "finish" would leave a large, hedgeable edge. Comparing crypto prediction-market prices with options has been done for closing-price contracts ([Lee, Lee and Lee 2026](https://www.sciencedirect.com/science/article/abs/pii/S1057521926003601); [arXiv 2606.19517](https://arxiv.org/html/2606.19517); public projects such as [implied-odds-research](https://github.com/tavelarocque/implied-odds-research)), and Kalshi's long-shot bias is documented ([Bürgi, Deng and Whelan 2025](https://www.ucd.ie/economics/t4media/WP2025_19.pdf)). For touch markets I found one informal analysis of a single monthly contract ([podshopguy](https://podshopguy.substack.com/p/polymarket-overprices-volatility)) and no systematic study.

## Data

All public, downloaded 2026-11-06:
- **Polymarket** "What price will Bitcoin hit" events: 243 daily, 70 weekly and 23 monthly, with market rules from the Gamma API and trades from the data API v2 (time, price, size, side and outcome only; no wallet fields).
- **Deribit** every BTC option trade with an expiry within 40 days, with its implied volatility and index price (history API).
- **Binance** BTCUSDT 1-minute klines (the touch markets resolve on these highs and lows), USDT-M funding rates ([public archive](https://data.binance.vision)).
- **Kalshi** KXBTCD 5 pm ET ladders with trades and taker side (Trade API v2).
- **Alternative.me Fear & Greed index.**

My Binance-based reading of each market's rules reproduces Polymarket's resolution on 5,359 of 5,360 markets.

## Method and baseline

A **trade** counts if the window has started, at least an hour is left, the price is between 3 and 97 cents, and the price has not yet touched the strike on Binance. For each trade, the Deribit option trades of the previous hour give a volatility smile per expiry (quadratic in log-moneyness), interpolated in time to the end of the touch window. From it:

| Fair value | What it is |
| --- | --- |
| **2 x digital** (primary) | Twice the options-implied probability of finishing beyond the strike: the reflection principle, exact for a driftless continuous price |
| Barrier formula | The closed-form one-touch probability under geometric Brownian motion, with the smile's volatility at the strike |
| Digital | The probability of finishing beyond: a hard lower bound for any touch |

Scores: the market price minus each fair value, weighted by shares within each event, events weighted equally; Brier scores paired by event. Uncertainty from a bootstrap over blocks of 10 days, Holm-adjusted over the three primary tests.

## Results

**Primary** (326 events; reach = up markets, dip = down markets):

| Test | Estimate | 95% interval | Holm p |
| --- | ---: | ---: | ---: |
| Reach: market minus 2 x digital | +1.65 cents | +1.35 to +1.99 | 0.002 |
| Dip: market minus 2 x digital | +1.76 cents | +1.46 to +2.14 | 0.002 |
| Brier: market minus 2 x digital | -0.0011 | -0.0028 to +0.0005 | 0.19 |

**Against the other fair values** (same tests):

| Fair value | Reach | Dip | Brier difference, p |
| --- | ---: | ---: | ---: |
| Barrier formula | -0.99 cents | -3.01 cents | -0.0017, 0.10 |
| Digital (lower bound) | +11.87 cents | +10.92 cents | -0.0271, 0.002 |

The crowd's prices fall between the two option models and well above the lower bound. The 2 x digital value is itself a little too low: contracts it prices at 57 cents touched 63% of the time. The crowd's 57-cent contracts touched 57% of the time.

**By series** (market minus 2 x digital, cents): daily +1.9 reach and +2.1 dip; weekly +0.8 and +1.1; monthly +2.1 and +0.3 (the monthly dip interval includes zero; 23 events).

**Mood and crowding.** The event-level premium, regressed on the standardized 30-day Fear & Greed mean and 7-day BTC funding mean known the day before the window: no slope is significant (reach on funding +0.29 cents per standard deviation, p = 0.09; dip on funding +0.23, p = 0.07; every other p above 0.25). The difference between up and down premiums does not move with either (p = 0.94 and 0.74).

**Trading rule (secondary).** Buying the side the 2 x digital value prices at least 4 cents above the trade price plus the 0.07 × p × (1 - p) fee returned +7.8% per dollar (95% interval -1.6% to +26.9%). Most of the profit came from the 23 monthly events, whose contracts all share one month's path; daily alone returned +4.1% (-2.4% to +8.8%). Not significant, and it assumes fills at printed prices.

**Follow-up: market prices against history for drawdown odds** (planned 2026-11-07, after the results above). A risk platform built on factor models forecasts risk from past volatility. Here the same reflection value was built from history (HAR volatility from Binance hourly returns over the last 1, 7 and 30 days) and compared with the crowd's price and the options value on the same trades.

| Dip markets ("will BTC fall to $X") | Events | Crowd | Options | History | Crowd minus history | Options minus history |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| All (primary) | 324 | 0.0926 | 0.0928 | 0.1034 | -0.0107 (Holm p 0.001) | -0.0106 (Holm p 0.001) |
| Daily | 233 | 0.0848 | 0.0856 | 0.0978 | -0.0130 (p 0.001) | -0.0122 (p 0.001) |
| Weekly | 68 | 0.1076 | 0.1070 | 0.1144 | -0.0068 (p 0.048) | -0.0074 (p 0.035) |
| Monthly | 23 | 0.1280 | 0.1240 | 0.1272 | +0.0007 (p 0.90) | -0.0032 (p 0.36) |
| Strike 5% or more below spot | 182 | 0.0517 | 0.0467 | 0.0478 | +0.0040 (p 0.20) | -0.0011 (p 0.20) |

On reach markets the result is the same (crowd 0.0945, options 0.0941, history 0.1039; both Holm p = 0.001). History is less sharp: it overstates the chance of near touches and understates the far ones. BTC fell over much of the sample, and all three forecasts underpriced dips in the middle of the range (crowd prices near 42 cents touched 56% of the time), so the dip results partly reflect one falling year.

**Kalshi bound.** For daily events, each Polymarket trade was paired with the last Kalshi trade within 5 minutes on the same day's 5 pm ladder, at the nearest strike at or beyond the touch strike. If BTC is beyond K at 5 pm it has touched K, so the touch price should never be lower. It was lower by more than both fees plus a cent in 262 of 129,997 pairs (0.2%, on 53 of 228 days, median 6 cents). In an exploratory check added after seeing them, 143 were within 60 seconds with BTC flat, and none were on executable sides: they paired a Polymarket print where someone sold the touch with a Kalshi print where someone bought. Over the whole sample only 3 were on executable sides.

## Limitations and what did not work

- **Model risk is larger than the effect.** The two standard option models disagree by 3 to 5 cents. Calling the crowd "1.7 cents rich" or "1 to 3 cents cheap" depends on the model, so the defensible statement is that the crowd is inside the range of reasonable fair values.
- **Binance is not the options index.** Touch markets resolve on one exchange's 1-minute wicks; Deribit's options settle on a multi-exchange index. Single-exchange wicks make touching slightly easier, which may be why 2 x digital runs low.
- **One path per window.** All strikes of an event share one price path, so the effective sample is the number of events, not trades. Monthly results rest on 23 events.
- **Prints are not quotes.** Trades show where someone traded, not the spread; the trading rule is an upper bound.
- **Attempts log.** Run 1 crashed on 20 weekly markets without their own end date; run 2 crashed at the Kalshi check. Run 3 completed and its numbers were read; the planned resolution check then found three data bugs (269 markets with unrecognized window wording, a strike parser that read a month name as "millions", and window ends an hour off around clock changes) plus five two-sided 2024 markets. After the fixes, run 4 is reported; the model, tests and filters did not change. Run 3 gave +2.25 and +1.78 cents for the two premiums.

## Reproduce

```bash
cd part2-btc-touch-markets
uv sync
uv run python -m touchmkt.cli download-binance     # BTCUSDT 1-minute klines, funding, Fear & Greed (about 50 MB)
uv run python -m touchmkt.cli download-polymarket  # about 330 MB, 40 minutes
uv run python -m touchmkt.cli download-deribit     # about 90 MB, 1 hour
uv run python -m touchmkt.cli download-kalshi      # about 600 MB, 3 hours at 3 requests per second
uv run python -m touchmkt.cli run                  # prices 1.9 million trades and runs every test, about 20 to 30 minutes
uv run python -m touchmkt.exploratory              # the executable-sides check on the Kalshi violations
uv run python -m touchmkt.crashodds                # market and options against history for drawdown odds
uv run python -m touchmkt.figure
uv run pytest
cd .. && npm start                                # both decks at http://127.0.0.1:4173/
```

## Where I would like feedback

1. Which fair value would a desk use for a 1-day one-touch on BTC: twice the smile digital, a local-volatility barrier price, or something calibrated to realized wicks?
2. Is the crowd's accuracy here surprising to you, given the long-shot bias found on Kalshi, or is a $1M-a-day market simply deep enough to be efficient?
3. Is there a cleaner way to test the touch-versus-terminal bound across venues with only trade prints, without order-book history?
