# MCP Predictor

진짜 간단한 시계열 예측 라이브러리입니다.

## 특징

- ✅ **진짜 간단한 사용법**
- ✅ **여러 config 파일로 여러 예측**
- ✅ **DB2, PostgreSQL, MongoDB 지원**
- ✅ **Prophet + LightGBM 시계열 예측**

## 설치

```bash
pip install mcp-predictor
```

## 사용법

### **진짜 간단한 사용법**

```python
from mcp_predictor import predict

# 한 줄로 예측
predict("config.yaml")
predict("config1.yaml")
predict("config2.yaml")
predict("config3.yaml")
```

### **설정 파일 예시**

```yaml
# config.yaml
input:
  source_type: "db"
  db_type: "db2"
  connection:
    host: "192.168.106.35"
    port: 25010
    user: "db2inst1"
    password: "mobigen01!"
    database: "EOTD"
  table: "DSTDM.T_PBAF3103S"
  features: ["RGN_CD", "CRTR_YR"]
  target: ["GRDR1_STDNT_NOPE", "GRDR2_STDNT_NOPE"]

prediction:
  task_type: "timeseries"
  future_steps: 5
  time_col: "CRTR_YR"
  group_key: "RGN_CD"

output:
  source_type: "db"
  db_type: "db2"
  connection:
    host: "192.168.106.35"
    port: 25010
    user: "db2inst1"
    password: "mobigen01!"
    database: "EOTD"
  table: "DSTDM.T_PBAF3103S_FCST"
```

## 프로젝트 구조

```
mcp-predictor/
├── core/
│   └── predictor.py          # 핵심 예측 로직
├── data/
│   ├── csv.py               # CSV 데이터 처리
│   ├── data.py              # 데이터 전처리
│   └── db.py                # 데이터베이스 연결
├── model/
│   └── model.py             # Prophet + LightGBM 모델
├── config/
│   └── config.py            # 설정 파일 로더
├── mcp_predictor.py         # 진짜 간단한 라이브러리
├── main.py                  # 직접 실행용
├── config.yaml              # 설정 파일
└── requirements.txt         # 의존성
```

## 라이브러리 배포

```bash
# PyPI에 업로드
pip install build twine
python -m build
twine upload dist/*
```

## 라이센스

MIT License
