#!/usr/bin/env python3
"""
스마트 타임아웃 계산기
예상 작업 시간에 따라 적절한 타임아웃을 자동 계산
"""

import math
from typing import Dict, Any, Optional
from enum import Enum

class TaskType(Enum):
    """작업 타입별 기본 설정"""
    QUICK_COMMAND = "quick_command"      # ls, ps 등
    DOWNLOAD_SMALL = "download_small"    # < 100MB
    DOWNLOAD_MEDIUM = "download_medium"  # 100MB - 1GB  
    DOWNLOAD_LARGE = "download_large"    # 1GB - 10GB
    DOWNLOAD_HUGE = "download_huge"      # > 10GB
    MODEL_TRAINING = "model_training"    # ML 모델 훈련
    DATABASE_BACKUP = "database_backup"  # DB 백업/복원
    COMPILATION = "compilation"          # 컴파일 작업

class SmartTimeout:
    """스마트 타임아웃 계산기"""
    
    # 기본 타임아웃 설정 (초)
    BASE_TIMEOUTS = {
        TaskType.QUICK_COMMAND: 30,      # 30초
        TaskType.DOWNLOAD_SMALL: 300,    # 5분
        TaskType.DOWNLOAD_MEDIUM: 1800,  # 30분
        TaskType.DOWNLOAD_LARGE: 3600,   # 1시간
        TaskType.DOWNLOAD_HUGE: 7200,    # 2시간
        TaskType.MODEL_TRAINING: 10800,  # 3시간
        TaskType.DATABASE_BACKUP: 3600,  # 1시간
        TaskType.COMPILATION: 1800       # 30분
    }
    
    # 안전 범위 (최소/최대 타임아웃)
    MIN_TIMEOUT = 30      # 최소 30초
    MAX_TIMEOUT = 21600   # 최대 6시간
    
    @staticmethod
    def calculate_download_timeout(file_size_mb: float, expected_speed_mbps: float = 5.0, buffer_factor: float = 2.0) -> int:
        """
        파일 다운로드 타임아웃 계산
        
        Args:
            file_size_mb: 파일 크기 (MB)
            expected_speed_mbps: 예상 다운로드 속도 (MB/s)
            buffer_factor: 안전 버퍼 (기본 2배)
        
        Returns:
            타임아웃 시간 (초)
        """
        if file_size_mb <= 0:
            return SmartTimeout.BASE_TIMEOUTS[TaskType.QUICK_COMMAND]
        
        # 기본 다운로드 시간 계산
        estimated_seconds = file_size_mb / expected_speed_mbps
        
        # 버퍼 적용
        timeout_seconds = int(estimated_seconds * buffer_factor)
        
        # 안전 범위 내로 제한
        timeout_seconds = max(SmartTimeout.MIN_TIMEOUT, min(timeout_seconds, SmartTimeout.MAX_TIMEOUT))
        
        return timeout_seconds
    
    @staticmethod
    def calculate_ollama_timeout(model_size_gb: float) -> int:
        """
        Ollama 모델 다운로드 타임아웃 계산
        
        Args:
            model_size_gb: 모델 크기 (GB)
            
        Returns:
            타임아웃 시간 (초)
        """
        # Ollama는 보통 느림 (평균 2MB/s 가정)
        file_size_mb = model_size_gb * 1024
        expected_speed_mbps = 2.0  # 보수적 추정
        buffer_factor = 1.5        # 적당한 버퍼
        
        return SmartTimeout.calculate_download_timeout(file_size_mb, expected_speed_mbps, buffer_factor)
    
    @staticmethod
    def get_timeout_for_task(task_type: TaskType, **kwargs) -> int:
        """
        작업 타입별 타임아웃 계산
        
        Args:
            task_type: 작업 타입
            **kwargs: 추가 파라미터 (file_size, model_size 등)
            
        Returns:
            타임아웃 시간 (초)
        """
        if task_type in [TaskType.DOWNLOAD_SMALL, TaskType.DOWNLOAD_MEDIUM, 
                        TaskType.DOWNLOAD_LARGE, TaskType.DOWNLOAD_HUGE]:
            file_size_mb = kwargs.get('file_size_mb', 100)
            return SmartTimeout.calculate_download_timeout(file_size_mb)
        
        return SmartTimeout.BASE_TIMEOUTS.get(task_type, 300)  # 기본 5분
    
    @staticmethod
    def format_timeout_display(timeout_seconds: int) -> str:
        """타임아웃을 읽기 쉬운 형태로 변환"""
        if timeout_seconds < 60:
            return f"{timeout_seconds}초"
        elif timeout_seconds < 3600:
            minutes = timeout_seconds // 60
            seconds = timeout_seconds % 60
            return f"{minutes}분 {seconds}초" if seconds > 0 else f"{minutes}분"
        else:
            hours = timeout_seconds // 3600
            minutes = (timeout_seconds % 3600) // 60
            return f"{hours}시간 {minutes}분" if minutes > 0 else f"{hours}시간"
    
    @staticmethod
    def suggest_timeout_for_command(command: str, **hints) -> Dict[str, Any]:
        """
        명령어에 따른 스마트 타임아웃 제안
        
        Args:
            command: 실행할 명령어
            **hints: 힌트 정보 (file_size, model_name 등)
            
        Returns:
            타임아웃 정보 딕셔너리
        """
        # 명령어 분석
        if "ollama pull" in command or "ollama run" in command:
            model_name = hints.get('model_name', '')
            
            # 모델 크기 추정
            if 'qwen3:14b' in model_name or '14b' in model_name:
                model_size_gb = 9.3
            elif 'llama3.1:8b' in model_name or '8b' in model_name:
                model_size_gb = 4.7
            elif 'mistral:7b' in model_name or '7b' in model_name:
                model_size_gb = 4.1
            elif '32b' in model_name:
                model_size_gb = 20.0
            else:
                model_size_gb = 5.0  # 기본값
            
            timeout = SmartTimeout.calculate_ollama_timeout(model_size_gb)
            task_type = TaskType.DOWNLOAD_LARGE
            
        elif "curl" in command and ("-O" in command or "--output" in command):
            file_size_mb = hints.get('file_size_mb', 100)
            timeout = SmartTimeout.calculate_download_timeout(file_size_mb)
            
            if file_size_mb < 100:
                task_type = TaskType.DOWNLOAD_SMALL
            elif file_size_mb < 1024:
                task_type = TaskType.DOWNLOAD_MEDIUM
            else:
                task_type = TaskType.DOWNLOAD_LARGE
                
        elif any(cmd in command for cmd in ["make", "gcc", "g++", "cargo build", "npm run build"]):
            timeout = SmartTimeout.BASE_TIMEOUTS[TaskType.COMPILATION]
            task_type = TaskType.COMPILATION
            
        elif any(cmd in command for cmd in ["mysqldump", "pg_dump", "mongodump"]):
            timeout = SmartTimeout.BASE_TIMEOUTS[TaskType.DATABASE_BACKUP]
            task_type = TaskType.DATABASE_BACKUP
            
        else:
            timeout = SmartTimeout.BASE_TIMEOUTS[TaskType.QUICK_COMMAND]
            task_type = TaskType.QUICK_COMMAND
        
        return {
            'timeout_seconds': timeout,
            'timeout_display': SmartTimeout.format_timeout_display(timeout),
            'task_type': task_type.value,
            'reasoning': f"'{command}' 명령어 분석 결과"
        }

# 편의 함수들
def get_ollama_timeout(model_name: str) -> int:
    """Ollama 모델별 타임아웃 반환"""
    suggestion = SmartTimeout.suggest_timeout_for_command(f"ollama pull {model_name}", model_name=model_name)
    return suggestion['timeout_seconds']

def get_download_timeout(file_size_mb: float, speed_mbps: float = 5.0) -> int:
    """파일 다운로드 타임아웃 반환"""
    return SmartTimeout.calculate_download_timeout(file_size_mb, speed_mbps)

def suggest_timeout(command: str, **hints) -> Dict[str, Any]:
    """명령어별 타임아웃 제안"""
    return SmartTimeout.suggest_timeout_for_command(command, **hints)

# 테스트
if __name__ == "__main__":
    print("🎯 스마트 타임아웃 계산기 테스트")
    print("=" * 50)
    
    # 테스트 케이스들
    test_cases = [
        ("ollama pull qwen3:14b", {"model_name": "qwen3:14b"}),
        ("ollama pull llama3.1:8b", {"model_name": "llama3.1:8b"}),
        ("curl -O https://example.com/bigfile.zip", {"file_size_mb": 2048}),
        ("make -j4", {}),
        ("ls -la", {}),
        ("python train_model.py", {})
    ]
    
    for command, hints in test_cases:
        result = suggest_timeout(command, **hints)
        print(f"명령어: {command}")
        print(f"  타임아웃: {result['timeout_display']} ({result['timeout_seconds']}초)")
        print(f"  작업 타입: {result['task_type']}")
        print(f"  이유: {result['reasoning']}")
        print()
    
    # qwen3:14b 다운로드 시간 계산
    print("🔍 qwen3:14b 다운로드 예상:")
    timeout = get_ollama_timeout("qwen3:14b")
    print(f"  권장 타임아웃: {SmartTimeout.format_timeout_display(timeout)}")
    print(f"  밀리초: {timeout * 1000}")  # Bash tool용