# Models Directory

This directory contains ML model files required for the application.

## Silero VAD Model

**File:** `silero_vad.onnx`  
**Purpose:** Voice Activity Detection (VAD) using Silero ONNX model  
**Source:** https://github.com/snakers4/silero-vad  
**License:** MIT

### Usage

The model is automatically loaded by `VADProcessor` on application startup.

### Download

If the model file is missing, download it:

```bash
curl -L https://github.com/snakers4/silero-vad/raw/master/files/silero_vad.onnx \
    -o models/silero_vad.onnx
```

Or it will be downloaded automatically during Docker build.
