#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
モジュールテストスクリプト
Speech Tension Detector Module の総合テスト
"""

import sys
import os
import time
from pathlib import Path

# モジュールのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent))

import speech_tension_detector
from speech_tension_detector import SpeechTensionDetector, SpeedOptimizedTensionDetector, ParallelBatchDetector

def test_module_import():
    """モジュールインポートテスト"""
    print("📦 モジュールインポートテスト")
    print("-" * 40)
    
    try:
        print(f"✅ パッケージバージョン: {speech_tension_detector.__version__}")
        print(f"✅ パッケージ作者: {speech_tension_detector.__author__}")
        
        # 主要クラスの確認
        assert SpeechTensionDetector is not None
        assert SpeedOptimizedTensionDetector is not None
        assert ParallelBatchDetector is not None
        
        print("✅ 全ての主要クラスがインポート可能")
        return True
        
    except Exception as e:
        print(f"❌ インポートエラー: {e}")
        return False

def test_detector_initialization():
    """検出器初期化テスト"""
    print("\n🔧 検出器初期化テスト")
    print("-" * 40)
    
    results = []
    
    # 標準検出器
    try:
        detector = SpeechTensionDetector()
        print("✅ 標準検出器: 初期化成功")
        results.append(True)
    except Exception as e:
        print(f"❌ 標準検出器: 初期化失敗 - {e}")
        results.append(False)
    
    # 高速化検出器
    try:
        speed_detector = SpeedOptimizedTensionDetector()
        print("✅ 高速化検出器: 初期化成功")
        results.append(True)
    except Exception as e:
        print(f"❌ 高速化検出器: 初期化失敗 - {e}")
        results.append(False)
    
    # 並列検出器
    try:
        parallel_detector = ParallelBatchDetector()
        print("✅ 並列検出器: 初期化成功")
        results.append(True)
    except Exception as e:
        print(f"❌ 並列検出器: 初期化失敗 - {e}")
        results.append(False)
    
    return all(results)

def test_sample_files():
    """サンプルファイルテスト"""
    print("\n🎵 サンプルファイルテスト")
    print("-" * 40)
    
    sample_dir = Path(__file__).parent.parent / "data" / "samples"
    
    if not sample_dir.exists():
        print(f"❌ サンプルディレクトリが存在しません: {sample_dir}")
        return False
    
    sample_files = list(sample_dir.glob("*.wav"))
    
    if not sample_files:
        print(f"❌ サンプルファイルが見つかりません")
        return False
    
    print(f"✅ サンプルディレクトリ: {sample_dir}")
    print(f"✅ サンプルファイル数: {len(sample_files)}")
    
    # 各カテゴリのファイル確認
    categories = ['Low', 'Neutral', 'High']
    for category in categories:
        category_files = [f for f in sample_files if category in f.name]
        print(f"  - {category}テンション: {len(category_files)}ファイル")
    
    return True

def test_detection_functionality():
    """検出機能テスト"""
    print("\n🎯 検出機能テスト")
    print("-" * 40)
    
    sample_dir = Path(__file__).parent.parent / "data" / "samples"
    sample_files = list(sample_dir.glob("*.wav"))
    
    if not sample_files:
        print("❌ テスト用サンプルファイルがありません")
        return False
    
    test_file = sample_files[0]
    print(f"テストファイル: {test_file.name}")
    
    results = []
    
    # 標準検出器テスト
    try:
        detector = SpeechTensionDetector()
        start_time = time.time()
        result = detector.detect_tension(str(test_file))
        processing_time = time.time() - start_time
        
        if isinstance(result, dict) and 'tension_score' in result:
            score = result['tension_score']
            confidence = result.get('confidence', 0)
            interpretation = result.get('interpretation', 'N/A')
            
            print(f"✅ 標準検出器:")
            print(f"   テンション値: {score:.3f}")
            print(f"   信頼度: {confidence:.3f}")
            print(f"   解釈: {interpretation}")
            print(f"   処理時間: {processing_time:.2f}秒")
            
            # 妥当性チェック
            if 0 <= score <= 1:
                results.append(True)
            else:
                print(f"❌ 無効なテンション値: {score}")
                results.append(False)
        else:
            print(f"❌ 無効な結果形式: {result}")
            results.append(False)
            
    except Exception as e:
        print(f"❌ 標準検出器エラー: {e}")
        results.append(False)
    
    # シンプルAPI テスト
    try:
        detector = SpeechTensionDetector()
        score = detector.predict_tension(str(test_file))
        
        if isinstance(score, (int, float)) and 0 <= score <= 1:
            print(f"✅ シンプルAPI: {score:.3f}")
            results.append(True)
        else:
            print(f"❌ シンプルAPI無効値: {score}")
            results.append(False)
            
    except Exception as e:
        print(f"❌ シンプルAPIエラー: {e}")
        results.append(False)
    
    return all(results)

def test_batch_processing():
    """バッチ処理テスト"""
    print("\n🚀 バッチ処理テスト")
    print("-" * 40)
    
    sample_dir = Path(__file__).parent.parent / "data" / "samples"
    sample_files = list(sample_dir.glob("*.wav"))
    
    if len(sample_files) < 2:
        print("❌ バッチテスト用ファイルが不足")
        return False
    
    test_files = [str(f) for f in sample_files[:3]]  # 最大3ファイル
    
    try:
        parallel_detector = ParallelBatchDetector()
        start_time = time.time()
        results = parallel_detector.process_batch_files(test_files)
        processing_time = time.time() - start_time
        
        print(f"✅ バッチ処理完了:")
        print(f"   ファイル数: {len(test_files)}")
        print(f"   処理時間: {processing_time:.2f}秒")
        print(f"   平均時間: {processing_time/len(test_files):.2f}秒/ファイル")
        
        # 結果検証
        valid_results = 0
        for i, (file_path, result) in enumerate(zip(test_files, results)):
            file_name = Path(file_path).name
            if isinstance(result, dict) and 'tension_score' in result:
                score = result['tension_score']
                if 0 <= score <= 1:
                    valid_results += 1
                    print(f"   {i+1}. {file_name}: {score:.3f}")
                else:
                    print(f"   {i+1}. {file_name}: 無効値 {score}")
            else:
                print(f"   {i+1}. {file_name}: エラー")
        
        if valid_results == len(test_files):
            print(f"✅ 全ファイル正常処理完了")
            return True
        else:
            print(f"❌ {len(test_files) - valid_results}ファイルでエラー")
            return False
            
    except Exception as e:
        print(f"❌ バッチ処理エラー: {e}")
        return False

def main():
    """メインテスト関数"""
    print("🧪 Speech Tension Detector Module - 総合テスト")
    print("=" * 60)
    
    tests = [
        ("モジュールインポート", test_module_import),
        ("検出器初期化", test_detector_initialization),
        ("サンプルファイル確認", test_sample_files),
        ("検出機能", test_detection_functionality),
        ("バッチ処理", test_batch_processing),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
            
            if result:
                print(f"\n✅ {test_name}: 成功")
            else:
                print(f"\n❌ {test_name}: 失敗")
                
        except Exception as e:
            print(f"\n💥 {test_name}: 例外発生 - {e}")
            results.append(False)
    
    # 最終結果
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 全テスト成功! ({passed}/{total})")
        print("モジュールは正常に動作しています。")
    else:
        print(f"⚠️  一部テスト失敗 ({passed}/{total})")
        print("エラーメッセージを確認してください。")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)