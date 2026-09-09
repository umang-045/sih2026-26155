from fastapi import FastAPI, UploadFile, File, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
import traceback
import os

from app.parser import extract_normalized_features, save_mapping
from app.reporter import generate_pdf_report

app = FastAPI(title="AI-Augmented Multi-Vendor Compliance Auditor")

OPA_URL = "http://localhost:8181/v1/data/network/compliance/deny"

# Mount static files directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(static_dir, "index.html"))

class TrainRequest(BaseModel):
    vendor: str
    feature_key: str
    cli_pattern: str

@app.post("/audit")
async def audit_config(file: UploadFile = File(...)):
    try:
        content = await file.read()
        normalized_data = extract_normalized_features(content, file.filename)
        
        opa_response = requests.post(OPA_URL, json={"input": normalized_data})
        opa_result = opa_response.json()
        violations = opa_result.get("result", [])
        
        return {
            "filename": file.filename,
            "hostname": normalized_data["hostname"],
            "status": "NON_COMPLIANT" if violations else "COMPLIANT",
            "violation_count": len(violations),
            "violations": violations,
            "extracted_metadata": normalized_data
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/audit/pdf")
async def audit_config_pdf(file: UploadFile = File(...)):
    try:
        content = await file.read()
        normalized_data = extract_normalized_features(content, file.filename)
        
        opa_response = requests.post(OPA_URL, json={"input": normalized_data})
        opa_result = opa_response.json()
        violations = opa_result.get("result", [])
        
        audit_result = {
            "filename": file.filename,
            "hostname": normalized_data["hostname"],
            "status": "NON_COMPLIANT" if violations else "COMPLIANT",
            "violation_count": len(violations),
            "violations": violations,
            "extracted_metadata": normalized_data
        }
        
        pdf_bytes = generate_pdf_report(audit_result)
        return Response(content=pdf_bytes, media_type="application/pdf", headers={
            "Content-Disposition": f"attachment; filename={file.filename}_report.pdf"
        })
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train")
async def train_mapping(payload: TrainRequest):
    try:
        save_mapping(payload.vendor.lower(), payload.feature_key, payload.cli_pattern)
        return {
            "status": "SUCCESS",
            "message": f"Successfully mapped '{payload.cli_pattern}' to '{payload.feature_key}' for vendor '{payload.vendor}'."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))