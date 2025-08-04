import pandas as pd

class Data:
    @staticmethod
    def preprocess(df: pd.DataFrame) -> pd.DataFrame:
        """
        간단한 전처리: NA 제거, 숫자형 컬럼 변환
        """
        df = df.dropna()
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")
        return df

    @staticmethod
    def select_features(df: pd.DataFrame, config: dict, prediction_cfg: dict = None):
        """
        features와 target을 선택하여 X, y로 반환
        - time_col과 group_key가 있으면 시계열 정렬 수행
        """
        features = config.get("features", [])
        target = config.get("target", [])

        if not features or not target:
            raise ValueError("features 또는 target이 지정되지 않았습니다.")

        if isinstance(target, str):
            target = [target]

        X = df[features]
        y = df[target]

        # ✅ 시계열 정렬 처리
        if prediction_cfg:
            time_col = prediction_cfg.get("time_col")
            group_key = prediction_cfg.get("group_key")

            if group_key and group_key in X.columns:
                sort_cols = [group_key]
                if time_col and time_col in X.columns:
                    sort_cols.append(time_col)
                X = X.sort_values(by=sort_cols)
                y = y.loc[X.index]
            elif time_col and time_col in X.columns:
                X = X.sort_values(by=time_col)
                y = y.loc[X.index]

        return X, y
