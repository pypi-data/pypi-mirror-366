from pydantic import BaseModel, Field
from docore_ai.model import intelligence_profiler
from fastapi import FastAPI, HTTPException
from docore_ai.utils.helpers import is_port_in_use
from docore_ai.utils.logger import dprint


if __name__ == "__main__":
    import uvicorn
    try:
        if is_port_in_use("127.0.0.1", 8000):
            dprint("⚠️ Port 8000 already in use. API server may already be running.")
        else:        
            uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)
    except Exception as e:
        dprint("Failed to launch DoCoreAI client. Please check your main configuration.")
        dprint("Conatct support (if issue persists): info@docoreai.com")


app = FastAPI(title="DoCoreAI", version="1.0")

class PromptRequest(BaseModel):
    user_content: str = Field(..., example="Can you help me to connect my laptop to wifi?")
    role: str = Field(None, example="Technical Support Agent", description="Role of LLM")


@app.post("/intelligence_profiler", summary="Give a prompt with intelligence paramters",  include_in_schema=False)
async def prompt_live_intelli_profiler(request: PromptRequest):
    try:
        optimal_response = intelligence_profiler(
            user_content=request.user_content,
            role=request.role,
        )
        return {"optimal_response":optimal_response}
    except Exception as e:
        dprint(f"❌ Profiling failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/", summary="Welcome to DoCoreAI Endpoint")
def home():
    return {"message": "Welcome to DoCoreAI API. Use /docs for more info."}

#@app.post("/normal_prompt", summary="For testing purpose only",  include_in_schema=False)
#def normal_prompt_live(request: PromptRequest):

#    normal_prompt_response = normal_prompt(
#        user_content=request.user_content,
#        role=request.role
#    )
#    return {"normal_response":normal_prompt_response}
    