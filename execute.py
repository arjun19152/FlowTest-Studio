import requests
# from dependency_resolver import resolve_dependencies
from dependency_resolver import resolve_dependencies_test
from request_handler import make_request
from utils import load_test_case_data
import json
from utils import update_response
from PyQt5.QtWidgets import QApplication
import copy
from datetime import datetime
from generate_report import generate_test_report_xlsx
import os

def execute_api_sequence(api_config, env_config, api_interactions, scenario_name, api_blocks, project_path):

    sequence = [api for api in api_interactions.keys() if api != "ENV"]
    test_case_data = load_test_case_data("testcases/testcases.json")[scenario_name]

    max_test_count = max(len(test_case_data.get(api, [])) for api in sequence)
    success_tracker = {api: 0 for api in sequence}

    print(f"Total Test Iterations = {max_test_count}")

    for test_index in range(max_test_count):
        print(f"\n=== Test Iteration {test_index+1}/{max_test_count} ===")

        copy_api_interactions = copy.deepcopy(api_interactions)

        for api_index, api_name in enumerate(sequence):

            if test_index >= len(test_case_data.get(api_name, [])):
                print(f"⚠ No testcase #{test_index+1} for {api_name}, skipping...")
                continue

            print(f"→ Executing: {api_name} testcase {test_index+1}")

            api_block = api_blocks[api_index]
            api_block.set_progress(f"Executing {test_index + 1}/{max_test_count} ...")

            # Prepare input data
            input_values = test_case_data[api_name][test_index]
            api_data = resolve_dependencies_test(api_name, api_config, copy_api_interactions, env_config, input_values)

            # Send request
            response = make_request(api_data)

            safe_response = {
                "status_code": response.status_code,
                "body": None,
                "error": None
            }

            if response:
                try:
                    # Try JSON first
                    safe_response["body"] = response.json()
                except Exception:
                    # Fallback to raw text (401/404 HTML etc.)
                    safe_response["body"] = response.text or ""
                    safe_response["error"] = response.reason or "Unknown"
            else:
                safe_response["error"] = "No response from server"


            if response and response.content:
                success_tracker[api_name] += 1
            

            update_response(scenario_name, api_name, copy_api_interactions, safe_response, test_index)

            QApplication.processEvents()
    
    # Final UI Status
    for i, api_name in enumerate(sequence):
        total_cases = len(test_case_data.get(api_name, []))
        passed = (success_tracker[api_name] == total_cases)
        fail_count = total_cases-success_tracker[api_name]
        api_blocks[i].set_status(success_tracker[api_name],fail_count)
        print(f"✔ {api_name}: Passed {success_tracker[api_name]}/{total_cases}")

    project_name = os.path.splitext(os.path.basename(project_path))[0]
    generate_test_report_xlsx(project_name,scenario_name)

    return api_interactions


