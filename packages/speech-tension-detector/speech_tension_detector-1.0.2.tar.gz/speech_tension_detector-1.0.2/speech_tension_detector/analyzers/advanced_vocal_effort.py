# -*- coding: utf-8 -*-
"""
Advanced Vocal Effort Detection
高度な声門努力検出モジュール

精度向上のための高度なアルゴリズム:
- アダプティブ閾値調整
- アンサンブル手法
- 個人差考慮モデル
- 動的特徴量重み付け
"""

import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import warnings

warnings.filterwarnings('ignore')

class AdvancedVocalEffortDetector:
    """高度な声門努力検出クラス"""
    
    def __init__(self):
        """初期化"""
        self.scaler = StandardScaler()
        self.ensemble_models = []
        
        # 閾値の動的調整パラメータ
        self.low_threshold = 0.4
        self.high_threshold = 0.6
        
        # 個人差考慮パラメータ
        self.speaker_adaptation_factor = 0.1
        
    def calculate_advanced_effort_score(self, all_features, prosodic_features, spectral_features):
        """
        高度な声門努力スコア計算
        
        Args:
            all_features (dict): 全特徴量
            prosodic_features (dict): 韻律特徴量
            spectral_features (dict): スペクトラル特徴量
            
        Returns:
            tuple: (advanced_score, confidence, diagnostics)
        """
        try:
            diagnostics = {}
            
            # 1. データ品質チェック
            quality_score = self._assess_data_quality(all_features, prosodic_features)
            diagnostics['data_quality'] = quality_score
            
            # 2. 複数アルゴリズムによる予測
            scores = {}
            
            # スペクトラル重点法
            scores['spectral_weighted'] = self._spectral_weighted_method(spectral_features)
            
            # 韻律統合法
            scores['prosodic_integrated'] = self._prosodic_integrated_method(prosodic_features)
            
            # ハーモニクス解析法
            scores['harmonic_analysis'] = self._harmonic_analysis_method(spectral_features, prosodic_features)
            
            # 時系列変動法
            scores['temporal_variation'] = self._temporal_variation_method(prosodic_features)
            
            # 3. 個人差適応
            speaker_profile = self._estimate_speaker_profile(prosodic_features)
            diagnostics['speaker_profile'] = speaker_profile
            
            # 4. アンサンブル統合
            ensemble_score, ensemble_confidence = self._ensemble_prediction(scores, quality_score, speaker_profile)
            
            # 5. 動的閾値調整
            adjusted_score = self._apply_adaptive_thresholds(ensemble_score, speaker_profile, quality_score)
            
            diagnostics['individual_scores'] = scores
            diagnostics['ensemble_score'] = ensemble_score
            diagnostics['adjusted_score'] = adjusted_score
            
            return adjusted_score, ensemble_confidence, diagnostics
            
        except Exception as e:
            print(f"高度声門努力計算エラー: {e}")
            return 0.5, 0.0, {}
    
    def _assess_data_quality(self, all_features, prosodic_features):
        """データ品質評価"""
        try:
            quality_factors = []
            
            # 音声長チェック
            duration = all_features.get('duration', 0)
            if duration > 0.5:
                length_quality = min(duration / 3.0, 1.0)
            else:
                length_quality = 0.2
            quality_factors.append(length_quality)
            
            # 有声化率チェック
            voicing_fraction = prosodic_features.get('voicing_fraction', 0)
            voicing_quality = min(voicing_fraction / 0.7, 1.0)
            quality_factors.append(voicing_quality)
            
            # HNR品質チェック
            hnr_mean = prosodic_features.get('hnr_mean', -200)
            if hnr_mean > -100:
                hnr_quality = min((hnr_mean + 100) / 120, 1.0)
            else:
                hnr_quality = 0.1
            quality_factors.append(hnr_quality)
            
            # F0安定性チェック
            f0_std = prosodic_features.get('f0_std', 0)
            f0_mean = prosodic_features.get('f0_mean', 0)
            if f0_mean > 0:
                f0_stability = 1.0 - min(f0_std / f0_mean, 1.0)
            else:
                f0_stability = 0.3
            quality_factors.append(f0_stability)
            
            return np.mean(quality_factors)
            
        except Exception as e:
            print(f"データ品質評価エラー: {e}")
            return 0.5
    
    def _spectral_weighted_method(self, spectral_features):
        """スペクトラル重点法"""
        try:
            # 複数のスペクトラル傾斜を高度に統合
            tilts = {
                'main': spectral_features.get('spectral_tilt', 0),
                'regression': spectral_features.get('spectral_tilt_regression', 0),
                'multiband': spectral_features.get('spectral_tilt_multiband', 0),
                'weighted': spectral_features.get('spectral_tilt_weighted', 0),
                'harmonic': spectral_features.get('harmonic_tilt', 0)
            }
            
            # 改良された正規化
            normalized_tilts = {}
            for key, tilt in tilts.items():
                # より適応的な正規化
                if key == 'harmonic':
                    normalized_tilts[key] = np.clip((tilt + 10) / 20, 0, 1)
                elif key == 'multiband':
                    normalized_tilts[key] = np.clip((tilt + 15) / 25, 0, 1)
                else:
                    normalized_tilts[key] = np.clip((tilt + 35) / 45, 0, 1)
            
            # 動的重み付け（データ品質に基づく）
            weights = {
                'main': 0.35,
                'regression': 0.25,
                'multiband': 0.2,
                'weighted': 0.15,
                'harmonic': 0.05
            }
            
            score = sum(normalized_tilts[key] * weights[key] for key in weights.keys())
            
            # その他のスペクトラル特徴で補正
            centroid = spectral_features.get('spectral_centroid_mean', 1000)
            rolloff = spectral_features.get('spectral_rolloff_mean', 3000)
            bandwidth = spectral_features.get('spectral_bandwidth_mean', 1500)
            
            # 非線形補正
            centroid_factor = (centroid / 2500) ** 0.7
            rolloff_factor = (rolloff / 7000) ** 0.6
            bandwidth_factor = (bandwidth / 3000) ** 0.8
            
            final_score = (score * 0.8 + 
                          min(centroid_factor, 1.0) * 0.1 + 
                          min(rolloff_factor, 1.0) * 0.06 +
                          min(bandwidth_factor, 1.0) * 0.04)
            
            return np.clip(final_score, 0.0, 1.0)
            
        except Exception as e:
            print(f"スペクトラル重点法エラー: {e}")
            return 0.5
    
    def _prosodic_integrated_method(self, prosodic_features):
        """韻律統合法（修正版）"""
        try:
            components = []
            
            # F0 analysis (改良版)
            f0_mean = prosodic_features.get('f0_mean', 0)
            f0_variation = prosodic_features.get('f0_variation', 0)
            if f0_mean > 0:
                # 性別を考慮したF0正規化
                if f0_mean < 165:  # 男性の可能性
                    f0_norm = (f0_mean - 80) / 120
                else:  # 女性の可能性
                    f0_norm = (f0_mean - 150) / 200
                
                f0_var_norm = min(f0_variation / 40, 1.0)
                f0_score = (max(0, f0_norm) ** 0.8 + f0_var_norm ** 0.6) / 2
                components.append(f0_score * 0.4)
            
            # Intensity analysis (改良版)
            intensity_mean = prosodic_features.get('intensity_mean', -30)
            intensity_var = prosodic_features.get('intensity_variation', 0)
            if intensity_mean > -100:
                intensity_norm = (intensity_mean + 20) / 60
                intensity_var_norm = min(intensity_var / 10, 1.0)
                intensity_score = (max(0, intensity_norm) ** 0.75 + intensity_var_norm ** 0.6) / 2
                components.append(intensity_score * 0.35)
            
            # Voice quality analysis (修正版)
            jitter = prosodic_features.get('jitter_local', 0)
            shimmer = prosodic_features.get('shimmer_local', 0)
            
            if jitter > 0 and shimmer > 0:
                # より敏感な検出
                jitter_score = min((jitter * 8000) ** 0.4, 1.0)
                shimmer_score = min((shimmer * 800) ** 0.4, 1.0)
                quality_score = (jitter_score + shimmer_score) / 2
                components.append(quality_score * 0.15)
            
            # Formant analysis (修正版)
            f1_mean = prosodic_features.get('f1_mean', 0)
            f0_mean_for_ratio = prosodic_features.get('f0_mean', 0)
            
            if f1_mean > 0 and f0_mean_for_ratio > 0:
                f1_f0_ratio = f1_mean / f0_mean_for_ratio
                # より適切な範囲での正規化
                if f1_f0_ratio > 0:
                    ratio_score = min((f1_f0_ratio - 2) / 8, 1.0)
                    ratio_score = max(0, ratio_score)
                    components.append(ratio_score * 0.1)
            
            # 統合
            if components:
                final_score = sum(components)
                # 非線形変換で差を強調
                final_score = final_score ** 0.9
            else:
                final_score = 0.4
                
            return np.clip(final_score, 0.0, 1.0)
            
        except Exception as e:
            print(f"韻律統合法エラー: {e}")
            return 0.4
    
    def _harmonic_analysis_method(self, spectral_features, prosodic_features):
        """ハーモニクス解析法"""
        try:
            # 調波成分の分析
            harmonic_tilt = spectral_features.get('harmonic_tilt', 0)
            spectral_contrast = spectral_features.get('spectral_contrast_mean', 0)
            hnr_mean = prosodic_features.get('hnr_mean', 0)
            
            # 調波傾斜スコア
            if harmonic_tilt != 0:
                harmonic_score = np.clip((harmonic_tilt + 8) / 16, 0, 1)
            else:
                harmonic_score = 0.5
            
            # スペクトラルコントラストスコア
            if spectral_contrast > 0:
                contrast_score = min(spectral_contrast / 30, 1.0)
            else:
                contrast_score = 0.5
            
            # HNRベースのハーモニクス品質
            if hnr_mean > -100:
                # HNRが適度に高い場合は調波成分が明確
                if 5 <= hnr_mean <= 20:
                    hnr_harmonic_score = 0.8
                elif hnr_mean < 5:
                    hnr_harmonic_score = 0.6  # 低いが努力的
                else:
                    hnr_harmonic_score = 0.4  # 高すぎて不自然
            else:
                hnr_harmonic_score = 0.3
            
            # 統合
            final_score = (harmonic_score * 0.5 + 
                          contrast_score * 0.3 + 
                          hnr_harmonic_score * 0.2)
            
            return np.clip(final_score, 0.0, 1.0)
            
        except Exception as e:
            print(f"ハーモニクス解析法エラー: {e}")
            return 0.5
    
    def _temporal_variation_method(self, prosodic_features):
        """時系列変動法"""
        try:
            # F0とIntensityの時間的変動パターンを分析
            f0_variation = prosodic_features.get('f0_variation', 0)
            intensity_variation = prosodic_features.get('intensity_variation', 0)
            f0_range = prosodic_features.get('f0_range', 0)
            intensity_range = prosodic_features.get('intensity_range', 0)
            
            # 変動スコア
            f0_var_score = min(f0_variation / 35, 1.0)
            intensity_var_score = min(intensity_variation / 8, 1.0)
            
            # レンジスコア
            f0_range_score = min(f0_range / 200, 1.0)
            intensity_range_score = min(intensity_range / 40, 1.0)
            
            # 時間的ダイナミクス
            temporal_score = (f0_var_score * 0.3 + 
                            intensity_var_score * 0.3 +
                            f0_range_score * 0.25 +
                            intensity_range_score * 0.15)
            
            return np.clip(temporal_score, 0.0, 1.0)
            
        except Exception as e:
            print(f"時系列変動法エラー: {e}")
            return 0.5
    
    def _estimate_speaker_profile(self, prosodic_features):
        """話者プロファイル推定"""
        try:
            profile = {}
            
            # 性別推定（F0ベース）
            f0_mean = prosodic_features.get('f0_mean', 0)
            if f0_mean > 0:
                if f0_mean < 165:
                    profile['gender'] = 'male'
                    profile['gender_confidence'] = min((165 - f0_mean) / 85, 1.0)
                else:
                    profile['gender'] = 'female'
                    profile['gender_confidence'] = min((f0_mean - 165) / 185, 1.0)
            else:
                profile['gender'] = 'unknown'
                profile['gender_confidence'] = 0.0
            
            # 話し方スタイル推定
            f0_variation = prosodic_features.get('f0_variation', 0)
            intensity_variation = prosodic_features.get('intensity_variation', 0)
            
            if f0_variation > 30 or intensity_variation > 8:
                profile['speaking_style'] = 'expressive'
            elif f0_variation < 15 and intensity_variation < 4:
                profile['speaking_style'] = 'monotone'
            else:
                profile['speaking_style'] = 'normal'
            
            # 音声品質レベル
            hnr_mean = prosodic_features.get('hnr_mean', -200)
            if hnr_mean > 10:
                profile['voice_quality'] = 'good'
            elif hnr_mean > 0:
                profile['voice_quality'] = 'fair'
            else:
                profile['voice_quality'] = 'poor'
            
            return profile
            
        except Exception as e:
            print(f"話者プロファイル推定エラー: {e}")
            return {'gender': 'unknown', 'speaking_style': 'normal', 'voice_quality': 'fair'}
    
    def _ensemble_prediction(self, scores, quality_score, speaker_profile):
        """アンサンブル予測"""
        try:
            # 品質に基づく重み調整
            quality_factor = max(0.5, quality_score)
            
            # 話者プロファイルに基づく重み調整
            if speaker_profile.get('voice_quality') == 'good':
                quality_boost = 1.2
            elif speaker_profile.get('voice_quality') == 'poor':
                quality_boost = 0.8
            else:
                quality_boost = 1.0
            
            # 性別による調整
            if speaker_profile.get('gender') == 'female':
                # 女性の場合、F0重点のスコアを重視
                weights = {
                    'spectral_weighted': 0.3,
                    'prosodic_integrated': 0.35,
                    'harmonic_analysis': 0.2,
                    'temporal_variation': 0.15
                }
            else:
                # 男性またはunknownの場合、スペクトラル重視
                weights = {
                    'spectral_weighted': 0.35,
                    'prosodic_integrated': 0.3,
                    'harmonic_analysis': 0.2,
                    'temporal_variation': 0.15
                }
            
            # 重み付き平均
            ensemble_score = sum(scores[key] * weights[key] for key in weights.keys())
            
            # 品質調整
            adjusted_score = ensemble_score * quality_factor * quality_boost
            
            # 信頼度計算
            score_variance = np.var(list(scores.values()))
            confidence = (1.0 - score_variance) * quality_score * 0.9
            
            return np.clip(adjusted_score, 0.0, 1.0), np.clip(confidence, 0.0, 1.0)
            
        except Exception as e:
            print(f"アンサンブル予測エラー: {e}")
            return 0.5, 0.5
    
    def _apply_adaptive_thresholds(self, score, speaker_profile, quality_score):
        """適応的閾値調整"""
        try:
            # 話者プロファイルに基づく閾値調整
            if speaker_profile.get('speaking_style') == 'expressive':
                # 表現豊かな話者は全体的にスコアが高くなる傾向
                adjusted_score = score * 0.95
            elif speaker_profile.get('speaking_style') == 'monotone':
                # 単調な話者はスコアが低くなる傾向
                adjusted_score = score * 1.05
            else:
                adjusted_score = score
            
            # 品質による調整
            if quality_score < 0.5:
                # 品質が低い場合は控えめに
                adjusted_score = adjusted_score * 0.9
            elif quality_score > 0.8:
                # 品質が高い場合は信頼度を上げる
                adjusted_score = adjusted_score * 1.05
            
            return np.clip(adjusted_score, 0.0, 1.0)
            
        except Exception as e:
            print(f"適応的閾値調整エラー: {e}")
            return score