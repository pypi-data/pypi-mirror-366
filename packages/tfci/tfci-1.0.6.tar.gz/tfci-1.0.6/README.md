# TFCI (Time Forecasting CI)

간단한 시계열 예측 라이브러리

### 기본 라이브러리 (tfci)
```bash
pip install tfci
```


## 사용법

### 기본 라이브러리 사용
```python
from tfci import predict

# YAML 설정 파일로 예측 실행
predict("config.yaml")
```


## 기능

### tfci 라이브러리
- ✅ 시계열 예측 (Prophet 기반)
- ✅ YAML 설정 파일 지원
- ✅ DB2 데이터베이스 연동
- ✅ group_key 리스트 지원
- ✅ 멀티프로세싱 지원

### tfci-mcp 패키지
- ✅ MCP (Model Context Protocol) 지원
- ✅ 다른 MCP들과 조합 가능
- ✅ JSON-RPC 통신
- ✅ 서버/클라이언트 분리

## 설정 파일 예시

```yaml
input:
  source_type: "db" # or csv
  db_type: "db2"
  connection:
    host: "DBURL"
    port: PortNumber
    user: "UserName"
    password: "Pwd!"
    database: "DBName"
  table: "TableName"
  features: ["COL_1", "COL_2", "COL_3"]
  target: ["COL_4"]
prediction:
  task_type: "timeseries"
  future_steps: 5 # 예측 구간 (5년 후)
  time_col: "COL_1"
  group_key: ["COL_2", "COL_3"]
output:
  source_type: "db" # or csv
  db_type: "db2"
  connection:
    host: "DBURL"
    port: PortNumber
    user: "UserName"
    password: "Pwd!"
    database: "DBName"
  table: "TableName"
```

## 의존성

### tfci
- pandas>=2.0.0
- numpy>=1.20.0
- prophet>=1.1.0
- scikit-learn>=1.0.0
- tqdm>=4.60.0
- PyYAML>=6.0
- requests>=2.25.0

### tfci-mcp
- tfci>=1.0.4

## 라이선스

MIT License
