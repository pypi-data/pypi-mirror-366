from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from docore_ai.model import intelligence_profiler
import json

app = FastAPI(title="DoCoreAI Test Server", version="test")

# Enable CORS for local Postman testing or frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to http://localhost:3000 if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request body schema
class IntelligenceInput(BaseModel):
    user_content: str
    role: str

@app.get("/")
def health_check():
    return {"status": "DoCoreAI test server running"}

@app.post("/intelligence_profiler")
async def run_intelligence_profiler(body: IntelligenceInput):
    try:
        print("⚙️  Received profiling request via HTTP POST")
        print("→", body.user_content, "| Role:", body.role)

        result = intelligence_profiler(
            user_content=body.user_content,
            role=body.role
        )
        if result.get("status") == "failure":
            return JSONResponse(status_code=400, content=result)
        print("---------------")
        print("🧠 LLM Result:")
        #print(result)  # This line prints the actual output from the LLM
        print(json.dumps(result, indent=2, ensure_ascii=False))

        return {"status": "ok", "result": result}
    except Exception as e:
        #import traceback
        #traceback.print_exc()
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e)
        })
