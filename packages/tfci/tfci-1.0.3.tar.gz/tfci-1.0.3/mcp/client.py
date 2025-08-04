#!/usr/bin/env python3
"""
MCP Client - 라이브러리처럼 사용하는 MCP 클라이언트
"""

import requests
import json
from typing import Dict, Any

class MCPClient:
    """라이브러리처럼 사용하는 MCP 클라이언트"""
    
    def __init__(self, server_url: str = "http://localhost:9999"):
        """
        MCP 클라이언트 초기화
        
        Args:
            server_url (str): MCP 서버 URL (기본값: http://localhost:9999)
        """
        self.server_url = server_url
        
    def predict(self, config_path: str) -> Dict[str, Any]:
        """
        config 파일 경로로 예측 실행
        
        Args:
            config_path (str): 설정 파일 경로
            
        Returns:
            Dict[str, Any]: 예측 결과
        """
        try:
            # HTTP 요청으로 예측 실행
            response = requests.post(
                f"{self.server_url}/predict",
                json={"config_path": config_path},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "message": f"HTTP {response.status_code}: {response.text}"}
                
        except requests.exceptions.ConnectionError:
            return {"status": "error", "message": f"서버에 연결할 수 없습니다: {self.server_url}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def initialize(self, config_path: str = "config.yaml") -> Dict[str, Any]:
        """
        서버 초기화
        
        Args:
            config_path (str): 초기화용 설정 파일 경로
            
        Returns:
            Dict[str, Any]: 초기화 결과
        """
        try:
            response = requests.post(
                f"{self.server_url}/init",
                json={"config_path": config_path},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "message": f"HTTP {response.status_code}: {response.text}"}
                
        except requests.exceptions.ConnectionError:
            return {"status": "error", "message": f"서버에 연결할 수 없습니다: {self.server_url}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_config(self) -> Dict[str, Any]:
        """
        현재 설정 조회
        
        Returns:
            Dict[str, Any]: 현재 설정
        """
        try:
            response = requests.get(f"{self.server_url}/setting")
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "message": f"HTTP {response.status_code}: {response.text}"}
                
        except requests.exceptions.ConnectionError:
            return {"status": "error", "message": f"서버에 연결할 수 없습니다: {self.server_url}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

# 사용 예시
if __name__ == "__main__":
    # 클라이언트 생성
    client = MCPClient("http://localhost:9999")
    
    # 서버 초기화
    print("서버 초기화 중...")
    init_result = client.initialize("config.yaml")
    print(f"초기화 결과: {init_result}")
    
    # 여러 config 파일로 예측
    configs = ["config.yaml", "config2.yaml", "config3.yaml", "config4.yaml"]
    
    for config in configs:
        print(f"\n{config} 예측 중...")
        result = client.predict(config)
        print(f"결과: {result}") 