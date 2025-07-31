#!/usr/bin/env python3
"""
범용 다운로드/진행률 모니터링 MCP 서버
모든 종류의 파일 다운로드, 설치, 처리 작업의 진행률을 추적하고 시각화
"""

import asyncio
import json
import subprocess
import time
import os
import re
import threading
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import urllib.request
import urllib.parse

class TaskType(Enum):
    """작업 타입"""
    DOWNLOAD = "download"
    OLLAMA_PULL = "ollama_pull"
    FILE_COPY = "file_copy"
    COMPRESSION = "compression"
    INSTALLATION = "installation"
    CUSTOM = "custom"

class TaskStatus(Enum):
    """작업 상태"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ProgressInfo:
    """진행률 정보"""
    task_id: str
    task_name: str
    task_type: TaskType
    status: TaskStatus
    
    # 진행률 데이터
    total_size: int = 0
    completed_size: int = 0
    progress_percent: float = 0.0
    
    # 속도 및 시간
    speed: float = 0.0  # bytes/second
    eta_seconds: int = 0
    elapsed_seconds: float = 0.0
    
    # 메타데이터
    start_time: float = 0
    last_update: float = 0
    error_message: str = ""
    additional_info: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_info is None:
            self.additional_info = {}

class UniversalProgressMonitor:
    """범용 진행률 모니터"""
    
    def __init__(self):
        self.active_tasks: Dict[str, ProgressInfo] = {}
        self.completed_tasks: List[ProgressInfo] = []
        self.monitoring_threads: Dict[str, threading.Thread] = {}
        self._next_task_id = 1
    
    def _generate_task_id(self) -> str:
        """고유 작업 ID 생성"""
        task_id = f"task_{self._next_task_id:04d}"
        self._next_task_id += 1
        return task_id
    
    def _format_size(self, bytes_size: int) -> str:
        """바이트를 읽기 쉬운 형태로 변환"""
        if bytes_size == 0:
            return "0B"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f}{unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f}PB"
    
    def _format_speed(self, bytes_per_second: float) -> str:
        """속도를 읽기 쉬운 형태로 변환"""
        return f"{self._format_size(int(bytes_per_second))}/s"
    
    def _format_time(self, seconds: int) -> str:
        """초를 읽기 쉬운 시간으로 변환"""
        if seconds < 60:
            return f"{seconds}초"
        elif seconds < 3600:
            return f"{seconds//60}분 {seconds%60}초"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}시간 {minutes}분"
    
    def _generate_progress_bar(self, progress: float, width: int = 40) -> str:
        """ASCII progress bar 생성"""
        filled = int(width * progress / 100)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}] {progress:.1f}%"
    
    def start_ollama_pull_task(self, model_name: str) -> str:
        """Ollama 모델 다운로드 작업 시작"""
        task_id = self._generate_task_id()
        
        progress = ProgressInfo(
            task_id=task_id,
            task_name=f"Ollama Pull: {model_name}",
            task_type=TaskType.OLLAMA_PULL,
            status=TaskStatus.RUNNING,
            start_time=time.time(),
            last_update=time.time(),
            additional_info={"model_name": model_name}
        )
        
        self.active_tasks[task_id] = progress
        
        # 모니터링 스레드 시작
        thread = threading.Thread(
            target=self._monitor_ollama_pull,
            args=(task_id, model_name),
            daemon=True
        )
        thread.start()
        self.monitoring_threads[task_id] = thread
        
        return task_id
    
    def start_download_task(self, url: str, destination: str, task_name: str = None) -> str:
        """파일 다운로드 작업 시작"""
        task_id = self._generate_task_id()
        
        if not task_name:
            task_name = f"Download: {os.path.basename(url)}"
        
        progress = ProgressInfo(
            task_id=task_id,
            task_name=task_name,
            task_type=TaskType.DOWNLOAD,
            status=TaskStatus.RUNNING,
            start_time=time.time(),
            last_update=time.time(),
            additional_info={"url": url, "destination": destination}
        )
        
        self.active_tasks[task_id] = progress
        
        # 다운로드 스레드 시작
        thread = threading.Thread(
            target=self._monitor_download,
            args=(task_id, url, destination),
            daemon=True
        )
        thread.start()
        self.monitoring_threads[task_id] = thread
        
        return task_id
    
    def start_custom_task(self, task_name: str, command: List[str], task_type: TaskType = TaskType.CUSTOM) -> str:
        """커스텀 명령어 작업 시작"""
        task_id = self._generate_task_id()
        
        progress = ProgressInfo(
            task_id=task_id,
            task_name=task_name,
            task_type=task_type,
            status=TaskStatus.RUNNING,
            start_time=time.time(),
            last_update=time.time(),
            additional_info={"command": command}
        )
        
        self.active_tasks[task_id] = progress
        
        # 명령어 실행 스레드 시작
        thread = threading.Thread(
            target=self._monitor_command,
            args=(task_id, command),
            daemon=True
        )
        thread.start()
        self.monitoring_threads[task_id] = thread
        
        return task_id
    
    def _monitor_ollama_pull(self, task_id: str, model_name: str):
        """Ollama pull 모니터링"""
        try:
            # curl로 Ollama API 호출
            process = subprocess.Popen([
                'curl', '-X', 'POST', 'http://localhost:11435/api/pull',
                '-d', json.dumps({"name": model_name}),
                '-H', 'Content-Type: application/json'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                
                try:
                    data = json.loads(line.strip())
                    self._update_ollama_progress(task_id, data)
                except json.JSONDecodeError:
                    continue
            
            # 프로세스 완료 확인
            return_code = process.wait()
            
            if task_id in self.active_tasks:
                if return_code == 0:
                    self.active_tasks[task_id].status = TaskStatus.COMPLETED
                    self.active_tasks[task_id].progress_percent = 100.0
                else:
                    self.active_tasks[task_id].status = TaskStatus.FAILED
                    self.active_tasks[task_id].error_message = "Pull failed"
                
                self._move_to_completed(task_id)
                
        except Exception as e:
            if task_id in self.active_tasks:
                self.active_tasks[task_id].status = TaskStatus.FAILED
                self.active_tasks[task_id].error_message = str(e)
                self._move_to_completed(task_id)
    
    def _monitor_download(self, task_id: str, url: str, destination: str):
        """파일 다운로드 모니터링"""
        try:
            def progress_hook(block_num, block_size, total_size):
                if task_id not in self.active_tasks:
                    return
                    
                progress = self.active_tasks[task_id]
                progress.total_size = total_size
                progress.completed_size = block_num * block_size
                progress.last_update = time.time()
                
                if total_size > 0:
                    progress.progress_percent = min((progress.completed_size / total_size) * 100, 100)
                
                # 속도 계산
                elapsed = progress.last_update - progress.start_time
                if elapsed > 0:
                    progress.speed = progress.completed_size / elapsed
                    
                    # ETA 계산
                    if progress.speed > 0:
                        remaining = total_size - progress.completed_size
                        progress.eta_seconds = int(remaining / progress.speed)
                
                progress.elapsed_seconds = elapsed
                self._print_progress(progress)
            
            # 다운로드 실행
            urllib.request.urlretrieve(url, destination, progress_hook)
            
            if task_id in self.active_tasks:
                self.active_tasks[task_id].status = TaskStatus.COMPLETED
                self.active_tasks[task_id].progress_percent = 100.0
                self._move_to_completed(task_id)
                
        except Exception as e:
            if task_id in self.active_tasks:
                self.active_tasks[task_id].status = TaskStatus.FAILED
                self.active_tasks[task_id].error_message = str(e)
                self._move_to_completed(task_id)
    
    def _monitor_command(self, task_id: str, command: List[str]):
        """커스텀 명령어 모니터링"""
        try:
            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            
            # 프로세스 실행 중 상태 업데이트
            while process.poll() is None:
                if task_id in self.active_tasks:
                    progress = self.active_tasks[task_id] 
                    progress.last_update = time.time()
                    progress.elapsed_seconds = progress.last_update - progress.start_time
                    
                time.sleep(1)
            
            return_code = process.wait()
            
            if task_id in self.active_tasks:
                if return_code == 0:
                    self.active_tasks[task_id].status = TaskStatus.COMPLETED
                    self.active_tasks[task_id].progress_percent = 100.0
                else:
                    self.active_tasks[task_id].status = TaskStatus.FAILED
                    stderr_output = process.stderr.read()
                    self.active_tasks[task_id].error_message = stderr_output[:200]
                
                self._move_to_completed(task_id)
                
        except Exception as e:
            if task_id in self.active_tasks:
                self.active_tasks[task_id].status = TaskStatus.FAILED
                self.active_tasks[task_id].error_message = str(e)
                self._move_to_completed(task_id)
    
    def _update_ollama_progress(self, task_id: str, data: Dict[str, Any]):
        """Ollama 진행률 업데이트"""
        if task_id not in self.active_tasks:
            return
            
        progress = self.active_tasks[task_id]
        progress.last_update = time.time()
        progress.elapsed_seconds = progress.last_update - progress.start_time
        
        # 상태 업데이트
        status = data.get("status", "")
        if "completed" in data and "total" in data:
            progress.total_size = data["total"]
            progress.completed_size = data["completed"]
            
            if progress.total_size > 0:
                progress.progress_percent = (progress.completed_size / progress.total_size) * 100
                
                # 속도 계산
                if progress.elapsed_seconds > 0:
                    progress.speed = progress.completed_size / progress.elapsed_seconds
                    
                    # ETA 계산
                    if progress.speed > 0:
                        remaining = progress.total_size - progress.completed_size
                        progress.eta_seconds = int(remaining / progress.speed)
        
        # 상태별 처리
        if status == "success":
            progress.status = TaskStatus.COMPLETED
            progress.progress_percent = 100.0
        elif status in ["error", "failed"]:
            progress.status = TaskStatus.FAILED
            progress.error_message = data.get("error", "Unknown error")
        
        self._print_progress(progress)
    
    def _print_progress(self, progress: ProgressInfo, suppress_frequent_updates: bool = True):
        """진행률 출력 (Claude Code 환경 최적화)"""
        # 너무 자주 업데이트하지 않도록 제한 (1초마다만)
        if suppress_frequent_updates:
            current_time = time.time()
            if hasattr(progress, '_last_print_time'):
                if current_time - progress._last_print_time < 1.0:  # 1초 미만이면 스킵
                    return
            progress._last_print_time = current_time
        
        if progress.total_size > 0:
            bar = self._generate_progress_bar(progress.progress_percent)
            size_info = f"{self._format_size(progress.completed_size)}/{self._format_size(progress.total_size)}"
            speed_info = self._format_speed(progress.speed) if progress.speed > 0 else "계산 중..."
            eta_info = self._format_time(progress.eta_seconds) if progress.eta_seconds > 0 else "계산 중..."
            
            # Claude Code에서는 새 라인으로 출력하되, 진행률만 표시
            print(f"📥 {progress.task_name}: {progress.progress_percent:.1f}% | {size_info} | {speed_info} | ETA: {eta_info}")
        else:
            elapsed_str = self._format_time(int(progress.elapsed_seconds))
            print(f"🔄 {progress.task_name}: 진행 중... ({elapsed_str})")
    
    def _move_to_completed(self, task_id: str):
        """완료된 작업을 완료 목록으로 이동"""
        if task_id in self.active_tasks:
            completed_task = self.active_tasks[task_id]
            self.completed_tasks.append(completed_task)
            del self.active_tasks[task_id]
            
            # 스레드 정리
            if task_id in self.monitoring_threads:
                del self.monitoring_threads[task_id]
            
            # 최종 상태 출력
            if completed_task.status == TaskStatus.COMPLETED:
                print(f"\n✅ {completed_task.task_name} 완료! ({self._format_time(int(completed_task.elapsed_seconds))})")
            else:
                print(f"\n❌ {completed_task.task_name} 실패: {completed_task.error_message}")
    
    def get_all_tasks(self) -> Dict[str, Any]:
        """모든 작업 상태 조회"""
        return {
            "active_tasks": [asdict(task) for task in self.active_tasks.values()],
            "completed_tasks": [asdict(task) for task in self.completed_tasks[-10:]],  # 최근 10개만
            "summary": {
                "active_count": len(self.active_tasks),
                "completed_count": len(self.completed_tasks),
                "overall_progress": self._calculate_overall_progress()
            }
        }
    
    def _calculate_overall_progress(self) -> float:
        """전체 진행률 계산"""
        if not self.active_tasks:
            return 100.0
            
        total_progress = sum(task.progress_percent for task in self.active_tasks.values())
        return total_progress / len(self.active_tasks)
    
    def cancel_task(self, task_id: str) -> bool:
        """작업 취소"""
        if task_id in self.active_tasks:
            self.active_tasks[task_id].status = TaskStatus.CANCELLED
            self._move_to_completed(task_id)
            return True
        return False
    
    def get_task_status(self, task_id: str) -> Optional[ProgressInfo]:
        """특정 작업 상태 조회"""
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
        
        for completed_task in self.completed_tasks:
            if completed_task.task_id == task_id:
                return completed_task
                
        return None

# 전역 모니터 인스턴스
global_monitor = UniversalProgressMonitor()

# 편의 함수들
def start_ollama_pull(model_name: str) -> str:
    """Ollama 모델 다운로드 시작"""
    return global_monitor.start_ollama_pull_task(model_name)

def start_download(url: str, destination: str, task_name: str = None) -> str:
    """파일 다운로드 시작"""
    return global_monitor.start_download_task(url, destination, task_name)

def start_command(task_name: str, command: List[str], task_type: TaskType = TaskType.CUSTOM) -> str:
    """커스텀 명령어 시작"""
    return global_monitor.start_custom_task(task_name, command, task_type)

def get_all_progress() -> Dict[str, Any]:
    """모든 진행률 조회"""
    return global_monitor.get_all_tasks()

def get_task_progress(task_id: str) -> Optional[Dict[str, Any]]:
    """특정 작업 진행률 조회"""
    task = global_monitor.get_task_status(task_id)
    return asdict(task) if task else None

def cancel_task(task_id: str) -> bool:
    """작업 취소"""
    return global_monitor.cancel_task(task_id)

# 테스트용 함수
def test_monitor():
    """모니터 테스트"""
    print("🎯 Universal Progress Monitor")
    print("=" * 50)
    
    # 현재 qwen3:14b 다운로드가 진행 중인지 확인
    print("현재 진행 중인 작업 확인...")
    
    # 예시: qwen3:14b 모니터링 시작 (이미 진행 중이면 감지)
    task_id = start_ollama_pull("qwen3:14b")
    print(f"작업 ID: {task_id}")
    
    # 진행 상황 모니터링
    try:
        while True:
            time.sleep(2)
            progress = get_task_progress(task_id)
            if progress and progress["status"] in ["completed", "failed", "cancelled"]:
                break
                
    except KeyboardInterrupt:
        print("\n작업 모니터링 중단")
        cancel_task(task_id)

if __name__ == "__main__":
    test_monitor()