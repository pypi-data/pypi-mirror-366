"""
Speech Tension Detector Module Setup
"""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# README.mdを読み込み
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="speech-tension-detector",
    version="1.0.0",
    author="hiroshi-tamura",
    author_email="hiroshi.tamura.dev@example.com",
    description="高精度音声テンション検出ライブラリ - AI搭載音声緊張度・感情強度解析システム",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hiroshi-tamura/speech-tension-detector",
    project_urls={
        "Bug Reports": "https://github.com/hiroshi-tamura/speech-tension-detector/issues",
        "Source": "https://github.com/hiroshi-tamura/speech-tension-detector",
        "Documentation": "https://github.com/hiroshi-tamura/speech-tension-detector/blob/main/API_DOCUMENTATION.md",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",  
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Natural Language :: Japanese",
        "Natural Language :: English",
    ],
    keywords=[
        "speech", "audio", "tension", "detection", "voice", "analysis", 
        "machine-learning", "deep-learning", "AI", "emotion", "sentiment",
        "wav2vec2", "whisper", "spectral-analysis", "prosodic-features",
        "vocal-effort", "glottal", "speech-processing", "sound-analysis",
        "音声", "テンション", "検出", "感情", "解析", "機械学習"
    ],
    python_requires=">=3.8",
    install_requires=[
        # 必須音声処理ライブラリ
        "librosa>=0.10.0",
        "soundfile>=0.12.1",
        
        # 必須数値計算ライブラリ
        "numpy>=1.20.0",
        "scipy>=1.8.0",
        
        # 必須機械学習ライブラリ
        "scikit-learn>=1.0.0",
        
        # ユーティリティ
        "tqdm>=4.60.0",
    ],
    extras_require={
        # 高精度分析機能（推奨）
        "full": [
            "parselmouth>=0.4.3",           # 韻律特徴量分析
            "torch>=2.0.0",                # ディープラーニング
            "transformers>=4.30.0",        # Wav2Vec2, Whisper
            "pandas>=2.0.0",               # データ処理
            "matplotlib>=3.7.0",           # 可視化
        ],
        
        # GPU対応
        "gpu": [
            "torch>=2.0.0",
            "transformers[torch]>=4.30.0",
            "accelerate>=0.21.0",
        ],
        
        # 高度な特徴量分析
        "advanced": [
            "opensmile>=2.5.0",            # OpenSMILE特徴量
            "tensorflow>=2.13.0",          # 追加モデル
            "datasets>=2.14.0",           # データセット処理
        ],
        
        # 開発ツール
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "sphinx>=5.0.0",              # ドキュメント生成
        ],
        
        # 可視化・分析
        "viz": [
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
            "plotly>=5.0.0",
        ],
        
        # 全機能
        "all": [
            "parselmouth>=0.4.3",
            "torch>=2.0.0",
            "transformers>=4.30.0",
            "pandas>=2.0.0",
            "matplotlib>=3.7.0",
            "opensmile>=2.5.0",
            "tensorflow>=2.13.0",
            "datasets>=2.14.0",
            "accelerate>=0.21.0",
            "seaborn>=0.12.0",
            "plotly>=5.0.0",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
    entry_points={
        "console_scripts": [
            "speech-tension-detect=speech_tension_detector.cli:main",
        ],
    },
)