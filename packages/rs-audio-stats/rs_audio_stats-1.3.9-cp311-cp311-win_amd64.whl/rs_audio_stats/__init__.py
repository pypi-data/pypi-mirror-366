"""
rs_audio_stats: Professional-grade audio analysis tool

This module provides Python bindings for the rs_audio_stats library,
offering EBU R128 loudness measurement and audio normalization capabilities.
"""

try:
    # Import native module if available
    from .rs_audio_stats import *
    
    # High-level convenience functions
    __all__ = [
        # Core analysis functions
        "analyze_audio",
        "analyze_audio_all", 
        "get_audio_info_py",
        
        # Normalization functions
        "normalize_true_peak",
        "normalize_integrated_loudness",
        "normalize_short_term_loudness",
        "normalize_momentary_loudness",
        "normalize_rms_max",
        "normalize_rms_average",
        
        # Export functions
        "export_to_csv",
        "export_to_tsv",
        "export_to_xml",
        "export_to_json",
        
        # Batch processing
        "batch_analyze",
        "batch_analyze_directory",
        "find_audio_files",
        
        # Convenience wrappers
        "normalize_to_lufs",
        "normalize_to_dbfs",
        "normalize_to_short_term_lufs",
        "normalize_to_momentary_lufs",
        "get_loudness",
        "get_true_peak",
    ]
    
    # Convenience wrapper functions
    def normalize_to_lufs(input_path: str, target_lufs: float, output_path: str = None) -> None:
        """Normalize audio to target LUFS level"""
        if output_path is None:
            output_path = input_path.replace('.wav', '_normalized.wav')
        normalize_integrated_loudness(input_path, target_lufs, output_path)
    
    def normalize_to_dbfs(input_path: str, target_dbfs: float, output_path: str = None) -> None:
        """Normalize audio to target dBFS true peak level"""
        if output_path is None:
            output_path = input_path.replace('.wav', '_peaked.wav')
        normalize_true_peak(input_path, target_dbfs, output_path)
    
    def get_loudness(file_path: str) -> float:
        """Get integrated loudness of audio file"""
        _, results = analyze_audio(file_path, True, False, False, False, False, False, False)
        return results.integrated_loudness
    
    def get_true_peak(file_path: str) -> float:
        """Get true peak of audio file"""
        _, results = analyze_audio(file_path, False, False, False, False, True, False, False)
        return results.true_peak
    
    def normalize_to_short_term_lufs(input_path: str, target_lufs: float, output_path: str = None) -> None:
        """Normalize audio to target short-term LUFS level"""
        if output_path is None:
            output_path = input_path.replace('.wav', '_short_term_normalized.wav')
        normalize_short_term_loudness(input_path, target_lufs, output_path)
    
    def normalize_to_momentary_lufs(input_path: str, target_lufs: float, output_path: str = None) -> None:
        """Normalize audio to target momentary LUFS level"""
        if output_path is None:
            output_path = input_path.replace('.wav', '_momentary_normalized.wav')
        normalize_momentary_loudness(input_path, target_lufs, output_path)
    
    def batch_analyze_directory(directory_path: str, integrated_loudness: bool = False, short_term_loudness: bool = False, 
                               momentary_loudness: bool = False, loudness_range: bool = False, true_peak: bool = False, 
                               rms_max: bool = False, rms_average: bool = False):
        """Batch analyze all audio files in a directory (EXE version compatibility)"""
        return batch_analyze_directory_py(directory_path, integrated_loudness, short_term_loudness, 
                                         momentary_loudness, loudness_range, true_peak, rms_max, rms_average)

except ImportError:
    # If native module is not available, provide stub implementations
    import warnings
    warnings.warn("Python bindings are not available. This is expected in a cross-compilation environment.")
    
    class AudioInfo:
        def __init__(self):
            self.sample_rate = 0
            self.channels = 0
            self.bit_depth = 0
            self.duration_seconds = 0.0
    
    class AnalysisResults:
        def __init__(self):
            self.integrated_loudness = None
            self.short_term_loudness = None
            self.momentary_loudness = None
            self.loudness_range = None
            self.true_peak = None
            self.rms_max = None
            self.rms_average = None
    
    def analyze_audio(*args, **kwargs):
        raise NotImplementedError("Python bindings not available")
    
    def analyze_audio_all(*args, **kwargs):
        raise NotImplementedError("Python bindings not available")
    
    def get_audio_info_py(*args, **kwargs):
        raise NotImplementedError("Python bindings not available")
    
    def normalize_true_peak(*args, **kwargs):
        raise NotImplementedError("Python bindings not available")
    
    def normalize_integrated_loudness(*args, **kwargs):
        raise NotImplementedError("Python bindings not available")
    
    def normalize_short_term_loudness(*args, **kwargs):
        raise NotImplementedError("Python bindings not available")
    
    def normalize_momentary_loudness(*args, **kwargs):
        raise NotImplementedError("Python bindings not available")
    
    def normalize_rms_max(*args, **kwargs):
        raise NotImplementedError("Python bindings not available")
    
    def normalize_rms_average(*args, **kwargs):
        raise NotImplementedError("Python bindings not available")
    
    def export_to_csv(*args, **kwargs):
        raise NotImplementedError("Python bindings not available")
    
    def export_to_tsv(*args, **kwargs):
        raise NotImplementedError("Python bindings not available")
    
    def export_to_xml(*args, **kwargs):
        raise NotImplementedError("Python bindings not available")
    
    def export_to_json(*args, **kwargs):
        raise NotImplementedError("Python bindings not available")
    
    def batch_analyze(*args, **kwargs):
        raise NotImplementedError("Python bindings not available")
    
    def batch_analyze_directory(*args, **kwargs):
        raise NotImplementedError("Python bindings not available")
    
    def find_audio_files(*args, **kwargs):
        raise NotImplementedError("Python bindings not available")
    
    def normalize_to_lufs(*args, **kwargs):
        raise NotImplementedError("Python bindings not available")
    
    def normalize_to_dbfs(*args, **kwargs):
        raise NotImplementedError("Python bindings not available")
    
    def normalize_to_short_term_lufs(*args, **kwargs):
        raise NotImplementedError("Python bindings not available")
    
    def normalize_to_momentary_lufs(*args, **kwargs):
        raise NotImplementedError("Python bindings not available")
    
    def get_loudness(*args, **kwargs):
        raise NotImplementedError("Python bindings not available")
    
    def get_true_peak(*args, **kwargs):
        raise NotImplementedError("Python bindings not available")

__version__ = "1.2.4"