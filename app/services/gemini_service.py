"""
Gemini AI Service for Image and Video Analysis
Uses Google Gemini API for vision tasks
"""
from typing import Optional, Dict, Any, List, TYPE_CHECKING, cast
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

if TYPE_CHECKING:
    from google.genai import types as types_module
else:
    types_module = types
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
        if genai is None or types_module is None:
            raise ValueError("google-genai package not installed. Run: pip install google-genai")
        
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not configured in environment variables")
        
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model_name = settings.gemini_model
        self.temperature = settings.gemini_temperature
        # Store types module as instance variable for use in other methods
        self.types = cast(Any, types_module)
    
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
                    self.types.Content(
                        role="user",
                        parts=[
                            self.types.Part(text=prompt),
                            self.types.Part(
                                inline_data=self.types.Blob(
                                    mime_type=file.content_type,
                                    data=content
                                )
                            )
                        ]
                    )
                ],
                config=self.types.GenerateContentConfig(
                    temperature=self.temperature
                )
            )
            
            # Extract text from response
            result_text = ""
            if hasattr(response, 'text'):
                result_text = response.text
            elif hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content is not None and hasattr(candidate.content, 'parts'):
                    parts_text = []
                    content_parts = cast(Any, candidate.content.parts)
                    for part in content_parts:
                        if hasattr(part, 'text'):
                            parts_text.append(part.text)
                    result_text = " ".join(parts_text)
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
                    self.types.Content(
                        role="user",
                        parts=[
                            self.types.Part(text=prompt),
                            self.types.Part(
                                inline_data=self.types.Blob(
                                    mime_type=file.content_type,
                                    data=content
                                )
                            )
                        ]
                    )
                ],
                config=self.types.GenerateContentConfig(
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
            parts = [self.types.Part(text=prompt)]
            for img_part in image_parts:
                parts.append(
                    self.types.Part(
                        inline_data=self.types.Blob(
                            mime_type=img_part["mime_type"],
                            data=img_part["data"]
                        )
                    )
                )
            
            # Generate response with new API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    self.types.Content(
                        role="user",
                        parts=parts
                    )
                ],
                config=self.types.GenerateContentConfig(
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
    
    async def ask_question(
        self,
        question: str
    ) -> Dict[str, Any]:
        """
        Ask a question to the AI assistant with topic restrictions
        
        Args:
            question: User's question
            
        Returns:
            Dict containing the answer
        """
        try:
            # System instruction for the assistant
            system_instruction = """Anda adalah asisten aplikasi "Program Bantuan Santri" yang dirancang khusus untuk membantu pengguna memahami berbagai aspek terkait santri, pesantren, dan program bantuan sosial.

**IDENTITAS ANDA:**
- Nama: Asisten Program Bantuan Santri
- Peran: Membantu memberikan informasi dan pengetahuan seputar dunia pesantren dan program bantuan

**TOPIK YANG BOLEH DIBAHAS:**
1. Santri dan kehidupan santri
2. Pesantren (sejarah, sistem pendidikan, kurikulum)
3. Nahdlatul Ulama (NU) dan organisasinya
4. Program bantuan sosial dan mekanismenya
5. Pengentasan kemiskinan dan program kesejahteraan
6. Kemiskinan dan solusinya
7. Pendidikan (formal dan non-formal, termasuk pendidikan pesantren)
8. Dakwah dan metode dakwah
9. Kitab kuning dan kajian kitab
10. Islam (ajaran, praktik ibadah, akhlak, muamalah)
11. Sejarah Islam dan perkembangannya
12. Sejarah pesantren di Indonesia
13. Sejarah Hari Santri (22 Oktober)
14. Hari Pahlawan dan pahlawan nasional
15. Nilai-nilai kearifan lokal dan tradisi pesantren

**TOPIK YANG DILARANG KERAS:**
1. Politik praktis dan kebijakan pemerintah yang kontroversial
2. Partai politik dan kampanye politik
3. Perbandingan agama atau debat antar agama
4. Konten yang memecah belah atau provokatif
5. Isu SARA yang sensitif

**CARA MERESPONS:**
- Jika pertanyaan sesuai topik: Berikan jawaban yang informatif, akurat, dan bermanfaat dengan bahasa yang sopan dan mudah dipahami
- Jika pertanyaan di luar topik: Dengan sopan arahkan pengguna kembali ke topik yang relevan dengan mengatakan: "Maaf, saya adalah asisten Program Bantuan Santri yang fokus pada topik santri, pesantren, pendidikan, dan bantuan sosial. Saya tidak dapat membahas topik [sebutkan topik yang ditanyakan]. Apakah ada yang ingin Anda tanyakan seputar santri, pesantren, atau program bantuan?"
- Jika pertanyaan terkait topik terlarang: Dengan tegas namun sopan tolak dengan mengatakan: "Maaf, saya tidak dapat membahas topik [politik/partai politik/perbandingan agama] karena di luar ruang lingkup asisten Program Bantuan Santri. Silakan ajukan pertanyaan seputar santri, pesantren, pendidikan, atau bantuan sosial."

**PRINSIP MENJAWAB:**
- Gunakan bahasa Indonesia yang baik dan benar
- Berikan jawaban yang objektif dan berdasarkan fakta
- Jika tidak yakin, akui keterbatasan pengetahuan
- Selalu hormati keberagaman dan hindari bias
- Fokus pada edukasi dan memberikan manfaat

Ingat: Tujuan Anda adalah membantu pengguna mendapatkan informasi bermanfaat seputar dunia santri dan pesantren untuk mendukung program bantuan sosial."""

            # Generate response with system instruction
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    self.types.Content(
                        role="user",
                        parts=[self.types.Part(text=question)]
                    )
                ],
                config=self.types.GenerateContentConfig(
                    temperature=self.temperature,
                    system_instruction=system_instruction
                )
            )
            
            # Extract text from response
            result_text = ""
            if hasattr(response, 'text'):
                result_text = response.text
            elif hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content is not None and hasattr(candidate.content, 'parts'):
                    parts_text = []
                    content_parts = cast(Any, candidate.content.parts)
                    for part in content_parts:
                        if hasattr(part, 'text'):
                            parts_text.append(part.text)
                    result_text = " ".join(parts_text)
            else:
                result_text = str(response)
            
            return {
                "success": True,
                "question": question,
                "answer": result_text,
                "model": settings.gemini_model
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing question: {str(e)}"
            )


# Create singleton instance
gemini_service = GeminiService()
