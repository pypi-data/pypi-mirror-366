# TFCI MCP

TFCI (Time Forecasting CI) MCP (Model Context Protocol) Client for Time Series Prediction

**이 패키지는 [tfci](https://pypi.org/project/tfci/) 라이브러리의 MCP 확장입니다.**

## 설치

```bash
pip install tfci-mcp
```

## 사용법

### 기본 사용법

```python
from tfci_mcp import TFCIMCPClient

# 클라이언트 생성
client = TFCIMCPClient()

# 서버 시작
client.start_server()

# 예측 실행
result = client.predict("config.yaml")
print(result)

# 서버 종료
client.stop_server()
```

### 다른 MCP들과 함께 사용

```python
from tfci_mcp import TFCIMCPClient
from viz_mcp import VizMCPClient

# TFCI 예측
tfci_client = TFCIMCPClient()
tfci_client.start_server()
result = tfci_client.predict("config.yaml")

# 시각화
viz_client = VizMCPClient()
chart = viz_client.create_chart(result)

# 정리
tfci_client.stop_server()
```

## API

### TFCIMCPClient

#### `__init__(server_script=None)`
- `server_script`: 서버 스크립트 경로 (기본값: 자동 감지)

#### `start_server()`
MCP 서버를 시작합니다.

#### `stop_server()`
MCP 서버를 종료합니다.

#### `predict(config_path)`
- `config_path`: YAML 설정 파일 경로
- 반환값: 예측 결과 딕셔너리

## 의존성

- `tfci>=1.0.4`: TFCI 예측 라이브러리

## 관련 패키지

- **[tfci](https://pypi.org/project/tfci/)**: 메인 시계열 예측 라이브러리
- **tfci-mcp**: MCP 확장 패키지 (현재 패키지)

## 라이선스

MIT License 