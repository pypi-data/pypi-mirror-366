# -*- coding: utf-8 -*-
"""
Speech Tension Detector - Main Module
音声のテンション（声門努力・緊張度）を数値で検出するメインモジュール
"""

import numpy as np
import librosa
import soundfile as sf
import warnings
from typing import Tuple, Dict, Optional

# 相対インポート
from ..analyzers.prosodic_features import ProsodicFeatureExtractor
from ..analyzers.spectral_analysis import SpectralAnalyzer
from ..analyzers.advanced_vocal_effort import AdvancedVocalEffortDetector
from ..analyzers.quality_separation import QualitySeparationEngine
from ..analyzers.glottal_source_analysis import GlottalSourceAnalyzer
from ..analyzers.wavelet_fractal_analysis import WaveletFractalAnalyzer

# 分類器の条件付きインポート
try:
    from ..classifiers.pretrained_model import PretrainedModelClassifier
    PRETRAINED_AVAILABLE = True
except ImportError as e:
    print(f"事前訓練済みモデルインポートエラー: {e}")
    PretrainedModelClassifier = None
    PRETRAINED_AVAILABLE = False

try:
    from ..classifiers.advanced_signal import AdvancedSignalClassifier
    ADVANCED_CLASSIFIER_AVAILABLE = True
except ImportError as e:
    print(f"高度分類器インポートエラー: {e}")
    AdvancedSignalClassifier = None
    ADVANCED_CLASSIFIER_AVAILABLE = False

warnings.filterwarnings('ignore')

class SpeechTensionDetector:
    """音声テンション検出メインクラス"""
    
    def __init__(self):
        """初期化"""
        self.sample_rate = 22050  # 標準サンプリングレート
        self.hop_length = 512
        self.win_length = 2048
        
        # 特徴抽出器を初期化
        try:
            self.prosodic_extractor = ProsodicFeatureExtractor()
            self.spectral_analyzer = SpectralAnalyzer(
                sample_rate=self.sample_rate,
                hop_length=self.hop_length,
                win_length=self.win_length
            )
            self.advanced_detector = AdvancedVocalEffortDetector()
            
            # 新しい高度解析システム
            self.quality_separator = QualitySeparationEngine(sample_rate=self.sample_rate)
            self.glottal_analyzer = GlottalSourceAnalyzer(sample_rate=self.sample_rate)
            self.wavelet_fractal_analyzer = WaveletFractalAnalyzer(sample_rate=self.sample_rate)
            
            # 最高精度分類器群の初期化
            classifier_count = 0
            
            # 事前訓練済みディープラーニングモデル（最高精度）
            if PRETRAINED_AVAILABLE:
                try:
                    self.pretrained_classifier = PretrainedModelClassifier()
                    classifier_count += 1
                    print("事前訓練済みモデル初期化完了（Wav2Vec2+Whisper）")
                except Exception as e:
                    self.pretrained_classifier = None
                    print(f"事前訓練済みモデル初期化エラー: {e}")
            else:
                self.pretrained_classifier = None
            
            # 軽量高度分類器（補強・フォールバック）
            if ADVANCED_CLASSIFIER_AVAILABLE:
                self.advanced_classifier = AdvancedSignalClassifier()
                classifier_count += 1
                print("軽量高度分類器初期化完了（17KB）")
            else:
                self.advanced_classifier = None
            
            print(f"高精度アンサンブルシステム初期化完了（{classifier_count}個の分類器）")
        except Exception as e:
            print(f"初期化エラー: {e}")
            self.prosodic_extractor = None
            self.spectral_analyzer = None
            self.advanced_detector = None
            self.quality_separator = None
            self.glottal_analyzer = None
            self.wavelet_fractal_analyzer = None
            self.pretrained_classifier = None
            self.advanced_classifier = None
        
    def load_audio(self, audio_path: str) -> Tuple[np.ndarray, int]:
        """
        音声ファイルを読み込む
        
        Args:
            audio_path (str): 音声ファイルパス
            
        Returns:
            tuple: (audio_data, sample_rate)
        """
        try:
            # librosaで音声読み込み（自動的にモノラル変換・リサンプリング）
            audio, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)
            
            # 音声の長さチェック
            duration = len(audio) / sr
            if duration < 0.5:
                raise ValueError(f"音声が短すぎます（{duration:.2f}秒）。最低0.5秒以上必要です。")
            
            print(f"音声読み込み完了: {duration:.2f}秒, SR={sr}Hz")
            return audio, sr
            
        except Exception as e:
            raise Exception(f"音声ファイル読み込みエラー: {e}")
    
    def normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """
        音声を正規化（音量に依存しない処理のため）
        
        Args:
            audio (np.ndarray): 音声データ
            
        Returns:
            np.ndarray: 正規化された音声データ
        """
        # RMS正規化（音量レベルを統一）
        rms = np.sqrt(np.mean(audio**2))
        if rms > 0:
            audio_normalized = audio / rms * 0.1  # 適度なレベルに調整
        else:
            audio_normalized = audio
            
        return audio_normalized
    
    def extract_basic_features(self, audio: np.ndarray, sr: int) -> Dict:
        """
        基本的な音響特徴量を抽出
        
        Args:
            audio (np.ndarray): 音声データ
            sr (int): サンプリングレート
            
        Returns:
            dict: 特徴量辞書
        """
        features = {}
        
        try:
            # 1. MFCC特徴量
            mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13, 
                                      hop_length=self.hop_length)
            features['mfcc_mean'] = np.mean(mfcc, axis=1)
            features['mfcc_std'] = np.std(mfcc, axis=1)
            
            # 2. スペクトラル特徴量
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr, 
                                                                 hop_length=self.hop_length)[0]
            features['spectral_centroid_mean'] = np.mean(spectral_centroids)
            features['spectral_centroid_std'] = np.std(spectral_centroids)
            
            # 3. スペクトラルロールオフ
            rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr, 
                                                     hop_length=self.hop_length)[0]
            features['spectral_rolloff_mean'] = np.mean(rolloff)
            features['spectral_rolloff_std'] = np.std(rolloff)
            
            # 4. ゼロクロッシングレート
            zcr = librosa.feature.zero_crossing_rate(audio, hop_length=self.hop_length)[0]
            features['zcr_mean'] = np.mean(zcr)
            features['zcr_std'] = np.std(zcr)
            
            # 5. RMS エネルギー
            rms = librosa.feature.rms(y=audio, hop_length=self.hop_length)[0]
            features['rms_mean'] = np.mean(rms)
            features['rms_std'] = np.std(rms)
            
            print(f"基本特徴量抽出完了: {len(features)}種類")
            return features
            
        except Exception as e:
            print(f"基本特徴量抽出エラー: {e}")
            return {}
    
    def detect_tension(self, audio_path: str, verbose: bool = False) -> Dict:
        """
        音声テンション検出メイン処理
        
        Args:
            audio_path (str): 音声ファイルパス
            verbose (bool): 詳細出力フラグ
            
        Returns:
            dict: 検出結果
        """
        try:
            print(f"音声テンション解析開始: {audio_path}")
            print("-" * 50)
            
            # 1. 音声読み込み
            audio, sr = self.load_audio(audio_path)
            
            # 2. 音声正規化
            audio_normalized = self.normalize_audio(audio)
            
            # 3. 基本特徴量抽出
            basic_features = self.extract_basic_features(audio_normalized, sr)
            
            # 4. 韻律特徴量抽出
            prosodic_features = {}
            if self.prosodic_extractor:
                prosodic_features = self.prosodic_extractor.extract_all_features(audio_path)
            
            # 5. スペクトラル特徴量抽出
            spectral_features = {}
            if self.spectral_analyzer:
                spectral_features = self.spectral_analyzer.extract_all_spectral_features(audio_normalized)
            
            # 6. 高度解析システム
            advanced_results = {}
            
            # 高度声門努力検出
            if self.advanced_detector:
                effort_result = self.advanced_detector.calculate_advanced_effort_score(
                    basic_features, prosodic_features, spectral_features
                )
                advanced_results['advanced_effort'] = effort_result
            
            # 品質分離解析
            if self.quality_separator:
                quality_result = self.quality_separator.separate_quality_and_tension(
                    basic_features, prosodic_features, spectral_features
                )
                advanced_results['quality_separation'] = quality_result
            
            # 声門源解析
            if self.glottal_analyzer:
                glottal_result = self.glottal_analyzer.analyze_glottal_source(audio_normalized)
                advanced_results['glottal_analysis'] = glottal_result
            
            # Wavelet-Fractal解析
            if self.wavelet_fractal_analyzer:
                wavelet_result = self.wavelet_fractal_analyzer.analyze_wavelet_fractal_features(audio_normalized)
                advanced_results['wavelet_fractal'] = wavelet_result
            
            # 7. 最高精度分類器による予測
            classifier_predictions = {}
            
            # 事前訓練済みモデル予測
            if self.pretrained_classifier:
                try:
                    pretrained_pred = self.pretrained_classifier.predict_tension(audio_path)
                    classifier_predictions['pretrained'] = pretrained_pred
                except Exception as e:
                    print(f"事前訓練済みモデル予測エラー: {e}")
            
            # 軽量高度分類器予測
            if self.advanced_classifier:
                try:
                    all_features = {**basic_features, **prosodic_features, **spectral_features}
                    advanced_pred = self.advanced_classifier.predict_comprehensive(all_features)
                    classifier_predictions['advanced'] = advanced_pred
                except Exception as e:
                    print(f"高度分類器予測エラー: {e}")
            
            # 8. 最終統合予測
            final_score, confidence, interpretation = self._integrate_predictions(
                basic_features, prosodic_features, spectral_features, 
                advanced_results, classifier_predictions
            )
            
            # 9. 結果の整理
            result = {
                'tension_score': final_score,
                'confidence': confidence,
                'interpretation': interpretation,
                'spectral_tilt': spectral_features.get('spectral_tilt', 0),
                'processing_time': 0,  # 必要に応じて計算
                'audio_duration': len(audio) / sr,
                'audio_path': audio_path
            }
            
            if verbose:
                result['detailed_features'] = {
                    'basic': basic_features,
                    'prosodic': prosodic_features,
                    'spectral': spectral_features,
                    'advanced': advanced_results,
                    'classifier_predictions': classifier_predictions
                }
            
            # 結果出力
            print(f"テンション値: {final_score:.3f} (信頼度: {confidence:.3f})")
            print(f"解釈: {interpretation}")
            if spectral_features.get('spectral_tilt'):
                print(f"スペクトラル傾斜: {spectral_features['spectral_tilt']:.1f} dB")
            
            return result
            
        except Exception as e:
            print(f"テンション検出エラー: {e}")
            return {
                'tension_score': 0.5,
                'confidence': 0.0,
                'interpretation': 'エラーが発生しました',
                'error': str(e)
            }
    
    def _integrate_predictions(self, basic_features, prosodic_features, spectral_features, 
                              advanced_results, classifier_predictions):
        """複数の予測結果を統合"""
        try:
            predictions = []
            weights = []
            
            # スペクトラル傾斜ベース予測（基本）
            spectral_tilt = spectral_features.get('spectral_tilt', 0)
            if spectral_tilt != 0:
                spectral_score = np.clip((spectral_tilt + 20) / 30, 0, 1)
                predictions.append(spectral_score)
                weights.append(0.3)
            
            # 韻律特徴量ベース予測
            prosodic_score = prosodic_features.get('vocal_effort_score', 0.5)
            predictions.append(prosodic_score)
            weights.append(0.2)
            
            # 高度解析結果
            if 'advanced_effort' in advanced_results:
                effort_data = advanced_results['advanced_effort']
                if isinstance(effort_data, tuple) and len(effort_data) >= 2:
                    advanced_score = effort_data[0]
                    predictions.append(advanced_score)
                    weights.append(0.25)
            
            # 分類器予測
            if 'pretrained' in classifier_predictions:
                pretrained_score = classifier_predictions['pretrained']
                if isinstance(pretrained_score, (int, float)):
                    predictions.append(pretrained_score)
                    weights.append(0.15)
            
            if 'advanced' in classifier_predictions:
                advanced_score = classifier_predictions['advanced']
                if isinstance(advanced_score, (int, float)):
                    predictions.append(advanced_score)
                    weights.append(0.1)
            
            # 重み付き平均
            if predictions and weights:
                # 重みを正規化
                weights = np.array(weights)
                weights = weights / np.sum(weights)
                
                final_score = np.average(predictions, weights=weights)
                confidence = 1.0 - np.std(predictions)  # 予測のばらつきから信頼度計算
            else:
                final_score = 0.5
                confidence = 0.0
            
            # 解釈生成
            if final_score < 0.333:
                interpretation = "低テンション（小声・ささやき）"
            elif final_score < 0.666:
                interpretation = "中テンション（通常会話）"
            else:
                interpretation = "高テンション（叫び声・興奮状態）"
            
            return final_score, confidence, interpretation
            
        except Exception as e:
            print(f"予測統合エラー: {e}")
            return 0.5, 0.0, "統合処理エラー"
    
    def predict_tension(self, audio_path: str) -> float:
        """
        シンプルなテンション予測インターフェース
        
        Args:
            audio_path (str): 音声ファイルパス
            
        Returns:
            float: テンションスコア (0.0-1.0)
        """
        result = self.detect_tension(audio_path, verbose=False)
        return result.get('tension_score', 0.5)