from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import gen
import json
from typing import Any
import os

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

@app.get("/input-example")
async def get_input_example(model_name: str = Query(...)):
    try:
        model_dir = os.path.join('onnx', model_name)
        input_example_path = os.path.join(model_dir, 'input.json')

        if not os.path.exists(input_example_path):
            raise HTTPException(status_code=404, detail="Input example not found for the specified model.")

        with open(input_example_path, "r") as f:
            example_input = json.load(f)

        if 'input_data' not in example_input:
            raise HTTPException(status_code=500, detail="`input_data` field not found in the input example.")

        return example_input['input_data']
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "Error reading input example", "details": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)