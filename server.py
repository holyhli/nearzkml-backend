from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import gen
from typing import Any

app = FastAPI()

class InputData(BaseModel):
    input_data: Any

@app.post("/generate-proof")
async def generate_proof(input: InputData, model_name: str):
    try:
        result = await gen.generate_proof(input.dict(), model_name)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result)
        return {"proof": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating proof: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)