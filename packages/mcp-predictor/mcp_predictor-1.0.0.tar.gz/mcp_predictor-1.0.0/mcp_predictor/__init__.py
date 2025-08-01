#!/usr/bin/env python3
"""
MCP Predictor - 진짜 간단한 시계열 예측 라이브러리
"""

import sys
import os
from .core.predictor import Predictor

def predict(config_path: str = "config.yaml"):
    """
    간단한 예측 함수
    
    Args:
        config_path (str): 설정 파일 경로 (기본값: config.yaml)
    
    Returns:
        dict: 예측 결과
    """
    try:
        # 설정 파일 로드
        from .config.config import load_config
        config = load_config(config_path)
        
        # 예측 실행
        predictor = Predictor(config)
        result = predictor.run()
        
        return {"status": "success", "result": result}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 사용 예시
if __name__ == "__main__":
    import sys
    
    # 명령행 인수로 설정 파일 받기
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    
    result = predict(config_file)
    print(f"예측 결과: {result}") 