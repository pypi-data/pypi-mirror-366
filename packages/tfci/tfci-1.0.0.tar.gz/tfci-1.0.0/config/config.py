import yaml
import os

def load_config(path: str):
    """YAML 설정 파일 로드 및 검증"""
    if not os.path.exists(path):
        raise FileNotFoundError("config.yaml 파일이 존재하지 않습니다.")

    with open(path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)

    # 필수 키 체크
    required_keys = ["input", "output", "prediction"]
    for key in required_keys:
        if key not in config:
            raise KeyError(f"config.yaml에 {key} 섹션이 누락되었습니다.")

    return config