#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
機械学習用特徴量抽出器
全サンプルから包括的特徴量を抽出してデータベース化
"""

import os
import numpy as np
import pandas as pd
import librosa
import soundfile as sf
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 自作モジュール（相対インポートに変更）
try:
    from ..analyzers.prosodic_features import ProsodicFeatureExtractor
    from ..analyzers.spectral_analysis import SpectralAnalyzer
    from ..analyzers.quality_separation import QualitySeparationEngine
    from ..analyzers.glottal_source_analysis import GlottalSourceAnalyzer
except ImportError:
    # フォールバック用
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'analyzers'))
    from prosodic_features import ProsodicFeatureExtractor
    from spectral_analysis import SpectralAnalyzer
    from quality_separation import QualitySeparationEngine
    from glottal_source_analysis import GlottalSourceAnalyzer

class MLFeatureExtractor:
    """機械学習用包括的特徴量抽出器"""
    
    def __init__(self):
        self.sample_rate = 22050
        self.hop_length = 512
        self.win_length = 2048
        
        # 抽出器初期化
        try:
            self.prosodic_extractor = ProsodicFeatureExtractor()
            self.spectral_analyzer = SpectralAnalyzer(
                sample_rate=self.sample_rate,
                hop_length=self.hop_length,
                win_length=self.win_length
            )
            self.quality_separator = QualitySeparationEngine(sample_rate=self.sample_rate)
            self.glottal_analyzer = GlottalSourceAnalyzer(sample_rate=self.sample_rate)
        except Exception as e:
            print(f"警告: 一部の抽出器の初期化に失敗しました: {e}")
            self.prosodic_extractor = None
            self.spectral_analyzer = None
            self.quality_separator = None
            self.glottal_analyzer = None
        
    def extract_comprehensive_features(self, audio_path):
        """包括的特徴量抽出"""
        print(f"特徴量抽出中: {os.path.basename(audio_path)}")
        
        try:
            # 音声読み込み
            audio, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)
            
            # RMS正規化
            rms = np.sqrt(np.mean(audio**2))
            if rms > 0:
                audio_normalized = audio / rms * 0.1
            else:
                audio_normalized = audio
            
            features = {}
            
            # 1. 基本的音響特徴量
            features.update(self._extract_basic_features(audio_normalized, sr))
            
            # 2. 韻律特徴量（Parselmouth）
            if self.prosodic_extractor:
                temp_path = "temp_ml_audio.wav"
                sf.write(temp_path, audio_normalized, sr)
                prosodic_features = self.prosodic_extractor.extract_all_features(temp_path)
                features.update(prosodic_features)
                try:
                    os.remove(temp_path)
                except:
                    pass
            
            # 3. スペクトラル特徴量
            if self.spectral_analyzer:
                spectral_features = self.spectral_analyzer.extract_all_spectral_features(audio_normalized)
                features.update(spectral_features)
            
            # 4. 品質関連特徴量
            if self.quality_separator and self.prosodic_extractor and self.spectral_analyzer:
                quality_tension, quality_profile, quality_diag = self.quality_separator.separate_quality_and_tension(
                    features, prosodic_features, spectral_features
                )
                features['quality_tension'] = quality_tension
                features['quality_overall_score'] = quality_profile.get('overall_score', 0.5)
                features['quality_hnr_score'] = quality_profile.get('hnr_score', 0.5)
                features['quality_voicing_score'] = quality_profile.get('voicing_score', 0.5)
                features['quality_spectral_score'] = quality_profile.get('spectral_score', 0.5)
                features['quality_stability_score'] = quality_profile.get('stability_score', 0.5)
            
            # 5. 声門源特徴量
            if self.glottal_analyzer:
                glottal_results = self.glottal_analyzer.analyze_glottal_source(audio_normalized, None, None)
                features['glottal_effort_score'] = glottal_results.get('glottal_effort_score', 0.5)
                features['glottal_confidence'] = glottal_results.get('glottal_confidence', 0.5)
                features['glottal_pulse_count'] = glottal_results.get('glottal_pulse_count', 0)
                features['avg_pulse_energy'] = glottal_results.get('avg_pulse_energy', 0)
                features['avg_asymmetry_ratio'] = glottal_results.get('avg_asymmetry_ratio', 1.0)
                features['avg_opening_quotient'] = glottal_results.get('avg_opening_quotient', 0.5)
            
            # 6. 高次統計特徴量
            features.update(self._extract_advanced_statistics(audio_normalized))
            
            # 7. 時間-周波数領域特徴量
            features.update(self._extract_time_frequency_features(audio_normalized, sr))
            
            # 8. 非線形動力学特徴量
            features.update(self._extract_nonlinear_dynamics(audio_normalized))
            
            return features
            
        except Exception as e:
            print(f"特徴量抽出エラー: {e}")
            return {}
    
    def _extract_basic_features(self, audio, sr):
        """基本音響特徴量"""
        features = {}
        
        try:
            # MFCC（13次元）
            mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13, hop_length=self.hop_length)
            for i in range(13):
                features[f'mfcc_{i}_mean'] = np.mean(mfcc[i])
                features[f'mfcc_{i}_std'] = np.std(mfcc[i])
                features[f'mfcc_{i}_skew'] = self._safe_skewness(mfcc[i])
                features[f'mfcc_{i}_kurt'] = self._safe_kurtosis(mfcc[i])
            
            # MFCC delta features
            mfcc_delta = librosa.feature.delta(mfcc)
            for i in range(13):
                features[f'mfcc_delta_{i}_mean'] = np.mean(mfcc_delta[i])
                features[f'mfcc_delta_{i}_std'] = np.std(mfcc_delta[i])
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=audio, sr=sr, hop_length=self.hop_length)
            features['chroma_mean'] = np.mean(chroma)
            features['chroma_std'] = np.std(chroma)
            features['chroma_var'] = np.var(chroma)
            
            # Spectral contrast
            contrast = librosa.feature.spectral_contrast(y=audio, sr=sr, hop_length=self.hop_length)
            features['spectral_contrast_mean'] = np.mean(contrast)
            features['spectral_contrast_std'] = np.std(contrast)
            
            # Tonnetz features
            tonnetz = librosa.feature.tonnetz(y=audio, sr=sr)
            features['tonnetz_mean'] = np.mean(tonnetz)
            features['tonnetz_std'] = np.std(tonnetz)
            
            # Poly features
            poly_features = librosa.feature.poly_features(y=audio, sr=sr, hop_length=self.hop_length, order=1)
            features['poly_0_mean'] = np.mean(poly_features[0])
            features['poly_1_mean'] = np.mean(poly_features[1])
            
        except Exception as e:
            print(f"基本特徴量抽出エラー: {e}")
            
        return features
    
    def _extract_advanced_statistics(self, audio):
        """高次統計特徴量"""
        features = {}
        
        try:
            # 振幅の統計量
            features['audio_mean'] = np.mean(audio)
            features['audio_std'] = np.std(audio)
            features['audio_var'] = np.var(audio)
            features['audio_skewness'] = self._safe_skewness(audio)
            features['audio_kurtosis'] = self._safe_kurtosis(audio)
            features['audio_min'] = np.min(audio)
            features['audio_max'] = np.max(audio)
            features['audio_range'] = np.max(audio) - np.min(audio)
            features['audio_iqr'] = np.percentile(audio, 75) - np.percentile(audio, 25)
            
            # エネルギー関連
            energy = audio ** 2
            features['energy_mean'] = np.mean(energy)
            features['energy_std'] = np.std(energy)
            features['energy_entropy'] = self._calculate_entropy(energy)
            
            # パワースペクトラム統計
            fft = np.abs(np.fft.fft(audio))
            power_spectrum = fft ** 2
            features['power_spectrum_mean'] = np.mean(power_spectrum)
            features['power_spectrum_std'] = np.std(power_spectrum)
            features['power_spectrum_skew'] = self._safe_skewness(power_spectrum)
            features['power_spectrum_kurt'] = self._safe_kurtosis(power_spectrum)
            
        except Exception as e:
            print(f"高次統計特徴量エラー: {e}")
            
        return features
    
    def _extract_time_frequency_features(self, audio, sr):
        """時間-周波数領域特徴量"""
        features = {}
        
        try:
            # Short-time Fourier transform
            stft = librosa.stft(audio, hop_length=self.hop_length, win_length=self.win_length)
            magnitude = np.abs(stft)
            
            # スペクトログラム統計
            features['spectrogram_mean'] = np.mean(magnitude)
            features['spectrogram_std'] = np.std(magnitude)
            features['spectrogram_var'] = np.var(magnitude)
            
            # 周波数別統計
            freq_means = np.mean(magnitude, axis=1)
            features['freq_means_mean'] = np.mean(freq_means)
            features['freq_means_std'] = np.std(freq_means)
            
            # 時間別統計
            time_means = np.mean(magnitude, axis=0)
            features['time_means_mean'] = np.mean(time_means)
            features['time_means_std'] = np.std(time_means)
            
            # スペクトラルバンドエネルギー比
            freqs = librosa.fft_frequencies(sr=sr, n_fft=self.win_length)
            
            # 低周波帯域 (0-1kHz)
            low_mask = (freqs >= 0) & (freqs <= 1000)
            low_energy = np.mean(magnitude[low_mask, :])
            
            # 中周波帯域 (1-4kHz)
            mid_mask = (freqs > 1000) & (freqs <= 4000)
            mid_energy = np.mean(magnitude[mid_mask, :])
            
            # 高周波帯域 (4kHz-Nyquist)
            high_mask = (freqs > 4000) & (freqs <= sr//2)
            high_energy = np.mean(magnitude[high_mask, :])
            
            total_energy = low_energy + mid_energy + high_energy
            if total_energy > 0:
                features['low_freq_ratio'] = low_energy / total_energy
                features['mid_freq_ratio'] = mid_energy / total_energy
                features['high_freq_ratio'] = high_energy / total_energy
            else:
                features['low_freq_ratio'] = 0.33
                features['mid_freq_ratio'] = 0.33
                features['high_freq_ratio'] = 0.34
                
        except Exception as e:
            print(f"時間-周波数特徴量エラー: {e}")
            
        return features
    
    def _extract_nonlinear_dynamics(self, audio):
        """非線形動力学特徴量"""
        features = {}
        
        try:
            # サンプルエントロピー簡易版
            features['sample_entropy'] = self._simple_sample_entropy(audio)
            
            # 近似エントロピー
            features['approx_entropy'] = self._approximate_entropy(audio)
            
            # Hurst指数簡易推定
            features['hurst_exponent'] = self._simple_hurst_exponent(audio)
            
            # Lyapunov指数簡易推定
            features['lyapunov_exponent'] = self._simple_lyapunov_exponent(audio)
            
        except Exception as e:
            print(f"非線形動力学特徴量エラー: {e}")
            
        return features
    
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
            hist, _ = np.histogram(data, bins=50)
            hist = hist + 1e-8  # ゼロ除算回避
            prob = hist / np.sum(hist)
            entropy = -np.sum(prob * np.log2(prob))
            return entropy
        except:
            return 1.0
    
    def _simple_sample_entropy(self, data, m=2, r=None):
        """簡易サンプルエントロピー"""
        try:
            if r is None:
                r = 0.2 * np.std(data)
            N = len(data)
            if N < 100:
                return 1.0
                
            def _maxdist(xi, xj, N):
                return max([abs(ua - va) for ua, va in zip(xi, xj)])
            
            def _phi(m):
                patterns = np.array([data[i:i + m] for i in range(N - m + 1)])
                C = np.zeros(N - m + 1)
                
                for i in range(N - m + 1):
                    template = patterns[i]
                    distances = [_maxdist(template, patterns[j], m) 
                               for j in range(N - m + 1)]
                    C[i] = sum([1 for d in distances if d <= r])
                
                return (N - m + 1.0) / sum(C)
            
            return np.log(_phi(m) / _phi(m + 1))
        except:
            return 1.0
    
    def _approximate_entropy(self, data, m=2, r=None):
        """近似エントロピー"""
        try:
            if r is None:
                r = 0.2 * np.std(data)
            N = len(data)
            if N < 100:
                return 1.0
            
            def _phi(m):
                patterns = np.array([data[i:i + m] for i in range(N - m + 1)])
                phi = 0.0
                
                for i in range(N - m + 1):
                    template = patterns[i]
                    matches = 0
                    for j in range(N - m + 1):
                        if max([abs(ua - va) for ua, va in zip(template, patterns[j])]) <= r:
                            matches += 1
                    phi += np.log((matches) / (N - m + 1.0))
                
                return phi / (N - m + 1.0)
            
            return _phi(m) - _phi(m + 1)
        except:
            return 1.0
    
    def _simple_hurst_exponent(self, data):
        """簡易Hurst指数"""
        try:
            N = len(data)
            if N < 100:
                return 0.5
            
            # R/S analysis simplified
            mean_data = np.mean(data)
            y = np.cumsum(data - mean_data)
            
            R = np.max(y) - np.min(y)
            S = np.std(data)
            
            if S == 0:
                return 0.5
            
            rs = R / S
            hurst = np.log(rs) / np.log(N)
            return max(0.0, min(1.0, hurst))
        except:
            return 0.5
    
    def _simple_lyapunov_exponent(self, data):
        """簡易Lyapunov指数"""
        try:
            N = len(data)
            if N < 100:
                return 0.0
            
            # 簡易的な最大Lyapunov指数推定
            embedding_dim = 3
            delay = 1
            
            # 位相空間再構成
            M = N - (embedding_dim - 1) * delay
            if M <= 0:
                return 0.0
            
            embedded = np.zeros((M, embedding_dim))
            for i in range(M):
                for j in range(embedding_dim):
                    embedded[i, j] = data[i + j * delay]
            
            # 最近傍点間の平均発散率を計算（簡易版）
            divergences = []
            sample_size = min(M, 50)  # 計算効率のため制限
            
            for i in range(sample_size):
                distances = [np.linalg.norm(embedded[i] - embedded[j]) 
                           for j in range(M) if j != i]
                if distances:
                    min_distance = min(distances)
                    if min_distance > 0:
                        divergences.append(np.log(min_distance))
            
            if divergences:
                return np.mean(divergences)
            else:
                return 0.0
        except:
            return 0.0

def extract_all_samples():
    """全サンプルの特徴量を抽出"""
    
    # サンプルファイルのリスト
    sample_files = [
        ("sample/Tension_Low_01.wav", "Low"),
        ("sample/Tension_Low_02.wav", "Low"),
        ("sample/Tension_Low_03.wav", "Low"),
        ("sample/Tension_Neutral_01.wav", "Neutral"),
        ("sample/Tension_Neutral_02.wav", "Neutral"),
        ("sample/Tension_Neutral_03.wav", "Neutral"),
        ("sample/Tension_High_01.wav", "High"),
        ("sample/Tension_High_02.wav", "High"),
        ("sample/Tension_High_03.wav", "High"),
    ]
    
    extractor = MLFeatureExtractor()
    dataset = []
    
    print("=" * 60)
    print("機械学習用特徴量データベース構築開始")
    print("=" * 60)
    
    for file_path, label in sample_files:
        if os.path.exists(file_path):
            features = extractor.extract_comprehensive_features(file_path)
            if features:
                features['filename'] = os.path.basename(file_path)
                features['label'] = label
                dataset.append(features)
                print(f"✓ {os.path.basename(file_path)}: {len(features)}個の特徴量抽出完了")
            else:
                print(f"✗ {os.path.basename(file_path)}: 特徴量抽出失敗")
        else:
            print(f"✗ ファイルが見つかりません: {file_path}")
    
    if dataset:
        # DataFrameに変換
        df = pd.DataFrame(dataset)
        
        # CSVファイルに保存
        output_file = "ml_features_database.csv"
        df.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"\n✓ 特徴量データベース保存完了: {output_file}")
        print(f"  - サンプル数: {len(df)}")
        print(f"  - 特徴量次元: {len(df.columns) - 2}")  # filename, labelを除く
        print(f"  - Low: {len(df[df['label'] == 'Low'])}")
        print(f"  - Neutral: {len(df[df['label'] == 'Neutral'])}")
        print(f"  - High: {len(df[df['label'] == 'High'])}")
        
        return df
    else:
        print("✗ 特徴量抽出に失敗しました")
        return None

if __name__ == "__main__":
    extract_all_samples()