# -*- coding: utf-8 -*-
"""
Prosodic Features Extractor using Parselmouth
Parselmouthを使用した韻律特徴量抽出モジュール

声門努力検出に重要な韻律特徴量を精密に抽出:
- F0 (基本周波数)
- Intensity (音声強度)
- HNR (Harmonics-to-Noise Ratio)
- Jitter (基本周波数摂動)
- Shimmer (振幅摂動)
- フォルマント周波数 (F1, F2, F3)
"""

import numpy as np
import parselmouth
from parselmouth.praat import call
import warnings

warnings.filterwarnings('ignore')

class ProsodicFeatureExtractor:
    """Parselmouthを使用した韻律特徴量抽出クラス"""
    
    def __init__(self):
        """初期化"""
        # 基本パラメータ
        self.f0_min = 75.0      # 最小F0 (男性の低い声)
        self.f0_max = 500.0     # 最大F0 (女性の高い声)
        self.time_step = 0.01   # 時間ステップ（10ms）
        
        # 音声品質分析パラメータ
        self.silence_threshold = 0.03
        self.voicing_threshold = 0.45
    
    def extract_all_features(self, audio_path):
        """
        全ての韻律特徴量を抽出
        
        Args:
            audio_path (str): 音声ファイルパス
            
        Returns:
            dict: 韻律特徴量辞書
        """
        try:
            # Parselmouthで音声読み込み
            sound = parselmouth.Sound(audio_path)
            
            features = {}
            
            # 1. F0 (基本周波数) 解析
            f0_features = self._extract_f0_features(sound)
            features.update(f0_features)
            
            # 2. Intensity (音声強度) 解析
            intensity_features = self._extract_intensity_features(sound)
            features.update(intensity_features)
            
            # 3. HNR (Harmonics-to-Noise Ratio) 解析
            hnr_features = self._extract_hnr_features(sound)
            features.update(hnr_features)
            
            # 4. Jitter & Shimmer (音声品質) 解析
            quality_features = self._extract_voice_quality_features(sound)
            features.update(quality_features)
            
            # 5. フォルマント解析
            formant_features = self._extract_formant_features(sound)
            features.update(formant_features)
            
            # 6. 音声のメタ情報
            meta_features = self._extract_meta_features(sound)
            features.update(meta_features)
            
            # 7. 声門努力スコア計算
            features['vocal_effort_score'] = self.calculate_vocal_effort_score(features)
            
            print(f"Parselmouth特徴量抽出完了: {len(features)}種類")
            return features
            
        except Exception as e:
            print(f"Parselmouth特徴量抽出エラー: {e}")
            return {}
    
    def _extract_f0_features(self, sound):
        """F0関連特徴量を抽出"""
        features = {}
        
        try:
            # F0軌跡を抽出
            pitch = sound.to_pitch(time_step=self.time_step, 
                                 pitch_floor=self.f0_min, 
                                 pitch_ceiling=self.f0_max)
            
            # F0値を取得（0はunvoiced）
            f0_values = pitch.selected_array['frequency']
            voiced_f0 = f0_values[f0_values > 0]  # 有声部分のみ
            
            if len(voiced_f0) > 0:
                features['f0_mean'] = np.mean(voiced_f0)
                features['f0_median'] = np.median(voiced_f0)
                features['f0_std'] = np.std(voiced_f0)
                features['f0_min'] = np.min(voiced_f0)
                features['f0_max'] = np.max(voiced_f0)
                features['f0_range'] = features['f0_max'] - features['f0_min']
                
                # F0変動率（声門努力の指標）
                if len(voiced_f0) > 1:
                    f0_diff = np.diff(voiced_f0)
                    features['f0_variation'] = np.std(f0_diff)
                    features['f0_slope'] = np.mean(f0_diff)
                else:
                    features['f0_variation'] = 0.0
                    features['f0_slope'] = 0.0
                
                # 有声化率（発話の特徴）
                features['voicing_fraction'] = len(voiced_f0) / len(f0_values)
            else:
                # F0が検出されない場合のデフォルト値
                for key in ['f0_mean', 'f0_median', 'f0_std', 'f0_min', 'f0_max', 
                           'f0_range', 'f0_variation', 'f0_slope']:
                    features[key] = 0.0
                features['voicing_fraction'] = 0.0
            
        except Exception as e:
            print(f"F0抽出エラー: {e}")
            # エラー時のデフォルト値
            for key in ['f0_mean', 'f0_median', 'f0_std', 'f0_min', 'f0_max', 
                       'f0_range', 'f0_variation', 'f0_slope', 'voicing_fraction']:
                features[key] = 0.0
        
        return features
    
    def _extract_intensity_features(self, sound):
        """音声強度関連特徴量を抽出"""
        features = {}
        
        try:
            # 音声強度を抽出
            intensity = sound.to_intensity(time_step=self.time_step)
            intensity_values = intensity.values[0]  # dB値
            
            # 無音部分を除外
            audible_intensity = intensity_values[intensity_values > -np.inf]
            
            if len(audible_intensity) > 0:
                features['intensity_mean'] = np.mean(audible_intensity)
                features['intensity_median'] = np.median(audible_intensity)
                features['intensity_std'] = np.std(audible_intensity)
                features['intensity_min'] = np.min(audible_intensity)
                features['intensity_max'] = np.max(audible_intensity)
                features['intensity_range'] = features['intensity_max'] - features['intensity_min']
                
                # 強度変動（声門努力の重要指標）
                if len(audible_intensity) > 1:
                    intensity_diff = np.diff(audible_intensity)
                    features['intensity_variation'] = np.std(intensity_diff)
                else:
                    features['intensity_variation'] = 0.0
            else:
                for key in ['intensity_mean', 'intensity_median', 'intensity_std', 
                           'intensity_min', 'intensity_max', 'intensity_range', 
                           'intensity_variation']:
                    features[key] = 0.0
                    
        except Exception as e:
            print(f"Intensity抽出エラー: {e}")
            for key in ['intensity_mean', 'intensity_median', 'intensity_std', 
                       'intensity_min', 'intensity_max', 'intensity_range', 
                       'intensity_variation']:
                features[key] = 0.0
        
        return features
    
    def _extract_hnr_features(self, sound):
        """HNR (Harmonics-to-Noise Ratio) 特徴量を抽出"""
        features = {}
        
        try:
            # HNRを計算
            harmonicity = sound.to_harmonicity(time_step=self.time_step)
            hnr_values = harmonicity.values[0]
            
            # 有効なHNR値のみ抽出
            valid_hnr = hnr_values[~np.isinf(hnr_values)]
            
            if len(valid_hnr) > 0:
                features['hnr_mean'] = np.mean(valid_hnr)
                features['hnr_median'] = np.median(valid_hnr)
                features['hnr_std'] = np.std(valid_hnr)
                features['hnr_min'] = np.min(valid_hnr)
                features['hnr_max'] = np.max(valid_hnr)
            else:
                for key in ['hnr_mean', 'hnr_median', 'hnr_std', 'hnr_min', 'hnr_max']:
                    features[key] = 0.0
                    
        except Exception as e:
            print(f"HNR抽出エラー: {e}")
            for key in ['hnr_mean', 'hnr_median', 'hnr_std', 'hnr_min', 'hnr_max']:
                features[key] = 0.0
        
        return features
    
    def _extract_voice_quality_features(self, sound):
        """音声品質特徴量（Jitter, Shimmer）を抽出"""
        features = {}
        
        try:
            # PointProcessを作成（F0から）
            pitch = sound.to_pitch(time_step=self.time_step, 
                                 pitch_floor=self.f0_min, 
                                 pitch_ceiling=self.f0_max)
            point_process = call(pitch, "To PointProcess")
            
            # Jitter計算（基本周波数の摂動）
            try:
                jitter_local = call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
                features['jitter_local'] = jitter_local if not np.isnan(jitter_local) else 0.0
                
                jitter_rap = call(point_process, "Get jitter (rap)", 0, 0, 0.0001, 0.02, 1.3)
                features['jitter_rap'] = jitter_rap if not np.isnan(jitter_rap) else 0.0
                
                jitter_ppq5 = call(point_process, "Get jitter (ppq5)", 0, 0, 0.0001, 0.02, 1.3)
                features['jitter_ppq5'] = jitter_ppq5 if not np.isnan(jitter_ppq5) else 0.0
            except:
                features['jitter_local'] = 0.0
                features['jitter_rap'] = 0.0
                features['jitter_ppq5'] = 0.0
            
            # Shimmer計算（振幅の摂動）
            try:
                shimmer_local = call([sound, point_process], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
                features['shimmer_local'] = shimmer_local if not np.isnan(shimmer_local) else 0.0
                
                shimmer_apq3 = call([sound, point_process], "Get shimmer (apq3)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
                features['shimmer_apq3'] = shimmer_apq3 if not np.isnan(shimmer_apq3) else 0.0
                
                shimmer_apq5 = call([sound, point_process], "Get shimmer (apq5)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
                features['shimmer_apq5'] = shimmer_apq5 if not np.isnan(shimmer_apq5) else 0.0
            except:
                features['shimmer_local'] = 0.0
                features['shimmer_apq3'] = 0.0
                features['shimmer_apq5'] = 0.0
                
        except Exception as e:
            print(f"音声品質抽出エラー: {e}")
            for key in ['jitter_local', 'jitter_rap', 'jitter_ppq5', 
                       'shimmer_local', 'shimmer_apq3', 'shimmer_apq5']:
                features[key] = 0.0
        
        return features
    
    def _extract_formant_features(self, sound):
        """フォルマント特徴量を抽出"""
        features = {}
        
        try:
            # フォルマント解析
            formants = sound.to_formant_burg(time_step=self.time_step, 
                                           max_number_of_formants=5, 
                                           maximum_formant=5500, 
                                           window_length=0.025)
            
            # F1, F2, F3を抽出
            for formant_num in range(1, 4):  # F1, F2, F3
                try:
                    formant_values = []
                    duration = sound.get_total_duration()
                    
                    # 時間軸に沿ってフォルマント値を取得
                    for t in np.arange(0, duration, self.time_step):
                        try:
                            f_val = call(formants, "Get value at time", formant_num, t, "Hertz", "Linear")
                            if not np.isnan(f_val) and f_val > 0:
                                formant_values.append(f_val)
                        except:
                            continue
                    
                    if formant_values:
                        formant_array = np.array(formant_values)
                        features[f'f{formant_num}_mean'] = np.mean(formant_array)
                        features[f'f{formant_num}_std'] = np.std(formant_array)
                        features[f'f{formant_num}_median'] = np.median(formant_array)
                    else:
                        features[f'f{formant_num}_mean'] = 0.0
                        features[f'f{formant_num}_std'] = 0.0
                        features[f'f{formant_num}_median'] = 0.0
                        
                except Exception as e:
                    features[f'f{formant_num}_mean'] = 0.0
                    features[f'f{formant_num}_std'] = 0.0
                    features[f'f{formant_num}_median'] = 0.0
            
            # フォルマント関連の声門努力指標（バグ修正）
            f1_mean = features.get('f1_mean', 0)
            f0_mean = features.get('f0_mean', 0)
            
            if f1_mean > 0 and f0_mean > 0:
                # F1/F0比（声道の共鳴特性）
                features['f1_f0_ratio'] = f1_mean / f0_mean
            else:
                features['f1_f0_ratio'] = 0.0
                
        except Exception as e:
            print(f"フォルマント抽出エラー: {e}")
            for formant_num in range(1, 4):
                features[f'f{formant_num}_mean'] = 0.0
                features[f'f{formant_num}_std'] = 0.0
                features[f'f{formant_num}_median'] = 0.0
            features['f1_f0_ratio'] = 0.0
        
        return features
    
    def _extract_meta_features(self, sound):
        """音声のメタ情報を抽出"""
        features = {}
        
        try:
            features['duration'] = sound.get_total_duration()
            features['sampling_frequency'] = sound.get_sampling_frequency()
            
            # 音声の動的範囲
            values = sound.values[0]
            features['amplitude_range'] = np.max(values) - np.min(values)
            features['rms_amplitude'] = np.sqrt(np.mean(values**2))
            
        except Exception as e:
            print(f"メタ情報抽出エラー: {e}")
            features['duration'] = 0.0
            features['sampling_frequency'] = 22050.0
            features['amplitude_range'] = 0.0
            features['rms_amplitude'] = 0.0
        
        return features
    
    def calculate_vocal_effort_score(self, features):
        """
        韻律特徴量から声門努力スコアを計算
        
        Args:
            features (dict): 韻律特徴量
            
        Returns:
            float: 声門努力スコア (0.0-1.0)
        """
        try:
            # 各指標の重み
            weights = {
                'f0': 0.25,      # 基本周波数関連
                'intensity': 0.30,  # 音声強度関連
                'hnr': 0.15,     # 調波雑音比
                'quality': 0.20,  # 音声品質（jitter/shimmer）
                'formant': 0.10   # フォルマント関連
            }
            
            effort_score = 0.0
            
            # F0関連スコア
            f0_mean = features.get('f0_mean', 0)
            f0_variation = features.get('f0_variation', 0)
            if f0_mean > 0:
                # 高いF0と大きな変動は高努力を示す
                f0_score = min((f0_mean - 100) / 300, 1.0)  # 100-400Hzを0-1に正規化
                f0_var_score = min(f0_variation / 50, 1.0)  # 変動も考慮
                f0_total = (f0_score + f0_var_score) / 2
            else:
                f0_total = 0.0
            
            # Intensity関連スコア
            intensity_mean = features.get('intensity_mean', 0)
            intensity_variation = features.get('intensity_variation', 0)
            if intensity_mean > -np.inf:
                # 高い強度と大きな変動は高努力を示す
                intensity_score = min((intensity_mean + 20) / 40, 1.0)  # -20~20dBを0-1に正規化
                intensity_var_score = min(intensity_variation / 10, 1.0)
                intensity_total = (intensity_score + intensity_var_score) / 2
            else:
                intensity_total = 0.0
            
            # HNR関連スコア（低いHNRは高努力を示す場合がある）
            hnr_mean = features.get('hnr_mean', 0)
            if hnr_mean > 0:
                # HNRが非常に高い or 低い場合は努力的
                hnr_score = 1.0 - min(abs(hnr_mean - 10) / 10, 1.0)
            else:
                hnr_score = 0.0
            
            # 音声品質スコア（高いjitter/shimmerは高努力）
            jitter = features.get('jitter_local', 0)
            shimmer = features.get('shimmer_local', 0)
            quality_score = min((jitter * 1000 + shimmer * 100) / 2, 1.0)
            
            # フォルマントスコア
            f1_mean = features.get('f1_mean', 0)
            f1_f0_ratio = features.get('f1_f0_ratio', 0)
            if f1_mean > 0:
                formant_score = min(f1_f0_ratio / 10, 1.0)  # F1/F0比を考慮
            else:
                formant_score = 0.0
            
            # 重み付き合計
            effort_score = (
                f0_total * weights['f0'] +
                intensity_total * weights['intensity'] +
                hnr_score * weights['hnr'] +
                quality_score * weights['quality'] +
                formant_score * weights['formant']
            )
            
            return np.clip(effort_score, 0.0, 1.0)
            
        except Exception as e:
            print(f"声門努力スコア計算エラー: {e}")
            return 0.5  # デフォルト値