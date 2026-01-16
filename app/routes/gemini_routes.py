"""
Gemini AI Vision Analysis Routes
Endpoints for image and video analysis using Google Gemini
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, List
from app.services.gemini_service import gemini_service

router = APIRouter(prefix="/gemini", tags=["Gemini AI Vision"])


@router.post("/analyze/image", response_model=None)
async def analyze_image(
    file: UploadFile = File(..., description="Image file to analyze"),
    prompt: Optional[str] = Form(None, description="Custom analysis prompt")
):
    """
    Analyze a single image using Gemini Vision AI
    
    **Supported formats:** JPG, PNG, GIF, WEBP, BMP
    
    **Parameters:**
    - **file**: Image file (required)
    - **prompt**: Custom analysis prompt (optional)
    
    **Example prompts:**
    - "Describe the condition of this building"
    - "What objects are visible in this image?"
    - "Is this a residential or commercial property?"
    - "Analyze the cleanliness and maintenance of this facility"
    
    **Returns:** Detailed analysis of the image
    """
    try:
        result = await gemini_service.analyze_image(file, prompt)
        return {
            "status": "success",
            "data": result
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Configuration error: {str(e)}"
        )
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze image: {str(e)}\n{traceback.format_exc()}"
        )


@router.post("/analyze/video", response_model=None)
async def analyze_video(
    file: UploadFile = File(..., description="Video file to analyze"),
    prompt: Optional[str] = Form(None, description="Custom analysis prompt")
):
    """
    Analyze a video using Gemini Vision AI
    
    **Supported formats:** MP4, MOV, AVI, WEBM
    **Maximum size:** 20MB
    
    **Parameters:**
    - **file**: Video file (required)
    - **prompt**: Custom analysis prompt (optional)
    
    **Example prompts:**
    - "Describe what happens in this video"
    - "What activities are shown in this video?"
    - "Analyze the condition and quality of the facility shown"
    - "Identify any safety concerns or issues visible"
    
    **Returns:** Detailed analysis of the video content
    """
    try:
        result = await gemini_service.analyze_video(file, prompt)
        return {
            "status": "success",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze video: {str(e)}"
        )


@router.post("/analyze/multiple-images", response_model=None)
async def analyze_multiple_images(
    files: List[UploadFile] = File(..., description="Multiple image files to analyze"),
    prompt: Optional[str] = Form(None, description="Custom analysis prompt")
):
    """
    Analyze multiple images together using Gemini Vision AI
    
    **Supported formats:** JPG, PNG, GIF, WEBP, BMP
    **Maximum images:** 10 per request
    
    **Parameters:**
    - **files**: List of image files (required)
    - **prompt**: Custom analysis prompt (optional)
    
    **Use cases:**
    - Compare before/after photos
    - Analyze multiple angles of a facility
    - Compare conditions across different locations
    - Assess progress over time
    
    **Example prompts:**
    - "Compare the condition of these facilities"
    - "Identify common issues across these images"
    - "Which of these locations is in better condition?"
    - "Analyze the progression shown in these images"
    
    **Returns:** Comprehensive analysis across all images
    """
    try:
        result = await gemini_service.analyze_multiple_images(files, prompt)
        return {
            "status": "success",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze images: {str(e)}"
        )


@router.post("/ocr", response_model=None)
async def extract_text_from_image(
    file: UploadFile = File(..., description="Image file containing text")
):
    """
    Extract text from an image using Gemini Vision AI (OCR)
    
    **Supported formats:** JPG, PNG, GIF, WEBP, BMP
    
    **Use cases:**
    - Extract text from documents
    - Read signs or labels in photos
    - Digitize printed information
    - Extract data from forms or certificates
    
    **Parameters:**
    - **file**: Image file containing text (required)
    
    **Returns:** Extracted text from the image
    """
    try:
        result = await gemini_service.extract_text_from_image(file)
        return {
            "status": "success",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract text: {str(e)}"
        )


@router.get("/health", response_model=None)
async def gemini_health_check():
    """
    Check if Gemini AI service is configured properly
    
    **Returns:** Service status and configuration info
    """
    from app.core.config import settings
    
    return {
        "status": "ok",
        "service": "Gemini AI Vision",
        "configured": settings.gemini_api_key is not None,
        "model": settings.gemini_model,
        "temperature": settings.gemini_temperature
    }


@router.post("/analyze/pesantren-facility", response_model=None)
async def analyze_pesantren_facility(
    file: UploadFile = File(..., description="Image of pesantren facility")
):
    """
    Specialized analysis for pesantren facilities
    
    Analyzes images of pesantren buildings, facilities, and infrastructure
    with focus on condition, maintenance, and suitability for educational purposes.
    
    **Parameters:**
    - **file**: Image of pesantren facility (required)
    
    **Returns:** Detailed facility assessment
    """
    prompt = """Analyze this pesantren (Islamic boarding school) facility image. Provide:

1. **Facility Type Identification:**
   - What type of facility is shown? (classroom, dormitory, mosque, dining hall, bathroom, etc.)

2. **Condition Assessment:**
   - Overall physical condition (excellent, good, fair, poor)
   - Visible maintenance issues or damage
   - Cleanliness and hygiene level

3. **Infrastructure Quality:**
   - Building materials and construction quality
   - Structural integrity observations
   - Roof, walls, floors condition

4. **Capacity and Space:**
   - Approximate capacity/size
   - Space adequacy for intended use
   - Ventilation and lighting

5. **Safety and Compliance:**
   - Any safety concerns
   - Fire safety elements visible
   - Accessibility features

6. **Recommendations:**
   - Priority maintenance needs
   - Suggested improvements
   - Estimated urgency of repairs (if needed)

Provide a professional assessment suitable for facility management and planning."""
    
    try:
        result = await gemini_service.analyze_image(file, prompt)
        return {
            "status": "success",
            "data": result,
            "analysis_type": "pesantren_facility"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze facility: {str(e)}"
        )


@router.post("/analyze/santri-housing", response_model=None)
async def analyze_santri_housing(
    file: UploadFile = File(..., description="Image of santri housing")
):
    """
    Specialized analysis for santri (student) housing conditions
    
    Analyzes images of santri homes and living conditions with focus
    on socio-economic indicators and living standards.
    
    **Parameters:**
    - **file**: Image of santri housing (required)
    
    **Returns:** Housing condition assessment
    """
    prompt = """Analyze this santri (Islamic boarding school student) housing image. Provide:

1. **Housing Type:**
   - Type of dwelling (permanent house, semi-permanent, temporary)
   - Ownership status indicators (owned, rented, informal)

2. **Living Conditions:**
   - Overall condition rating (excellent, good, adequate, poor, critical)
   - Visible quality indicators
   - Maintenance level

3. **Infrastructure:**
   - Building materials (concrete, brick, wood, bamboo, etc.)
   - Roof condition and material
   - Wall and floor condition
   - Foundation assessment

4. **Basic Amenities Visible:**
   - Electricity access indicators
   - Water supply indicators
   - Sanitation facilities (if visible)
   - Ventilation and natural light

5. **Socio-Economic Indicators:**
   - Signs of poverty or economic hardship
   - Living standard assessment
   - Asset ownership indicators
   - General hygiene and cleanliness

6. **Recommendations:**
   - Priority needs for assistance
   - Suggested interventions
   - Urgency level (critical, high, moderate, low)

Provide an objective, respectful assessment suitable for social assistance program planning."""
    
    try:
        result = await gemini_service.analyze_image(file, prompt)
        return {
            "status": "success",
            "data": result,
            "analysis_type": "santri_housing"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze housing: {str(e)}"
        )
