import ezkl
import os
import json
from typing import Any

# Base directory for models
base_dir = 'onnx'

py_run_args = ezkl.PyRunArgs()
py_run_args.input_visibility = "public"
py_run_args.output_visibility = "public"
py_run_args.param_visibility = "fixed"

def validate_input_data(input_data: Any, reference_data: Any) -> bool:
    print("Validating input data...")

    if isinstance(input_data, list) and isinstance(reference_data, list):
        print("Both input_data and reference_data are lists.")
        if len(input_data) != len(reference_data):
            print("Length mismatch between input_data and reference_data lists.")
            return False
        for i in range(len(input_data)):
            print(f"Validating list element {i}...")
            if not validate_input_data(input_data[i], reference_data[i]):
                print(f"Validation failed for list element {i}.")
                return False
    elif isinstance(input_data, dict) and isinstance(reference_data, dict):
        print("Both input_data and reference_data are dictionaries.")
        if input_data.keys() != reference_data.keys():
            print("Key mismatch between input_data and reference_data dictionaries.")
            return False
        for key in input_data:
            print(f"Validating dictionary key '{key}'...")
            if not validate_input_data(input_data[key], reference_data[key]):
                print(f"Validation failed for dictionary key '{key}'.")
                return False
    else:
        result = isinstance(input_data, type(reference_data))
        print(f"Comparing types: {type(input_data)} and {type(reference_data)} - Result: {result}")
        return result

    print("Validation successful.")
    return True

async def generate_proof(input: Any, model_name: str) -> Any:
    model_dir = os.path.join(base_dir, model_name)

    if not os.path.exists(model_dir):
        raise FileNotFoundError(f"Model directory {model_dir} does not exist.")

    # Paths
    model_path = os.path.join(model_dir, 'network.onnx')
    compiled_model_path = os.path.join(model_dir, 'network.compiled')
    settings_path = os.path.join(model_dir, 'settings.json')
    srs_path = os.path.join(model_dir, 'kzg.srs')
    pk_path = os.path.join(model_dir, 'test.pk')
    vk_path = os.path.join(model_dir, 'test.vk')
    proof_path = os.path.join(model_dir, 'proof.json')
    witness_path = os.path.join(model_dir, 'witness.json')
    input_file_path = os.path.join(model_dir, 'input.json')

    # Load reference input data structure
    with open(input_file_path, 'r') as f:
        reference_input = json.load(f)

    # Parse the input data
    input_data = json.loads(input['input_data'])
    input['input_data'] = input_data  # Update the input dictionary with the parsed data

    # Validate input data structure
    if not validate_input_data(input_data, reference_input['input_data']):
        return {
            "error": "Invalid input data structure",
            "expected_structure": reference_input['input_data']
        }

    print("Generating settings...", input_data)
    res = ezkl.gen_settings(model_path, settings_path, py_run_args=py_run_args)
    assert res == True
    print("Settings generated.")

    print("Calibrating settings...")
    res = await ezkl.calibrate_settings(input_file_path, model_path, settings_path, "resources")
    print("Settings calibrated.")

    print("Compiling circuit...")
    res = ezkl.compile_circuit(model_path, compiled_model_path, settings_path)
    assert res == True
    print("Circuit compiled.")

    print("Getting SRS...")
    with open(settings_path, 'r') as f:
        settings = json.load(f)
    logrows = int(settings['run_args']['logrows'])
    print("Game over")
    res = await ezkl.get_srs(settings_path, logrows)
    print("SRS obtained.")

    print("Setting up circuit...")
    res = ezkl.setup(
            compiled_model_path,
            vk_path,
            pk_path,
        )
    assert res == True
    assert os.path.isfile(vk_path)
    assert os.path.isfile(pk_path)
    print("Circuit setup complete.")

    print("Generating witness...")
    script_dir = os.path.dirname(__file__)
    temp_input_file_path = os.path.join(script_dir, 'temp_input.json')
    with open(temp_input_file_path, 'w') as temp_input_file:
        json.dump(input, temp_input_file)
    print("Temp File Created...", temp_input_file_path)
    res = await ezkl.gen_witness(
        temp_input_file_path,
        compiled_model_path,
        witness_path,
        vk_path)
    assert os.path.isfile(witness_path)
    print("Witness generated.")

    print("Generating proof...")
    res = ezkl.prove(
                        witness_path,
                        compiled_model_path,
                        pk_path,
                        proof_path,

                        'single',
                    )
    print("Proof generated.")
    assert os.path.isfile(proof_path)

    return res