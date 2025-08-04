#!/usr/bin/env python3
"""
HTTP 기반 MCP 서버
"""

import json
import traceback
from typing import Any, Dict, Optional
from flask import Flask, request, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import load_config
from core.predictor import Predictor

app = Flask(__name__)
mcp_server = None

class HTTPMCPServer:
    def __init__(self):
        self.predictor = None
        self.config = None

    def initialize(self, config_path: str = "config.yaml") -> Dict[str, Any]:
        """서버 초기화"""
        try:
            print(f"[INFO] HTTP MCP 서버 초기화: {config_path}")
            self.config = load_config(config_path)
            self.predictor = Predictor(self.config)
            return {"status": "success", "message": "HTTP MCP 서버 초기화 완료"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def predict(self, config_path: str) -> Dict[str, Any]:
        """config 파일 경로를 받아서 예측 실행"""
        try:
            print(f"[INFO] HTTP MCP 예측 시작: {config_path}")
            
            # config 파일 로드
            config = load_config(config_path)
            
            # 예측 실행
            predictor = Predictor(config)
            result = predictor.run()
            
            return {
                "status": "success", 
                "result": result,
                "config_used": config_path
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_config(self) -> Dict[str, Any]:
        """현재 설정 조회"""
        return {"config": self.config}

    def update_config(self, new_config: Dict[str, Any]) -> Dict[str, Any]:
        """설정 업데이트"""
        self.config = new_config
        return {"status": "success", "message": "설정 업데이트 완료"}

mcp_server = HTTPMCPServer()

@app.route('/init', methods=['POST'])
def initialize():
    """서버 초기화"""
    try:
        data = request.get_json() or {}
        config_path = data.get('config_path', 'config.yaml')
        result = mcp_server.initialize(config_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/predict', methods=['POST'])
def predict():
    """예측 실행"""
    try:
        data = request.get_json() or {}
        config_path = data.get('config_path')
        
        if not config_path:
            return jsonify({"status": "error", "message": "config_path is required"}), 400
            
        result = mcp_server.predict(config_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/setting', methods=['GET'])
def get_config():
    """설정 조회"""
    try:
        result = mcp_server.get_config()
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/setting', methods=['PUT'])
def update_config():
    """설정 업데이트"""
    try:
        data = request.get_json() or {}
        result = mcp_server.update_config(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("HTTP MCP Time Series Prediction Server 시작")
    print("서버 주소: http://localhost:9999")
    print("API 문서:")
    print("  POST /init            - 서버 초기화")
    print("  POST /predict         - 예측 실행")
    print("  GET  /setting         - 설정 조회")
    print("  PUT  /setting         - 설정 업데이트")
    print("-" * 50)
    app.run(host='0.0.0.0', port=9999, debug=True) 