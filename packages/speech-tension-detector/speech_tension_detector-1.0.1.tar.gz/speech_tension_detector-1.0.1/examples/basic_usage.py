#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本的な使用例
Speech Tension Detector Module の基本的な使い方
"""

import sys
import os
from pathlib import Path

# モジュールのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from speech_tension_detector import SpeechTensionDetector, SpeedOptimizedTensionDetector, ParallelBatchDetector

def main():
    """基本的な使用例のデモ"""
    
    print("🎯 音声テンション検出モジュール - 基本使用例")
    print("=" * 60)
    
    # サンプルデータのパス
    sample_dir = Path(__file__).parent.parent / "data" / "samples"
    
    if not sample_dir.exists():
        print(f"エラー: サンプルディレクトリが見つかりません: {sample_dir}")
        return
    
    # サンプルファイルを探す
    sample_files = list(sample_dir.glob("*.wav"))
    if not sample_files:
        print(f"エラー: サンプルファイルが見つかりません: {sample_dir}")
        return
    
    print(f"サンプルディレクトリ: {sample_dir}")
    print(f"発見されたファイル数: {len(sample_files)}")
    print()
    
    # 1. 標準検出器のテスト
    print("1️⃣ 標準検出器テスト")
    print("-" * 30)
    
    try:
        detector = SpeechTensionDetector()
        
        # 最初のサンプルファイルをテスト
        test_file = sample_files[0]
        print(f"テストファイル: {test_file.name}")
        
        result = detector.detect_tension(str(test_file))
        
        print(f"✅ テンション値: {result['tension_score']:.3f}")
        print(f"✅ 信頼度: {result['confidence']:.3f}")
        print(f"✅ 解釈: {result['interpretation']}")
        print()
        
    except Exception as e:
        print(f"❌ 標準検出器エラー: {e}")
        print()
    
    # 2. 高速化検出器のテスト
    print("2️⃣ 高速化検出器テスト")
    print("-" * 30)
    
    try:
        speed_detector = SpeedOptimizedTensionDetector()
        
        result = speed_detector.detect_tension(str(test_file))
        
        print(f"✅ テンション値: {result['tension_score']:.3f}")
        print(f"✅ 信頼度: {result['confidence']:.3f}")
        print(f"✅ 解釈: {result['interpretation']}")
        print()
        
    except Exception as e:
        print(f"❌ 高速化検出器エラー: {e}")
        print()
    
    # 3. 並列バッチ処理のテスト
    print("3️⃣ 並列バッチ処理テスト")
    print("-" * 30)
    
    try:
        parallel_detector = ParallelBatchDetector()
        
        # 最大3ファイルでテスト
        test_files = [str(f) for f in sample_files[:3]]
        print(f"テストファイル数: {len(test_files)}")
        
        results = parallel_detector.process_batch_files(test_files)
        
        for i, (file_path, result) in enumerate(zip(test_files, results)):
            file_name = Path(file_path).name
            if isinstance(result, dict) and 'tension_score' in result:
                print(f"  {i+1}. {file_name}: {result['tension_score']:.3f} - {result['interpretation']}")
            else:
                print(f"  {i+1}. {file_name}: エラー")
        print()
        
    except Exception as e:
        print(f"❌ 並列処理エラー: {e}")
        print()
    
    # 4. シンプルAPIのテスト
    print("4️⃣ シンプルAPIテスト")
    print("-" * 30)
    
    try:
        detector = SpeechTensionDetector()
        
        # シンプルな予測
        tension_score = detector.predict_tension(str(test_file))
        print(f"✅ シンプル予測結果: {tension_score:.3f}")
        print()
        
    except Exception as e:
        print(f"❌ シンプルAPIエラー: {e}")
        print()
    
    print("🎉 全てのテストが完了しました！")

if __name__ == '__main__':
    main()