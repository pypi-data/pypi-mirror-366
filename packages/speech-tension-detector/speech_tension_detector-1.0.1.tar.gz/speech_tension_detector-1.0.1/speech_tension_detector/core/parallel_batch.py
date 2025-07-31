#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
並列バッチ音声テンション検出器
複数音声ファイルの同時並列処理
"""

import os
import sys
import time
import numpy as np
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 高速化検出器を相対インポート
from .speed_optimized import SpeedOptimizedTensionDetector

class ParallelBatchDetector:
    """並列バッチ処理音声テンション検出器"""
    
    def __init__(self, max_workers=None):
        """
        Args:
            max_workers (int): 最大並列ワーカー数（Noneの場合はCPUコア数）
        """
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        print(f"並列バッチ検出器初期化: 最大{self.max_workers}並列")
        
        # 検出器プール（スレッドローカル）
        self._detector_pool = {}
        self._pool_lock = threading.Lock()
        
    def _get_detector(self):
        """スレッドローカル検出器取得"""
        thread_id = threading.get_ident()
        
        if thread_id not in self._detector_pool:
            with self._pool_lock:
                if thread_id not in self._detector_pool:
                    self._detector_pool[thread_id] = SpeedOptimizedTensionDetector()
        
        return self._detector_pool[thread_id]
    
    def process_single_audio(self, audio_path):
        """単一音声ファイル処理（並列実行用）"""
        try:
            start_time = time.time()
            
            # スレッドローカル検出器取得
            detector = self._get_detector()
            
            # テンション検出
            tension, confidence, diagnostics = detector.predict_tension_fast(audio_path)
            
            processing_time = time.time() - start_time
            
            # 解釈
            if tension < 0.333:
                interpretation = "低テンション（小声・ささやき）"
            elif tension < 0.666:
                interpretation = "中テンション（通常の発話）"
            else:
                interpretation = "高テンション（叫び声・興奮状態）"
            
            return {
                'file': os.path.basename(audio_path),
                'path': audio_path,
                'tension': tension,
                'confidence': confidence,
                'interpretation': interpretation,
                'processing_time': processing_time,
                'thread_id': threading.get_ident(),
                'success': True,
                'error': None
            }
            
        except Exception as e:
            return {
                'file': os.path.basename(audio_path),
                'path': audio_path,
                'tension': None,
                'confidence': None,
                'interpretation': f"エラー: {str(e)}",
                'processing_time': 0,
                'thread_id': threading.get_ident(),
                'success': False,
                'error': str(e)
            }
    
    def process_batch_parallel(self, audio_paths, show_progress=True):
        """複数音声ファイルの並列バッチ処理"""
        print(f"並列バッチ処理開始: {len(audio_paths)}ファイル, {self.max_workers}並列")
        batch_start_time = time.time()
        
        results = []
        completed_count = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 全タスクを並列実行
            future_to_path = {
                executor.submit(self.process_single_audio, path): path 
                for path in audio_paths
            }
            
            # 完了順に結果を取得
            for future in as_completed(future_to_path):
                result = future.result()
                results.append(result)
                completed_count += 1
                
                if show_progress:
                    print(f"[{completed_count}/{len(audio_paths)}] {result['file']}: "
                          f"{result['tension']:.3f} ({result['processing_time']:.2f}s, "
                          f"Thread-{result['thread_id']})")
        
        batch_time = time.time() - batch_start_time
        
        # 結果を元の順序に並び替え
        path_to_result = {result['path']: result for result in results}
        ordered_results = [path_to_result[path] for path in audio_paths]
        
        # 統計計算
        successful_results = [r for r in results if r['success']]
        total_processing_time = sum(r['processing_time'] for r in successful_results)
        avg_processing_time = total_processing_time / len(successful_results) if successful_results else 0
        parallel_efficiency = (total_processing_time / batch_time) if batch_time > 0 else 0
        
        return {
            'results': ordered_results,
            'batch_time': batch_time,
            'total_processing_time': total_processing_time,
            'avg_processing_time': avg_processing_time,
            'parallel_efficiency': parallel_efficiency,
            'success_count': len(successful_results),
            'error_count': len(results) - len(successful_results),
            'speedup_factor': total_processing_time / batch_time if batch_time > 0 else 1
        }
    
    def process_directory_parallel(self, directory_path, pattern="*.wav", show_progress=True):
        """ディレクトリ内の音声ファイル並列処理"""
        directory = Path(directory_path)
        audio_files = list(directory.glob(pattern))
        
        if not audio_files:
            print(f"音声ファイルが見つかりません: {directory_path}/{pattern}")
            return None
        
        print(f"ディレクトリ並列処理: {directory_path}")
        print(f"検出ファイル数: {len(audio_files)}")
        
        return self.process_batch_parallel([str(f) for f in audio_files], show_progress)

def run_parallel_demo():
    """並列処理デモンストレーション"""
    sample_files = [
        "sample/Tension_Low_01.wav",
        "sample/Tension_Low_02.wav", 
        "sample/Tension_Low_03.wav",
        "sample/Tension_Neutral_01.wav",
        "sample/Tension_Neutral_02.wav",
        "sample/Tension_Neutral_03.wav",
        "sample/Tension_High_01.wav",
        "sample/Tension_High_02.wav",
        "sample/Tension_High_03.wav"
    ]
    
    # 存在するファイルのみフィルタ
    existing_files = [f for f in sample_files if os.path.exists(f)]
    
    if not existing_files:
        print("サンプルファイルが見つかりません")
        return
    
    print("=" * 80)
    print("並列バッチ音声テンション検出デモ")
    print("=" * 80)
    
    # 並列処理実行
    detector = ParallelBatchDetector(max_workers=4)  # 4並列
    batch_result = detector.process_batch_parallel(existing_files)
    
    # 結果表示
    print("\n" + "=" * 80)
    print("並列処理結果")
    print("=" * 80)
    print(f"{'No.':<3} {'ファイル名':<22} {'テンション':<10} {'信頼度':<8} {'解釈':<25} {'時間':<8}")
    print("-" * 80)
    
    for i, result in enumerate(batch_result['results'], 1):
        if result['success']:
            print(f"{i:<3} {result['file']:<22} {result['tension']:.3f}      "
                  f"{result['confidence']:.3f}    {result['interpretation'][:23]:<25} "
                  f"{result['processing_time']:.2f}s")
        else:
            print(f"{i:<3} {result['file']:<22} {'ERROR':<10} {'N/A':<8} "
                  f"{result['interpretation'][:23]:<25} {'N/A':<8}")
    
    # 統計表示
    print("-" * 80)
    print(f"成功: {batch_result['success_count']}/{len(existing_files)}")
    print(f"並列処理時間: {batch_result['batch_time']:.2f}秒")
    print(f"総計算時間: {batch_result['total_processing_time']:.2f}秒")
    print(f"平均処理時間: {batch_result['avg_processing_time']:.2f}秒/サンプル")
    print(f"並列効率: {batch_result['parallel_efficiency']:.1%}")
    print(f"高速化倍率: {batch_result['speedup_factor']:.1f}x")
    
    # 逐次処理との比較
    sequential_time = batch_result['total_processing_time']
    parallel_time = batch_result['batch_time']
    time_saved = sequential_time - parallel_time
    
    print(f"\n** 並列処理効果 **")
    print(f"逐次処理推定時間: {sequential_time:.2f}秒")
    print(f"並列処理実時間: {parallel_time:.2f}秒")
    print(f"時間短縮: {time_saved:.2f}秒 ({time_saved/sequential_time*100:.1f}%削減)")
    
    print("=" * 80)

def main():
    """メイン処理"""
    if len(sys.argv) == 1:
        # デモ実行
        run_parallel_demo()
    elif len(sys.argv) == 2:
        # ディレクトリ処理
        directory = sys.argv[1]
        detector = ParallelBatchDetector()
        result = detector.process_directory_parallel(directory)
        if result:
            print(f"処理完了: {result['success_count']}ファイル, {result['batch_time']:.2f}秒")
    else:
        # 複数ファイル処理
        audio_files = sys.argv[1:]
        detector = ParallelBatchDetector()
        result = detector.process_batch_parallel(audio_files)
        print(f"処理完了: {result['success_count']}ファイル, {result['batch_time']:.2f}秒")

if __name__ == "__main__":
    main()