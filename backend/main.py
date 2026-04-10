from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI(
    title="Government Scheme Matchmaker API",
    description="RAG-based API that matches farmers to government schemes based on their profile.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "message": "Government Scheme Matchmaker API is running.",
        "docs": "/docs",
    }


# Fallback for router prefix issues
@app.post("/api/v1/analyze-hsi")
@app.post("/api/v1/analyze-hsi/")
async def analyze_hsi_fallback(file: UploadFile = File(...)):
    from rag.hsi_processor import analyze_hsi_cube
    import numpy as np
    import io
    contents = await file.read()
    X = np.load(io.BytesIO(contents))
    result, error = analyze_hsi_cube(X)
    if error:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=error)
    return result
