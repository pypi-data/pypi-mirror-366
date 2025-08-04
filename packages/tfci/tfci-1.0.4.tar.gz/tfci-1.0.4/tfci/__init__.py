#!/usr/bin/env python3
"""
TFCI (Time Forecasting CI) - 라이브러리용
"""

import sys
import traceback
from config.config import load_config
from core.predictor import Predictor

def predict(config_path: str = "config.yaml"):
    """
    설정 파일을 기반으로 시계열 예측을 실행합니다.
    
    Args:
        config_path (str): 설정 파일 경로 (기본값: "config.yaml")
    
    Example:
        >>> from tfci import predict
        >>> predict("config.yaml")
        >>> predict("config2.yaml")
        >>> predict("config3.yaml")
    """
    try:
        config = load_config(config_path)
        pipeline = Predictor(config)
        pipeline.run()
        print(f"[SUCCESS] 예측 완료: {config_path}")
    except Exception as e:
        print(f"[ERROR] 예측 실패: {e}")
        traceback.print_exc()

# 라이브러리 버전 정보
__version__ = "1.0.4"
__author__ = "TFCI Team"
__email__ = "rosci671233@gmail.com" 