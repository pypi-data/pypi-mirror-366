"""
音声テンション検出モジュール
Speech Tension Detector Module

音声ファイルから話者の緊張度・テンションを検出するPythonモジュール
"""

__version__ = "1.0.1"
__author__ = "hiroshi-tamura"

from .core.detector import SpeechTensionDetector
from .core.speed_optimized import SpeedOptimizedTensionDetector
from .core.parallel_batch import ParallelBatchDetector

__all__ = [
    "SpeechTensionDetector",
    "SpeedOptimizedTensionDetector", 
    "ParallelBatchDetector"
]