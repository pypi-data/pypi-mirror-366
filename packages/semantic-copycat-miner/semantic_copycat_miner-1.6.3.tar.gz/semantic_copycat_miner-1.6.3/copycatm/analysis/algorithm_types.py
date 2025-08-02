"""
Algorithm type classifications for CopycatM.
"""

from enum import Enum
from typing import Dict, Any


class AlgorithmType(Enum):
    """Comprehensive algorithm type classification."""
    
    # Core Computer Science Algorithms
    SORTING_ALGORITHM = "sorting_algorithm"
    SEARCH_ALGORITHM = "search_algorithm"
    GRAPH_TRAVERSAL = "graph_traversal"
    DYNAMIC_PROGRAMMING = "dynamic_programming"
    DIVIDE_AND_CONQUER = "divide_and_conquer"
    STRING_MATCHING = "string_matching"
    NUMERICAL_ALGORITHM = "numerical_algorithm"
    
    # Data Structure Manipulation
    OBJECT_MANIPULATION = "object_manipulation"
    ARRAY_MANIPULATION = "array_manipulation"
    ITERATOR_PATTERN = "iterator_pattern"
    POLYFILL_PATTERN = "polyfill_pattern"
    
    # Security & Cryptography
    CRYPTOGRAPHIC_ALGORITHM = "cryptographic_algorithm"
    SECURITY = "security"
    CRYPTOGRAPHY = "cryptography"
    ANTI_TAMPERING = "anti_tampering"
    
    # Media & Compression
    COMPRESSION_ALGORITHM = "compression_algorithm"
    AUDIO_CODEC = "audio_codec"
    VIDEO_CODEC = "video_codec"
    IMAGE_PROCESSING = "image_processing"
    VIDEO_PROCESSING = "video_processing"
    AUDIO_PROCESSING = "audio_processing"
    SIGNAL_PROCESSING = "signal_processing"
    ENCODING_ALGORITHM = "encoding_algorithm"
    
    # Machine Learning & AI
    MACHINE_LEARNING = "machine_learning"
    
    # Graphics & Rendering
    GRAPHICS_RENDERING = "graphics_rendering"
    
    # System & Network
    NETWORK_PROTOCOL = "network_protocol"
    DATABASE_STORAGE = "database_storage"
    HARDWARE_SPECIFIC = "hardware_specific"
    REAL_TIME_SYSTEMS = "real_time_systems"
    
    # System Components
    DRIVER = "driver"
    BOOTLOADER = "bootloader"
    FIRMWARE = "firmware"
    KERNEL = "kernel"
    
    # Legal & Licensing
    PROPRIETARY = "proprietary"
    PATENTED = "patented"
    COPYLEFT = "copyleft"
    OPEN_SOURCE = "open_source"
    COMMERCIAL = "commercial"
    EXPORT_CONTROLLED = "export_controlled"
    ACADEMIC_RESEARCH = "academic_research"
    PROPRIETARY_SDK = "proprietary_sdk"
    
    # Content Protection
    DRM = "drm"
    
    # Domain-Specific
    FINANCIAL = "financial"
    MEDICAL_BIOINFORMATICS = "medical_bioinformatics"
    AUTOMOTIVE_TRANSPORTATION = "automotive_transportation"
    TELECOMMUNICATIONS = "telecommunications"
    GAMING_ENTERTAINMENT = "gaming_entertainment"
    MATHEMATICAL_SCIENTIFIC = "mathematical_scientific"


def get_algorithm_patterns() -> Dict[AlgorithmType, Dict[str, Any]]:
    """Get comprehensive algorithm patterns for detection."""
    
    return {
        AlgorithmType.SORTING_ALGORITHM: {
            'keywords': ['sort', 'quicksort', 'mergesort', 'bubblesort', 'insertionsort', 'selectionsort', 'heapsort'],
            'patterns': ['swap', 'partition', 'pivot', 'merge', 'bubble', 'insert', 'select', 'heap'],
            'confidence': 0.7
        },
        AlgorithmType.SEARCH_ALGORITHM: {
            'keywords': ['search', 'find', 'binary', 'linear', 'depth', 'breadth', 'bfs', 'dfs'],
            'patterns': ['binary_search', 'linear_search', 'depth_first', 'breadth_first'],
            'confidence': 0.7
        },
        AlgorithmType.GRAPH_TRAVERSAL: {
            'keywords': ['graph', 'node', 'edge', 'vertex', 'traversal', 'dijkstra', 'bfs', 'dfs'],
            'patterns': ['shortest_path', 'minimum_spanning', 'topological_sort'],
            'confidence': 0.8
        },
        AlgorithmType.DYNAMIC_PROGRAMMING: {
            'keywords': ['memo', 'cache', 'dp', 'dynamic', 'recursive', 'subproblem'],
            'patterns': ['memoization', 'caching', 'optimal_substructure'],
            'confidence': 0.8
        },
        AlgorithmType.DIVIDE_AND_CONQUER: {
            'keywords': ['divide', 'conquer', 'merge', 'split', 'recursive'],
            'patterns': ['divide_and_conquer', 'merge_sort', 'quick_sort'],
            'confidence': 0.7
        },
        AlgorithmType.STRING_MATCHING: {
            'keywords': ['string', 'pattern', 'match', 'kmp', 'boyer', 'moore'],
            'patterns': ['string_matching', 'pattern_matching', 'substring'],
            'confidence': 0.7
        },
        AlgorithmType.NUMERICAL_ALGORITHM: {
            'keywords': ['math', 'numerical', 'algorithm', 'gcd', 'lcm', 'prime', 'factor'],
            'patterns': ['euclidean', 'sieve', 'factorization'],
            'confidence': 0.6
        },
        AlgorithmType.OBJECT_MANIPULATION: {
            'keywords': ['assign', 'merge', 'extend', 'mixin', 'spread', 'rest', 'destructure', 'clone', 'copy', 'hasOwnProperty', 'propertyIsEnumerable', 'getOwnPropertySymbols', 'defineProperty'],
            'patterns': ['object_merge', 'object_spread', 'property_iteration', 'property_copy', 'deep_clone', 'shallow_copy', 'mixin_pattern'],
            'confidence': 0.7
        },
        AlgorithmType.ARRAY_MANIPULATION: {
            'keywords': ['concat', 'spread', 'slice', 'splice', 'push', 'pop', 'shift', 'unshift', 'flatten', 'reduce', 'accumulate', 'array', 'length'],
            'patterns': ['array_merge', 'array_spread', 'array_slice', 'array_flatten', 'array_accumulation', 'nested_loops', 'array_indexing'],
            'confidence': 0.7
        },
        AlgorithmType.ITERATOR_PATTERN: {
            'keywords': ['iterator', 'generator', 'yield', 'next', 'done', 'value', 'Symbol.iterator', 'Symbol.asyncIterator', 'async', 'await', '__values', '__read', '__await'],
            'patterns': ['iterator_protocol', 'generator_function', 'async_iterator', 'state_machine', 'promise_handling'],
            'confidence': 0.8
        },
        AlgorithmType.POLYFILL_PATTERN: {
            'keywords': ['polyfill', 'shim', 'fallback', '__', 'helper', 'runtime', 'tslib', 'babel', 'Object.assign', 'Array.prototype', 'prototype'],
            'patterns': ['polyfill_implementation', 'runtime_helper', 'native_check', 'fallback_implementation', 'feature_detection'],
            'confidence': 0.7
        },
        AlgorithmType.CRYPTOGRAPHIC_ALGORITHM: {
            'keywords': ['crypto', 'hash', 'encrypt', 'decrypt', 'sha', 'md5', 'aes', 'rsa', 'blowfish', 'des', '3des', 'chacha20', 'poly1305', 'ed25519', 'x25519', 'curve25519', 'secp256k1', 'ecc', 'elliptic', 'hmac', 'pbkdf2', 'bcrypt', 'scrypt', 'argon2'],
            'patterns': ['cryptographic', 'encryption', 'hashing', 'digital_signature', 'key_exchange', 'public_key', 'private_key', 'symmetric', 'asymmetric', 'block_cipher', 'stream_cipher', 'hash_function', 'message_digest'],
            'confidence': 0.9
        },
        AlgorithmType.COMPRESSION_ALGORITHM: {
            'keywords': ['compress', 'decompress', 'zip', 'gzip', 'lz', 'huffman', 'audio', 'codec', 'pcm', 'sample', 'format', 'video', 'h264', 'h265', 'hevc', 'avc', 'mpeg', 'vp9', 'av1', 'theora', 'divx', 'xvid'],
            'patterns': ['compression', 'decompression', 'encoding', 'audio_codec', 'audio_format', 'sample_rate', 'channels', 'video_codec', 'video_format', 'frame_rate', 'bitrate', 'resolution', 'pixel_format', 'color_space', 'yuv', 'rgb', 'hsv'],
            'confidence': 0.8
        },
        AlgorithmType.AUDIO_CODEC: {
            'keywords': ['audio', 'codec', 'pcm', 'alaw', 'ulaw', 'g711', 'g711a', 'g711u', 'sample', 'rate', 'bitrate', 'channels', 'quantization', 'companding', 'int16', 'uint8', 'int8', 'float32', 'float64', 'mp3', 'aac', 'ac3', 'dolby', 'dts', 'vorbis', 'flac', 'opus', 'amr', 'g722', 'g729', 'audio_watermarking', 'noise_reduction', '3d_audio', 'binaural', 'hrtf', 'audio_fingerprinting', 'psychoacoustic', 'multi_channel', 'speech_codec', 'telephony_codec'],
            'patterns': ['audio_codec', 'audio_format', 'sample_rate', 'num_channels', 'bit_depth', 'quantization', 'companding', 'alaw_from_pcm', 'alaw_to_pcm', 'ulaw_from_pcm', 'ulaw_to_pcm', 'g711_encode', 'g711_decode', 'mp3_encoder', 'mp3_decoder', 'aac_encoder', 'aac_decoder', 'audio_watermarking', 'noise_reduction', '3d_audio_processing', 'audio_fingerprinting', 'psychoacoustic_masking'],
            'confidence': 0.9
        },
        AlgorithmType.VIDEO_CODEC: {
            'keywords': ['h264', 'h265', 'h266', 'avc', 'hevc', 'vvc', 'vp8', 'vp9', 'av1', 'mpeg2', 'mpeg4', 'divx', 'xvid', 'motion_estimation', 'motion_compensation', 'loop_filtering', 'intra_prediction', 'transform_coding', 'quantization', 'rate_control', 'error_concealment', 'video_scaling', 'deinterlacing', 'video_watermarking', 'real_time_video'],
            'patterns': ['h264_encoder', 'h265_encoder', 'h266_encoder', 'avc_codec', 'hevc_codec', 'vvc_codec', 'vp8_codec', 'vp9_codec', 'av1_codec', 'mpeg2_codec', 'mpeg4_codec', 'motion_estimation', 'motion_compensation', 'loop_filtering', 'intra_prediction', 'transform_coding', 'quantization', 'rate_control'],
            'confidence': 0.8
        },
        AlgorithmType.IMAGE_PROCESSING: {
            'keywords': ['jpeg', 'jpeg2000', 'webp', 'avif', 'bpg', 'fractal_compression', 'spiht', 'super_resolution', 'edge_detection', 'canny', 'sobel', 'image_segmentation', 'feature_detection', 'sift', 'surf', 'orb', 'image_stabilization', 'hdr_tone_mapping', 'image_denoising', 'morphological_operations'],
            'patterns': ['jpeg_encoder', 'jpeg_decoder', 'jpeg2000_compression', 'webp_format', 'avif_codec', 'bpg_compression', 'fractal_compression', 'spiht_algorithm', 'super_resolution', 'edge_detection', 'image_segmentation', 'feature_detection', 'image_stabilization', 'hdr_tone_mapping', 'image_denoising'],
            'confidence': 0.8
        },
        AlgorithmType.MACHINE_LEARNING: {
            'keywords': ['neural_network', 'transformer', 'attention_mechanism', 'convolutional', 'recurrent', 'lstm', 'gru', 'optimization', 'adam', 'rmsprop', 'quantization', 'pruning', 'knowledge_distillation', 'federated_learning', 'differential_privacy', 'adversarial_training', 'neural_architecture_search', 'automl', 'reinforcement_learning', 'computer_vision', 'nlp', 'speech_recognition', 'recommendation_system', 'tpu', 'gpu_acceleration'],
            'patterns': ['neural_network_architecture', 'transformer_attention', 'convolutional_neural_network', 'recurrent_neural_network', 'lstm_network', 'gru_network', 'optimization_algorithm', 'quantization_technique', 'pruning_algorithm', 'knowledge_distillation', 'federated_learning', 'differential_privacy', 'adversarial_training', 'neural_architecture_search', 'automl', 'reinforcement_learning'],
            'confidence': 0.8
        },
        AlgorithmType.GRAPHICS_RENDERING: {
            'keywords': ['s3tc', 'dxtn', 'astc', 'etc', 'etc2', 'pvrtc', 'ray_tracing', 'bvh', 'anti_aliasing', 'fxaa', 'msaa', 'temporal_aa', 'shader_optimization', 'geometry_processing', 'tessellation', 'shadow_mapping', 'screen_space_reflections', 'ambient_occlusion', 'ssao', 'hbao', 'pbr', 'physically_based_rendering', 'volume_rendering', 'lod', 'level_of_detail', 'culling', 'frustum', 'occlusion', 'mesh_simplification', 'uv_mapping'],
            'patterns': ['s3tc_compression', 'dxtn_compression', 'astc_compression', 'etc_compression', 'pvrtc_compression', 'ray_tracing', 'bvh_structure', 'anti_aliasing', 'shader_optimization', 'geometry_processing', 'tessellation', 'shadow_mapping', 'screen_space_reflections', 'ambient_occlusion', 'pbr_rendering', 'volume_rendering', 'lod_algorithm', 'culling_algorithm'],
            'confidence': 0.8
        },
        AlgorithmType.NETWORK_PROTOCOL: {
            'keywords': ['tcp_optimization', 'udp_optimization', 'error_correction', 'reed_solomon', 'ldpc', 'network_coding', 'routing_algorithm', 'qos_scheduling', 'congestion_control', 'load_balancing', 'network_compression', 'vpn_tunneling', 'peer_to_peer', 'blockchain_consensus', 'webrtc', 'quic_protocol', '5g_protocol', 'lte_protocol', 'wifi_protocol', 'bluetooth_protocol', 'mesh_networking'],
            'patterns': ['tcp_optimization', 'udp_optimization', 'error_correction_code', 'reed_solomon_code', 'ldpc_code', 'network_coding', 'routing_algorithm', 'qos_scheduling', 'congestion_control', 'load_balancing', 'network_compression', 'vpn_tunneling', 'peer_to_peer', 'blockchain_consensus', 'webrtc', 'quic_protocol'],
            'confidence': 0.8
        },
        AlgorithmType.DATABASE_STORAGE: {
            'keywords': ['b_tree', 'lsm_tree', 'bloom_filter', 'consistent_hashing', 'distributed_consensus', 'raft', 'pbft', 'cache_replacement', 'arc', 'clock', 'transaction_isolation', 'query_optimization', 'index_compression', 'database_compression', 'replication_protocol', 'sharding_strategy', 'acid_compliance', 'nosql_storage', 'time_series_database', 'graph_database', 'in_memory_database'],
            'patterns': ['b_tree_variant', 'lsm_tree', 'bloom_filter', 'consistent_hashing', 'distributed_consensus', 'raft_protocol', 'pbft_protocol', 'cache_replacement_policy', 'transaction_isolation', 'query_optimization', 'index_compression', 'database_compression', 'replication_protocol', 'sharding_strategy', 'acid_compliance'],
            'confidence': 0.8
        },
        AlgorithmType.HARDWARE_SPECIFIC: {
            'keywords': ['cpu_optimization', 'simd', 'sse', 'avx', 'gpu_compute', 'cuda', 'opencl', 'memory_management', 'cache_optimization', 'power_management', 'thermal_management', 'real_time_scheduling', 'interrupt_handling', 'dma_transfer', 'hardware_random', 'hardware_security', 'fpga_implementation', 'dsp_optimization', 'embedded_system'],
            'patterns': ['cpu_instruction_optimization', 'simd_optimization', 'sse_implementation', 'avx_implementation', 'gpu_compute_kernel', 'cuda_kernel', 'opencl_kernel', 'memory_management', 'cache_optimization', 'power_management', 'thermal_management', 'real_time_scheduling', 'interrupt_handling', 'dma_transfer', 'hardware_random_number', 'hardware_security', 'fpga_implementation'],
            'confidence': 0.8
        },
        AlgorithmType.FINANCIAL: {
            'keywords': ['high_frequency_trading', 'risk_calculation', 'portfolio_optimization', 'credit_scoring', 'fraud_detection', 'algorithmic_trading', 'market_making', 'options_pricing', 'cryptocurrency_mining', 'blockchain_validation', 'trading_algorithm', 'risk_model', 'credit_model', 'fraud_model', 'market_model'],
            'patterns': ['high_frequency_trading', 'risk_calculation_model', 'portfolio_optimization', 'credit_scoring_algorithm', 'fraud_detection_system', 'algorithmic_trading', 'market_making_algorithm', 'options_pricing_model', 'cryptocurrency_mining', 'blockchain_validation', 'trading_algorithm', 'risk_model', 'credit_model'],
            'confidence': 0.8
        },
        AlgorithmType.MEDICAL_BIOINFORMATICS: {
            'keywords': ['medical_imaging', 'mri', 'ct', 'xray', 'dna_sequencing', 'protein_folding', 'drug_discovery', 'medical_diagnosis', 'biometric_recognition', 'fingerprint', 'iris', 'facial', 'genomic_analysis', 'medical_device', 'telemedicine', 'health_monitoring', 'bioinformatics', 'genomics', 'proteomics'],
            'patterns': ['medical_imaging_processing', 'mri_processing', 'ct_processing', 'xray_processing', 'dna_sequencing_algorithm', 'protein_folding_prediction', 'drug_discovery_algorithm', 'medical_diagnosis_ai', 'biometric_recognition', 'genomic_analysis_tool', 'medical_device_control', 'telemedicine_protocol', 'health_monitoring_algorithm'],
            'confidence': 0.8
        },
        AlgorithmType.AUTOMOTIVE_TRANSPORTATION: {
            'keywords': ['collision_detection', 'path_planning', 'autonomous_driving', 'engine_control', 'navigation_system', 'traffic_optimization', 'vehicle_to_vehicle', 'parking_assistance', 'adaptive_cruise_control', 'lane_departure', 'autonomous_vehicle', 'self_driving', 'driver_assistance', 'traffic_management'],
            'patterns': ['collision_detection_algorithm', 'path_planning_algorithm', 'autonomous_driving_ai', 'engine_control_algorithm', 'navigation_system', 'traffic_optimization', 'vehicle_to_vehicle_communication', 'parking_assistance_system', 'adaptive_cruise_control', 'lane_departure_warning'],
            'confidence': 0.8
        },
        AlgorithmType.TELECOMMUNICATIONS: {
            'keywords': ['signal_processing', 'modulation', 'demodulation', 'channel_coding', 'antenna_array', 'beamforming', 'mimo', 'software_defined_radio', 'spectrum_management', 'interference_cancellation', 'network_optimization', 'telecommunications', 'wireless_communication', 'radio_communication'],
            'patterns': ['signal_processing_algorithm', 'modulation_technique', 'demodulation_technique', 'channel_coding_algorithm', 'antenna_array_processing', 'beamforming_algorithm', 'mimo_system', 'software_defined_radio', 'spectrum_management_algorithm', 'interference_cancellation', 'network_optimization'],
            'confidence': 0.8
        },
        AlgorithmType.GAMING_ENTERTAINMENT: {
            'keywords': ['physics_engine', 'ai_behavior', 'procedural_generation', 'audio_engine', 'network_synchronization', 'anti_cheat', 'digital_rights_management', 'content_delivery', 'streaming_protocol', 'virtual_reality', 'game_engine', 'rendering_engine', 'animation_system'],
            'patterns': ['physics_engine_implementation', 'ai_behavior_algorithm', 'procedural_generation_algorithm', 'audio_engine_optimization', 'network_synchronization', 'anti_cheat_mechanism', 'digital_rights_management', 'content_delivery_optimization', 'streaming_protocol', 'virtual_reality_algorithm'],
            'confidence': 0.8
        },
        AlgorithmType.MATHEMATICAL_SCIENTIFIC: {
            'keywords': ['fast_fourier_transform', 'fft', 'linear_algebra', 'blas', 'lapack', 'sparse_matrix', 'numerical_optimization', 'monte_carlo', 'finite_element', 'computational_fluid_dynamics', 'weather_prediction', 'scientific_visualization', 'high_performance_computing', 'mathematical_computing', 'scientific_computing'],
            'patterns': ['fast_fourier_transform', 'fft_optimization', 'linear_algebra_optimization', 'blas_implementation', 'lapack_implementation', 'sparse_matrix_algorithm', 'numerical_optimization_method', 'monte_carlo_method', 'finite_element_analysis', 'computational_fluid_dynamics', 'weather_prediction_model'],
            'confidence': 0.8
        },
        AlgorithmType.REAL_TIME_SYSTEMS: {
            'keywords': ['real_time_scheduling', 'deadline_scheduling', 'priority_inversion', 'resource_allocation', 'interrupt_latency', 'jitter_reduction', 'deterministic_execution', 'fault_tolerance', 'safety_critical', 'mission_critical', 'real_time_system', 'hard_real_time', 'soft_real_time'],
            'patterns': ['real_time_scheduling_algorithm', 'deadline_scheduling', 'priority_inversion_handling', 'resource_allocation_strategy', 'interrupt_latency_optimization', 'jitter_reduction_technique', 'deterministic_execution', 'fault_tolerance_mechanism', 'safety_critical_system', 'mission_critical_algorithm'],
            'confidence': 0.8
        },
        AlgorithmType.ANTI_TAMPERING: {
            'keywords': ['code_obfuscation', 'anti_debugging', 'software_protection', 'license_verification', 'tamper_detection', 'secure_boot', 'key_management', 'certificate_validation', 'intrusion_detection', 'malware_detection', 'fuzzy_hashing', 'lsh', 'tlsh', 'deephash', 'ssdeep', 'anti_tampering', 'software_integrity'],
            'patterns': ['code_obfuscation_technique', 'anti_debugging_mechanism', 'software_protection_scheme', 'license_verification_system', 'tamper_detection_algorithm', 'secure_boot_implementation', 'key_management_system', 'certificate_validation', 'intrusion_detection_system', 'malware_detection_algorithm', 'fuzzy_hashing_algorithm'],
            'confidence': 0.8
        },
        AlgorithmType.DRIVER: {
            'keywords': ['driver', 'device_driver', 'hardware_driver', 'kernel_driver', 'loadable_kernel_module', 'lkm', 'device_control', 'hardware_interface', 'peripheral_driver', 'usb_driver', 'pci_driver', 'network_driver', 'storage_driver', 'audio_driver', 'video_driver', 'input_driver'],
            'patterns': ['device_driver', 'hardware_driver', 'kernel_driver', 'loadable_kernel_module', 'device_control', 'hardware_interface', 'peripheral_driver', 'usb_driver', 'pci_driver', 'network_driver', 'storage_driver', 'audio_driver', 'video_driver', 'input_driver'],
            'confidence': 0.8
        },
        AlgorithmType.BOOTLOADER: {
            'keywords': ['bootloader', 'boot_loader', 'bootstrap', 'grub', 'lilo', 'syslinux', 'u_boot', 'coreboot', 'seabios', 'openbios', 'bios', 'uefi', 'secure_boot', 'boot_manager', 'boot_partition', 'mbr', 'gpt', 'boot_sector'],
            'patterns': ['bootloader', 'boot_loader', 'bootstrap', 'grub', 'lilo', 'syslinux', 'u_boot', 'coreboot', 'seabios', 'openbios', 'bios', 'uefi', 'secure_boot', 'boot_manager', 'boot_partition', 'mbr', 'gpt', 'boot_sector'],
            'confidence': 0.8
        },
        AlgorithmType.DRM: {
            'keywords': ['drm', 'digital_rights_management', 'content_protection', 'copy_protection', 'watermarking', 'encryption', 'license_management', 'rights_management', 'content_control', 'access_control', 'playback_control', 'usage_restriction', 'digital_watermark', 'fingerprinting'],
            'patterns': ['drm_system', 'digital_rights_management', 'content_protection', 'copy_protection', 'watermarking', 'license_management', 'rights_management', 'content_control', 'access_control', 'playback_control', 'usage_restriction', 'digital_watermark', 'fingerprinting'],
            'confidence': 0.8
        },
        AlgorithmType.FIRMWARE: {
            'keywords': ['firmware', 'microcode', 'bios', 'uefi', 'bootloader', 'device_firmware', 'embedded_firmware', 'hardware_firmware', 'system_firmware', 'update_firmware', 'flash_firmware', 'rom_firmware', 'eeprom', 'flash_memory'],
            'patterns': ['firmware_update', 'microcode_update', 'bios_update', 'uefi_update', 'device_firmware', 'embedded_firmware', 'hardware_firmware', 'system_firmware', 'update_firmware', 'flash_firmware', 'rom_firmware', 'eeprom', 'flash_memory'],
            'confidence': 0.8
        },
        AlgorithmType.KERNEL: {
            'keywords': ['kernel', 'operating_system_kernel', 'system_kernel', 'linux_kernel', 'windows_kernel', 'macos_kernel', 'unix_kernel', 'bsd_kernel', 'kernel_module', 'loadable_kernel_module', 'lkm', 'kernel_space', 'user_space', 'system_call', 'interrupt_handler'],
            'patterns': ['kernel_module', 'loadable_kernel_module', 'system_call', 'interrupt_handler', 'kernel_space', 'user_space', 'operating_system_kernel', 'system_kernel', 'linux_kernel', 'windows_kernel', 'macos_kernel', 'unix_kernel', 'bsd_kernel'],
            'confidence': 0.8
        },
        AlgorithmType.SECURITY: {
            'keywords': ['security', 'authentication', 'authorization', 'access_control', 'identity_management', 'single_sign_on', 'sso', 'multi_factor', 'mfa', 'two_factor', '2fa', 'biometric', 'password', 'encryption', 'decryption', 'key_management', 'certificate', 'ssl', 'tls'],
            'patterns': ['security_system', 'authentication_system', 'authorization_system', 'access_control', 'identity_management', 'single_sign_on', 'multi_factor', 'two_factor', 'biometric', 'password', 'encryption', 'decryption', 'key_management', 'certificate', 'ssl', 'tls'],
            'confidence': 0.8
        },
        AlgorithmType.CRYPTOGRAPHY: {
            'keywords': ['cryptography', 'crypto', 'encryption', 'decryption', 'hash', 'signature', 'key_exchange', 'public_key', 'private_key', 'symmetric', 'asymmetric', 'block_cipher', 'stream_cipher', 'hash_function', 'digital_signature', 'certificate', 'ca', 'pki'],
            'patterns': ['cryptography_system', 'encryption_system', 'decryption_system', 'hash_function', 'signature_system', 'key_exchange', 'public_key', 'private_key', 'symmetric', 'asymmetric', 'block_cipher', 'stream_cipher', 'hash_function', 'digital_signature', 'certificate', 'ca', 'pki'],
            'confidence': 0.8
        },
        AlgorithmType.PROPRIETARY: {
            'keywords': ['proprietary', 'patent', 'copyright', 'trademark', 'trade_secret', 'confidential', 'internal', 'custom', 'private', 'commercial', 'licensed', 'restricted', 'exclusive'],
            'patterns': ['proprietary_algorithm', 'patented_algorithm', 'copyrighted_algorithm', 'trade_secret', 'confidential_algorithm', 'internal_algorithm', 'custom_algorithm', 'private_algorithm', 'commercial_algorithm', 'licensed_algorithm'],
            'confidence': 0.7
        },
        AlgorithmType.PATENTED: {
            'keywords': ['patent', 'patented', 'patent_number', 'us_patent', 'european_patent', 'patent_application', 'patent_pending', 'patent_holder', 'patent_owner', 'patent_license', 'patent_royalty'],
            'patterns': ['patented_algorithm', 'patent_protected', 'patent_licensed', 'patent_royalty', 'patent_holder', 'patent_owner', 'patent_application', 'patent_pending'],
            'confidence': 0.8
        },
        AlgorithmType.COPYLEFT: {
            'keywords': ['copyleft', 'gpl', 'lgpl', 'agpl', 'cc_by_sa', 'free_software', 'open_source', 'foss', 'floss', 'viral_license', 'share_alike', 'reciprocal'],
            'patterns': ['copyleft_license', 'gpl_licensed', 'lgpl_licensed', 'agpl_licensed', 'free_software', 'open_source_software', 'foss_licensed', 'viral_license', 'share_alike_license'],
            'confidence': 0.8
        },
        AlgorithmType.OPEN_SOURCE: {
            'keywords': ['open_source', 'mit', 'apache', 'bsd', 'isc', 'cc0', 'unlicense', 'public_domain', 'permissive', 'free_software', 'foss', 'floss'],
            'patterns': ['open_source_license', 'mit_licensed', 'apache_licensed', 'bsd_licensed', 'isc_licensed', 'permissive_license', 'public_domain', 'free_software'],
            'confidence': 0.8
        },
        AlgorithmType.COMMERCIAL: {
            'keywords': ['commercial', 'enterprise', 'business', 'paid', 'licensed', 'subscription', 'proprietary', 'private', 'restricted', 'exclusive', 'tiered', 'premium'],
            'patterns': ['commercial_license', 'enterprise_license', 'business_license', 'paid_license', 'subscription_license', 'proprietary_license', 'restricted_license', 'exclusive_license'],
            'confidence': 0.7
        },
        AlgorithmType.EXPORT_CONTROLLED: {
            'keywords': ['strong_encryption', 'military_grade', 'government_classified', 'dual_use_technology', 'satellite_communication', 'export_controlled', 'classified_algorithm', 'military_algorithm', 'government_algorithm', 'restricted_technology'],
            'patterns': ['strong_encryption_implementation', 'military_grade_algorithm', 'government_classified_technique', 'dual_use_technology_implementation', 'satellite_communication_protocol', 'export_controlled_algorithm', 'classified_algorithm', 'military_algorithm'],
            'confidence': 0.8
        },
        AlgorithmType.ACADEMIC_RESEARCH: {
            'keywords': ['research_paper', 'university_developed', 'non_commercial', 'publication_restricted', 'academic_algorithm', 'research_algorithm', 'university_algorithm', 'academic_license', 'research_license', 'educational_use'],
            'patterns': ['research_paper_implementation', 'university_developed_algorithm', 'non_commercial_research', 'publication_restricted_implementation', 'academic_algorithm', 'research_algorithm', 'university_algorithm'],
            'confidence': 0.8
        },
        AlgorithmType.PROPRIETARY_SDK: {
            'keywords': ['intel_ipp', 'nvidia_cuda', 'microsoft_cryptographic', 'oracle_sun_proprietary', 'adobe_proprietary', 'apple_specific', 'google_specific', 'proprietary_sdk', 'vendor_specific', 'platform_specific', 'sdk_dependency'],
            'patterns': ['intel_ipp_implementation', 'nvidia_cuda_api', 'microsoft_cryptographic_api', 'oracle_sun_proprietary', 'adobe_proprietary_format', 'apple_specific_framework', 'google_specific_service', 'proprietary_sdk', 'vendor_specific_api'],
            'confidence': 0.8
        }
    }