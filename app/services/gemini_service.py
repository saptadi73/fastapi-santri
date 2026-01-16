"""
Gemini AI Service for Image and Video Analysis
Uses Google Gemini API for vision tasks
"""
from typing import Optional, Dict, Any, List
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None
from fastapi import UploadFile, HTTPException
import base64
from io import BytesIO
from PIL import Image
import mimetypes
from app.core.config import settings


class GeminiService:
    """Service for interacting with Gemini AI for vision analysis"""
    
    def __init__(self):
        """Initialize Gemini API with configuration"""
        if genai is None:
            raise ValueError("google-genai package not installed. Run: pip install google-genai")
        
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not configured in environment variables")
        
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model_name = settings.gemini_model
        self.temperature = settings.gemini_temperature
    
    async def analyze_image(
        self, 
        file: UploadFile, 
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze an image using Gemini Vision
        
        Args:
            file: Uploaded image file
            prompt: Custom prompt for analysis (optional)
            
        Returns:
            Dict containing analysis results
        """
        try:
            # Validate file type
            if not file.content_type or not file.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid file type: {file.content_type}. Only images are supported."
                )
            
            # Read file content
            content = await file.read()
            
            # Convert to PIL Image for validation and processing
            try:
                image = Image.open(BytesIO(content))
                # Optionally resize if image is too large
                max_size = (1024, 1024)
                if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                    image.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Convert back to bytes
                img_byte_arr = BytesIO()
                image.save(img_byte_arr, format=image.format or 'PNG')
                content = img_byte_arr.getvalue()
                
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to process image: {str(e)}"
                )
            
            # Default prompt if none provided
            if not prompt:
                prompt = """Analyze this image in detail. Provide:
1. A comprehensive description of what you see
2. Key objects, people, or elements present
3. The setting or context
4. Any text visible in the image
5. Overall quality and condition assessment"""
            
            # Generate response with new API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part(text=prompt),
                            types.Part(
                                inline_data=types.Blob(
                                    mime_type=file.content_type,
                                    data=content
                                )
                            )
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    temperature=self.temperature
                )
            )
            
            # Extract text from response
            result_text = ""
            if hasattr(response, 'text'):
                result_text = response.text
            elif hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    result_text = " ".join(part.text for part in candidate.content.parts if hasattr(part, 'text'))
            else:
                result_text = str(response)
            
            return {
                "success": True,
                "filename": file.filename,
                "analysis": result_text,
                "model": settings.gemini_model,
                "prompt_used": prompt
            }
            
        except HTTPException:
            raise
        except Exception as e:
            import traceback
            error_detail = f"Error analyzing image: {str(e)}\n{traceback.format_exc()}"
            raise HTTPException(
                status_code=500,
                detail=error_detail
            )
    
    async def analyze_video(
        self,
        file: UploadFile,
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a video using Gemini Vision
        
        Args:
            file: Uploaded video file
            prompt: Custom prompt for analysis (optional)
            
        Returns:
            Dict containing analysis results
        """
        try:
            # Validate file type
            if not file.content_type or not file.content_type.startswith('video/'):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type: {file.content_type}. Only videos are supported."
                )
            
            # Read file content
            content = await file.read()
            
            # Check file size (Gemini has limits, typically ~20MB for free tier)
            max_size = 20 * 1024 * 1024  # 20MB
            if len(content) > max_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"Video file too large. Maximum size is {max_size / (1024*1024)}MB"
                )
            
            # Default prompt if none provided
            if not prompt:
                prompt = """Analyze this video in detail. Provide:
1. A comprehensive description of what happens in the video
2. Key activities, people, or objects present
3. The setting and context
4. Timeline of major events or scenes
5. Any text, signs, or important visual information
6. Overall quality and condition assessment"""
            
            # Generate response with new API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part(text=prompt),
                            types.Part(
                                inline_data=types.Blob(
                                    mime_type=file.content_type,
                                    data=content
                                )
                            )
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    temperature=self.temperature
                )
            )
            
            return {
                "success": True,
                "filename": file.filename,
                "analysis": response.text,
                "model": settings.gemini_model,
                "prompt_used": prompt
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error analyzing video: {str(e)}"
            )
    
    async def analyze_multiple_images(
        self,
        files: List[UploadFile],
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze multiple images together
        
        Args:
            files: List of uploaded image files
            prompt: Custom prompt for analysis (optional)
            
        Returns:
            Dict containing analysis results
        """
        try:
            if not files:
                raise HTTPException(
                    status_code=400,
                    detail="No files provided"
                )
            
            if len(files) > 10:
                raise HTTPException(
                    status_code=400,
                    detail="Maximum 10 images can be analyzed at once"
                )
            
            # Prepare all images
            image_parts = []
            filenames = []
            
            for file in files:
                # Validate file type
                if not file.content_type or not file.content_type.startswith('image/'):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid file type for {file.filename}: {file.content_type}"
                    )
                
                content = await file.read()
                
                # Process image
                try:
                    image = Image.open(BytesIO(content))
                    max_size = (800, 800)
                    if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                        image.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    img_byte_arr = BytesIO()
                    image.save(img_byte_arr, format=image.format or 'PNG')
                    content = img_byte_arr.getvalue()
                except Exception as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Failed to process {file.filename}: {str(e)}"
                    )
                
                image_parts.append({
                    "mime_type": file.content_type,
                    "data": content
                })
                filenames.append(file.filename)
            
            # Default prompt if none provided
            if not prompt:
                prompt = f"""Analyze these {len(files)} images together. Provide:
1. A description of each image
2. Common themes or patterns across the images
3. Differences or contrasts between the images
4. Overall assessment and insights
5. Any recommendations or observations"""
            
            # Build parts list with prompt and all images
            parts = [types.Part(text=prompt)]
            for img_part in image_parts:
                parts.append(
                    types.Part(
                        inline_data=types.Blob(
                            mime_type=img_part["mime_type"],
                            data=img_part["data"]
                        )
                    )
                )
            
            # Generate response with new API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Content(
                        role="user",
                        parts=parts
                    )
                ],
                config=types.GenerateContentConfig(
                    temperature=self.temperature
                )
            )
            
            return {
                "success": True,
                "filenames": filenames,
                "image_count": len(files),
                "analysis": response.text,
                "model": settings.gemini_model,
                "prompt_used": prompt
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error analyzing images: {str(e)}"
            )
    
    async def extract_text_from_image(
        self,
        file: UploadFile
    ) -> Dict[str, Any]:
        """
        Extract text from an image (OCR)
        
        Args:
            file: Uploaded image file
            
        Returns:
            Dict containing extracted text
        """
        prompt = """Extract all text visible in this image. 
Provide the text exactly as it appears, maintaining formatting where possible.
If there is no text, state "No text detected"."""
        
        return await self.analyze_image(file, prompt)


# Create singleton instance
gemini_service = GeminiService()
