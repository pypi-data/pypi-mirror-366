# -*- coding: utf-8 -*-
"""
Command Line Interface for Speech Tension Detector
音声テンション検出のコマンドラインインターフェース
"""

import argparse
import sys
import os
import time
from pathlib import Path

from .core.detector import SpeechTensionDetector
from .core.speed_optimized import SpeedOptimizedTensionDetector
from .core.parallel_batch import ParallelBatchDetector

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='音声テンション検出システム',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 単一ファイル処理
  speech-tension-detect sample.wav
  
  # 高速処理
  speech-tension-detect sample.wav --speed-optimized
  
  # 詳細出力
  speech-tension-detect sample.wav --verbose
  
  # 並列バッチ処理
  speech-tension-detect dir/*.wav --parallel
        """
    )
    
    parser.add_argument('input', 
                       help='音声ファイルパスまたはディレクトリ')
    
    parser.add_argument('--speed-optimized', '-s', 
                       action='store_true',
                       help='高速化処理を使用')
    
    parser.add_argument('--parallel', '-p',
                       action='store_true', 
                       help='並列処理を使用')
    
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='詳細出力')
    
    parser.add_argument('--version',
                       action='version',
                       version='Speech Tension Detector Module 1.0.0')
    
    args = parser.parse_args()
    
    try:
        # 入力ファイル・ディレクトリの確認
        input_path = Path(args.input)
        
        if input_path.is_file():
            # 単一ファイル処理
            process_single_file(input_path, args)
        elif input_path.is_dir():
            # ディレクトリ内のWAVファイル処理
            wav_files = list(input_path.glob('*.wav'))
            if not wav_files:
                print(f"エラー: {input_path} にWAVファイルが見つかりません")
                return 1
            
            if args.parallel:
                process_parallel_batch(wav_files, args)
            else:
                for wav_file in wav_files:
                    process_single_file(wav_file, args)
        else:
            print(f"エラー: {args.input} は有効なファイルまたはディレクトリではありません")
            return 1
            
        return 0
        
    except KeyboardInterrupt:
        print("\n処理が中断されました")
        return 1
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return 1

def process_single_file(file_path: Path, args):
    """単一ファイル処理"""
    print(f"=" * 50)
    print(f"音声テンション解析: {file_path.name}")
    print(f"=" * 50)
    
    start_time = time.time()
    
    try:
        # 検出器選択
        if args.speed_optimized:
            detector = SpeedOptimizedTensionDetector()
            print("高速化検出器を使用")
        else:
            detector = SpeechTensionDetector()
            print("標準検出器を使用")
        
        # テンション検出実行
        result = detector.detect_tension(str(file_path), verbose=args.verbose)
        
        # 処理時間計算
        processing_time = time.time() - start_time
        
        # 結果表示
        print(f"\n📊 解析結果")
        print(f"=" * 50)
        print(f"テンション値: {result['tension_score']:.3f}")
        print(f"信頼度: {result['confidence']:.3f}")
        print(f"解釈: {result['interpretation']}")
        
        if 'spectral_tilt' in result and result['spectral_tilt'] != 0:
            print(f"スペクトラル傾斜: {result['spectral_tilt']:.1f} dB")
        
        print(f"処理時間: {processing_time:.2f}秒")
        print(f"音声長: {result.get('audio_duration', 0):.2f}秒")
        
        if args.verbose and 'detailed_features' in result:
            print(f"\n🔍 詳細情報")
            print(f"-" * 30)
            detailed = result['detailed_features']
            
            if 'prosodic' in detailed:
                prosodic = detailed['prosodic']
                if 'f0_mean' in prosodic and prosodic['f0_mean'] > 0:
                    print(f"平均F0: {prosodic['f0_mean']:.1f} Hz")
                if 'intensity_mean' in prosodic:
                    print(f"平均強度: {prosodic['intensity_mean']:.1f} dB")
                if 'hnr_mean' in prosodic:
                    print(f"HNR: {prosodic['hnr_mean']:.1f} dB")
            
            if 'classifier_predictions' in detailed:
                pred = detailed['classifier_predictions']
                print(f"分類器予測:")
                for name, value in pred.items():
                    if isinstance(value, (int, float)):
                        print(f"  {name}: {value:.3f}")
        
    except Exception as e:
        print(f"処理エラー: {e}")

def process_parallel_batch(wav_files: list, args):
    """並列バッチ処理"""
    print(f"🚀 並列バッチ処理開始")
    print(f"ファイル数: {len(wav_files)}")
    print(f"=" * 50)
    
    start_time = time.time()
    
    try:
        detector = ParallelBatchDetector()
        
        # ファイルパスを文字列に変換
        file_paths = [str(f) for f in wav_files]
        
        # 並列処理実行
        results = detector.process_batch_files(file_paths)
        
        # 処理時間計算
        total_time = time.time() - start_time
        
        # 結果表示
        print(f"\n📊 バッチ処理結果")
        print(f"=" * 50)
        
        for i, (file_path, result) in enumerate(zip(file_paths, results)):
            file_name = Path(file_path).name
            
            if isinstance(result, dict) and 'tension_score' in result:
                score = result['tension_score']
                interpretation = result.get('interpretation', '')
                print(f"{i+1:2d}. {file_name:<25} | {score:.3f} | {interpretation}")
            else:
                print(f"{i+1:2d}. {file_name:<25} | エラー")
        
        print(f"\n⏱️  処理時間: {total_time:.2f}秒")
        print(f"平均処理時間: {total_time/len(wav_files):.2f}秒/ファイル")
        
        # 統計表示
        valid_scores = []
        for result in results:
            if isinstance(result, dict) and 'tension_score' in result:
                valid_scores.append(result['tension_score'])
        
        if valid_scores:
            import numpy as np
            print(f"\n📈 統計情報")
            print(f"平均テンション: {np.mean(valid_scores):.3f}")
            print(f"最小テンション: {np.min(valid_scores):.3f}")
            print(f"最大テンション: {np.max(valid_scores):.3f}")
            print(f"標準偏差: {np.std(valid_scores):.3f}")
        
    except Exception as e:
        print(f"並列処理エラー: {e}")

if __name__ == '__main__':
    sys.exit(main())