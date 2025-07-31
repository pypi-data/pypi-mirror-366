# -*- coding: utf-8 -*-
"""
Wavelet-Fractal Analysis System
Wavelet-フラクタル統合解析システム

多重解像度解析とフラクタル理論による声門努力検出:
- Continuous Wavelet Transform (CWT)
- フラクタル次元計算
- マルチスケール・エントロピー
- 複雑度ベース・テンション
"""

import numpy as np
from scipy import signal
from scipy.stats import entropy
import warnings

warnings.filterwarnings('ignore')

class WaveletFractalAnalyzer:
    """Wavelet-Fractal解析器"""
    
    def __init__(self, sample_rate=22050):
        """初期化"""
        self.sample_rate = sample_rate
        
        # Wavelet analysis parameters (軽量化)
        self.wavelet_scales = np.arange(1, 32)  # Scale range reduced
        self.wavelet_name = 'morlet'  # Morlet wavelet for good time-frequency resolution
        
        # Fractal analysis parameters (軽量化)
        self.box_sizes = np.logspace(0.5, 2.5, 10)  # Reduced from 20 to 10
        self.embedding_dimensions = [2, 3]    # Reduced dimensions
        
        # Multiscale entropy parameters (軽量化)  
        self.scale_factors = range(1, 6)  # Reduced from 11 to 6
        self.pattern_length = 2
        self.tolerance_factor = 0.15
    
    def analyze_wavelet_fractal_features(self, audio, f0_contour=None):
        """
        Wavelet-Fractal特徴量解析
        
        Args:
            audio (np.ndarray): 音声信号
            f0_contour (np.ndarray): F0軌跡（オプション）
            
        Returns:
            dict: Wavelet-Fractal解析結果
        """
        try:
            results = {}
            
            # 1. Continuous Wavelet Transform
            cwt_results = self._continuous_wavelet_transform(audio)
            results.update(cwt_results)
            
            # 2. フラクタル次元解析
            fractal_results = self._fractal_dimension_analysis(audio)
            results.update(fractal_results)
            
            # 3. マルチスケール・エントロピー
            mse_results = self._multiscale_entropy_analysis(audio)
            results.update(mse_results)
            
            # 4. 時間-周波数複雑度
            tf_complexity = self._time_frequency_complexity(cwt_results.get('cwt_coeffs', np.array([])))
            results.update(tf_complexity)
            
            # 5. 統合複雑度スコア
            complexity_score = self._calculate_integrated_complexity_score(results)
            results['integrated_complexity_score'] = complexity_score
            
            # 6. Wavelet-Fractalテンション推定
            wavelet_fractal_tension = self._estimate_wavelet_fractal_tension(results)
            results['wavelet_fractal_tension'] = wavelet_fractal_tension
            
            return results
            
        except Exception as e:
            print(f"Wavelet-Fractal解析エラー: {e}")
            return {'wavelet_fractal_tension': 0.5}
    
    def _continuous_wavelet_transform(self, audio):
        """連続ウェーブレット変換"""
        try:
            # Morlet wavelet CWT
            cwt_coeffs = signal.cwt(audio, signal.morlet2, self.wavelet_scales)
            
            # Power spectral density
            cwt_power = np.abs(cwt_coeffs)**2
            
            # Time-averaged power for each scale
            scale_powers = np.mean(cwt_power, axis=1)
            
            # Frequency distribution analysis
            total_power = np.sum(scale_powers)
            if total_power > 0:
                power_distribution = scale_powers / total_power
                
                # Spectral centroid in wavelet domain
                wavelet_centroid = np.sum(self.wavelet_scales * power_distribution)
                
                # Spectral spread in wavelet domain
                wavelet_spread = np.sqrt(np.sum(((self.wavelet_scales - wavelet_centroid)**2) * power_distribution))
                
                # Spectral skewness (asymmetry)
                wavelet_skewness = np.sum(((self.wavelet_scales - wavelet_centroid)**3) * power_distribution) / (wavelet_spread**3 + 1e-8)
                
                # Spectral kurtosis (peakedness)
                wavelet_kurtosis = np.sum(((self.wavelet_scales - wavelet_centroid)**4) * power_distribution) / (wavelet_spread**4 + 1e-8)
            else:
                wavelet_centroid = wavelet_spread = wavelet_skewness = wavelet_kurtosis = 0
            
            # Wavelet entropy
            if total_power > 0:
                wavelet_entropy = entropy(power_distribution + 1e-8)
            else:
                wavelet_entropy = 0
            
            return {
                'cwt_coeffs': cwt_coeffs,
                'cwt_power': cwt_power,
                'scale_powers': scale_powers,
                'wavelet_centroid': wavelet_centroid,
                'wavelet_spread': wavelet_spread,
                'wavelet_skewness': wavelet_skewness,
                'wavelet_kurtosis': wavelet_kurtosis,
                'wavelet_entropy': wavelet_entropy,
                'total_wavelet_power': total_power
            }
            
        except Exception as e:
            print(f"CWT解析エラー: {e}")
            return {'wavelet_fractal_tension': 0.5}
    
    def _fractal_dimension_analysis(self, audio):
        """フラクタル次元解析"""
        try:
            results = {}
            
            # 1. Box-counting dimension
            box_dimension = self._box_counting_dimension(audio)
            results['box_counting_dimension'] = box_dimension
            
            # 2. Correlation dimension
            correlation_dimension = self._correlation_dimension(audio)
            results['correlation_dimension'] = correlation_dimension
            
            # 3. Higuchi fractal dimension
            higuchi_dimension = self._higuchi_fractal_dimension(audio)
            results['higuchi_dimension'] = higuchi_dimension
            
            # 4. Detrended Fluctuation Analysis (DFA)
            dfa_exponent = self._detrended_fluctuation_analysis(audio)
            results['dfa_exponent'] = dfa_exponent
            
            return results
            
        except Exception as e:
            print(f"フラクタル次元解析エラー: {e}")
            return {}
    
    def _box_counting_dimension(self, audio):
        """Box-counting次元計算"""
        try:
            # Convert to binary image approach
            audio_normalized = (audio - np.min(audio)) / (np.max(audio) - np.min(audio) + 1e-8)
            
            # Create 2D representation (time vs amplitude)
            time_points = len(audio_normalized)
            amplitude_levels = 32  # Reduced discretization levels for speed
            
            # Discretize amplitude
            audio_discrete = np.floor(audio_normalized * (amplitude_levels - 1)).astype(int)
            
            # Count boxes at different scales
            box_counts = []
            scales = []
            
            for box_size in range(2, min(32, time_points//4), 2):
                count = 0
                
                for t in range(0, time_points - box_size, box_size):
                    t_end = min(t + box_size, time_points)
                    segment = audio_discrete[t:t_end]
                    
                    if len(segment) > 0:
                        amp_range = np.max(segment) - np.min(segment)
                        if amp_range > 0:  # Non-empty box
                            count += 1
                
                if count > 0:
                    box_counts.append(count)
                    scales.append(1.0 / box_size)
            
            # Linear regression to find dimension
            if len(box_counts) > 2:
                log_scales = np.log(scales)
                log_counts = np.log(box_counts)
                
                # Least squares fit
                A = np.vstack([log_scales, np.ones(len(log_scales))]).T
                dimension, _ = np.linalg.lstsq(A, log_counts, rcond=None)[0]
                
                return abs(dimension)  # Take absolute value
            else:
                return 1.5  # Default fractal dimension
                
        except Exception as e:
            print(f"Box-counting次元エラー: {e}")
            return 1.5
    
    def _correlation_dimension(self, audio):
        """相関次元計算"""
        try:
            # Phase space reconstruction using delay embedding
            embedding_delay = 1
            embedding_dim = 3
            
            # Create embedded vectors
            N = len(audio)
            M = N - (embedding_dim - 1) * embedding_delay
            
            if M <= 0:
                return 2.0
            
            embedded = np.zeros((M, embedding_dim))
            for i in range(M):
                for j in range(embedding_dim):
                    embedded[i, j] = audio[i + j * embedding_delay]
            
            # Calculate correlation integral
            distances = []
            max_points = min(M, 200)  # Further reduced for speed
            
            if max_points < 10:
                return 2.0
            
            embedded_sample = embedded[:max_points]
            
            for i in range(max_points):
                for j in range(i+1, max_points):
                    dist = np.linalg.norm(embedded_sample[i] - embedded_sample[j])
                    distances.append(dist)
            
            distances = np.array(distances)
            
            if len(distances) == 0:
                return 2.0
            
            # Calculate correlation dimension
            r_values = np.logspace(np.log10(np.min(distances) + 1e-8), 
                                 np.log10(np.max(distances)), 20)
            
            correlations = []
            for r in r_values:
                count = np.sum(distances < r)
                correlation = count / len(distances)
                correlations.append(max(correlation, 1e-8))
            
            # Linear regression in log-log plot
            valid_indices = np.array(correlations) > 1e-8
            if np.sum(valid_indices) > 2:
                log_r = np.log(r_values[valid_indices])
                log_c = np.log(np.array(correlations)[valid_indices])
                
                A = np.vstack([log_r, np.ones(len(log_r))]).T
                dimension, _ = np.linalg.lstsq(A, log_c, rcond=None)[0]
                
                return max(0.5, min(abs(dimension), 5.0))  # Clamp to reasonable range
            else:
                return 2.0
                
        except Exception as e:
            print(f"相関次元エラー: {e}")
            return 2.0
    
    def _higuchi_fractal_dimension(self, audio):
        """Higuchi フラクタル次元"""
        try:
            N = len(audio)
            if N < 10:
                return 1.5
            
            k_values = range(1, min(10, N//4))
            L_values = []
            
            for k in k_values:
                L_k = []
                
                for m in range(k):
                    # Create subseries
                    indices = range(m, N, k)
                    if len(indices) < 2:
                        continue
                    
                    subseries = audio[indices]
                    
                    # Calculate length
                    length = 0
                    for i in range(len(subseries) - 1):
                        length += abs(subseries[i+1] - subseries[i])
                    
                    # Normalize
                    length = length * (N - 1) / (k * len(subseries))
                    L_k.append(length)
                
                if L_k:
                    L_values.append(np.mean(L_k))
                else:
                    L_values.append(0)
            
            # Remove zero values
            valid_L = [L for L in L_values if L > 0]
            valid_k = [k for k, L in zip(k_values, L_values) if L > 0]
            
            if len(valid_L) > 2:
                log_k = np.log(valid_k)
                log_L = np.log(valid_L)
                
                # Linear regression
                A = np.vstack([log_k, np.ones(len(log_k))]).T
                slope, _ = np.linalg.lstsq(A, log_L, rcond=None)[0]
                
                higuchi_dim = -slope
                return max(1.0, min(higuchi_dim, 2.0))
            else:
                return 1.5
                
        except Exception as e:
            print(f"Higuchi次元エラー: {e}")
            return 1.5
    
    def _detrended_fluctuation_analysis(self, audio):
        """Detrended Fluctuation Analysis"""
        try:
            N = len(audio)
            if N < 16:
                return 1.0
            
            # Integrate the series
            y = np.cumsum(audio - np.mean(audio))
            
            # Define scales
            scales = np.unique(np.logspace(0.7, np.log10(N//4), 15).astype(int))
            scales = scales[scales >= 4]
            
            if len(scales) < 3:
                return 1.0
            
            fluctuations = []
            
            for scale in scales:
                # Divide into segments
                segments = N // scale
                if segments < 2:
                    continue
                
                segment_fluctuations = []
                
                for i in range(segments):
                    start = i * scale
                    end = start + scale
                    segment = y[start:end]
                    
                    # Linear detrend
                    x = np.arange(len(segment))
                    coeffs = np.polyfit(x, segment, 1)
                    trend = np.polyval(coeffs, x)
                    
                    # Calculate fluctuation
                    fluctuation = np.sqrt(np.mean((segment - trend)**2))
                    segment_fluctuations.append(fluctuation)
                
                if segment_fluctuations:
                    fluctuations.append(np.mean(segment_fluctuations))
                else:
                    fluctuations.append(0)
            
            # Remove zero fluctuations
            valid_fluct = [f for f in fluctuations if f > 0]
            valid_scales = [s for s, f in zip(scales, fluctuations) if f > 0]
            
            if len(valid_fluct) > 2:
                log_scales = np.log(valid_scales)
                log_fluct = np.log(valid_fluct)
                
                # Linear regression
                A = np.vstack([log_scales, np.ones(len(log_scales))]).T
                alpha, _ = np.linalg.lstsq(A, log_fluct, rcond=None)[0]
                
                return max(0.5, min(alpha, 2.0))
            else:
                return 1.0
                
        except Exception as e:
            print(f"DFA解析エラー: {e}")
            return 1.0
    
    def _multiscale_entropy_analysis(self, audio):
        """マルチスケール・エントロピー解析"""
        try:
            mse_values = []
            
            for scale in self.scale_factors:
                # Coarse-grained series
                coarse_grained = self._coarse_grain(audio, scale)
                
                if len(coarse_grained) > 10:
                    # Sample entropy
                    sample_ent = self._sample_entropy(coarse_grained, 
                                                    self.pattern_length, 
                                                    self.tolerance_factor)
                    mse_values.append(sample_ent)
                else:
                    mse_values.append(0)
            
            return {
                'multiscale_entropy': mse_values,
                'mse_mean': np.mean(mse_values),
                'mse_std': np.std(mse_values),
                'mse_complexity_index': np.sum(mse_values) / len(mse_values) if mse_values else 0
            }
            
        except Exception as e:
            print(f"MSE解析エラー: {e}")
            return {'mse_complexity_index': 1.0}
    
    def _coarse_grain(self, signal, scale):
        """粗視化処理"""
        N = len(signal)
        coarse_length = N // scale
        
        if coarse_length == 0:
            return np.array([])
        
        coarse = np.zeros(coarse_length)
        for i in range(coarse_length):
            start = i * scale
            end = min(start + scale, N)
            coarse[i] = np.mean(signal[start:end])
        
        return coarse
    
    def _sample_entropy(self, signal, pattern_length, tolerance):
        """サンプル・エントロピー計算"""
        try:
            N = len(signal)
            
            if N <= pattern_length:
                return 0
            
            # Tolerance based on standard deviation
            tolerance_value = tolerance * np.std(signal)
            
            def _maxdist(xi, xj, N):
                return max([abs(ua - va) for ua, va in zip(xi, xj)])
            
            def _phi(m):
                patterns = np.array([signal[i:i + m] for i in range(N - m + 1)])
                C = np.zeros(N - m + 1)
                
                for i in range(N - m + 1):
                    template = patterns[i]
                    distances = [_maxdist(template, patterns[j], m) 
                               for j in range(N - m + 1)]
                    C[i] = sum([1 for d in distances if d <= tolerance_value])
                
                return (N - m + 1.0) / sum(C)
            
            return np.log(_phi(pattern_length) / _phi(pattern_length + 1))
            
        except Exception as e:
            return 0
    
    def _time_frequency_complexity(self, cwt_coeffs):
        """時間-周波数複雑度"""
        try:
            if cwt_coeffs.size == 0:
                return {'tf_complexity': 0.5}
            
            # Power matrix
            power_matrix = np.abs(cwt_coeffs)**2
            
            # Normalize
            total_power = np.sum(power_matrix)
            if total_power > 0:
                power_matrix_norm = power_matrix / total_power
            else:
                return {'tf_complexity': 0.5}
            
            # Time-frequency entropy
            tf_entropy = entropy(power_matrix_norm.flatten() + 1e-8)
            
            # Spectral complexity
            time_marginal = np.sum(power_matrix_norm, axis=0)
            freq_marginal = np.sum(power_matrix_norm, axis=1)
            
            time_entropy = entropy(time_marginal + 1e-8)
            freq_entropy = entropy(freq_marginal + 1e-8)
            
            # Complexity index
            complexity_index = tf_entropy / (time_entropy + freq_entropy + 1e-8)
            
            return {
                'tf_entropy': tf_entropy,
                'time_entropy': time_entropy,
                'freq_entropy': freq_entropy,
                'tf_complexity': complexity_index
            }
            
        except Exception as e:
            print(f"時間-周波数複雑度エラー: {e}")
            return {'tf_complexity': 0.5}
    
    def _calculate_integrated_complexity_score(self, results):
        """統合複雑度スコア計算"""
        try:
            # Collect complexity metrics
            components = []
            
            # Fractal dimensions (normalized)
            box_dim = results.get('box_counting_dimension', 1.5)
            components.append(min(box_dim / 2.0, 1.0) * 0.2)
            
            corr_dim = results.get('correlation_dimension', 2.0)
            components.append(min(corr_dim / 3.0, 1.0) * 0.15)
            
            higuchi_dim = results.get('higuchi_dimension', 1.5)
            components.append(min(higuchi_dim / 2.0, 1.0) * 0.15)
            
            dfa_exp = results.get('dfa_exponent', 1.0)
            components.append(min(abs(dfa_exp - 1.0), 1.0) * 0.1)
            
            # Wavelet entropy
            wavelet_ent = results.get('wavelet_entropy', 0)
            components.append(min(wavelet_ent / 5.0, 1.0) * 0.15)
            
            # Multiscale entropy
            mse_complexity = results.get('mse_complexity_index', 1.0)
            components.append(min(mse_complexity / 2.0, 1.0) * 0.15)
            
            # Time-frequency complexity
            tf_complexity = results.get('tf_complexity', 0.5)
            components.append(tf_complexity * 0.1)
            
            return sum(components)
            
        except Exception as e:
            print(f"統合複雑度計算エラー: {e}")
            return 0.5
    
    def _estimate_wavelet_fractal_tension(self, results):
        """Wavelet-Fractalテンション推定"""
        try:
            # 複雑度ベースのテンション推定
            complexity_score = results.get('integrated_complexity_score', 0.5)
            
            # Higher complexity often indicates more vocal effort
            # But relationship is non-linear
            
            # Wavelet features
            wavelet_skewness = abs(results.get('wavelet_skewness', 0))
            wavelet_kurtosis = results.get('wavelet_kurtosis', 0)
            
            # Fractal features  
            box_dim = results.get('box_counting_dimension', 1.5)
            dfa_exp = results.get('dfa_exponent', 1.0)
            
            # MSE features
            mse_complexity = results.get('mse_complexity_index', 1.0)
            
            # Combined tension estimation
            tension_components = []
            
            # Complexity-based (40%)
            complexity_tension = min(complexity_score * 1.5, 1.0)
            tension_components.append(complexity_tension * 0.4)
            
            # Wavelet skewness-based (20%)
            skewness_tension = min(wavelet_skewness / 2.0, 1.0)
            tension_components.append(skewness_tension * 0.2)
            
            # Fractal dimension deviation (20%)
            # Deviation from natural speech fractal dimension (~1.7)
            fractal_deviation = abs(box_dim - 1.7) / 0.5
            fractal_tension = min(fractal_deviation, 1.0)
            tension_components.append(fractal_tension * 0.2)
            
            # DFA exponent deviation (10%)
            # Deviation from typical speech DFA (~1.0)
            dfa_deviation = abs(dfa_exp - 1.0)
            dfa_tension = min(dfa_deviation, 1.0)
            tension_components.append(dfa_tension * 0.1)
            
            # MSE complexity (10%)
            mse_tension = min(mse_complexity / 1.5, 1.0)
            tension_components.append(mse_tension * 0.1)
            
            # Final tension
            wavelet_fractal_tension = sum(tension_components)
            
            # Apply adjusted sigmoid-like transformation for better range distribution
            # Adjust center point and slope for wider distribution
            tension_adjusted = 1 / (1 + np.exp(-4 * (wavelet_fractal_tension - 0.4)))
            
            # Further range expansion
            if tension_adjusted < 0.3:
                tension_final = tension_adjusted * 1.1
            elif tension_adjusted > 0.7:
                tension_final = 0.7 + (tension_adjusted - 0.7) * 1.3
            else:
                tension_final = tension_adjusted
            
            return np.clip(tension_final, 0.0, 1.0)
            
        except Exception as e:
            print(f"Wavelet-Fractalテンション推定エラー: {e}")
            return 0.5