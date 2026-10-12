# Predictive Valuation Model Performance & Architecture

- Architecture: Super-Ensemble (Gradient Boosting + Random Forest + Extra Trees)
- Split: 80% Training / 20% Out-of-Sample Testing
- Test Accuracy: 99.46% (R² = 0.9946)
- Mean Percentage Error (MAPE): 2.13%
- Valuation Horizon: 10-Year compounding projections with empirical 80% prediction intervals
- Leakage Safeguards: Strict exclusion of derived targets from feature pipeline
