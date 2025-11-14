"""
Thai TTS REST API - Simple REST API wrapper for Thai Text-to-Speech

This module provides a REST API for Thai TTS operations with the following features:
- Text-to-speech synthesis
- Voice cloning from reference audio
- Batch processing
- Real-time streaming
- Voice style transfer
- Thai text preprocessing

API Endpoints:
- POST /tts/synthesize - Synthesize speech from text
- POST /tts/clone - Clone voice from reference audio
- POST /tts/batch - Batch process multiple texts
- POST /tts/stream - Stream TTS audio
- GET /tts/models - List available models
- GET /tts/health - Health check
- GET /tts/info - API information
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import torch
import soundfile as sf
import numpy as np
import io
import os
import sys
import json
import time
import uuid
import logging
from datetime import datetime
from pathlib import Path

# Add TTS to path
try:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from TTS.api import TTS
    from TTS.utils.generic_utils import get_user_data_dir
    import pythainlp
    from pythainlp.util import normalize as normalize_thai
    THAI_TTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Thai TTS libraries not available: {e}")
    THAI_TTS_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Thai TTS API",
    description="Simple REST API for Thai Text-to-Speech synthesis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global TTS instance
tts_engine = None
device = "cpu"

# Request/Response Models
class TTSRequest(BaseModel):
    text: str = Field(..., description="Thai text to synthesize", example="สวัสดีครับ")
    language: str = Field(default="th", description="Language code", example="th")
    speed: float = Field(default=1.0, description="Speech speed multiplier", example=1.0)
    output_format: str = Field(default="wav", description="Output audio format", example="wav")

class TTSResponse(BaseModel):
    success: bool
    audio_url: Optional[str] = None
    duration: Optional[float] = None
    message: str
    processing_time: float

class CloneRequest(BaseModel):
    texts: List[str] = Field(..., description="List of Thai texts to synthesize")
    language: str = Field(default="th", description="Language code")
    output_format: str = Field(default="wav", description="Output audio format")

class CloneResponse(BaseModel):
    success: bool
    audio_files: List[str]
    message: str
    processing_time: float

class BatchRequest(BaseModel):
    texts: List[str] = Field(..., description="List of Thai texts to process")
    language: str = Field(default="th", description="Language code")
    output_format: str = Field(default="wav", description="Output audio format")

class BatchResponse(BaseModel):
    success: bool
    results: List[Dict[str, Any]]
    message: str
    processing_time: float

class StreamRequest(BaseModel):
    text: str = Field(..., description="Thai text to stream")
    language: str = Field(default="th", description="Language code")
    chunk_size: int = Field(default=1024, description="Audio chunk size")

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    thai_tts_available: bool
    device: str
    model_loaded: bool

class InfoResponse(BaseModel):
    name: str
    version: str
    description: str
    features: List[str]
    endpoints: List[str]

# Helper functions
def setup_tts() -> bool:
    """Setup TTS engine"""
    global tts_engine, device
    
    try:
        if not THAI_TTS_AVAILABLE:
            logger.error("Thai TTS libraries not available")
            return False
        
        # Check device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")
        
        # Load TTS model
        model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        logger.info(f"Loading TTS model: {model_name}")
        
        tts_engine = TTS(model_name).to(device)
        logger.info("TTS engine loaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to setup TTS: {e}")
        return False

def preprocess_thai_text(text: str) -> str:
    """Preprocess Thai text for TTS"""
    try:
        return normalize_thai(text)
    except Exception as e:
        logger.warning(f"Failed to preprocess Thai text: {e}")
        return text

def generate_audio(text: str, language: str = "th", speaker_wav: Optional[str] = None) -> np.ndarray:
    """Generate audio from text"""
    if tts_engine is None:
        raise RuntimeError("TTS engine not initialized")
    
    # Preprocess text
    processed_text = preprocess_thai_text(text)
    
    # Generate audio
    audio = tts_engine.tts(
        text=processed_text,
        speaker_wav=speaker_wav,
        language=language
    )
    
    # Convert to numpy
    if isinstance(audio, torch.Tensor):
        audio = audio.cpu().numpy()
    
    return audio

def create_audio_response(audio_data: np.ndarray, format: str = "wav") -> io.BytesIO:
    """Create audio response from numpy array"""
    audio_buffer = io.BytesIO()
    
    if format.lower() == "wav":
        sf.write(audio_buffer, audio_data, 22050, format='WAV')
    else:
        sf.write(audio_buffer, audio_data, 22050, format=format.upper())
    
    audio_buffer.seek(0)
    return audio_buffer

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize TTS engine on startup"""
    logger.info("Starting Thai TTS API...")
    if setup_tts():
        logger.info("Thai TTS API started successfully")
    else:
        logger.warning("Thai TTS API started without TTS engine")

# API Endpoints
@app.get("/", response_model=InfoResponse)
async def root():
    """API information"""
    return InfoResponse(
        name="Thai TTS API",
        version="1.0.0",
        description="Simple REST API for Thai Text-to-Speech synthesis",
        features=[
            "Text-to-speech synthesis",
            "Voice cloning",
            "Batch processing",
            "Real-time streaming",
            "Thai text preprocessing",
            "Multiple output formats"
        ],
        endpoints=[
            "POST /tts/synthesize",
            "POST /tts/clone",
            "POST /tts/batch",
            "POST /tts/stream",
            "GET /tts/models",
            "GET /tts/health",
            "GET /",
            "GET /docs"
        ]
    )

@app.get("/tts/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if tts_engine is not None else "unhealthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        thai_tts_available=THAI_TTS_AVAILABLE,
        device=device,
        model_loaded=tts_engine is not None
    )

@app.get("/tts/models")
async def list_models():
    """List available TTS models"""
    try:
        if tts_engine:
            available_models = TTS.list_models()
            return {
                "success": True,
                "models": available_models[:20],  # Limit to first 20 models
                "current_model": "tts_models/multilingual/multi-dataset/xtts_v2"
            }
        else:
            return {
                "success": False,
                "error": "TTS engine not initialized",
                "models": []
            }
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tts/synthesize")
async def synthesize_speech(request: TTSRequest):
    """Synthesize speech from text"""
    try:
        start_time = time.time()
        
        # Generate audio
        audio_data = generate_audio(
            text=request.text,
            language=request.language
        )
        
        # Calculate duration
        duration = len(audio_data) / 22050
        processing_time = time.time() - start_time
        
        # Create audio response
        audio_buffer = create_audio_response(audio_data, request.output_format)
        
        logger.info(f"Synthesized audio: {duration:.2f}s in {processing_time:.2f}s")
        
        # Return audio file
        return StreamingResponse(
            audio_buffer,
            media_type=f"audio/{request.output_format}",
            headers={
                "Content-Disposition": f"attachment; filename=synthesized_{int(time.time())}.{request.output_format}",
                "X-Duration": str(duration),
                "X-Processing-Time": str(processing_time)
            }
        )
        
    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {str(e)}")

@app.post("/tts/synthesize-with-response")
async def synthesize_speech_with_response(request: TTSRequest):
    """Synthesize speech and return JSON response with audio URL"""
    try:
        start_time = time.time()
        
        # Generate audio
        audio_data = generate_audio(
            text=request.text,
            language=request.language
        )
        
        # Calculate duration
        duration = len(audio_data) / 22050
        processing_time = time.time() - start_time
        
        # Save to temporary file
        temp_id = str(uuid.uuid4())
        temp_file = f"temp_{temp_id}.wav"
        sf.write(temp_file, audio_data, 22050)
        
        logger.info(f"Synthesized audio: {duration:.2f}s in {processing_time:.2f}s")
        
        return TTSResponse(
            success=True,
            audio_url=f"/audio/{temp_id}",
            duration=duration,
            message="Speech synthesized successfully",
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        return TTSResponse(
            success=False,
            message=f"Synthesis failed: {str(e)}",
            processing_time=time.time() - start_time
        )

@app.post("/tts/clone")
async def clone_voice(
    reference_audio: UploadFile = File(...),
    texts: str = Form(...),
    language: str = Form("th"),
    output_format: str = Form("wav")
):
    """Clone voice from reference audio"""
    try:
        start_time = time.time()
        
        # Parse texts
        try:
            text_list = json.loads(texts)
            if not isinstance(text_list, list):
                raise ValueError("Texts must be a list")
        except json.JSONDecodeError:
            # Try as comma-separated string
            text_list = [t.strip() for t in texts.split(",") if t.strip()]
        
        # Save reference audio temporarily
        ref_id = str(uuid.uuid4())
        ref_file = f"ref_{ref_id}.wav"
        
        content = await reference_audio.read()
        with open(ref_file, "wb") as f:
            f.write(content)
        
        # Process each text
        audio_files = []
        results = []
        
        for i, text in enumerate(text_list):
            try:
                # Generate audio
                audio_data = generate_audio(
                    text=text,
                    language=language,
                    speaker_wav=ref_file
                )
                
                # Save audio
                audio_id = str(uuid.uuid4())
                audio_file = f"cloned_{audio_id}.wav"
                sf.write(audio_file, audio_data, 22050)
                
                audio_files.append(audio_file)
                results.append({
                    "text": text,
                    "audio_file": audio_file,
                    "success": True
                })
                
            except Exception as e:
                results.append({
                    "text": text,
                    "success": False,
                    "error": str(e)
                })
        
        # Cleanup reference file
        if os.path.exists(ref_file):
            os.remove(ref_file)
        
        processing_time = time.time() - start_time
        
        successful = sum(1 for r in results if r["success"])
        logger.info(f"Voice cloning complete: {successful}/{len(text_list)} successful in {processing_time:.2f}s")
        
        return CloneResponse(
            success=successful > 0,
            audio_files=audio_files,
            message=f"Voice cloning complete: {successful}/{len(text_list)} successful",
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Voice cloning failed: {e}")
        raise HTTPException(status_code=500, detail=f"Voice cloning failed: {str(e)}")

@app.post("/tts/batch")
async def batch_process(request: BatchRequest):
    """Batch process multiple texts"""
    try:
        start_time = time.time()
        
        results = []
        audio_files = []
        
        for i, text in enumerate(request.texts):
            try:
                # Generate audio
                audio_data = generate_audio(
                    text=text,
                    language=request.language
                )
                
                # Save audio
                audio_id = str(uuid.uuid4())
                audio_file = f"batch_{i}_{audio_id}.wav"
                sf.write(audio_file, audio_data, 22050)
                
                duration = len(audio_data) / 22050
                
                results.append({
                    "index": i,
                    "text": text,
                    "audio_file": audio_file,
                    "duration": duration,
                    "success": True
                })
                
                audio_files.append(audio_file)
                
            except Exception as e:
                results.append({
                    "index": i,
                    "text": text,
                    "success": False,
                    "error": str(e)
                })
        
        processing_time = time.time() - start_time
        successful = sum(1 for r in results if r["success"])
        
        logger.info(f"Batch processing complete: {successful}/{len(request.texts)} successful in {processing_time:.2f}s")
        
        return BatchResponse(
            success=successful > 0,
            results=results,
            message=f"Batch processing complete: {successful}/{len(request.texts)} successful",
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")

@app.post("/tts/stream")
async def stream_tts(request: StreamRequest):
    """Stream TTS audio in real-time"""
    try:
        def audio_streamer():
            """Stream audio in chunks"""
            # Generate audio
            audio_data = generate_audio(
                text=request.text,
                language=request.language
            )
            
            # Convert to bytes and stream in chunks
            audio_buffer = io.BytesIO()
            sf.write(audio_buffer, audio_data, 22050, format='WAV')
            audio_buffer.seek(0)
            
            # Stream in chunks
            while True:
                chunk = audio_buffer.read(request.chunk_size)
                if not chunk:
                    break
                yield chunk
        
        return StreamingResponse(
            audio_streamer(),
            media_type="audio/wav",
            headers={
                "Cache-Control": "no-cache",
                "X-Text": request.text,
                "X-Language": request.language
            }
        )
        
    except Exception as e:
        logger.error(f"Streaming failed: {e}")
        raise HTTPException(status_code=500, detail=f"Streaming failed: {str(e)}")

@app.get("/audio/{audio_id}")
async def get_audio_file(audio_id: str):
    """Get audio file by ID"""
    temp_file = f"temp_{audio_id}.wav"
    if os.path.exists(temp_file):
        return FileResponse(
            temp_file,
            media_type="audio/wav",
            headers={"Cache-Control": "no-cache"}
        )
    else:
        raise HTTPException(status_code=404, detail="Audio file not found")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Not found", "status": 404}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal error: {exc}")
    return {"error": "Internal server error", "status": 500}

if __name__ == "__main__":
    import uvicorn
    
    # Setup TTS before starting server
    if setup_tts():
        logger.info("Starting Thai TTS API server...")
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000,
            log_level="info"
        )
    else:
        logger.error("Failed to setup TTS engine. Cannot start server.")
        sys.exit(1)