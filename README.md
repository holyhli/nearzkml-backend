# Near ZKML Backend

This repository contains the backend part of the Near ZKML project. The backend is responsible for generating proofs for different models that we have in the list. The input and output data is public.

## Features

- Generate proofs for various machine learning models.
- Validate input data structure against reference data.
- Provide detailed error messages for invalid inputs.

## Setup

### Prerequisites

- Python 3.8+
- `pip` (Python package installer)

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/your-organization/nearzkml-backend.git
   cd nearzkml-backend
   ```

2. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Running the Server

1. Start the FastAPI server:
   ```sh
   uvicorn server:app --host 0.0.0.0 --port 8000
   ```

2. The server will be running at `http://0.0.0.0:8000`.

## API Usage

### Generate Proof

- **Endpoint:** `/generate-proof`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "input_data": { ... },
    "model_name": "model_name"
  }
  ```
- **Response:**
    - **Success:**
      ```json
      {
        "proof": { ... }
      }
      ```
    - **Error:**
      ```json
      {
        "detail": "Error message"
      }
      ```

### Example

```sh
curl -X POST "http://0.0.0.0:8000/generate-proof" -H "Content-Type: application/json" -d '{
  "input_data": { ... },
  "model_name": "example_model"
}'
```

## ezkl

`ezkl` is a library used for generating zero-knowledge proofs for machine learning models. It provides functionalities to generate settings, compile circuits, obtain structured reference strings (SRS), set up circuits, generate witnesses, and finally generate proofs.

### Key Functions

- `gen_settings`: Generates settings for the model.
- `calibrate_settings`: Calibrates the settings based on input data.
- `compile_circuit`: Compiles the model into a circuit.
- `get_srs`: Obtains the structured reference string.
- `setup`: Sets up the circuit with verification and proving keys.
- `gen_witness`: Generates the witness for the proof.
- `prove`: Generates the proof.

## Models

The following models are available for generating proofs:

- `model1`: Description of model1.
- `model2`: Description of model2.
- `model3`: Description of model3.

## Contributing

We welcome contributions! Please read our [contributing guidelines](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
