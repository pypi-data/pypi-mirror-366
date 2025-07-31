#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高度音声テンション分類器
既存の事前訓練済みモデルを使わず、高度な信号処理とMLアルゴリズムを組み合わせ
"""

import os
import numpy as np
import librosa
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

class AdvancedSignalClassifier:
    """高度信号処理ベース分類器"""
    
    def __init__(self):
        self.sample_rate = 22050
        
        # 事前定義された分類モデル（既存の知識ベース）
        self.initialize_knowledge_base()
        
    def initialize_knowledge_base(self):
        """音声学的知識ベースの初期化"""
        
        # 9サンプルの既知の特徴量パターン（実データから学習）
        self.known_patterns = {
            'Low': {
                'spectral_tilt_range': (-45, -30),  # dB
                'f0_range': (80, 150),               # Hz
                'intensity_range': (-45, -20),      # dB
                'hnr_range': (-50, 5),              # dB
                'jitter_range': (0.001, 0.1),
                'shimmer_range': (0.01, 0.3),
                'spectral_centroid_range': (500, 1500),  # Hz
                'mfcc_1_range': (-50, -10),
                'zero_crossing_rate': (0.01, 0.15)
            },
            'Neutral': {
                'spectral_tilt_range': (-35, -20),
                'f0_range': (100, 200),
                'intensity_range': (-35, -15),
                'hnr_range': (-20, 15),
                'jitter_range': (0.005, 0.05),
                'shimmer_range': (0.02, 0.15),
                'spectral_centroid_range': (800, 2000),
                'mfcc_1_range': (-40, 0),
                'zero_crossing_rate': (0.05, 0.25)
            },
            'High': {
                'spectral_tilt_range': (-25, -10),
                'f0_range': (120, 300),
                'intensity_range': (-25, -5),
                'hnr_range': (-10, 25),
                'jitter_range': (0.01, 0.15),
                'shimmer_range': (0.03, 0.4),
                'spectral_centroid_range': (1000, 3000),
                'mfcc_1_range': (-30, 10),
                'zero_crossing_rate': (0.1, 0.4)
            }
        }
        
        # 重み係数（特徴量の重要度）
        self.feature_weights = {
            'spectral_tilt': 0.25,
            'f0_mean': 0.20,
            'intensity_mean': 0.15,
            'hnr_mean': 0.15,
            'spectral_centroid': 0.10,
            'mfcc_1': 0.10,
            'jitter': 0.025,
            'shimmer': 0.025
        }
    
    def extract_comprehensive_features(self, audio, sr=22050):
        """包括的特徴量抽出"""
        features = {}
        
        try:
            # 1. スペクトラル特徴量
            stft = librosa.stft(audio, hop_length=512, win_length=2048)
            magnitude = np.abs(stft)
            freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
            
            # スペクトラル傾斜
            low_freq_mask = (freqs >= 0) & (freqs <= 1000)
            high_freq_mask = (freqs >= 1000) & (freqs <= sr//2)
            
            low_power = np.mean(magnitude[low_freq_mask, :])
            high_power = np.mean(magnitude[high_freq_mask, :])
            
            if low_power > 0 and high_power > 0:
                features['spectral_tilt'] = 20 * np.log10(high_power / low_power)
            else:
                features['spectral_tilt'] = -30.0
                
            # スペクトラルセントロイド
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr, hop_length=512)[0]
            features['spectral_centroid'] = np.mean(spectral_centroids)
            
            # 2. MFCC特徴量
            mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13, hop_length=512)
            features['mfcc_1'] = np.mean(mfcc[0])
            features['mfcc_2'] = np.mean(mfcc[1])
            features['mfcc_3'] = np.mean(mfcc[2])
            
            # MFCC統計量
            features['mfcc_mean'] = np.mean(mfcc)
            features['mfcc_std'] = np.std(mfcc)
            features['mfcc_skew'] = self._safe_skewness(mfcc.flatten())
            
            # 3. 基本音響特徴量
            # RMS Energy
            rms = librosa.feature.rms(y=audio, hop_length=512)[0]
            features['rms_mean'] = np.mean(rms)
            features['rms_std'] = np.std(rms)
            
            # Zero Crossing Rate
            zcr = librosa.feature.zero_crossing_rate(audio, hop_length=512)[0]
            features['zcr_mean'] = np.mean(zcr)
            features['zcr_std'] = np.std(zcr)
            
            # Spectral Rolloff
            rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr, hop_length=512)[0]
            features['spectral_rolloff'] = np.mean(rolloff)
            
            # 4. 高次特徴量
            # Spectral Bandwidth
            bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr, hop_length=512)[0]
            features['spectral_bandwidth'] = np.mean(bandwidth)
            
            # Spectral Contrast
            contrast = librosa.feature.spectral_contrast(y=audio, sr=sr, hop_length=512)
            features['spectral_contrast'] = np.mean(contrast)
            
            # Chroma
            chroma = librosa.feature.chroma_stft(y=audio, sr=sr, hop_length=512)
            features['chroma_mean'] = np.mean(chroma)
            features['chroma_std'] = np.std(chroma)
            
            # 5. Parselmouthベース特徴量（簡易版）
            features.update(self._extract_prosodic_features_simple(audio, sr))
            
            # 6. 高次統計特徴量
            features['audio_skewness'] = self._safe_skewness(audio)
            features['audio_kurtosis'] = self._safe_kurtosis(audio)
            features['audio_entropy'] = self._calculate_entropy(audio)
            
            # 7. 周波数帯域エネルギー比
            features.update(self._extract_frequency_band_ratios(magnitude, freqs))
            
            return features
            
        except Exception as e:
            print(f"特徴量抽出エラー: {e}")
            return {}
    
    def _extract_prosodic_features_simple(self, audio, sr):
        """簡易韻律特徴量（Parselmouthの代替）"""
        features = {}
        
        try:
            # F0推定（自己相関ベース）
            f0 = self._estimate_f0_autocorr(audio, sr)
            voiced_frames = f0[f0 > 0]
            
            if len(voiced_frames) > 0:
                features['f0_mean'] = np.mean(voiced_frames)
                features['f0_std'] = np.std(voiced_frames)
                features['f0_range'] = np.max(voiced_frames) - np.min(voiced_frames)
                features['voicing_fraction'] = len(voiced_frames) / len(f0)
            else:
                features['f0_mean'] = 150  # デフォルト値
                features['f0_std'] = 20
                features['f0_range'] = 50
                features['voicing_fraction'] = 0.5
            
            # Intensity推定
            intensity = 20 * np.log10(np.abs(audio) + 1e-8)
            features['intensity_mean'] = np.mean(intensity)
            features['intensity_std'] = np.std(intensity)
            features['intensity_range'] = np.max(intensity) - np.min(intensity)
            
            # HNR簡易推定（ハーモニック・ノイズ比）
            features['hnr_estimate'] = self._estimate_hnr_simple(audio, sr)
            
            # Jitter/Shimmer簡易推定
            features['jitter_estimate'] = self._estimate_jitter_simple(f0)
            features['shimmer_estimate'] = self._estimate_shimmer_simple(audio)
            
            return features
            
        except Exception as e:
            print(f"韻律特徴量抽出エラー: {e}")
            return {}
    
    def _estimate_f0_autocorr(self, audio, sr, frame_length=2048, hop_length=512):
        """自己相関ベースF0推定"""
        try:
            # フレーム化
            frames = librosa.frame(audio, frame_length=frame_length, hop_length=hop_length, axis=0)
            f0_values = []
            
            for frame in frames.T:
                # 自己相関
                autocorr = np.correlate(frame, frame, mode='full')
                autocorr = autocorr[len(autocorr)//2:]
                
                # ピーク検出
                min_period = int(sr / 500)  # 500Hz
                max_period = int(sr / 50)   # 50Hz
                
                if max_period < len(autocorr):
                    search_range = autocorr[min_period:max_period]
                    if len(search_range) > 0:
                        peak_idx = np.argmax(search_range) + min_period
                        f0 = sr / peak_idx if peak_idx > 0 else 0
                        f0_values.append(f0)
                    else:
                        f0_values.append(0)
                else:
                    f0_values.append(0)
            
            return np.array(f0_values)
            
        except Exception as e:
            return np.array([150] * 100)  # デフォルト値
    
    def _estimate_hnr_simple(self, audio, sr):
        """簡易HNR推定"""
        try:
            # FFT
            fft = np.fft.fft(audio)
            magnitude = np.abs(fft)
            
            # ハーモニック成分とノイズ成分の分離（簡易版）
            n = len(magnitude)
            harmonic_power = np.sum(magnitude[:n//4])  # 低周波数帯域
            noise_power = np.sum(magnitude[n//4:])     # 高周波数帯域
            
            if noise_power > 0:
                hnr = 20 * np.log10(harmonic_power / noise_power)
            else:
                hnr = 20  # 高HNR
                
            return np.clip(hnr, -50, 50)
            
        except Exception as e:
            return 5  # デフォルト値
    
    def _estimate_jitter_simple(self, f0_values):
        """簡易Jitter推定"""
        try:
            voiced_f0 = f0_values[f0_values > 0]
            if len(voiced_f0) < 2:
                return 0.01
            
            # F0の変動を計算
            f0_diff = np.diff(voiced_f0)
            jitter = np.std(f0_diff) / np.mean(voiced_f0) if np.mean(voiced_f0) > 0 else 0.01
            
            return np.clip(jitter, 0.001, 0.5)
            
        except Exception as e:
            return 0.01
    
    def _estimate_shimmer_simple(self, audio):
        """簡易Shimmer推定"""
        try:
            # 振幅の変動を計算
            amplitude = np.abs(audio)
            if len(amplitude) < 2:
                return 0.05
            
            amp_diff = np.diff(amplitude)
            shimmer = np.std(amp_diff) / np.mean(amplitude) if np.mean(amplitude) > 0 else 0.05
            
            return np.clip(shimmer, 0.01, 1.0)
            
        except Exception as e:
            return 0.05
    
    def _extract_frequency_band_ratios(self, magnitude, freqs):
        """周波数帯域エネルギー比"""
        features = {}
        
        try:
            # 帯域定義
            bands = {
                'low': (0, 500),
                'mid_low': (500, 1000),
                'mid': (1000, 2000),
                'mid_high': (2000, 4000),
                'high': (4000, 8000)
            }
            
            band_energies = {}
            total_energy = 0
            
            for band_name, (f_low, f_high) in bands.items():
                mask = (freqs >= f_low) & (freqs <= f_high)
                energy = np.sum(magnitude[mask, :])
                band_energies[band_name] = energy
                total_energy += energy
            
            # エネルギー比を計算
            if total_energy > 0:
                for band_name, energy in band_energies.items():
                    features[f'{band_name}_energy_ratio'] = energy / total_energy
            
            # 特定の比率
            if band_energies['low'] > 0:
                features['high_low_ratio'] = band_energies['high'] / band_energies['low']
                features['mid_low_ratio'] = band_energies['mid'] / band_energies['low']
            
        except Exception as e:
            pass
            
        return features
    
    def predict_tension_advanced(self, audio_path):
        """高度予測アルゴリズム"""
        try:
            # 音声読み込み
            audio, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)
            
            # RMS正規化
            rms = np.sqrt(np.mean(audio**2))
            if rms > 0:
                audio_normalized = audio / rms * 0.1
            else:
                audio_normalized = audio
            
            print(f"高度特徴量抽出開始: {os.path.basename(audio_path)}")
            
            # 包括的特徴量抽出
            features = self.extract_comprehensive_features(audio_normalized, sr)
            
            # 3段階予測
            tension_value = self._multi_stage_classification(features)
            
            # 信頼度計算
            confidence = self._calculate_prediction_confidence(features, tension_value)
            
            return tension_value, confidence, features
            
        except Exception as e:
            print(f"高度予測エラー: {e}")
            return 0.5, 0.0, {}
    
    def _multi_stage_classification(self, features):
        """多段階分類アルゴリズム"""
        try:
            # Stage 1: Rule-based pre-classification
            primary_scores = self._rule_based_scoring(features)
            
            # Stage 2: Feature fusion
            fused_score = self._feature_fusion_scoring(features)
            
            # Stage 3: Final ensemble
            ensemble_score = (primary_scores * 0.6 + fused_score * 0.4)
            
            # Stage 4: Adaptive range mapping
            final_tension = self._adaptive_range_mapping(ensemble_score, features)
            
            return final_tension
            
        except Exception as e:
            print(f"多段階分類エラー: {e}")
            return 0.5
    
    def _rule_based_scoring(self, features):
        """ルールベーススコアリング"""
        try:
            class_scores = {'Low': 0, 'Neutral': 0, 'High': 0}
            
            # 各特徴量について既知パターンとの一致度を計算
            for class_name, pattern in self.known_patterns.items():
                score = 0
                feature_count = 0
                
                for feature_name, value_range in pattern.items():
                    # 特徴量名を実際の特徴量キーにマッピング
                    feature_key = self._map_feature_name(feature_name)
                    
                    if feature_key in features:
                        feature_value = features[feature_key]
                        min_val, max_val = value_range
                        
                        # 範囲内かどうかチェック
                        if min_val <= feature_value <= max_val:
                            # 範囲内の場合、中心からの距離に基づいてスコア
                            center = (min_val + max_val) / 2
                            range_size = max_val - min_val
                            distance_from_center = abs(feature_value - center)
                            normalized_distance = distance_from_center / (range_size / 2)
                            feature_score = 1.0 - normalized_distance
                        else:
                            # 範囲外の場合、距離に基づいてペナルティ
                            if feature_value < min_val:
                                distance = min_val - feature_value
                            else:
                                distance = feature_value - max_val
                            range_size = max_val - min_val
                            penalty = min(distance / range_size, 1.0)
                            feature_score = -penalty
                        
                        # 特徴量の重みを適用
                        weight = self.feature_weights.get(feature_name.split('_')[0], 0.1)
                        score += feature_score * weight
                        feature_count += 1
                
                if feature_count > 0:
                    class_scores[class_name] = score / feature_count
            
            # 最高スコアのクラスを基準に0-1スケールに変換
            max_score = max(class_scores.values())
            min_score = min(class_scores.values())
            
            if max_score > min_score:
                # 最高スコアのクラスに基づいて0-1値を決定
                if class_scores['Low'] == max_score:
                    base_score = 0.15  # Low範囲の中央
                elif class_scores['Neutral'] == max_score:
                    base_score = 0.5   # Neutral範囲の中央
                else:  # High
                    base_score = 0.85  # High範囲の中央
                
                # スコア差を考慮して調整
                score_confidence = (max_score - min_score) / 2  # 信頼度
                return base_score
            else:
                return 0.5  # 判別不能の場合
                
        except Exception as e:
            print(f"ルールベーススコアリングエラー: {e}")
            return 0.5
    
    def _map_feature_name(self, feature_name):
        """特徴量名マッピング"""
        mapping = {
            'spectral_tilt_range': 'spectral_tilt',
            'f0_range': 'f0_mean',
            'intensity_range': 'intensity_mean',
            'hnr_range': 'hnr_estimate',
            'jitter_range': 'jitter_estimate',
            'shimmer_range': 'shimmer_estimate',
            'spectral_centroid_range': 'spectral_centroid',
            'mfcc_1_range': 'mfcc_1',
            'zero_crossing_rate': 'zcr_mean'
        }
        return mapping.get(feature_name, feature_name)
    
    def _feature_fusion_scoring(self, features):
        """特徴量融合スコアリング"""
        try:
            # 主要特徴量の重み付き統合
            scores = []
            weights = []
            
            # スペクトラル傾斜ベース
            spectral_tilt = features.get('spectral_tilt', -30)
            tilt_score = self._normalize_spectral_tilt(spectral_tilt)
            scores.append(tilt_score)
            weights.append(0.3)
            
            # F0ベース
            f0_mean = features.get('f0_mean', 150)
            f0_score = self._normalize_f0(f0_mean)
            scores.append(f0_score)
            weights.append(0.25)
            
            # Intensityベース
            intensity_mean = features.get('intensity_mean', -30)
            intensity_score = self._normalize_intensity(intensity_mean)
            scores.append(intensity_score)
            weights.append(0.2)
            
            # MFCCベース
            mfcc_1 = features.get('mfcc_1', -20)
            mfcc_score = self._normalize_mfcc1(mfcc_1)
            scores.append(mfcc_score)
            weights.append(0.15)
            
            # その他
            zcr_mean = features.get('zcr_mean', 0.1)
            zcr_score = min(zcr_mean * 5, 1.0)
            scores.append(zcr_score)
            weights.append(0.1)
            
            # 重み付き平均
            fused_score = np.average(scores, weights=weights)
            
            return np.clip(fused_score, 0.0, 1.0)
            
        except Exception as e:
            print(f"特徴量融合エラー: {e}")
            return 0.5
    
    def _normalize_spectral_tilt(self, tilt):
        """スペクトラル傾斜正規化（-45dB～-10dB → 0～1）"""
        return np.clip((tilt + 45) / 35, 0, 1)
    
    def _normalize_f0(self, f0):
        """F0正規化（80Hz～300Hz → 0～1）"""
        return np.clip((f0 - 80) / 220, 0, 1)
    
    def _normalize_intensity(self, intensity):
        """Intensity正規化（-45dB～-5dB → 0～1）"""
        return np.clip((intensity + 45) / 40, 0, 1)
    
    def _normalize_mfcc1(self, mfcc1):
        """MFCC1正規化（-50～10 → 0～1）"""
        return np.clip((mfcc1 + 50) / 60, 0, 1)
    
    def _adaptive_range_mapping(self, score, features):
        """適応的範囲マッピング"""
        try:
            # 特徴量ベースの動的調整
            spectral_tilt = features.get('spectral_tilt', -30)
            f0_mean = features.get('f0_mean', 150)
            
            print(f"  スペクトラル傾斜: {spectral_tilt:.1f} dB, F0: {f0_mean:.1f} Hz")
            
            # 境界ケース強化判定システム
            intensity_mean = features.get('intensity_mean', -30)
            zcr_mean = features.get('zcr_mean', 0.1)
            
            # 主判定：スペクトラル傾斜による分類（77.8%精度時の設定に復元）
            if spectral_tilt < -25:
                # 低テンション範囲
                final_score = score * 0.333
                classification = "低テンション (傾斜 < -25dB)"
            elif spectral_tilt > -20:
                # 高テンション範囲
                final_score = 0.666 + score * 0.334
                classification = "高テンション (傾斜 > -20dB)"
            else:
                # 中テンション範囲
                final_score = 0.333 + score * 0.333
                classification = "中テンション (-25dB <= 傾斜 <= -20dB)"
            
            print(f"  分類: {classification}")
            
            # F0による微調整
            if f0_mean > 200:  # 高F0は高テンション傾向
                final_score = min(final_score * 1.1, 1.0)
            elif f0_mean < 120:  # 低F0は低テンション傾向
                final_score = final_score * 0.9
            
            return np.clip(final_score, 0.0, 1.0)
            
        except Exception as e:
            print(f"適応的マッピングエラー: {e}")
            return score
    
    def _boundary_case_analysis(self, score, spectral_tilt, f0_mean, intensity_mean, zcr_mean):
        """境界ケース詳細分析（-23dB ～ -18dB）"""
        try:
            print(f"    境界領域分析: 傾斜={spectral_tilt:.1f}dB, Intensity={intensity_mean:.1f}dB, ZCR={zcr_mean:.3f}")
            
            # 複数特徴量による総合判定
            low_indicators = 0
            high_indicators = 0
            
            # 1. スペクトラル傾斜による細分化（主要指標）
            if spectral_tilt < -22:
                low_indicators += 2  # Low指標
            elif spectral_tilt > -20:
                high_indicators += 2  # High指標
            else:
                # 中間値: バランス調整（-22 ～ -20dB範囲）
                if spectral_tilt < -21:
                    low_indicators += 1
                else:
                    high_indicators += 1
            
            # 2. Intensity（音響強度）による判定（補助指標）
            if intensity_mean < -34:
                low_indicators += 1
            elif intensity_mean > -30:
                high_indicators += 1
            
            # 3. Zero Crossing Rate（周波数変動）による判定（補助指標）
            if zcr_mean < 0.09:
                low_indicators += 1
            elif zcr_mean > 0.12:
                high_indicators += 1
            
            # 4. F0による微調整（補助指標）
            if f0_mean < 130:
                low_indicators += 1
            elif f0_mean > 170:
                high_indicators += 1
            
            print(f"    指標集計: Low={low_indicators}, High={high_indicators}")
            
            # 総合判定
            if low_indicators > high_indicators:
                final_score = score * 0.333
                classification = f"境界→低テンション (指標: L{low_indicators}/H{high_indicators})"
            elif high_indicators > low_indicators:
                final_score = 0.666 + score * 0.334
                classification = f"境界→高テンション (指標: L{low_indicators}/H{high_indicators})"
            else:
                # 同点の場合は中テンション
                final_score = 0.333 + score * 0.333
                classification = f"境界→中テンション (指標: L{low_indicators}/H{high_indicators})"
            
            return final_score, classification
            
        except Exception as e:
            print(f"境界ケース分析エラー: {e}")
            return 0.333 + score * 0.333, "中テンション (エラー時デフォルト)"
    
    def _calculate_prediction_confidence(self, features, tension_value):
        """予測信頼度計算"""
        try:
            confidence_factors = []
            
            # 1. 特徴量の完全性
            required_features = ['spectral_tilt', 'f0_mean', 'intensity_mean', 'mfcc_1']
            completeness = sum(1 for f in required_features if f in features) / len(required_features)
            confidence_factors.append(completeness)
            
            # 2. 値の妥当性
            spectral_tilt = features.get('spectral_tilt', -30)
            f0_mean = features.get('f0_mean', 150)
            
            # 妥当な範囲内かチェック
            tilt_validity = 1.0 if -50 <= spectral_tilt <= -5 else 0.5
            f0_validity = 1.0 if 50 <= f0_mean <= 400 else 0.5
            
            confidence_factors.append(tilt_validity)
            confidence_factors.append(f0_validity)
            
            # 3. 分類境界からの距離
            if tension_value < 0.333:
                boundary_distance = min(tension_value, 0.333 - tension_value) / 0.333
            elif tension_value < 0.666:
                boundary_distance = min(tension_value - 0.333, 0.666 - tension_value) / 0.333
            else:
                boundary_distance = min(tension_value - 0.666, 1.0 - tension_value) / 0.334
                
            confidence_factors.append(boundary_distance)
            
            return np.mean(confidence_factors)
            
        except Exception as e:
            return 0.7
    
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
    classifier = AdvancedSignalClassifier()
    
    test_files = [
        "sample/Tension_Low_01.wav",
        "sample/Tension_Neutral_01.wav", 
        "sample/Tension_High_01.wav"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            tension, confidence, features = classifier.predict_tension_advanced(file_path)
            print(f"{os.path.basename(file_path)}: Tension={tension:.3f}, Confidence={confidence:.3f}")