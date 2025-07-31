# -*- coding: utf-8 -*-
"""
Quality Separation System
品質分離システム

音声品質とテンションを分離して真の声門努力を検出:
- 品質マスク生成
- 品質正規化処理  
- テンション純粋抽出
- 品質非依存評価
"""

import numpy as np
import librosa
from scipy import signal, stats
from scipy.ndimage import uniform_filter1d
import warnings

warnings.filterwarnings('ignore')

class QualitySeparationEngine:
    """品質分離エンジン"""
    
    def __init__(self, sample_rate=22050):
        """初期化"""
        self.sample_rate = sample_rate
        
        # 品質評価閾値
        self.hnr_good_threshold = 10.0
        self.hnr_poor_threshold = -10.0
        self.voicing_good_threshold = 0.6
        self.voicing_poor_threshold = 0.3
        
        # 品質補正パラメータ
        self.quality_boost_factors = {
            'excellent': 0.95,
            'good': 1.0,
            'fair': 1.1,
            'poor': 1.25,
            'very_poor': 1.4
        }
    
    def separate_quality_and_tension(self, all_features, prosodic_features, spectral_features):
        """
        品質とテンションを分離
        
        Args:
            all_features (dict): 全特徴量
            prosodic_features (dict): 韻律特徴量
            spectral_features (dict): スペクトラル特徴量
            
        Returns:
            tuple: (quality_independent_tension, quality_profile, diagnostics)
        """
        try:
            diagnostics = {}
            
            # 1. 品質プロファイル構築
            quality_profile = self._build_quality_profile(prosodic_features, spectral_features)
            diagnostics['quality_profile'] = quality_profile
            
            # 2. 品質マスク生成
            quality_masks = self._generate_quality_masks(prosodic_features, quality_profile)
            diagnostics['quality_masks'] = quality_masks
            
            # 3. 品質補正係数計算
            correction_factors = self._calculate_correction_factors(quality_profile, quality_masks)
            diagnostics['correction_factors'] = correction_factors
            
            # 4. テンション特徴量の品質補正
            corrected_features = self._apply_quality_correction(
                all_features, prosodic_features, spectral_features, correction_factors
            )
            diagnostics['corrected_features'] = corrected_features
            
            # 5. 品質非依存テンション計算
            quality_independent_tension = self._calculate_quality_independent_tension(
                corrected_features, quality_profile
            )
            
            return quality_independent_tension, quality_profile, diagnostics
            
        except Exception as e:
            print(f"品質分離エラー: {e}")
            return 0.5, {}, {}
    
    def _build_quality_profile(self, prosodic_features, spectral_features):
        """品質プロファイル構築"""
        try:
            profile = {}
            
            # HNR based quality assessment
            hnr_mean = prosodic_features.get('hnr_mean', -200)
            if hnr_mean > self.hnr_good_threshold:
                profile['hnr_quality'] = 'good'
                profile['hnr_score'] = min((hnr_mean - 10) / 15, 1.0)
            elif hnr_mean < self.hnr_poor_threshold:
                profile['hnr_quality'] = 'poor'
                profile['hnr_score'] = 0.1
            else:
                profile['hnr_quality'] = 'fair'
                profile['hnr_score'] = (hnr_mean + 10) / 20
            
            # Voicing quality assessment
            voicing_fraction = prosodic_features.get('voicing_fraction', 0)
            if voicing_fraction > self.voicing_good_threshold:
                profile['voicing_quality'] = 'good'
                profile['voicing_score'] = voicing_fraction
            elif voicing_fraction < self.voicing_poor_threshold:
                profile['voicing_quality'] = 'poor'
                profile['voicing_score'] = voicing_fraction
            else:
                profile['voicing_quality'] = 'fair'
                profile['voicing_score'] = voicing_fraction
            
            # Spectral quality assessment
            spectral_flatness = spectral_features.get('spectral_flatness_mean', 0)
            if spectral_flatness < 0.005:  # Low flatness = more harmonic
                profile['spectral_quality'] = 'good'
                profile['spectral_score'] = 1.0 - spectral_flatness * 100
            elif spectral_flatness > 0.02:  # High flatness = more noisy
                profile['spectral_quality'] = 'poor'
                profile['spectral_score'] = max(0.1, 1.0 - spectral_flatness * 25)
            else:
                profile['spectral_quality'] = 'fair'
                profile['spectral_score'] = 1.0 - spectral_flatness * 50
            
            # Jitter/Shimmer quality
            jitter = prosodic_features.get('jitter_local', 0)
            shimmer = prosodic_features.get('shimmer_local', 0)
            
            voice_stability = 1.0 - min((jitter * 1000 + shimmer * 100) / 2, 1.0)
            if voice_stability > 0.8:
                profile['stability_quality'] = 'good'
            elif voice_stability < 0.5:
                profile['stability_quality'] = 'poor'
            else:
                profile['stability_quality'] = 'fair'
            profile['stability_score'] = voice_stability
            
            # Overall quality rating
            overall_score = (
                profile['hnr_score'] * 0.3 +
                profile['voicing_score'] * 0.25 +
                profile['spectral_score'] * 0.25 +
                profile['stability_score'] * 0.2
            )
            
            if overall_score > 0.8:
                profile['overall_quality'] = 'excellent'
            elif overall_score > 0.6:
                profile['overall_quality'] = 'good'
            elif overall_score > 0.4:
                profile['overall_quality'] = 'fair'
            elif overall_score > 0.2:
                profile['overall_quality'] = 'poor'
            else:
                profile['overall_quality'] = 'very_poor'
            
            profile['overall_score'] = overall_score
            
            return profile
            
        except Exception as e:
            print(f"品質プロファイル構築エラー: {e}")
            return {'overall_quality': 'fair', 'overall_score': 0.5}
    
    def _generate_quality_masks(self, prosodic_features, quality_profile):
        """品質マスク生成"""
        try:
            masks = {}
            
            # HNR mask - 低品質部分を特定
            hnr_mean = prosodic_features.get('hnr_mean', -200)
            if hnr_mean < -50:
                masks['hnr_unreliable'] = True
                masks['hnr_confidence'] = 0.2
            elif hnr_mean < 0:
                masks['hnr_unreliable'] = False
                masks['hnr_confidence'] = 0.6
            else:
                masks['hnr_unreliable'] = False
                masks['hnr_confidence'] = 0.9
            
            # Voicing mask
            voicing_fraction = prosodic_features.get('voicing_fraction', 0)
            masks['voicing_reliable'] = voicing_fraction > 0.3
            masks['voicing_confidence'] = min(voicing_fraction / 0.7, 1.0)
            
            # F0 tracking quality
            f0_variation = prosodic_features.get('f0_variation', 0)
            f0_mean = prosodic_features.get('f0_mean', 0)
            if f0_mean > 0:
                f0_cv = f0_variation / f0_mean if f0_mean > 0 else 1.0
                masks['f0_stable'] = f0_cv < 0.3
                masks['f0_confidence'] = max(0.1, 1.0 - f0_cv)
            else:
                masks['f0_stable'] = False
                masks['f0_confidence'] = 0.1
            
            return masks
            
        except Exception as e:
            print(f"品質マスク生成エラー: {e}")
            return {'default_confidence': 0.5}
    
    def _calculate_correction_factors(self, quality_profile, quality_masks):
        """品質補正係数計算"""
        try:
            factors = {}
            
            # Overall quality based correction
            overall_quality = quality_profile.get('overall_quality', 'fair')
            base_factor = self.quality_boost_factors.get(overall_quality, 1.0)
            
            # HNR correction
            if quality_profile.get('hnr_quality') == 'poor':
                factors['hnr_correction'] = 1.3  # Boost poor HNR signals
            elif quality_profile.get('hnr_quality') == 'good':
                factors['hnr_correction'] = 0.95  # Slight reduction for excellent signals
            else:
                factors['hnr_correction'] = 1.0
            
            # Voicing correction
            voicing_score = quality_profile.get('voicing_score', 0.5)
            if voicing_score < 0.4:
                factors['voicing_correction'] = 1.2  # Boost low voicing
            else:
                factors['voicing_correction'] = 1.0
            
            # Spectral correction
            spectral_quality = quality_profile.get('spectral_quality', 'fair')
            if spectral_quality == 'poor':
                factors['spectral_correction'] = 1.15
            else:
                factors['spectral_correction'] = 1.0
            
            # Combined correction factor
            factors['combined_factor'] = (
                base_factor * 0.4 +
                factors['hnr_correction'] * 0.3 +
                factors['voicing_correction'] * 0.2 +
                factors['spectral_correction'] * 0.1
            )
            
            return factors
            
        except Exception as e:
            print(f"補正係数計算エラー: {e}")
            return {'combined_factor': 1.0}
    
    def _apply_quality_correction(self, all_features, prosodic_features, spectral_features, correction_factors):
        """品質補正適用"""
        try:
            corrected = {}
            
            combined_factor = correction_factors.get('combined_factor', 1.0)
            
            # Spectral features correction
            spectral_tilt = spectral_features.get('spectral_tilt', 0)
            # Poor quality often makes spectral tilt appear more negative
            if correction_factors.get('hnr_correction', 1.0) > 1.1:
                # Correct for poor quality bias
                corrected['spectral_tilt_corrected'] = spectral_tilt * 0.85  # Make less negative
            else:
                corrected['spectral_tilt_corrected'] = spectral_tilt
            
            # F0 features correction
            f0_mean = prosodic_features.get('f0_mean', 0)
            if f0_mean > 0 and correction_factors.get('voicing_correction', 1.0) > 1.1:
                # Poor voicing quality may affect F0 estimation
                corrected['f0_mean_corrected'] = f0_mean
                corrected['f0_reliability'] = 0.7  # Reduced reliability
            else:
                corrected['f0_mean_corrected'] = f0_mean
                corrected['f0_reliability'] = 1.0
            
            # Intensity correction
            intensity_mean = prosodic_features.get('intensity_mean', 0)
            intensity_variation = prosodic_features.get('intensity_variation', 0)
            
            # Poor quality may dampen intensity variations
            if correction_factors.get('combined_factor', 1.0) > 1.1:
                corrected['intensity_variation_corrected'] = intensity_variation * 1.2
            else:
                corrected['intensity_variation_corrected'] = intensity_variation
            
            corrected['intensity_mean_corrected'] = intensity_mean
            
            # Formant correction
            f1_mean = prosodic_features.get('f1_mean', 0)
            if f1_mean > 0:
                # Poor quality may affect formant estimation
                reliability_factor = 1.0 / max(1.0, correction_factors.get('combined_factor', 1.0))
                corrected['f1_mean_corrected'] = f1_mean
                corrected['formant_reliability'] = reliability_factor
            else:
                corrected['f1_mean_corrected'] = f1_mean
                corrected['formant_reliability'] = 0.5
            
            return corrected
            
        except Exception as e:
            print(f"品質補正適用エラー: {e}")
            return {}
    
    def _calculate_quality_independent_tension(self, corrected_features, quality_profile):
        """品質非依存テンション計算"""
        try:
            tension_components = []
            
            # 1. Corrected spectral tilt based tension (拡張レンジ版)
            spectral_tilt_corrected = corrected_features.get('spectral_tilt_corrected', 0)
            # Use adaptive normalization based on quality with expanded range
            if quality_profile.get('overall_quality') in ['poor', 'very_poor']:
                # More aggressive normalization for poor quality
                tilt_score = np.clip((spectral_tilt_corrected + 50) / 60, 0, 1) ** 0.5
            else:
                # Standard normalization for good quality  
                tilt_score = np.clip((spectral_tilt_corrected + 40) / 50, 0, 1) ** 0.6
            
            tension_components.append(tilt_score * 0.4)
            
            # 2. Quality-adjusted F0 tension
            f0_corrected = corrected_features.get('f0_mean_corrected', 0)
            f0_reliability = corrected_features.get('f0_reliability', 1.0)
            
            if f0_corrected > 0:
                # Gender-adaptive F0 scoring
                if f0_corrected < 165:  # Likely male
                    f0_tension = ((f0_corrected - 80) / 120) ** 0.8
                else:  # Likely female
                    f0_tension = ((f0_corrected - 150) / 200) ** 0.8
                
                f0_tension = max(0, min(f0_tension, 1.0)) * f0_reliability
                tension_components.append(f0_tension * 0.25)
            
            # 3. Quality-adjusted intensity variation
            intensity_var_corrected = corrected_features.get('intensity_variation_corrected', 0)
            intensity_tension = min(intensity_var_corrected / 12, 1.0) ** 0.6
            tension_components.append(intensity_tension * 0.2)
            
            # 4. Formant-based tension (quality adjusted)
            formant_reliability = corrected_features.get('formant_reliability', 0.5)
            f1_corrected = corrected_features.get('f1_mean_corrected', 0)
            
            if f1_corrected > 0 and f0_corrected > 0:
                f1_f0_ratio = f1_corrected / f0_corrected
                formant_tension = min((f1_f0_ratio - 2) / 8, 1.0)
                formant_tension = max(0, formant_tension) * formant_reliability
                tension_components.append(formant_tension * 0.15)
            
            # 5. Quality bonus/penalty
            quality_score = quality_profile.get('overall_score', 0.5)
            if quality_score < 0.3:
                # Very poor quality - apply correction boost
                quality_adjustment = 0.1
            elif quality_score > 0.7:
                # Good quality - slight reduction
                quality_adjustment = -0.05
            else:
                quality_adjustment = 0.0
            
            # Final calculation
            base_tension = sum(tension_components)
            final_tension = base_tension + quality_adjustment
            
            # Apply non-linear transformation to enhance differences and expand range
            final_tension = final_tension ** 0.75  # 軽い非線形変換で差を保持
            
            # Range expansion transformation for better distribution
            if final_tension < 0.3:
                final_tension = final_tension * 1.2  # 低値を少し増幅
            elif final_tension > 0.7:
                final_tension = 0.7 + (final_tension - 0.7) * 1.5  # 高値をより増幅
            
            return np.clip(final_tension, 0.0, 1.0)
            
        except Exception as e:
            print(f"品質非依存テンション計算エラー: {e}")
            return 0.5