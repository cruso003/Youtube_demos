"""
Vision Processing Service
Integrates OpenAI Vision API for image analysis capabilities
"""

import os
import base64
import logging
import asyncio
from typing import Dict, Any, Optional, List
import json
from PIL import Image
import io

logger = logging.getLogger(__name__)

class VisionService:
    """Service for vision processing using OpenAI Vision API"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY not found. Vision processing will be disabled.")
    
    async def analyze_image(self, image_data: bytes, adapter_instructions: str = None, image_format: str = "jpeg") -> Dict[str, Any]:
        """
        Analyze image using OpenAI Vision API
        
        Args:
            image_data: Raw image bytes
            adapter_instructions: Custom instructions from business logic adapter
            image_format: Image format (jpeg, png, etc.)
            
        Returns:
            Dict with analysis results
        """
        try:
            if not self.openai_api_key:
                return {
                    "success": False,
                    "error": "OpenAI API key not configured",
                    "analysis": ""
                }
            
            # Process image data
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Default instructions if none provided by adapter
            if not adapter_instructions:
                adapter_instructions = """Analyze this image and provide a detailed description. 
                Include any relevant details about objects, people, text, scenes, or activities visible in the image."""
            
            try:
                import openai
                
                # Initialize OpenAI client
                client = openai.OpenAI(api_key=self.openai_api_key)
                
                # Prepare the message for vision analysis
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": adapter_instructions
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/{image_format};base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ]
                
                # Call OpenAI Vision API
                response = await asyncio.to_thread(
                    client.chat.completions.create,
                    model="gpt-4o",  # GPT-4 with vision capabilities
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7
                )
                
                # Extract analysis
                if response.choices and len(response.choices) > 0:
                    analysis = response.choices[0].message.content
                    
                    return {
                        "success": True,
                        "analysis": analysis,
                        "model": "gpt-4o",
                        "usage": {
                            "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                            "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                            "total_tokens": response.usage.total_tokens if response.usage else 0
                        },
                        "error": None
                    }
                else:
                    return {
                        "success": False,
                        "analysis": "",
                        "error": "No analysis result received from OpenAI"
                    }
                    
            except ImportError:
                logger.warning("OpenAI SDK not available. Using mock vision analysis.")
                # Mock vision analysis for testing
                return {
                    "success": True,
                    "analysis": f"[Mock Vision Analysis - OpenAI SDK not installed]\nAdapter Instructions: {adapter_instructions}\nImage format: {image_format}",
                    "model": "gpt-4o-mock",
                    "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
                    "error": None,
                    "mock": True
                }
                
        except Exception as e:
            logger.error(f"Vision analysis error: {e}")
            return {
                "success": False,
                "analysis": "",
                "error": str(e)
            }
    
    async def process_image_upload(self, image_data: bytes, session_id: str, adapter_instructions: str = None) -> Dict[str, Any]:
        """
        Process uploaded image for a specific session
        
        Args:
            image_data: Raw image bytes
            session_id: Session identifier
            adapter_instructions: Custom instructions from business adapter
            
        Returns:
            Dict with processing results including analysis and session context
        """
        try:
            # Validate image data
            validation_result = self._validate_image(image_data)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"Invalid image: {validation_result['error']}",
                    "analysis": ""
                }
            
            # Analyze image
            analysis_result = await self.analyze_image(
                image_data, 
                adapter_instructions, 
                validation_result["format"]
            )
            
            if analysis_result["success"]:
                # Add session context
                return {
                    "success": True,
                    "session_id": session_id,
                    "image_analysis": analysis_result["analysis"],
                    "image_format": validation_result["format"],
                    "image_size": validation_result["size"],
                    "processing_time": analysis_result.get("processing_time", 0),
                    "usage": analysis_result.get("usage", {}),
                    "ready_for_conversation": True,
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "session_id": session_id,
                    "error": analysis_result["error"],
                    "analysis": ""
                }
                
        except Exception as e:
            logger.error(f"Image upload processing error: {e}")
            return {
                "success": False,
                "session_id": session_id,
                "error": str(e),
                "analysis": ""
            }
    
    def _validate_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Validate image data and extract metadata
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dict with validation results
        """
        try:
            # Check file size (limit to 20MB)
            max_size = 20 * 1024 * 1024  # 20MB
            if len(image_data) > max_size:
                return {
                    "valid": False,
                    "error": f"Image too large: {len(image_data)} bytes (max: {max_size})",
                    "format": None,
                    "size": None
                }
            
            # Try to open with PIL to validate format
            try:
                image = Image.open(io.BytesIO(image_data))
                image_format = image.format.lower() if image.format else "unknown"
                image_size = image.size
                
                # Check supported formats
                supported_formats = ["jpeg", "jpg", "png", "gif", "bmp", "webp"]
                if image_format not in supported_formats:
                    return {
                        "valid": False,
                        "error": f"Unsupported format: {image_format}",
                        "format": image_format,
                        "size": image_size
                    }
                
                return {
                    "valid": True,
                    "error": None,
                    "format": image_format,
                    "size": image_size,
                    "bytes": len(image_data)
                }
                
            except Exception as pil_error:
                return {
                    "valid": False,
                    "error": f"Invalid image data: {pil_error}",
                    "format": None,
                    "size": None
                }
                
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {e}",
                "format": None,
                "size": None
            }
    
    async def extract_text_from_image(self, image_data: bytes, language: str = "en") -> Dict[str, Any]:
        """
        Extract text from image using OCR capabilities
        
        Args:
            image_data: Raw image bytes
            language: Target language for OCR
            
        Returns:
            Dict with extracted text
        """
        try:
            # Use OpenAI Vision for text extraction
            text_extraction_prompt = f"""Extract all visible text from this image. 
            If the text appears to be in {language}, provide the original text and a translation if needed.
            Format the response as:
            
            EXTRACTED TEXT:
            [text content here]
            
            If there's no readable text, respond with "No readable text found."
            """
            
            result = await self.analyze_image(image_data, text_extraction_prompt)
            
            if result["success"]:
                return {
                    "success": True,
                    "extracted_text": result["analysis"],
                    "language": language,
                    "method": "openai_vision",
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "extracted_text": "",
                    "error": result["error"]
                }
                
        except Exception as e:
            logger.error(f"Text extraction error: {e}")
            return {
                "success": False,
                "extracted_text": "",
                "error": str(e)
            }

# Global vision service instance
_vision_service = None

def get_vision_service() -> VisionService:
    """Get the global vision service instance"""
    global _vision_service
    if _vision_service is None:
        _vision_service = VisionService()
    return _vision_service