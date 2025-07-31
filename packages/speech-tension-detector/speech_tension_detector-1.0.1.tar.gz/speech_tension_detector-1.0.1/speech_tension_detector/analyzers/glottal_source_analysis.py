# -*- coding: utf-8 -*-
"""
Glottal Source Analysis
声門源解析システム

Source-Filter理論に基づく声門気流の直接解析:
- 声道フィルタ除去
- 声門波形再構成
- 声門努力直接測定
- Opening/Closing位相解析
"""

import numpy as np
import librosa
from scipy import signal
from scipy.optimize import minimize_scalar
import warnings

warnings.filterwarnings('ignore')

class GlottalSourceAnalyzer:
    """声門源解析器"""
    
    def __init__(self, sample_rate=22050):
        """初期化"""
        self.sample_rate = sample_rate
        self.frame_length = 0.025  # 25ms
        self.hop_length = 0.010   # 10ms
        self.pre_emphasis_coeff = 0.97
        
        # 声門パルス検出パラメータ
        self.min_f0 = 50
        self.max_f0 = 500
        
    def analyze_glottal_source(self, audio, f0_contour=None, formant_frequencies=None):
        """
        声門源解析メイン処理
        
        Args:
            audio (np.ndarray): 音声信号
            f0_contour (np.ndarray): F0軌跡（オプション）
            formant_frequencies (dict): フォルマント周波数（オプション）
            
        Returns:
            dict: 声門源解析結果
        """
        try:
            results = {}
            
            # 1. 前処理
            processed_audio = self._preprocess_audio(audio)
            
            # 2. F0推定（提供されない場合）
            if f0_contour is None:
                f0_contour = self._estimate_f0_precise(processed_audio)
            results['f0_contour'] = f0_contour
            
            # 3. 声門閉鎖瞬間検出 (GCI: Glottal Closure Instants)
            gci_locations = self._detect_glottal_closure_instants(processed_audio, f0_contour)
            results['gci_locations'] = gci_locations
            
            # 4. 声門源信号推定
            glottal_source = self._estimate_glottal_source(processed_audio, gci_locations, f0_contour)
            results['glottal_source'] = glottal_source
            
            # 5. 声門パルス解析
            pulse_analysis = self._analyze_glottal_pulses(glottal_source, gci_locations, f0_contour)
            results.update(pulse_analysis)
            
            # 6. 声門努力度計算
            effort_metrics = self._calculate_glottal_effort_metrics(results)
            results.update(effort_metrics)
            
            return results
            
        except Exception as e:
            print(f"声門源解析エラー: {e}")
            return {}
    
    def _preprocess_audio(self, audio):
        """音声前処理"""
        # Pre-emphasis filtering
        processed = signal.lfilter([1, -self.pre_emphasis_coeff], [1], audio)
        
        # DC removal
        processed = processed - np.mean(processed)
        
        # Normalization
        processed = processed / (np.max(np.abs(processed)) + 1e-8)
        
        return processed
    
    def _estimate_f0_precise(self, audio):
        """高精度F0推定"""
        try:
            # YIN algorithm for precise F0 estimation
            f0 = librosa.yin(audio, fmin=self.min_f0, fmax=self.max_f0, sr=self.sample_rate)
            
            # Median filtering for smoothing
            f0_smooth = signal.medfilt(f0, kernel_size=5)
            
            # Interpolate unvoiced regions
            voiced_indices = f0_smooth > 0
            if np.any(voiced_indices):
                f0_interp = np.copy(f0_smooth)
                unvoiced_indices = f0_smooth == 0
                if np.any(unvoiced_indices):
                    f0_interp[unvoiced_indices] = np.interp(
                        np.where(unvoiced_indices)[0],
                        np.where(voiced_indices)[0],
                        f0_smooth[voiced_indices]
                    )
                return f0_interp
            else:
                return f0_smooth
                
        except Exception as e:
            print(f"F0推定エラー: {e}")
            return np.zeros(len(audio) // self.sample_rate * 100)  # Dummy F0
    
    def _detect_glottal_closure_instants(self, audio, f0_contour):
        """声門閉鎖瞬間検出"""
        try:
            # DYPSA-like GCI detection
            # 1. Differentiate and find negative peaks
            diff_signal = np.diff(audio)
            
            # 2. Find potential GCI candidates
            gci_candidates = []
            
            # Use F0 information to guide search
            hop_samples = int(self.sample_rate * self.hop_length)
            
            for i, f0_val in enumerate(f0_contour):
                if f0_val > 0:
                    # Expected period in samples
                    period_samples = int(self.sample_rate / f0_val)
                    center_sample = i * hop_samples
                    
                    # Search in a window around expected location
                    search_start = max(0, center_sample - period_samples // 4)
                    search_end = min(len(diff_signal), center_sample + period_samples // 4)
                    
                    if search_end > search_start:
                        search_window = diff_signal[search_start:search_end]
                        
                        # Find negative peak (closure)
                        if len(search_window) > 0:
                            min_idx = np.argmin(search_window)
                            gci_location = search_start + min_idx
                            
                            # Validate GCI
                            if abs(diff_signal[gci_location]) > 0.01:  # Threshold
                                gci_candidates.append(gci_location)
            
            return np.array(gci_candidates)
            
        except Exception as e:
            print(f"GCI検出エラー: {e}")
            return np.array([])
    
    def _estimate_glottal_source(self, audio, gci_locations, f0_contour):
        """声門源信号推定"""
        try:
            if len(gci_locations) < 2:
                return np.zeros_like(audio)
            
            # Simple inverse filtering approach
            # 1. Estimate vocal tract transfer function
            
            # Use linear prediction to model vocal tract
            lpc_order = int(self.sample_rate / 1000) + 2  # Typical: 12-16 for 16kHz
            
            # Apply LPC analysis in frames
            frame_samples = int(self.frame_length * self.sample_rate)
            hop_samples = int(self.hop_length * self.sample_rate)
            
            glottal_source = np.zeros_like(audio)
            
            for i in range(0, len(audio) - frame_samples, hop_samples):
                frame = audio[i:i + frame_samples]
                
                if len(frame) == frame_samples:
                    # LPC analysis
                    try:
                        # Calculate autocorrelation
                        autocorr = np.correlate(frame, frame, mode='full')
                        autocorr = autocorr[len(autocorr)//2:]
                        
                        # Solve Yule-Walker equations
                        if len(autocorr) > lpc_order:
                            R = autocorr[:lpc_order+1]
                            if R[0] > 0:
                                # Levinson-Durbin algorithm
                                lpc_coeffs = self._levinson_durbin(R)
                                
                                # Apply inverse filter
                                if len(lpc_coeffs) > 0:
                                    # Create inverse filter
                                    inverse_filter = np.concatenate([[1], -lpc_coeffs[1:]])
                                    
                                    # Apply filtering
                                    filtered_frame = signal.lfilter(inverse_filter, [1], frame)
                                    glottal_source[i:i + frame_samples] = filtered_frame
                    except:
                        # If LPC fails, use original frame
                        glottal_source[i:i + frame_samples] = frame
            
            return glottal_source
            
        except Exception as e:
            print(f"声門源推定エラー: {e}")
            return np.zeros_like(audio)
    
    def _levinson_durbin(self, R):
        """Levinson-Durbin algorithm for LPC coefficients"""
        try:
            n = len(R) - 1
            if n <= 0 or R[0] == 0:
                return np.array([1.0])
            
            # Initialize
            a = np.zeros(n + 1)
            a[0] = 1.0
            E = R[0]
            
            for i in range(1, n + 1):
                # Reflection coefficient
                lambda_i = R[i]
                for j in range(1, i):
                    lambda_i -= a[j] * R[i - j]
                lambda_i /= E
                
                # Update coefficients
                a_new = np.zeros(n + 1)
                a_new[0] = 1.0
                a_new[i] = lambda_i
                
                for j in range(1, i):
                    a_new[j] = a[j] - lambda_i * a[i - j]
                
                a = a_new
                E *= (1 - lambda_i**2)
                
                if E <= 0:
                    break
            
            return a
            
        except Exception as e:
            print(f"Levinson-Durbin エラー: {e}")
            return np.array([1.0])
    
    def _analyze_glottal_pulses(self, glottal_source, gci_locations, f0_contour):
        """声門パルス解析"""
        try:
            analysis = {}
            
            if len(gci_locations) < 2:
                return {'glottal_pulse_count': 0}
            
            pulse_features = []
            
            # Analyze individual pulses
            for i in range(len(gci_locations) - 1):
                start_idx = gci_locations[i]
                end_idx = gci_locations[i + 1]
                
                if end_idx > start_idx and end_idx < len(glottal_source):
                    pulse = glottal_source[start_idx:end_idx]
                    
                    if len(pulse) > 10:  # Minimum pulse length
                        # Pulse features
                        pulse_energy = np.sum(pulse**2)
                        pulse_peak = np.max(np.abs(pulse))
                        pulse_duration = len(pulse) / self.sample_rate
                        
                        # Opening/Closing phase analysis
                        pulse_abs = np.abs(pulse)
                        peak_idx = np.argmax(pulse_abs)
                        
                        opening_phase = peak_idx / len(pulse)  # 0-1
                        closing_phase = (len(pulse) - peak_idx) / len(pulse)  # 0-1
                        
                        # Asymmetry ratio (important for vocal effort)
                        asymmetry_ratio = opening_phase / (closing_phase + 1e-8)
                        
                        pulse_features.append({
                            'energy': pulse_energy,
                            'peak': pulse_peak,
                            'duration': pulse_duration,
                            'opening_phase': opening_phase,
                            'closing_phase': closing_phase,
                            'asymmetry_ratio': asymmetry_ratio
                        })
            
            # Aggregate pulse statistics
            if pulse_features:
                analysis['glottal_pulse_count'] = len(pulse_features)
                analysis['avg_pulse_energy'] = np.mean([p['energy'] for p in pulse_features])
                analysis['std_pulse_energy'] = np.std([p['energy'] for p in pulse_features])
                analysis['avg_pulse_peak'] = np.mean([p['peak'] for p in pulse_features])
                analysis['avg_asymmetry_ratio'] = np.mean([p['asymmetry_ratio'] for p in pulse_features])
                analysis['std_asymmetry_ratio'] = np.std([p['asymmetry_ratio'] for p in pulse_features])
                
                # Opening quotient (important for effort)
                opening_quotients = [p['opening_phase'] for p in pulse_features]
                analysis['avg_opening_quotient'] = np.mean(opening_quotients)
                analysis['std_opening_quotient'] = np.std(opening_quotients)
                
            return analysis
            
        except Exception as e:
            print(f"声門パルス解析エラー: {e}")
            return {'glottal_pulse_count': 0}
    
    def _calculate_glottal_effort_metrics(self, glottal_analysis):
        """声門努力メトリクス計算"""
        try:
            effort_metrics = {}
            
            pulse_count = glottal_analysis.get('glottal_pulse_count', 0)
            
            if pulse_count == 0:
                effort_metrics['glottal_effort_score'] = 0.5
                effort_metrics['glottal_confidence'] = 0.1
                return effort_metrics
            
            # 1. Energy-based effort
            avg_energy = glottal_analysis.get('avg_pulse_energy', 0)
            energy_variation = glottal_analysis.get('std_pulse_energy', 0)
            
            # Normalize energy (higher energy = more effort)
            energy_effort = min(avg_energy * 1000, 1.0)
            
            # 2. Peak-based effort
            avg_peak = glottal_analysis.get('avg_pulse_peak', 0)
            peak_effort = min(avg_peak * 10, 1.0)
            
            # 3. Asymmetry-based effort (key indicator)
            avg_asymmetry = glottal_analysis.get('avg_asymmetry_ratio', 1.0)
            # Effort increases asymmetry (opening becomes shorter relative to closing)
            asymmetry_effort = min(abs(avg_asymmetry - 1.0) * 2, 1.0)
            
            # 4. Opening quotient effort
            avg_oq = glottal_analysis.get('avg_opening_quotient', 0.5)
            # Lower opening quotient often indicates more effort
            oq_effort = max(0, (0.6 - avg_oq) / 0.6) if avg_oq < 0.6 else 0
            
            # 5. Variability-based effort
            oq_std = glottal_analysis.get('std_opening_quotient', 0)
            variability_effort = min(oq_std * 5, 1.0)
            
            # Combine metrics
            glottal_effort = (
                energy_effort * 0.25 +
                peak_effort * 0.25 +
                asymmetry_effort * 0.25 +
                oq_effort * 0.15 +
                variability_effort * 0.10
            )
            
            # Apply non-linear transformation and range expansion
            glottal_effort = glottal_effort ** 0.7  # 軽い非線形変換
            
            # Range expansion for better distribution
            if glottal_effort < 0.25:
                glottal_effort = glottal_effort * 1.3  # 低値をブースト
            elif glottal_effort > 0.75:
                glottal_effort = 0.75 + (glottal_effort - 0.75) * 1.4  # 高値をさらにブースト
            
            # Confidence based on pulse count and regularity
            confidence = min(pulse_count / 20, 1.0) * 0.9
            
            effort_metrics['glottal_effort_score'] = np.clip(glottal_effort, 0.0, 1.0)
            effort_metrics['glottal_confidence'] = confidence
            
            # Additional detailed metrics
            effort_metrics['energy_component'] = energy_effort
            effort_metrics['peak_component'] = peak_effort
            effort_metrics['asymmetry_component'] = asymmetry_effort
            effort_metrics['opening_quotient_component'] = oq_effort
            effort_metrics['variability_component'] = variability_effort
            
            return effort_metrics
            
        except Exception as e:
            print(f"声門努力メトリクス計算エラー: {e}")
            return {'glottal_effort_score': 0.5, 'glottal_confidence': 0.1}