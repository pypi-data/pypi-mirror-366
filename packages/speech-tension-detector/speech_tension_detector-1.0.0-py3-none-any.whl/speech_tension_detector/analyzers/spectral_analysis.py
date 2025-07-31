# -*- coding: utf-8 -*-
"""
Spectral Analysis Module
スペクトラル解析モジュール

声門努力検出のための高精度スペクトラル特徴量抽出:
- Spectral Tilt (スペクトラル傾斜) - 主要な声門努力指標
- Spectral Centroid, Rolloff, Bandwidth
- 調波成分解析
- CEPSTRUMベースの分析
"""

import numpy as np
import librosa
import scipy.signal
from scipy import stats
import warnings

warnings.filterwarnings('ignore')

class SpectralAnalyzer:
    """スペクトラル解析クラス"""
    
    def __init__(self, sample_rate=22050, hop_length=512, win_length=2048):
        """
        初期化
        
        Args:
            sample_rate (int): サンプリングレート
            hop_length (int): ホップ長
            win_length (int): 窓長
        """
        self.sample_rate = sample_rate
        self.hop_length = hop_length
        self.win_length = win_length
        
        # スペクトラル解析パラメータ
        self.n_fft = win_length
        self.window = 'hann'
        
        # 周波数帯域定義（声門努力解析用）
        self.low_freq_min = 0
        self.low_freq_max = 1000      # 低周波数帯域: 0-1kHz
        self.high_freq_min = 1000
        self.high_freq_max = sample_rate // 2  # 高周波数帯域: 1kHz-Nyquist
        
        # 調波解析用
        self.harmonic_threshold = 0.1
        
    def extract_all_spectral_features(self, audio):
        """
        全スペクトラル特徴量を抽出
        
        Args:
            audio (np.ndarray): 音声信号
            
        Returns:
            dict: スペクトラル特徴量辞書
        """
        features = {}
        
        try:
            # 1. 基本スペクトラル傾斜計算
            spectral_tilt = self.calculate_spectral_tilt(audio)
            features['spectral_tilt'] = spectral_tilt
            
            # 2. 改良版スペクトラル傾斜（複数手法）
            tilt_features = self.calculate_advanced_spectral_tilt(audio)
            features.update(tilt_features)
            
            # 3. 調波成分ベースの傾斜
            harmonic_tilt = self.calculate_harmonic_tilt(audio)
            features['harmonic_tilt'] = harmonic_tilt
            
            # 4. その他のスペクトラル特徴量
            other_features = self.calculate_other_spectral_features(audio)
            features.update(other_features)
            
            # 5. CEPSTRUMベースの分析
            cepstral_features = self.calculate_cepstral_features(audio)
            features.update(cepstral_features)
            
            # 6. 声門努力スコア計算
            features['vocal_effort_score'] = self.calculate_vocal_effort_from_spectral(features)
            
            print(f"スペクトラル特徴量抽出完了: {len(features)}種類")
            return features
            
        except Exception as e:
            print(f"スペクトラル解析エラー: {e}")
            return {}
    
    def calculate_spectral_tilt(self, audio):
        """
        基本的なスペクトラル傾斜を計算
        
        Args:
            audio (np.ndarray): 音声信号
            
        Returns:
            float: スペクトラル傾斜 (dB)
        """
        try:
            # STFTでスペクトログラム取得
            stft = librosa.stft(audio, 
                              hop_length=self.hop_length, 
                              win_length=self.win_length,
                              window=self.window)
            magnitude = np.abs(stft)
            
            # 周波数軸
            freqs = librosa.fft_frequencies(sr=self.sample_rate, n_fft=self.n_fft)
            
            # 各フレームでスペクトラル傾斜を計算
            tilts = []
            
            for frame in range(magnitude.shape[1]):
                spec = magnitude[:, frame]
                
                # パワースペクトラムに変換
                power_spec = spec ** 2
                
                # 低周波数・高周波数帯域のマスク
                low_mask = (freqs >= self.low_freq_min) & (freqs <= self.low_freq_max)
                high_mask = (freqs >= self.high_freq_min) & (freqs <= self.high_freq_max)
                
                # 各帯域の平均パワー計算
                low_power = np.mean(power_spec[low_mask])
                high_power = np.mean(power_spec[high_mask])
                
                # dB変換して傾斜計算
                if low_power > 0 and high_power > 0:
                    low_db = 10 * np.log10(low_power)
                    high_db = 10 * np.log10(high_power)
                    tilt = high_db - low_db  # 高周波数 - 低周波数
                    tilts.append(tilt)
            
            # 全フレームの平均
            spectral_tilt = np.mean(tilts) if tilts else 0.0
            
            return spectral_tilt
            
        except Exception as e:
            print(f"スペクトラル傾斜計算エラー: {e}")
            return 0.0
    
    def calculate_advanced_spectral_tilt(self, audio):
        """
        改良版スペクトラル傾斜計算（複数手法）
        
        Args:
            audio (np.ndarray): 音声信号
            
        Returns:
            dict: 改良版傾斜特徴量
        """
        features = {}
        
        try:
            # STFT計算
            stft = librosa.stft(audio, 
                              hop_length=self.hop_length, 
                              win_length=self.win_length,
                              window=self.window)
            magnitude = np.abs(stft)
            power_spec = magnitude ** 2
            
            freqs = librosa.fft_frequencies(sr=self.sample_rate, n_fft=self.n_fft)
            
            # 手法1: 線形回帰による傾斜
            regression_tilts = []
            
            # 手法2: 複数帯域での傾斜
            multiband_tilts = []
            
            # 手法3: 重み付き傾斜
            weighted_tilts = []
            
            for frame in range(power_spec.shape[1]):
                spec = power_spec[:, frame]
                
                # 手法1: 線形回帰による傾斜計算
                valid_indices = spec > 0
                if np.sum(valid_indices) > 10:  # 十分なデータポイントがある場合
                    log_spec = 10 * np.log10(spec[valid_indices])
                    log_freqs = np.log10(freqs[valid_indices] + 1)  # +1 to avoid log(0)
                    
                    # 線形回帰でスロープ計算
                    slope, intercept, r_value, p_value, std_err = stats.linregress(log_freqs, log_spec)
                    regression_tilts.append(slope)
                
                # 手法2: 複数帯域での傾斜（より詳細）
                bands = [
                    (0, 500),      # 超低域
                    (500, 1000),   # 低域
                    (1000, 2000),  # 中低域
                    (2000, 4000),  # 中高域
                    (4000, 8000)   # 高域
                ]
                
                band_powers = []
                for low, high in bands:
                    mask = (freqs >= low) & (freqs <= high)
                    if np.sum(mask) > 0:
                        band_power = np.mean(spec[mask])
                        band_powers.append(10 * np.log10(band_power) if band_power > 0 else -80)
                    else:
                        band_powers.append(-80)
                
                if len(band_powers) == len(bands):
                    # 各帯域間の傾斜計算
                    multiband_tilt = (band_powers[-1] - band_powers[0]) / (len(bands) - 1)
                    multiband_tilts.append(multiband_tilt)
                
                # 手法3: 知覚重み付き傾斜
                # A-weighting similar curve for perceptual importance
                perceptual_weights = np.ones_like(freqs)
                for i, f in enumerate(freqs):
                    if f < 1000:
                        perceptual_weights[i] = 0.5
                    elif f > 4000:
                        perceptual_weights[i] = 2.0
                
                weighted_spec = spec * perceptual_weights
                low_weighted = np.mean(weighted_spec[freqs <= 1000])
                high_weighted = np.mean(weighted_spec[freqs > 1000])
                
                if low_weighted > 0 and high_weighted > 0:
                    weighted_tilt = 10 * np.log10(high_weighted) - 10 * np.log10(low_weighted)
                    weighted_tilts.append(weighted_tilt)
            
            # 結果の統計量を計算
            if regression_tilts:
                features['spectral_tilt_regression'] = np.mean(regression_tilts)
                features['spectral_tilt_regression_std'] = np.std(regression_tilts)
            else:
                features['spectral_tilt_regression'] = 0.0
                features['spectral_tilt_regression_std'] = 0.0
            
            if multiband_tilts:
                features['spectral_tilt_multiband'] = np.mean(multiband_tilts)
                features['spectral_tilt_multiband_std'] = np.std(multiband_tilts)
            else:
                features['spectral_tilt_multiband'] = 0.0
                features['spectral_tilt_multiband_std'] = 0.0
                
            if weighted_tilts:
                features['spectral_tilt_weighted'] = np.mean(weighted_tilts)
                features['spectral_tilt_weighted_std'] = np.std(weighted_tilts)
            else:
                features['spectral_tilt_weighted'] = 0.0
                features['spectral_tilt_weighted_std'] = 0.0
            
            return features
            
        except Exception as e:
            print(f"改良版スペクトラル傾斜計算エラー: {e}")
            return {
                'spectral_tilt_regression': 0.0,
                'spectral_tilt_regression_std': 0.0,
                'spectral_tilt_multiband': 0.0,
                'spectral_tilt_multiband_std': 0.0,
                'spectral_tilt_weighted': 0.0,
                'spectral_tilt_weighted_std': 0.0
            }
    
    def calculate_harmonic_tilt(self, audio):
        """
        調波成分ベースのスペクトラル傾斜を計算
        
        Args:
            audio (np.ndarray): 音声信号
            
        Returns:
            float: 調波スペクトラル傾斜
        """
        try:
            # F0推定
            f0 = librosa.yin(audio, 
                           fmin=librosa.note_to_hz('C2'), 
                           fmax=librosa.note_to_hz('C7'),
                           sr=self.sample_rate)
            
            # 平均F0計算（無声部分を除外）
            voiced_f0 = f0[f0 > 0]
            if len(voiced_f0) == 0:
                return 0.0
            
            mean_f0 = np.mean(voiced_f0)
            
            # STFTでスペクトル取得
            stft = librosa.stft(audio, 
                              hop_length=self.hop_length, 
                              win_length=self.win_length)
            magnitude = np.abs(stft)
            power_spec = magnitude ** 2
            
            freqs = librosa.fft_frequencies(sr=self.sample_rate, n_fft=self.n_fft)
            
            # 調波成分の位置を特定
            harmonics = []
            for h in range(1, 11):  # 1st to 10th harmonic
                harmonic_freq = mean_f0 * h
                if harmonic_freq < self.sample_rate / 2:
                    harmonics.append(harmonic_freq)
            
            if len(harmonics) < 3:
                return 0.0
            
            # 各調波での平均パワー計算
            harmonic_powers = []
            for harm_freq in harmonics:
                # 調波周波数周辺のパワーを取得
                freq_idx = np.argmin(np.abs(freqs - harm_freq))
                search_range = max(1, int(mean_f0 / 2 / (freqs[1] - freqs[0])))  # ±F0/2の範囲
                
                start_idx = max(0, freq_idx - search_range)
                end_idx = min(len(freqs), freq_idx + search_range)
                
                harm_power = np.mean(power_spec[start_idx:end_idx, :])
                harmonic_powers.append(10 * np.log10(harm_power) if harm_power > 0 else -80)
            
            # 調波パワーの傾斜を線形回帰で計算
            if len(harmonic_powers) >= 3:
                harmonic_indices = np.arange(len(harmonic_powers))
                slope, _, _, _, _ = stats.linregress(harmonic_indices, harmonic_powers)
                return slope
            else:
                return 0.0
                
        except Exception as e:
            print(f"調波スペクトラル傾斜計算エラー: {e}")
            return 0.0
    
    def calculate_other_spectral_features(self, audio):
        """
        その他のスペクトラル特徴量を計算
        
        Args:
            audio (np.ndarray): 音声信号
            
        Returns:
            dict: その他の特徴量
        """
        features = {}
        
        try:
            # Spectral Centroid
            spectral_centroids = librosa.feature.spectral_centroid(
                y=audio, sr=self.sample_rate, hop_length=self.hop_length)[0]
            features['spectral_centroid_mean'] = np.mean(spectral_centroids)
            features['spectral_centroid_std'] = np.std(spectral_centroids)
            
            # Spectral Rolloff
            spectral_rolloff = librosa.feature.spectral_rolloff(
                y=audio, sr=self.sample_rate, hop_length=self.hop_length)[0]
            features['spectral_rolloff_mean'] = np.mean(spectral_rolloff)
            features['spectral_rolloff_std'] = np.std(spectral_rolloff)
            
            # Spectral Bandwidth
            spectral_bandwidth = librosa.feature.spectral_bandwidth(
                y=audio, sr=self.sample_rate, hop_length=self.hop_length)[0]
            features['spectral_bandwidth_mean'] = np.mean(spectral_bandwidth)
            features['spectral_bandwidth_std'] = np.std(spectral_bandwidth)
            
            # Spectral Contrast
            spectral_contrast = librosa.feature.spectral_contrast(
                y=audio, sr=self.sample_rate, hop_length=self.hop_length)
            features['spectral_contrast_mean'] = np.mean(spectral_contrast)
            features['spectral_contrast_std'] = np.std(spectral_contrast)
            
            # Spectral Flatness (Wiener Entropy)
            spectral_flatness = librosa.feature.spectral_flatness(
                y=audio, hop_length=self.hop_length)[0]
            features['spectral_flatness_mean'] = np.mean(spectral_flatness)
            features['spectral_flatness_std'] = np.std(spectral_flatness)
            
            return features
            
        except Exception as e:
            print(f"その他スペクトラル特徴量計算エラー: {e}")
            return {
                'spectral_centroid_mean': 0.0, 'spectral_centroid_std': 0.0,
                'spectral_rolloff_mean': 0.0, 'spectral_rolloff_std': 0.0,
                'spectral_bandwidth_mean': 0.0, 'spectral_bandwidth_std': 0.0,
                'spectral_contrast_mean': 0.0, 'spectral_contrast_std': 0.0,
                'spectral_flatness_mean': 0.0, 'spectral_flatness_std': 0.0
            }
    
    def calculate_cepstral_features(self, audio):
        """
        CEPSTRUMベースの特徴量を計算
        
        Args:
            audio (np.ndarray): 音声信号
            
        Returns:
            dict: CEPSTRAL特徴量
        """
        features = {}
        
        try:
            # MFCC（既に他で計算されている可能性があるが、ここでも計算）
            mfcc = librosa.feature.mfcc(y=audio, sr=self.sample_rate, 
                                      n_mfcc=13, hop_length=self.hop_length)
            
            # MFCC統計量
            features['mfcc_mean'] = np.mean(mfcc, axis=1)
            features['mfcc_std'] = np.std(mfcc, axis=1)
            
            # Delta MFCC (1st derivative)
            mfcc_delta = librosa.feature.delta(mfcc)
            features['mfcc_delta_mean'] = np.mean(mfcc_delta, axis=1)
            features['mfcc_delta_std'] = np.std(mfcc_delta, axis=1)
            
            # Delta-Delta MFCC (2nd derivative)
            mfcc_delta2 = librosa.feature.delta(mfcc, order=2)
            features['mfcc_delta2_mean'] = np.mean(mfcc_delta2, axis=1)
            features['mfcc_delta2_std'] = np.std(mfcc_delta2, axis=1)
            
            return features
            
        except Exception as e:
            print(f"CEPSTRAL特徴量計算エラー: {e}")
            # デフォルト値を返す
            default_features = {}
            for feature_type in ['mfcc_mean', 'mfcc_std', 'mfcc_delta_mean', 
                               'mfcc_delta_std', 'mfcc_delta2_mean', 'mfcc_delta2_std']:
                default_features[feature_type] = np.zeros(13)
            return default_features
    
    def calculate_vocal_effort_from_spectral(self, features):
        """
        スペクトラル特徴量から声門努力を推定
        
        Args:
            features (dict): スペクトラル特徴量
            
        Returns:
            float: 声門努力スコア (0.0-1.0)
        """
        try:
            # スペクトラル傾斜を主要指標として使用
            main_tilt = features.get('spectral_tilt', 0)
            
            # 複数手法の結果を統合
            regression_tilt = features.get('spectral_tilt_regression', 0)
            multiband_tilt = features.get('spectral_tilt_multiband', 0)
            weighted_tilt = features.get('spectral_tilt_weighted', 0)
            harmonic_tilt = features.get('harmonic_tilt', 0)
            
            # 傾斜値の正規化（-20dB ~ +10dB を 0~1 に）
            def normalize_tilt(tilt_value):
                return np.clip((tilt_value + 20) / 30, 0, 1)
            
            # 各手法の重み
            weights = {
                'main': 0.3,
                'regression': 0.25,
                'multiband': 0.2,
                'weighted': 0.15,
                'harmonic': 0.1
            }
            
            # 重み付き平均
            effort_score = (
                normalize_tilt(main_tilt) * weights['main'] +
                normalize_tilt(regression_tilt) * weights['regression'] +
                normalize_tilt(multiband_tilt) * weights['multiband'] +
                normalize_tilt(weighted_tilt) * weights['weighted'] +
                normalize_tilt(harmonic_tilt) * weights['harmonic']
            )
            
            return np.clip(effort_score, 0.0, 1.0)
            
        except Exception as e:
            print(f"スペクトラルベース声門努力計算エラー: {e}")
            return 0.5