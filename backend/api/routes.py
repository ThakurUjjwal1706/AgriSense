from fastapi import APIRouter, HTTPException, File, UploadFile
from api.models import (
    MatchRequest, MatchResponse, ChatRequest, ChatResponse,
    TreatmentPlanRequest, TreatmentPlanResponse, VisionAnalysisResponse,
    CropYieldRequest, CropYieldResponse, HSIAnalysisResponse,
    DiseasePredictionResponse
)
from rag.retriever import match_schemes, ask_ai_question, generate_treatment_plan, analyze_crop_image
from rag.yield_predictor import predict_crop_yield
from rag.hsi_processor import analyze_hsi_cube
from rag.embedder import initialise
from services.tflite_predictor import predict_disease, get_predictor

router = APIRouter()


@router.post("/match", response_model=MatchResponse, summary="Match farmer to government schemes")
async def match_farmer_to_schemes(request: MatchRequest):
    """
    Given a farmer's profile, returns:
    - Top matched government schemes with eligibility & application steps
    - An AI-generated summary (Ollama if available, else rule-based)
    - Curated Google search links for further research
    """
    try:
        result = match_schemes(
            crop_type=request.crop_type,
            location=request.location,
            land_size_acres=request.land_size_acres,
            disease_or_yield_status=request.disease_or_yield_status,
            top_k=request.top_k,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ChatResponse, summary="Ask general farming or scheme questions")
async def general_farming_chat(request: ChatRequest):
    """
    General-purpose AI assistant specifically for:
    - Farming crop government schemes
    - Minimum Support Price (MSP)
    - Agricultural subsidies, insurance, and support
    """
    try:
        result = ask_ai_question(message=request.message, context=request.context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/treatment-plan", response_model=TreatmentPlanResponse, summary="Generate a recovery schedule for a crop disease")
async def get_treatment_plan(request: TreatmentPlanRequest):
    """
    Dedicated endpoint to generate a personalized recovery schedule (prescription)
    for a specific crop and disease/health status.
    """
    try:
        plan = generate_treatment_plan(crop_type=request.crop_type, disease_info=request.disease_info)
        if not plan:
            raise HTTPException(status_code=500, detail="Failed to generate treatment plan.")
        return {
            "treatment_plan": plan,
            "crop_type": request.crop_type,
            "disease_info": request.disease_info,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-leaf", response_model=VisionAnalysisResponse, summary="Analyze a leaf photo to describe disease/pest issues")
async def analyze_leaf_photo(file: UploadFile = File(...)):
    """
    Upload a photo of a crop/leaf to get a visual explanation of the detected issues.
    This provides a TFLite-powered primary diagnosis enriched with Gemini/Ollama explanation.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

    try:
        image_bytes = await file.read()

        # Run TFLite fast inference first
        tflite_label, tflite_conf = None, None
        try:
            predictor = get_predictor()
            if predictor.is_ready:
                tflite_label, tflite_conf = predict_disease(image_bytes)
        except Exception as tfe:
            print(f"[TFLite] Non-critical inference error on /analyze-leaf: {tfe}")

        # Primary Gemini/Ollama vision analysis (rich contextual output)
        result = analyze_crop_image(image_bytes=image_bytes, mime_type=file.content_type)

        # Enrich response with TFLite fields if available
        if tflite_label:
            result["tflite_disease"] = tflite_label
            result["tflite_confidence"] = tflite_conf
            # Override most_probable_disease with TFLite result when confidence is high
            if tflite_conf and tflite_conf >= 0.70:
                result["most_probable_disease"] = tflite_label.replace("___", " — ").replace("_", " ")

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict-disease", response_model=DiseasePredictionResponse, summary="TFLite-powered plant disease detection with AI explanation")
async def predict_plant_disease(file: UploadFile = File(...)):
    """
    Primary ML Disease Detection Endpoint.

    **Pipeline:**
    1. Validates uploaded image
    2. Runs TFLite 3D-CNN model for fast, accurate disease classification
    3. Passes predicted label to Ollama/Gemini for expert agronomic explanation
    4. Returns structured result with disease, confidence, and treatment advice

    **Designed for:** Flutter mobile app & farmers needing instant, offline-capable diagnosis.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a valid image (JPEG/PNG).")

    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Uploaded image file is empty.")
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read uploaded file.")

    # ── Step 1: TFLite Inference ─────────────────────────────────────────
    try:
        label, confidence = predict_disease(image_bytes)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=f"ML model not available: {str(e)}")
    except (ValueError, IndexError) as e:
        raise HTTPException(status_code=422, detail=f"Image processing error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")

    # ── Step 2: Parse Label ───────────────────────────────────────────────
    # Labels format: "Tomato___Early_blight" or "Corn_(maize)___healthy"
    parts = label.split("___", 1)
    crop_name = parts[0].replace("_", " ").replace("(", "").replace(")", "").strip()
    disease_name = parts[1].replace("_", " ").strip() if len(parts) > 1 else label
    is_healthy = "healthy" in disease_name.lower()
    human_label = f"{crop_name} — {disease_name}" if not is_healthy else f"{crop_name} (Healthy)"

    # ── Step 3: NDVI Score ────────────────────────────────────────────────
    from rag.retriever import calculate_pseudo_ndvi
    ndvi_score = calculate_pseudo_ndvi(image_bytes)

    # ── Step 4: AI Explanation via Ollama ─────────────────────────────────
    from rag.retriever import _ollama_chat_completion
    import textwrap

    if is_healthy:
        advice_prompt = [
            {"role": "system", "content": "You are an expert agronomist. Be concise and encouraging."},
            {"role": "user", "content": (
                f"A TFLite model classified the uploaded plant image as: '{human_label}' "
                f"(confidence: {confidence:.0%}). The plant appears healthy. "
                "Give 2-3 short tips to maintain optimal crop health for this plant type."
            )}
        ]
    else:
        advice_prompt = [
            {"role": "system", "content": (
                "You are a professional plant pathologist and agronomist. "
                "Provide structured, actionable diagnostic advice for farmers."
            )},
            {"role": "user", "content": textwrap.dedent(f"""
                A TFLite computer vision model has classified the uploaded leaf image as:
                Disease: {human_label}
                Model Confidence: {confidence:.0%}

                Please provide:
                1. A brief description of this disease (1-2 sentences)
                2. Key visible symptoms farmers should look for
                3. Recommended chemical or organic treatment steps
                4. Preventive measures for next season

                Keep it practical and farmer-friendly. Use simple language.
            """).strip()}
        ]

    try:
        advice = _ollama_chat_completion(advice_prompt, temperature=0.3)
        if not advice:
            advice = (
                f"Detected: {human_label} (confidence: {confidence:.0%}). "
                "For detailed treatment advice, consult your local agricultural extension officer "
                "or visit the Krishi Vigyan Kendra (KVK) in your district."
            )
    except Exception as ai_err:
        print(f"[predict-disease] Ollama explanation failed: {ai_err}")
        advice = (
            f"AI diagnosis complete: {human_label} (confidence: {confidence:.0%}). "
            "AI explanation is temporarily unavailable. Contact your local agriculture office."
        )

    return {
        "disease": human_label,
        "confidence": confidence,
        "advice": advice,
        "crop": crop_name,
        "is_healthy": is_healthy,
        "ndvi_score": ndvi_score,
    }


@router.post("/predict-yield", response_model=CropYieldResponse, summary="Predict crop yield based on climate, soil, and fertilizer data")
async def get_crop_yield_prediction(data: CropYieldRequest):
    """Predict crop yield based on climate, soil, and fertilizer data."""
    try:
        data_dict = data.dict()
        
        rf1 = data_dict.pop("Annual_rainfall", None)
        rf2 = data_dict.pop("Annual_rainfail", None)
        actual_rf = rf1 if rf1 is not None else (rf2 if rf2 is not None else 0.0)
        data_dict["Annual_rainfail"] = actual_rf
            
        result = predict_crop_yield(data_dict)

        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])

        base_yield = result["predicted_yield_tonnes_per_ha"]
        real_yield = base_yield * data.ndvi_score

        return {
            "status": result["status"],
            "predicted_yield_tonnes_per_ha": round(real_yield, 2),
            "inputs_received": data.dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hsi-ping", summary="Ping the HSI module")
async def ping_hsi():
    return {"message": "HSI module is active"}


@router.post("/analyze-hsi", response_model=HSIAnalysisResponse, summary="Analyze a hyperspectral .npy cube to generate a health map")
@router.post("/analyze-hsi/", response_model=HSIAnalysisResponse)
@router.post("/analyze_hsi", response_model=HSIAnalysisResponse)
@router.post("/analyze_hsi/", response_model=HSIAnalysisResponse)
async def analyze_hsi_hypercube(file: UploadFile = File(...)):
    """
    Upload a .npy file (hyperspectral cube) to get a health-mapped PNG image.
    Helps in detecting early-stage stress invisible to the naked eye.
    """
    if not file.filename.endswith(".npy"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a .npy hyperspectral cube.")

    try:
        import numpy as np
        import io
        contents = await file.read()
        X = np.load(io.BytesIO(contents))
        
        result, error = analyze_hsi_cube(X)
        if error:
            raise HTTPException(status_code=500, detail=error)
            
        return result
    except Exception as e:
        print(f"[HSI API Error] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schemes", summary="List all available schemes")
async def list_all_schemes():
    """Returns every scheme in the knowledge base (without embeddings)."""
    import json
    from pathlib import Path

    data_path = Path(__file__).parent.parent / "data.json"
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {
        "total": len(data["schemes"]),
        "ministry": data.get("ministry"),
        "source": data.get("source"),
        "schemes": data["schemes"],
    }


@router.get("/health", summary="Health check")
async def health():
    return {"status": "ok"}
