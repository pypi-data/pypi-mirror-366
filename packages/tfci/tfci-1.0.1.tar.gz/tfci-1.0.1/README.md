# TFCI (Time Forecasting CI)

간단한 시계열 예측 라이브러리입니다.

## 특징

- ✅ **진짜 간단한 사용법**
- ✅ **여러 config 파일로 여러 예측**
- ✅ **DB2 지원** (PostgreSQL, MongoDB는 미지원)
- ✅ **Prophet 시계열 예측**
- ✅ **하이브리드 예측 전략** (트렌드 기반 + Prophet)
- ✅ **멀티프로세싱 지원**

## 설치

### PyPI에서 설치 (권장)

```bash
# 기본 설치
pip install tfci

```

### 로컬 개발용

```bash
git clone https://github.com/rosci671233/tfci.git
```

## 사용법

### 1. 라이브러리 사용 (PyPI 배포)

```python
from tfci import predict

# 단일 예측
predict("config.yaml")

# 여러 설정 파일 순차 실행
predict("config1.yaml")
predict("config2.yaml")
predict("config3.yaml")
```

### 2. 로컬 실행

```bash
# 기본 실행 (config.yaml 사용)
python tfci.py

# 특정 설정 파일
python tfci.py config.yaml
```

### 3. MCP 서버 사용

```bash
# 직접 예측
python mcp_tfci.py --config config.yaml

# 여러 설정 파일 순차 실행
python mcp_tfci.py --config config1.yaml
python mcp_tfci.py --config config2.yaml
python mcp_tfci.py --config config3.yaml
```



### 설정 파일 예시

```yaml
# config.yaml
input:
  source_type: "db"       # db | csv
  db_type: "db2"          # db2만 지원
  connection:
    host: "localhost"
    port: 50000
    user: "db2user"
    password: "password"
    database: "SAMPLE"
  table: "MY_TABLE"
  features: ["RGN_CD", "CRTR_YR"]
  target: ["GRDR1_STDNT_NOPE", "GRDR2_STDNT_NOPE"]

prediction:
  task_type: "timeseries"
  future_steps: 5         # 5년 후 예측
  time_col: "CRTR_YR"     # 시계열 기준 컬럼
  group_key: "RGN_CD"     # 지역별로 개별 시계열 모델

output:
  source_type: "db"
  db_type: "db2"
  connection:
    host: "localhost"
    port: 50000
    user: "db2user"
    password: "password"
    database: "SAMPLE"
  table: "MY_TABLE_FCST"
```

## 프로젝트 구조

```
tfci/
├── tfci.py               # 로컬 실행용
├── lib_tfci.py           # PyPI 배포용 라이브러리
├── mcp_tfci.py           # MCP 서버 배포용
├── pyproject.toml        # PyPI 배포 설정
├── core/
│   └── predictor.py      # 핵심 예측 로직
├── data/
│   ├── csv.py            # CSV 데이터 처리
│   ├── data.py           # 데이터 전처리
│   └── db.py             # DB2 데이터베이스 연결
├── model/
│   └── model.py          # Prophet 시계열 모델
├── config/
│   └── config.py         # 설정 파일 로더
├── mcp/
│   ├── http_server.py    # HTTP 서버 (미사용)
│   └── mcp_server.py     # MCP 서버 (미사용)
├── config.yaml           # 설정 파일
└── requirements.txt      # 의존성
```

## 배포 방식

### 1. GitHub - 로컬 개발용
- `tfci.py`: 로컬에서 직접 실행
- 개발 및 테스트용

### 2. PyPI - 라이브러리용
- `lib_tfci.py`: 라이브러리 API 제공
- `pip install tfci`로 설치
- `from tfci import predict`로 사용

### 3. MCP - 서버용
- `mcp_tfci.py`: MCP 서버 실행
- `python mcp_tfci.py --config config.yaml`
- 배포 및 운영용



## 예측 방식

### 하이브리드 예측 전략
1. **트렌드 분석**: 데이터의 트렌드와 계절성 강도 분석
2. **모델 선택**: 
   - 트렌드가 명확하고 계절성이 약하면 → 단순 선형 트렌드
   - 복잡한 패턴이면 → Prophet 모델
3. **지역별 독립 예측**: 각 지역(`group_key`)별로 개별 시계열 모델
4. **자동 저장**: 예측 결과가 자동으로 DB에 저장됨

## 라이브러리 배포

```bash
# 빌드
python -m build

# PyPI 업로드
python -m twine upload dist/*

# 테스트 PyPI 업로드
python -m twine upload --repository testpypi dist/*
```

## 라이센스

MIT License

## 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
