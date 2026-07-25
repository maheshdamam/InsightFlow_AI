"""
Time-series forecasting for revenue / profit / demand / sales.

Uses Facebook Prophet when available (handles seasonality well with little
tuning). Falls back to a simple linear regression trend line if Prophet
isn't installed or fails to fit, so forecasting always returns something.
"""
from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd

from app.schemas.ai import ForecastPoint


def _linear_fallback(df: pd.DataFrame, periods: int) -> List[ForecastPoint]:
    from sklearn.linear_model import LinearRegression

    df = df.sort_values("ds").reset_index(drop=True)
    x = np.arange(len(df)).reshape(-1, 1)
    y = df["y"].values
    model = LinearRegression().fit(x, y)

    last_date = df["ds"].max()
    future_x = np.arange(len(df), len(df) + periods).reshape(-1, 1)
    preds = model.predict(future_x)
    future_dates = pd.date_range(start=last_date, periods=periods + 1, freq="D")[1:]

    return [
        ForecastPoint(date=d.strftime("%Y-%m-%d"), predicted_value=round(float(p), 2))
        for d, p in zip(future_dates, preds)
    ]


def _xgboost_forecast(df: pd.DataFrame, periods: int) -> List[ForecastPoint]:
    """
    Feature-based forecast using XGBoost: builds day-of-week / month / lag
    features from the historical series, then recursively predicts forward
    one day at a time (each prediction feeds into the next day's lag
    features). Useful when a dataset doesn't have enough history or
    seasonality for Prophet to model well, but has clear day-of-week /
    lag patterns.
    """
    from xgboost import XGBRegressor

    work = df.sort_values("ds").reset_index(drop=True).copy()
    work["ds"] = pd.to_datetime(work["ds"])

    # Reindex to a continuous daily series so lag features are well-defined
    full_range = pd.date_range(work["ds"].min(), work["ds"].max(), freq="D")
    work = work.set_index("ds").reindex(full_range).rename_axis("ds").reset_index()
    work["y"] = work["y"].interpolate().bfill().ffill()

    def build_features(frame: pd.DataFrame) -> pd.DataFrame:
        feats = pd.DataFrame({
            "dayofweek": frame["ds"].dt.dayofweek,
            "day": frame["ds"].dt.day,
            "month": frame["ds"].dt.month,
            "lag_1": frame["y"].shift(1),
            "lag_7": frame["y"].shift(7),
            "rolling_mean_7": frame["y"].shift(1).rolling(7, min_periods=1).mean(),
        })
        return feats

    feature_df = build_features(work)
    train_mask = feature_df.notna().all(axis=1)
    X_train, y_train = feature_df[train_mask], work.loc[train_mask, "y"]

    if len(X_train) < 10:
        return _linear_fallback(work.rename(columns={"ds": "ds", "y": "y"}), periods)

    model = XGBRegressor(n_estimators=200, max_depth=4, learning_rate=0.05, random_state=42)
    model.fit(X_train, y_train)

    history = work[["ds", "y"]].copy()
    results: List[ForecastPoint] = []
    last_date = history["ds"].max()

    for _ in range(periods):
        next_date = last_date + pd.Timedelta(days=1)
        temp = pd.concat([history, pd.DataFrame({"ds": [next_date], "y": [np.nan]})], ignore_index=True)
        feats = build_features(temp).iloc[[-1]]
        pred = float(model.predict(feats)[0])
        results.append(ForecastPoint(date=next_date.strftime("%Y-%m-%d"), predicted_value=round(pred, 2)))
        history = pd.concat([history, pd.DataFrame({"ds": [next_date], "y": [pred]})], ignore_index=True)
        last_date = next_date

    return results


def forecast_series(
    df: pd.DataFrame,
    date_col: str,
    target_col: str,
    periods: int = 30,
    model: str = "prophet",
) -> List[ForecastPoint]:
    """
    df: raw cleaned dataframe
    date_col / target_col: which columns to use
    periods: how many days ahead to forecast
    model: "prophet" (default, best for seasonal data) or "xgboost"
           (feature/lag-based, can work well with less data)
    """
    work = df[[date_col, target_col]].copy()
    work[date_col] = pd.to_datetime(work[date_col], errors="coerce")
    work = work.dropna(subset=[date_col, target_col])
    work = work.groupby(date_col, as_index=False)[target_col].sum()
    work = work.rename(columns={date_col: "ds", target_col: "y"})

    if len(work) < 5:
        return []

    if model == "xgboost":
        try:
            return _xgboost_forecast(work, periods)
        except Exception:
            return _linear_fallback(work, periods)

    try:
        from prophet import Prophet

        prophet_model = Prophet(daily_seasonality=False, yearly_seasonality=True, weekly_seasonality=True)
        prophet_model.fit(work)
        future = prophet_model.make_future_dataframe(periods=periods)
        forecast = prophet_model.predict(future)
        tail = forecast.tail(periods)
        return [
            ForecastPoint(
                date=row["ds"].strftime("%Y-%m-%d"),
                predicted_value=round(float(row["yhat"]), 2),
                lower_bound=round(float(row["yhat_lower"]), 2),
                upper_bound=round(float(row["yhat_upper"]), 2),
            )
            for _, row in tail.iterrows()
        ]
    except Exception:
        # Prophet not installed / failed to converge -> fall back to a linear trend
        return _linear_fallback(work, periods)
