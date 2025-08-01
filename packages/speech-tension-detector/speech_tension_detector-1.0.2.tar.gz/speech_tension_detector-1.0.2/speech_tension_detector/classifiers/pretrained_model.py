#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
事前訓練済みモデルベース音声テンション分類器
最新のディープラーニングモデルを活用
"""

import os
import numpy as np
import torch
import torch.nn as nn
import librosa
import warnings
warnings.filterwarnings('ignore')

try:
    # Transformers (Hugging Face)
    from transformers import (
        Wav2Vec2Processor, Wav2Vec2Model,
        WhisperProcessor, WhisperModel,
        AutoProcessor, AutoModel
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("警告: transformersがインストールされていません。pip install transformersを実行してください。")

try:
    # TorchAudio
    import torchaudio
    from torchaudio.transforms import MFCC, MelSpectrogram
    TORCHAUDIO_AVAILABLE = True
except ImportError:
    TORCHAUDIO_AVAILABLE = False
    print("警告: torchのaudioがインストールされていません。")

class PretrainedModelClassifier:
    """事前訓練済みモデルを使用したテンション分類器"""
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"使用デバイス: {self.device}")
        
        self.models = {}
        self.processors = {}
        
        # 複数の事前訓練済みモデルを初期化
        self._initialize_models()
        
        # 分類閾値（データドリブンで最適化予定）
        self.classification_thresholds = {
            'low_upper': 0.333,
            'neutral_upper': 0.666
        }
    
    def _initialize_models(self):
        """事前訓練済みモデルの初期化"""
        
        if not TRANSFORMERS_AVAILABLE:
            print("Transformersライブラリが利用不可能です。基本的な実装にフォールバックします。")
            return
        
        try:
            # 1. Wav2Vec2.0 - 音声表現学習のSOTA
            print("Wav2Vec2.0モデル読み込み中...")
            self.processors['wav2vec2'] = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base")
            self.models['wav2vec2'] = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base").to(self.device)
            self.models['wav2vec2'].eval()
            print("✓ Wav2Vec2.0モデル読み込み完了")
            
        except Exception as e:
            print(f"Wav2Vec2.0モデル読み込みエラー: {e}")
        
        try:
            # 2. Whisper - OpenAIの音声認識モデル（特徴抽出用）
            print("Whisperモデル読み込み中...")
            self.processors['whisper'] = WhisperProcessor.from_pretrained("openai/whisper-base")
            self.models['whisper'] = WhisperModel.from_pretrained("openai/whisper-base").to(self.device)
            self.models['whisper'].eval()
            print("✓ Whisperモデル読み込み完了")
            
        except Exception as e:
            print(f"Whisperモデル読み込みエラー: {e}")
        
        # GPU使用時はメモリ効率化
        if self.device.type == 'cuda':
            torch.cuda.empty_cache()
    
    def extract_wav2vec2_features(self, audio, sr=16000):
        """Wav2Vec2.0から特徴量抽出"""
        try:
            if 'wav2vec2' not in self.models:
                return np.array([0.5] * 768)  # デフォルト特徴量
            
            # リサンプリング（Wav2Vec2は16kHzが標準）
            if sr != 16000:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
            
            # 前処理
            inputs = self.processors['wav2vec2'](audio, sampling_rate=16000, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # 特徴量抽出
            with torch.no_grad():
                outputs = self.models['wav2vec2'](**inputs)
                
            # 隠れ状態から特徴量を取得
            hidden_states = outputs.last_hidden_state  # [batch, seq_len, hidden_dim]
            
            # 時間軸で平均化
            features = torch.mean(hidden_states, dim=1).squeeze()  # [hidden_dim]
            
            return features.cpu().numpy()
            
        except Exception as e:
            print(f"Wav2Vec2特徴量抽出エラー: {e}")
            return np.array([0.5] * 768)
    
    def extract_whisper_features(self, audio, sr=16000):
        """Whisperから特徴量抽出"""
        try:
            if 'whisper' not in self.models:
                return np.array([0.5] * 512)  # デフォルト特徴量
            
            # リサンプリング（Whisperも16kHzが標準）
            if sr != 16000:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
            
            # メル・スペクトログラム計算
            inputs = self.processors['whisper'](audio, sampling_rate=16000, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # エンコーダーから特徴量抽出
            with torch.no_grad():
                encoder_outputs = self.models['whisper'].encoder(**inputs)
                
            # エンコーダー出力から特徴量
            hidden_states = encoder_outputs.last_hidden_state  # [batch, seq_len, hidden_dim]
            
            # 時間軸で平均化
            features = torch.mean(hidden_states, dim=1).squeeze()  # [hidden_dim]
            
            return features.cpu().numpy()
            
        except Exception as e:
            print(f"Whisper特徴量抽出エラー: {e}")
            return np.array([0.5] * 512)
    
    def extract_deep_audio_features(self, audio, sr=22050):
        """深層学習ベース包括的特徴量抽出"""
        features = {}
        
        try:
            # 1. Wav2Vec2.0特徴量
            wav2vec2_features = self.extract_wav2vec2_features(audio, sr)
            
            # 統計的要約
            features['wav2vec2_mean'] = np.mean(wav2vec2_features)
            features['wav2vec2_std'] = np.std(wav2vec2_features)
            features['wav2vec2_max'] = np.max(wav2vec2_features)
            features['wav2vec2_min'] = np.min(wav2vec2_features)
            features['wav2vec2_range'] = np.max(wav2vec2_features) - np.min(wav2vec2_features)
            
            # 上位次元の統計
            features['wav2vec2_skew'] = self._safe_skewness(wav2vec2_features)
            features['wav2vec2_kurtosis'] = self._safe_kurtosis(wav2vec2_features)
            features['wav2vec2_entropy'] = self._calculate_entropy(wav2vec2_features)
            
            # クォンタイル
            features['wav2vec2_q25'] = np.percentile(wav2vec2_features, 25)
            features['wav2vec2_q75'] = np.percentile(wav2vec2_features, 75)
            features['wav2vec2_iqr'] = features['wav2vec2_q75'] - features['wav2vec2_q25']
            
            # 2. Whisper特徴量
            whisper_features = self.extract_whisper_features(audio, sr)
            
            features['whisper_mean'] = np.mean(whisper_features)
            features['whisper_std'] = np.std(whisper_features)
            features['whisper_max'] = np.max(whisper_features)
            features['whisper_min'] = np.min(whisper_features)
            features['whisper_range'] = np.max(whisper_features) - np.min(whisper_features)
            
            features['whisper_skew'] = self._safe_skewness(whisper_features)
            features['whisper_kurtosis'] = self._safe_kurtosis(whisper_features)
            features['whisper_entropy'] = self._calculate_entropy(whisper_features)
            
            # 3. モデル間相関特徴量
            if len(wav2vec2_features) > 0 and len(whisper_features) > 0:
                # 次元を合わせて相関計算
                min_dim = min(len(wav2vec2_features), len(whisper_features))
                corr = np.corrcoef(wav2vec2_features[:min_dim], whisper_features[:min_dim])[0, 1]
                features['model_correlation'] = corr if not np.isnan(corr) else 0.0
            else:
                features['model_correlation'] = 0.0
            
            # 4. PyTorchベース音響特徴量（GPU活用）
            if TORCHAUDIO_AVAILABLE:
                features.update(self._extract_torch_audio_features(audio, sr))
            
            return features
            
        except Exception as e:
            print(f"深層学習特徴量抽出エラー: {e}")
            return {'wav2vec2_mean': 0.5, 'whisper_mean': 0.5}
    
    def _extract_torch_audio_features(self, audio, sr=22050):
        """PyTorch/TorchAudioベース特徴量（GPU活用）"""
        features = {}
        
        try:
            # NumPy -> Torch tensor
            audio_tensor = torch.FloatTensor(audio).unsqueeze(0).to(self.device)
            
            # MELスペクトログラム（GPU処理）
            mel_transform = MelSpectrogram(
                sample_rate=sr,
                n_fft=2048,
                hop_length=512,
                n_mels=128
            ).to(self.device)
            
            mel_spec = mel_transform(audio_tensor)
            mel_spec_np = mel_spec.squeeze().cpu().numpy()
            
            # MEL統計特徴量
            features['mel_mean'] = np.mean(mel_spec_np)
            features['mel_std'] = np.std(mel_spec_np)
            features['mel_entropy'] = self._calculate_entropy(mel_spec_np.flatten())
            
            # MFCC（GPU処理）
            mfcc_transform = MFCC(
                sample_rate=sr,
                n_mfcc=13,
                melkwargs={"n_fft": 2048, "hop_length": 512, "n_mels": 128}
            ).to(self.device)
            
            mfcc = mfcc_transform(audio_tensor)
            mfcc_np = mfcc.squeeze().cpu().numpy()
            
            # MFCC統計特徴量
            features['mfcc_mean'] = np.mean(mfcc_np)
            features['mfcc_std'] = np.std(mfcc_np)
            features['mfcc_range'] = np.max(mfcc_np) - np.min(mfcc_np)
            
            # MFCC delta features
            mfcc_delta = torch.diff(mfcc, dim=-1)
            mfcc_delta_np = mfcc_delta.squeeze().cpu().numpy()
            
            features['mfcc_delta_mean'] = np.mean(mfcc_delta_np)
            features['mfcc_delta_std'] = np.std(mfcc_delta_np)
            
        except Exception as e:
            print(f"TorchAudio特徴量抽出エラー: {e}")
            
        return features
    
    def predict_tension_advanced(self, audio_path):
        """高度な事前訓練済みモデルベース予測"""
        try:
            # 音声読み込み
            audio, sr = librosa.load(audio_path, sr=22050, mono=True)
            
            # RMS正規化
            rms = np.sqrt(np.mean(audio**2))
            if rms > 0:
                audio_normalized = audio / rms * 0.1
            else:
                audio_normalized = audio
            
            print(f"深層学習特徴量抽出開始: {os.path.basename(audio_path)}")
            
            # 深層学習特徴量抽出
            deep_features = self.extract_deep_audio_features(audio_normalized, sr)
            
            # アンサンブル予測
            tension_value = self._ensemble_prediction(deep_features, audio_normalized, sr)
            
            # 信頼度計算
            confidence = self._calculate_confidence(deep_features)
            
            return tension_value, confidence, deep_features
            
        except Exception as e:
            print(f"高度予測エラー: {e}")
            return 0.5, 0.0, {}
    
    def _ensemble_prediction(self, deep_features, audio, sr):
        """アンサンブル予測（複数手法統合）"""
        try:
            predictions = []
            weights = []
            
            # 1. Wav2Vec2ベース予測
            wav2vec2_pred = self._wav2vec2_based_prediction(deep_features)
            predictions.append(wav2vec2_pred)
            weights.append(0.4)  # 最も信頼性が高い
            
            # 2. Whisperベース予測
            whisper_pred = self._whisper_based_prediction(deep_features)
            predictions.append(whisper_pred)
            weights.append(0.3)
            
            # 3. TorchAudioベース予測
            torch_pred = self._torch_audio_based_prediction(deep_features)
            predictions.append(torch_pred)
            weights.append(0.2)
            
            # 4. モデル相関ベース予測
            corr_pred = self._correlation_based_prediction(deep_features)
            predictions.append(corr_pred)
            weights.append(0.1)
            
            # 重み付け平均
            ensemble_prediction = np.average(predictions, weights=weights)
            
            # 3分割マッピング（データドリブン）
            final_tension = self._map_to_three_classes(ensemble_prediction, deep_features)
            
            return final_tension
            
        except Exception as e:
            print(f"アンサンブル予測エラー: {e}")
            return 0.5
    
    def _wav2vec2_based_prediction(self, features):
        """Wav2Vec2特徴量ベース予測"""
        try:
            # 特徴量の組み合わせによる予測
            mean_score = features.get('wav2vec2_mean', 0.5)
            std_score = features.get('wav2vec2_std', 0.5)
            range_score = features.get('wav2vec2_range', 0.5)
            entropy_score = features.get('wav2vec2_entropy', 0.5)
            
            # 正規化（-1～1を0～1に）
            mean_normalized = (mean_score + 1) / 2
            std_normalized = min(std_score, 1.0)
            range_normalized = min(range_score / 2, 1.0)
            entropy_normalized = min(entropy_score / 10, 1.0)
            
            # 重み付け統合
            prediction = (
                mean_normalized * 0.4 +
                std_normalized * 0.3 +
                range_normalized * 0.2 +
                entropy_normalized * 0.1
            )
            
            return np.clip(prediction, 0.0, 1.0)
            
        except Exception as e:
            return 0.5
    
    def _whisper_based_prediction(self, features):
        """Whisper特徴量ベース予測"""
        try:
            mean_score = features.get('whisper_mean', 0.5)
            std_score = features.get('whisper_std', 0.5)
            range_score = features.get('whisper_range', 0.5)
            
            # Whisperは音声認識モデルなので、より保守的な予測
            mean_normalized = (mean_score + 1) / 2
            std_normalized = min(std_score, 1.0)
            range_normalized = min(range_score / 2, 1.0)
            
            prediction = (
                mean_normalized * 0.5 +
                std_normalized * 0.3 +
                range_normalized * 0.2
            )
            
            return np.clip(prediction, 0.0, 1.0)
            
        except Exception as e:
            return 0.5
    
    def _torch_audio_based_prediction(self, features):
        """TorchAudio特徴量ベース予測"""
        try:
            mel_mean = features.get('mel_mean', 0.5)
            mfcc_range = features.get('mfcc_range', 1.0)
            mfcc_delta_std = features.get('mfcc_delta_std', 0.5)
            
            # MEL/MFCC特徴量ベース
            mel_normalized = min(abs(mel_mean) / 10, 1.0)
            mfcc_range_normalized = min(mfcc_range / 50, 1.0)
            delta_normalized = min(mfcc_delta_std, 1.0)
            
            prediction = (
                mel_normalized * 0.4 +
                mfcc_range_normalized * 0.4 +
                delta_normalized * 0.2
            )
            
            return np.clip(prediction, 0.0, 1.0)
            
        except Exception as e:
            return 0.5
    
    def _correlation_based_prediction(self, features):
        """モデル間相関ベース予測"""
        try:
            correlation = features.get('model_correlation', 0.0)
            
            # 相関が低い＝モデル間で異なる解釈＝高テンション傾向
            # 相関が高い＝一致した解釈＝低テンション傾向
            correlation_normalized = abs(correlation)
            prediction = 1.0 - correlation_normalized  # 逆転
            
            return np.clip(prediction, 0.0, 1.0)
            
        except Exception as e:
            return 0.5
    
    def _map_to_three_classes(self, ensemble_prediction, features):
        """3クラス範囲への適応的マッピング"""
        try:
            # 特徴量ベースの動的閾値調整
            wav2vec2_intensity = features.get('wav2vec2_range', 0.5)
            whisper_intensity = features.get('whisper_range', 0.5)
            
            # 強度に基づく適応的マッピング
            combined_intensity = (wav2vec2_intensity + whisper_intensity) / 2
            
            if combined_intensity < 0.3:
                # 低強度：Low範囲に偏向
                if ensemble_prediction < 0.6:
                    return ensemble_prediction * 0.333 / 0.6  # 0-0.333
                else:
                    return 0.333 + (ensemble_prediction - 0.6) * 0.333 / 0.4  # 0.333-0.666
            elif combined_intensity > 0.7:
                # 高強度：High範囲に偏向
                if ensemble_prediction < 0.4:
                    return 0.333 + ensemble_prediction * 0.333 / 0.4  # 0.333-0.666
                else:
                    return 0.666 + (ensemble_prediction - 0.4) * 0.334 / 0.6  # 0.666-1.0
            else:
                # 中強度：標準マッピング
                if ensemble_prediction < 0.33:
                    return ensemble_prediction  # 0-0.333
                elif ensemble_prediction < 0.67:
                    return 0.333 + (ensemble_prediction - 0.33) * 0.333 / 0.34
                else:
                    return 0.666 + (ensemble_prediction - 0.67) * 0.334 / 0.33
                    
        except Exception as e:
            print(f"マッピングエラー: {e}")
            # フォールバック：単純3分割
            if ensemble_prediction < 0.33:
                return ensemble_prediction
            elif ensemble_prediction < 0.67:
                return 0.333 + (ensemble_prediction - 0.33) * 0.333 / 0.34
            else:
                return 0.666 + (ensemble_prediction - 0.67) * 0.334 / 0.33
    
    def _calculate_confidence(self, features):
        """信頼度計算"""
        try:
            # 複数の指標から信頼度を計算
            confidence_factors = []
            
            # 1. Wav2Vec2特徴量の安定性
            wav2vec2_std = features.get('wav2vec2_std', 1.0)
            wav2vec2_stability = max(0.1, 1.0 - wav2vec2_std)
            confidence_factors.append(wav2vec2_stability)
            
            # 2. モデル間相関（高相関＝高信頼度）
            model_corr = abs(features.get('model_correlation', 0.0))
            confidence_factors.append(model_corr)
            
            # 3. Whisper特徴量の一貫性
            whisper_range = features.get('whisper_range', 2.0)
            whisper_consistency = max(0.1, 1.0 - min(whisper_range / 2, 1.0))
            confidence_factors.append(whisper_consistency)
            
            # 平均信頼度
            confidence = np.mean(confidence_factors)
            return np.clip(confidence, 0.1, 1.0)
            
        except Exception as e:
            return 0.5
    
    def _safe_skewness(self, data):
        """安全な歪度計算"""
        try:
            from scipy import stats
            return float(stats.skew(data))
        except:
            return 0.0
    
    def _safe_kurtosis(self, data):
        """安全な尖度計算"""
        try:
            from scipy import stats
            return float(stats.kurtosis(data))
        except:
            return 0.0
    
    def _calculate_entropy(self, data):
        """エントロピー計算"""
        try:
            data_flat = data.flatten() if hasattr(data, 'flatten') else data
            hist, _ = np.histogram(data_flat, bins=50)
            hist = hist + 1e-8
            prob = hist / np.sum(hist)
            entropy = -np.sum(prob * np.log2(prob))
            return entropy
        except:
            return 1.0

if __name__ == "__main__":
    # テスト用
    classifier = PretrainedModelClassifier()
    
    test_files = [
        "sample/Tension_Low_01.wav",
        "sample/Tension_Neutral_01.wav", 
        "sample/Tension_High_01.wav"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            tension, confidence, features = classifier.predict_tension_advanced(file_path)
            print(f"{os.path.basename(file_path)}: Tension={tension:.3f}, Confidence={confidence:.3f}")