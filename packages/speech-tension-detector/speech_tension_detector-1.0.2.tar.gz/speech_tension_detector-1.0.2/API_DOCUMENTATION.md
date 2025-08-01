# 📚 Speech Tension Detector - 完全APIドキュメント

**バージョン**: 1.0.0  
**作者**: hiroshi-tamura  
**更新日**: 2025年1月31日

## 📋 目次

1. [インストール](#installation)
2. [クイックスタート](#quickstart)
3. [メインAPI](#main-api)
4. [高速化API](#speed-optimized-api)
5. [並列処理API](#parallel-processing-api)
6. [コマンドライン](#command-line)
7. [設定とカスタマイズ](#configuration)
8. [エラーハンドリング](#error-handling)
9. [パフォーマンス最適化](#performance)
10. [実用例](#examples)

---

## 🔧 インストール {#installation}

### PyPIからのインストール
```bash
pip install speech-tension-detector
```

### 開発版インストール
```bash
git clone <repository-url>
cd speech_tension_detector_module
pip install -e .
```

### 必要な依存関係
```bash
# GPU対応版（推奨）
pip install speech-tension-detector[gpu]

# 開発ツール付き
pip install speech-tension-detector[dev]
```

---

## 🚀 クイックスタート {#quickstart}

### 最も簡単な使用方法

```python
from speech_tension_detector import SpeechTensionDetector

# 検出器を作成
detector = SpeechTensionDetector()

# 音声ファイルのテンション値を取得（0.0-1.0）
tension_score = detector.predict_tension("audio.wav")
print(f"テンション: {tension_score:.3f}")

# 詳細情報付きで解析
result = detector.detect_tension("audio.wav", verbose=True)
print(f"テンション: {result['tension_score']:.3f}")
print(f"解釈: {result['interpretation']}")
print(f"信頼度: {result['confidence']:.3f}")
```

---

## 🎯 メインAPI {#main-api}

### SpeechTensionDetector クラス

#### 初期化

```python
from speech_tension_detector import SpeechTensionDetector

detector = SpeechTensionDetector()
```

**パラメータ**: なし  
**戻り値**: SpeechTensionDetectorインスタンス

#### predict_tension()

```python
score = detector.predict_tension(audio_path)
```

**パラメータ**:
- `audio_path` (str): WAVファイルのパス

**戻り値**:
- `float`: テンション値 (0.0-1.0)
  - 0.0-0.333: 低テンション（小声・ささやき）
  - 0.333-0.666: 中テンション（通常会話）
  - 0.666-1.0: 高テンション（叫び声・興奮状態）

**例**:
```python
# 基本的な使用
score = detector.predict_tension("sample.wav")
print(f"テンション: {score:.3f}")

# 複数ファイル処理
files = ["file1.wav", "file2.wav", "file3.wav"]
for file_path in files:
    score = detector.predict_tension(file_path)
    print(f"{file_path}: {score:.3f}")
```

#### detect_tension()

```python
result = detector.detect_tension(audio_path, verbose=False)
```

**パラメータ**:
- `audio_path` (str): WAVファイルのパス
- `verbose` (bool, optional): 詳細出力フラグ（デフォルト: False）

**戻り値**:
- `dict`: 検出結果辞書
  - `tension_score` (float): テンション値 (0.0-1.0)
  - `confidence` (float): 信頼度 (0.0-1.0)
  - `interpretation` (str): 日本語解釈
  - `spectral_tilt` (float): スペクトラル傾斜 (dB)
  - `processing_time` (float): 処理時間（秒）
  - `audio_duration` (float): 音声長（秒）
  - `audio_path` (str): 音声ファイルパス

**例**:
```python
# 基本的な詳細解析
result = detector.detect_tension("sample.wav")
print(f"テンション: {result['tension_score']:.3f}")
print(f"解釈: {result['interpretation']}")
print(f"信頼度: {result['confidence']:.3f}")

# 詳細情報付き解析
result = detector.detect_tension("sample.wav", verbose=True)
if 'detailed_features' in result:
    features = result['detailed_features']
    print(f"基本特徴量: {len(features['basic'])}種類")
    print(f"韻律特徴量: {len(features['prosodic'])}種類")
    print(f"スペクトラル特徴量: {len(features['spectral'])}種類")
```

#### load_audio()

```python
audio, sr = detector.load_audio(audio_path)
```

**パラメータ**:
- `audio_path` (str): 音声ファイルパス

**戻り値**:
- `tuple`: (audio_data, sample_rate)
  - `audio_data` (np.ndarray): 音声信号配列
  - `sample_rate` (int): サンプリングレート

**例**:
```python
# 音声データを直接取得
audio, sr = detector.load_audio("sample.wav")
print(f"音声長: {len(audio)/sr:.2f}秒")
print(f"サンプリングレート: {sr}Hz")
```

#### normalize_audio()

```python
normalized_audio = detector.normalize_audio(audio)
```

**パラメータ**:
- `audio` (np.ndarray): 音声信号配列

**戻り値**:
- `np.ndarray`: 正規化された音声信号

**例**:
```python
# 音声を正規化
audio, sr = detector.load_audio("sample.wav")
normalized = detector.normalize_audio(audio)
print(f"正規化前RMS: {audio.std():.4f}")
print(f"正規化後RMS: {normalized.std():.4f}")
```

---

## ⚡ 高速化API {#speed-optimized-api}

### SpeedOptimizedTensionDetector クラス

高速処理に最適化された検出器。約2倍の高速化を実現。

```python
from speech_tension_detector import SpeedOptimizedTensionDetector

# 高速化検出器を初期化
speed_detector = SpeedOptimizedTensionDetector()

# 基本的な使用方法（SpeechTensionDetectorと同じAPI）
score = speed_detector.predict_tension("audio.wav")
result = speed_detector.detect_tension("audio.wav", verbose=True)
```

**特徴**:
- 軽量分類器を優先使用
- 事前訓練済みモデルの遅延初期化
- キャッシュシステムによる高速化
- 約2倍の処理速度向上

**使用例**:
```python
import time

# 標準検出器との速度比較
standard_detector = SpeechTensionDetector()
speed_detector = SpeedOptimizedTensionDetector()

# 標準検出器
start = time.time()
result1 = standard_detector.predict_tension("sample.wav")
time1 = time.time() - start

# 高速化検出器
start = time.time()
result2 = speed_detector.predict_tension("sample.wav")
time2 = time.time() - start

print(f"標準: {result1:.3f} ({time1:.2f}秒)")
print(f"高速: {result2:.3f} ({time2:.2f}秒)")
print(f"高速化倍率: {time1/time2:.1f}x")
```

---

## 🚀 並列処理API {#parallel-processing-api}

### ParallelBatchDetector クラス

複数ファイルの並列処理。最大23倍の高速化を実現。

#### 初期化

```python
from speech_tension_detector import ParallelBatchDetector

# デフォルト設定（CPU数に基づく自動設定）
parallel_detector = ParallelBatchDetector()

# ワーカー数を指定
parallel_detector = ParallelBatchDetector(max_workers=8)
```

**パラメータ**:
- `max_workers` (int, optional): 最大並列ワーカー数
  - None: CPU数 + 4（デフォルト）
  - 推奨: 4-16（システムに応じて調整）

#### process_batch_files()

```python
results = parallel_detector.process_batch_files(file_paths)
```

**パラメータ**:
- `file_paths` (list): 音声ファイルパスのリスト

**戻り値**:
- `list`: 検出結果のリスト（各要素はdict）

**例**:
```python
# ファイルリストを準備
files = ["file1.wav", "file2.wav", "file3.wav", "file4.wav"]

# 並列処理実行
parallel_detector = ParallelBatchDetector(max_workers=4)
results = parallel_detector.process_batch_files(files)

# 結果表示
for file_path, result in zip(files, results):
    if isinstance(result, dict) and 'tension_score' in result:
        score = result['tension_score']
        interpretation = result['interpretation']
        print(f"{file_path}: {score:.3f} - {interpretation}")
    else:
        print(f"{file_path}: エラー")
```

#### process_directory()

```python
results = parallel_detector.process_directory(directory_path, pattern="*.wav")
```

**パラメータ**:
- `directory_path` (str): ディレクトリパス
- `pattern` (str, optional): ファイルパターン（デフォルト: "*.wav"）

**戻り値**:
- `list`: (ファイルパス, 結果)のタプルのリスト

**例**:
```python
# ディレクトリ内の全WAVファイルを並列処理
results = parallel_detector.process_directory("audio_samples/")

# 結果統計
valid_results = [r for _, r in results if isinstance(r, dict)]
if valid_results:
    scores = [r['tension_score'] for r in valid_results]
    print(f"処理ファイル数: {len(valid_results)}")
    print(f"平均テンション: {sum(scores)/len(scores):.3f}")
    print(f"最小テンション: {min(scores):.3f}")
    print(f"最大テンション: {max(scores):.3f}")
```

---

## 💻 コマンドライン {#command-line}

### speech-tension-detect コマンド

```bash
speech-tension-detect [OPTIONS] INPUT
```

#### 基本的な使用方法

```bash
# 単一ファイル処理
speech-tension-detect sample.wav

# 詳細出力
speech-tension-detect sample.wav --verbose

# 高速化処理
speech-tension-detect sample.wav --speed-optimized
```

#### バッチ処理

```bash
# ディレクトリ内の全WAVファイル
speech-tension-detect audio_samples/

# 複数ファイル指定
speech-tension-detect file1.wav file2.wav file3.wav

# 並列バッチ処理
speech-tension-detect audio_samples/ --parallel
```

#### オプション

| オプション | 短縮形 | 説明 |
|------------|--------|------|
| `--verbose` | `-v` | 詳細出力 |
| `--speed-optimized` | `-s` | 高速化処理 |
| `--parallel` | `-p` | 並列処理 |
| `--version` | | バージョン表示 |

#### 出力例

```bash
$ speech-tension-detect sample.wav --verbose

==================================================
音声テンション解析: sample.wav
==================================================
音声読み込み完了: 1.15秒, SR=22050Hz
テンション値: 0.825 (信頼度: 0.869)
解釈: 高テンション（叫び声・興奮状態）
スペクトラル傾斜: -19.5 dB
処理時間: 0.11秒

🔍 詳細情報
------------------------------
平均F0: 245.3 Hz
平均強度: 68.2 dB
HNR: 12.4 dB
```

---

## ⚙️ 設定とカスタマイズ {#configuration}

### 検出器設定

```python
# カスタム設定で初期化
detector = SpeechTensionDetector()

# サンプリングレート確認・変更
print(f"現在のサンプリングレート: {detector.sample_rate}Hz")

# 内部パラメータ確認
print(f"ホップ長: {detector.hop_length}")
print(f"窓長: {detector.win_length}")
```

### パフォーマンス設定

```python
# 並列処理の最適化
import os
cpu_count = os.cpu_count()

# CPU数に応じたワーカー設定
if cpu_count <= 4:
    max_workers = cpu_count
elif cpu_count <= 8:
    max_workers = cpu_count + 2
else:
    max_workers = min(16, cpu_count + 4)

parallel_detector = ParallelBatchDetector(max_workers=max_workers)
```

### GPU設定確認

```python
import torch

# GPU利用可能性確認
if torch.cuda.is_available():
    print(f"GPU利用可能: {torch.cuda.get_device_name(0)}")
    print(f"CUDA バージョン: {torch.version.cuda}")
else:
    print("GPU利用不可、CPU処理モード")

# メモリ使用量確認
if torch.cuda.is_available():
    print(f"GPU メモリ使用量: {torch.cuda.memory_allocated()/1024**2:.1f} MB")
```

---

## 🚨 エラーハンドリング {#error-handling}

### 一般的なエラーパターン

```python
from speech_tension_detector import SpeechTensionDetector
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)

def safe_tension_detection(audio_path):
    """安全なテンション検出"""
    try:
        detector = SpeechTensionDetector()
        result = detector.detect_tension(audio_path)
        return result
        
    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません: {audio_path}")
        return None
        
    except ValueError as e:
        if "短すぎます" in str(e):
            print(f"エラー: 音声が短すぎます（0.5秒以上必要）")
        else:
            print(f"値エラー: {e}")
        return None
        
    except Exception as e:
        print(f"予期しないエラー: {e}")
        return None

# 使用例
result = safe_tension_detection("sample.wav")
if result:
    print(f"テンション: {result['tension_score']:.3f}")
else:
    print("処理に失敗しました")
```

### バッチ処理でのエラーハンドリング

```python
def robust_batch_processing(file_paths):
    """堅牢なバッチ処理"""
    detector = ParallelBatchDetector()
    
    # ファイル存在確認
    valid_files = []
    for file_path in file_paths:
        if os.path.exists(file_path):
            valid_files.append(file_path)
        else:
            print(f"警告: ファイルが見つかりません: {file_path}")
    
    if not valid_files:
        print("エラー: 処理可能なファイルがありません")
        return []
    
    try:
        results = detector.process_batch_files(valid_files)
        
        # 結果検証
        valid_results = []
        for file_path, result in zip(valid_files, results):
            if isinstance(result, dict) and 'tension_score' in result:
                valid_results.append((file_path, result))
            else:
                print(f"警告: {file_path} の処理に失敗")
        
        return valid_results
        
    except Exception as e:
        print(f"バッチ処理エラー: {e}")
        return []
```

---

## 🔧 パフォーマンス最適化 {#performance}

### メモリ使用量最適化

```python
import gc
import torch

def memory_efficient_processing(file_paths):
    """メモリ効率的な処理"""
    
    # 小さなバッチで処理
    batch_size = 5
    all_results = []
    
    for i in range(0, len(file_paths), batch_size):
        batch_files = file_paths[i:i+batch_size]
        
        # バッチ処理
        detector = ParallelBatchDetector(max_workers=2)  # メモリ制限
        batch_results = detector.process_batch_files(batch_files)
        all_results.extend(batch_results)
        
        # メモリクリア
        del detector
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        print(f"処理完了: {i+len(batch_files)}/{len(file_paths)}")
    
    return all_results
```

### 処理速度ベンチマーク

```python
import time
from pathlib import Path

def benchmark_detectors(test_file):
    """検出器性能比較"""
    
    detectors = {
        "標準": SpeechTensionDetector(),
        "高速化": SpeedOptimizedTensionDetector(),
    }
    
    results = {}
    
    for name, detector in detectors.items():
        # ウォームアップ
        _ = detector.predict_tension(test_file)
        
        # ベンチマーク（5回実行）
        times = []
        for _ in range(5):
            start = time.time()
            score = detector.predict_tension(test_file)
            end = time.time()
            times.append(end - start)
        
        avg_time = sum(times) / len(times)
        results[name] = {
            'avg_time': avg_time,
            'score': score
        }
    
    # 結果表示
    print("=== 性能比較結果 ===")
    base_time = results["標準"]['avg_time']
    
    for name, result in results.items():
        speedup = base_time / result['avg_time']
        print(f"{name:8s}: {result['avg_time']:.3f}秒 ({speedup:.1f}x) | スコア: {result['score']:.3f}")
```

---

## 💡 実用例 {#examples}

### 例1: 音声ファイル分析システム

```python
from speech_tension_detector import SpeechTensionDetector
import pandas as pd
from pathlib import Path

def analyze_audio_collection(directory_path):
    """音声コレクション分析"""
    
    detector = SpeechTensionDetector()
    audio_dir = Path(directory_path)
    
    results = []
    
    for audio_file in audio_dir.glob("*.wav"):
        try:
            result = detector.detect_tension(str(audio_file), verbose=True)
            
            # データ整理
            data = {
                'filename': audio_file.name,
                'tension_score': result['tension_score'],
                'confidence': result['confidence'],
                'interpretation': result['interpretation'],
                'duration': result['audio_duration'],
                'processing_time': result.get('processing_time', 0)
            }
            
            # 詳細特徴量があれば追加
            if 'detailed_features' in result:
                features = result['detailed_features']
                if 'prosodic' in features:
                    prosodic = features['prosodic']
                    data.update({
                        'f0_mean': prosodic.get('f0_mean', 0),
                        'intensity_mean': prosodic.get('intensity_mean', 0),
                        'hnr_mean': prosodic.get('hnr_mean', 0)
                    })
            
            results.append(data)
            print(f"✓ {audio_file.name}: {data['tension_score']:.3f}")
            
        except Exception as e:
            print(f"✗ {audio_file.name}: エラー - {e}")
    
    # DataFrame作成
    df = pd.DataFrame(results)
    
    # 統計情報
    print(f"\n=== 分析結果サマリー ===")
    print(f"総ファイル数: {len(df)}")
    print(f"平均テンション: {df['tension_score'].mean():.3f}")
    print(f"標準偏差: {df['tension_score'].std():.3f}")
    print(f"最小値: {df['tension_score'].min():.3f}")
    print(f"最大値: {df['tension_score'].max():.3f}")
    
    # CSV保存
    output_file = audio_dir / "tension_analysis_results.csv"
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n結果を保存: {output_file}")
    
    return df

# 使用例
# df = analyze_audio_collection("audio_samples/")
```

### 例2: リアルタイム音声モニタリング

```python
import time
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class AudioTensionMonitor(FileSystemEventHandler):
    """音声ファイル監視・自動解析"""
    
    def __init__(self, output_dir="results/"):
        self.detector = SpeechTensionDetector()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def on_created(self, event):
        """新しいファイル作成時の処理"""
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        
        # WAVファイルのみ処理
        if file_path.suffix.lower() == '.wav':
            # ファイル書き込み完了まで待機
            time.sleep(1)
            
            print(f"新しい音声ファイル検出: {file_path.name}")
            self.analyze_file(file_path)
    
    def analyze_file(self, file_path):
        """ファイル解析"""
        try:
            result = self.detector.detect_tension(str(file_path))
            
            # 結果をテキストファイルに保存
            result_file = self.output_dir / f"{file_path.stem}_result.txt"
            
            with open(result_file, 'w', encoding='utf-8') as f:
                f.write(f"ファイル: {file_path.name}\n")
                f.write(f"テンション値: {result['tension_score']:.3f}\n")
                f.write(f"解釈: {result['interpretation']}\n")
                f.write(f"信頼度: {result['confidence']:.3f}\n")
                f.write(f"処理時間: {result.get('processing_time', 0):.2f}秒\n")
            
            print(f"✓ 解析完了: {result['tension_score']:.3f} ({result['interpretation']})")
            
            # 高テンションの場合はアラート
            if result['tension_score'] > 0.7:
                self.send_alert(file_path, result)
                
        except Exception as e:
            print(f"✗ 解析エラー ({file_path.name}): {e}")
    
    def send_alert(self, file_path, result):
        """高テンション時のアラート"""
        print(f"🚨 高テンション検出! {file_path.name}: {result['tension_score']:.3f}")
        # ここに通知処理を追加（メール、Slack等）

def start_monitoring(watch_directory):
    """監視開始"""
    monitor = AudioTensionMonitor()
    observer = Observer()
    observer.schedule(monitor, watch_directory, recursive=False)
    
    observer.start()
    print(f"音声ファイル監視開始: {watch_directory}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("監視終了")
    
    observer.join()

# 使用例
# start_monitoring("incoming_audio/")
```

### 例3: 音声品質チェックシステム

```python
from speech_tension_detector import ParallelBatchDetector
import json
from datetime import datetime

def audio_quality_check(file_paths, quality_thresholds=None):
    """音声品質チェック"""
    
    if quality_thresholds is None:
        quality_thresholds = {
            'min_confidence': 0.7,
            'max_processing_time': 10.0,
            'acceptable_tension_range': (0.1, 0.9)
        }
    
    detector = ParallelBatchDetector()
    results = detector.process_batch_files(file_paths)
    
    quality_report = {
        'check_time': datetime.now().isoformat(),
        'total_files': len(file_paths),
        'thresholds': quality_thresholds,
        'files': [],
        'summary': {
            'passed': 0,
            'failed': 0,
            'warnings': 0
        }
    }
    
    for file_path, result in zip(file_paths, results):
        file_name = Path(file_path).name
        
        if not isinstance(result, dict) or 'tension_score' not in result:
            # 処理失敗
            file_report = {
                'filename': file_name,
                'status': 'FAILED',
                'reason': '処理エラー',
                'issues': ['処理に失敗しました']
            }
            quality_report['summary']['failed'] += 1
        else:
            # 品質チェック
            issues = []
            warnings = []
            
            # 信頼度チェック
            confidence = result.get('confidence', 0)
            if confidence < quality_thresholds['min_confidence']:
                issues.append(f"信頼度が低い: {confidence:.3f}")
            
            # 処理時間チェック
            proc_time = result.get('processing_time', 0)
            if proc_time > quality_thresholds['max_processing_time']:
                warnings.append(f"処理時間が長い: {proc_time:.2f}秒")
            
            # テンション範囲チェック
            tension = result['tension_score']
            min_t, max_t = quality_thresholds['acceptable_tension_range']
            if not (min_t <= tension <= max_t):
                warnings.append(f"テンション値が範囲外: {tension:.3f}")
            
            # 音声長チェック
            duration = result.get('audio_duration', 0)
            if duration < 0.5:
                issues.append(f"音声が短すぎる: {duration:.2f}秒")
            elif duration > 30:
                warnings.append(f"音声が長い: {duration:.2f}秒")
            
            # ステータス決定
            if issues:
                status = 'FAILED'
                quality_report['summary']['failed'] += 1
            elif warnings:
                status = 'WARNING'
                quality_report['summary']['warnings'] += 1
            else:
                status = 'PASSED'
                quality_report['summary']['passed'] += 1
            
            file_report = {
                'filename': file_name,
                'status': status,
                'tension_score': tension,
                'confidence': confidence,
                'processing_time': proc_time,
                'audio_duration': duration,
                'issues': issues,
                'warnings': warnings
            }
        
        quality_report['files'].append(file_report)
    
    # レポート表示
    print("=== 音声品質チェック結果 ===")
    print(f"総ファイル数: {quality_report['total_files']}")
    print(f"合格: {quality_report['summary']['passed']}")
    print(f"警告: {quality_report['summary']['warnings']}")
    print(f"不合格: {quality_report['summary']['failed']}")
    
    # 問題のあるファイル表示
    for file_report in quality_report['files']:
        if file_report['status'] != 'PASSED':
            print(f"\n{file_report['status']}: {file_report['filename']}")
            for issue in file_report.get('issues', []):
                print(f"  - 問題: {issue}")
            for warning in file_report.get('warnings', []):
                print(f"  - 警告: {warning}")
    
    # JSON レポート保存
    with open('quality_report.json', 'w', encoding='utf-8') as f:
        json.dump(quality_report, f, ensure_ascii=False, indent=2)
    
    return quality_report

# 使用例
# files = ["sample1.wav", "sample2.wav", "sample3.wav"]
# report = audio_quality_check(files)
```

---

## 📞 サポート・トラブルシューティング

### よくある問題

1. **インポートエラー**
   ```bash
   pip install --upgrade speech-tension-detector
   ```

2. **GPU関連エラー**
   ```python
   import torch
   print(f"CUDA利用可能: {torch.cuda.is_available()}")
   ```

3. **メモリエラー**
   - バッチサイズを削減
   - 並列ワーカー数を削減

4. **音声ファイルエラー**
   - WAVファイルであることを確認
   - サンプリングレート22kHz以上推奨
   - 音声長0.5秒以上必要

### バージョン情報確認

```python
import speech_tension_detector
print(f"バージョン: {speech_tension_detector.__version__}")
print(f"作者: {speech_tension_detector.__author__}")
```

### システム情報確認

```bash
speech-tension-detect --version
```

---

## 📜 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

---

**開発者**: hiroshi-tamura  
**最終更新**: 2025年1月31日  
**バージョン**: 1.0.0