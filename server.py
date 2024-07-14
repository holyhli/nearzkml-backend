from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import gen
import json
from typing import Any

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Adjust this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputData(BaseModel):
    input_data: Any

@app.post("/generate-proof")
async def generate_proof(input: InputData, model_name: str = Query(...)):
    try:
        result = await gen.generate_proof(input.dict(), model_name)
        if "error" in result:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": result["error"],
                    "expected_structure": result["expected_structure"]
                }
            )
        return {"proof": result}
    except Exception as e:
        try:
            error_details = json.loads(str(e).split(":", 1)[1].strip().replace("'", "\""))
        except (json.JSONDecodeError, IndexError):
            error_details = {"message": str(e)}
        raise HTTPException(status_code=500, detail={"error": "Error generating proof", "details": error_details})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)