import ezkl
import os
import tempfile
import json
from typing import Any

# Paths
model_path = 'network.onnx'
compiled_model_path = 'network.compiled'
settings_path = 'settings.json'
srs_path = 'kzg.srs'
pk_path = 'test.pk'
vk_path = 'test.vk'
proof_path = 'proof.json'
witness_path = 'witness.json'
input_file_path = 'input.json'

py_run_args = ezkl.PyRunArgs()
py_run_args.input_visibility = "public"
py_run_args.output_visibility = "public"
py_run_args.param_visibility = "fixed" # "fixed" for params means that the committed to params are used for all proofs

# Function to generate proof
async def generate_proof(input: Any) -> Any:
    print("Generating settings...", input)
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
    res = await ezkl.get_srs(settings_path, logrows, srs_path)
    print("SRS obtained.")

    print("Setting up circuit...")
    res = ezkl.setup(
            compiled_model_path,
            vk_path,
            pk_path,
            srs_path,
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
#     res = await ezkl.gen_witness(compiled_model_path, temp_input_file_path, witness_path, vk_path, srs_path)
    res = await ezkl.gen_witness(temp_input_file_path, compiled_model_path, witness_path)
    assert os.path.isfile(witness_path)
    print("Witness generated.")

    print("Generating proof...")
    res = ezkl.prove(
                        witness_path,
                        compiled_model_path,
                        pk_path,
                        proof_path,

                        "single",
                    )
    print("Proof generated.")
    assert os.path.isfile(proof_path)

    return res