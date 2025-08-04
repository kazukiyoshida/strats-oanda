# Changelog

## 0.1.6

Released 2025-08-04

- Fix
  - Fix InstrumentClient details
  - Fix logging in Trade state

## 0.1.5

Released 2025-07-22

- Feat
  - Add Trade and TradeMetrics class
- Test
  - Unit tests for OrderClient
  - Unit tests for Trade

## 0.1.4

Released 2025-07-19

- Bump up `strats` to 0.1.7

## 0.1.3

Released 2025-05-02

- Set timeout in stream API session
- Re-design OrderClient
- Add an argument `current_data` for `source_to_data` function

## 0.1.2

Released 2025-04-15

- Use cancel method instead of stop event

## 0.1.1

Released 2025-04-05

- Set up CI using GitHub Actions:
  - Run tests
  - Publish to PyPI

## 0.1.0

Released 2025-04-02

- Models and API Client for the following domain
  - instrument
  - order
  - pricing
  - transaction
- Converter function for strats pricing model
