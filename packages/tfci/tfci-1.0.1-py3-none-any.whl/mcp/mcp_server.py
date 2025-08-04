#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Server for Time Series Prediction
"""

import json
import sys
import traceback
from typing import Any, Dict, List, Optional
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import load_config
from core.predictor import Predictor

class MCPServer:
    def __init__(self):
        self.predictor = None
        self.config = None

    def initialize(self, config_path: str = "config.yaml") -> Dict[str, Any]:
        """서버 초기화"""
        try:
            print(f"[INFO] MCP 서버 초기화: {config_path}")
            self.config = load_config(config_path)
            self.predictor = Predictor(self.config)
            return {"status": "success", "message": "MCP 서버 초기화 완료"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def predict(self, config_path: str) -> Dict[str, Any]:
        """config 파일 경로를 받아서 예측 실행"""
        try:
            print(f"[INFO] MCP 예측 시작: {config_path}")
            
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

def handle_request(server: MCPServer, request: Dict[str, Any]) -> Dict[str, Any]:
    """JSON-RPC 요청 처리"""
    try:
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        if method == "initialize":
            config_path = params.get("config_path", "config.yaml")
            result = server.initialize(config_path)
        elif method == "predict":
            config_path = params.get("config_path")
            if not config_path:
                return {"error": {"code": -32602, "message": "config_path is required"}}
            result = server.predict(config_path)
        elif method == "get_config":
            result = server.get_config()
        elif method == "update_config":
            result = server.update_config(params.get("config", {}))
        else:
            return {"error": {"code": -32601, "message": f"Method {method} not found"}}

        return {"jsonrpc": "2.0", "result": result, "id": request_id}

    except Exception as e:
        return {"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}, "id": request.get("id")}

def main():
    print("MCP Time Series Prediction Server 시작")
    print("JSON-RPC 요청을 stdin으로 받습니다.")
    print("종료하려면 Ctrl+C를 누르세요.")
    print("-" * 50)

    server = MCPServer()

    try:
        while True:
            line = input()
            if not line:
                continue

            try:
                request = json.loads(line)
                response = handle_request(server, request)
                print(json.dumps(response, ensure_ascii=False))
                sys.stdout.flush()
            except json.JSONDecodeError:
                print(json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None}))
                sys.stdout.flush()

    except KeyboardInterrupt:
        print("\n[INFO] MCP 서버가 종료되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] 서버 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 