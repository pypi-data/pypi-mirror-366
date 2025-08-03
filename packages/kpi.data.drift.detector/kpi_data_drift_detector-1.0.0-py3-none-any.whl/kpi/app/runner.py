import numpy as np
import pandas as pd

from kpi.app.detector.detector import DataDriftDetector
from kpi.app.profiler.profiler import Profiler


def infer_feature_types(df: pd.DataFrame,
                        max_categories: int = 5):
    numeric, categorical = [], []
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            if df[col].nunique() <= max_categories:
                categorical.append(col)
            else:
                numeric.append(col)
        else:
            categorical.append(col)
    return numeric, categorical

def run_drift_monitoring(
    df_reference: pd.DataFrame,
    df_current:   pd.DataFrame
) -> pd.DataFrame:
    numeric_features, categorical_features = infer_feature_types(df_current, max_categories=5)

    # 2) Профилирование обоих наборов
    profiler = Profiler(numeric_bins=50)
    profile_ref = profiler.profile(df_reference, numeric_features, categorical_features)
    profile_cur = profiler.profile(df_current, numeric_features, categorical_features)

    detector = DataDriftDetector()
    drift_report = detector.detect(profile_ref, profile_cur)


    print(drift_report)


    print("start")
    return None


np.random.seed(0)

# Генерация тестового reference DataFrame
df_reference = pd.DataFrame({
    'days_active': np.random.normal(loc=100, scale=10, size=10).round().astype(int),
    'avg_call_duration': np.random.normal(loc=5, scale=1, size=10).round(2),
    'is_credit_card': np.random.choice([0, 1], size=10, p=[0.6, 0.4]),
    'region': np.random.choice(['US', 'EU', 'APAC'], size=10, p=[0.5, 0.3, 0.2])
})

# Генерация тестового current DataFrame с дрейфом
df_current = pd.DataFrame({
    'days_active': np.random.normal(loc=110, scale=12, size=10).round().astype(int),  # сдвиг среднего
    'avg_call_duration': np.random.normal(loc=6, scale=1.2, size=10).round(2),
    'is_credit_card': np.random.choice([0, 1], size=10, p=[0.4, 0.6]),                # сдвиг пропорций
    'region': np.random.choice(['US', 'EU', 'APAC', 'LATAM'], size=10,
                               p=[0.4, 0.25, 0.25, 0.10])  # появление новой категории
})

run_drift_monitoring(df_reference, df_current)