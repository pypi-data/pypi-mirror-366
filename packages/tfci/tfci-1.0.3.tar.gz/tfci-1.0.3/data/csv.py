import pandas as pd

class Csv:
    def __init__(self, config):
        self.config = config

    def load(self):
        path = self.config.get("csv_path")
        if not path:
            raise ValueError("CSV 경로가 지정되지 않았습니다.")
        return pd.read_csv(path)

    def save(self, df):
        path = self.config.get("csv_path", "./output.csv")
        df.to_csv(path, index=False)
        print(f"[INFO] CSV로 저장 완료: {path}")
