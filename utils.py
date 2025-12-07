import pandas as pd
import json
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
import os

def find_nested_value(data, key):
    """ Recursively searches for a key in a nested dictionary. """
    if isinstance(data, dict):
        if key in data:
            return data[key]
        for sub_key in data:
            result = find_nested_value(data[sub_key], key)
            if result is not None:
                return result
    elif isinstance(data, list):
        for item in data:
            result = find_nested_value(item, key)
            if result is not None:
                return result
    return None

def load_test_case_data(json_file_path):
    """
    Reads the test case JSON file and loads it into a dictionary.
    """
    with open(json_file_path, "r") as file:
        test_case_data = json.load(file)
    
    return test_case_data

# Initialize an API with a response placeholder
def initialize_api(api_name, api_interactions):
    if api_name not in api_interactions:
        api_interactions[api_name] = {"response": {}, "level": []}


def update_result(scenario_name, api_name, test_index, response_data):
    """
    Updates results.json with response data per scenario → API → testcase index.
    Ensures file & structure always exist before writing.
    """

    results_file = os.path.join("results", "results.json")

    # Ensure results folder exists
    os.makedirs("results", exist_ok=True)

    # If file does not exist, create empty structure
    if not os.path.exists(results_file):
        with open(results_file, "w") as f:
            json.dump({}, f, indent=4)

    # Load existing results
    with open(results_file, "r") as f:
        try:
            results = json.load(f)
        except json.JSONDecodeError:
            results = {}

    # Ensure structure exists for scenario & API
    if scenario_name not in results:
        results[scenario_name] = {}

    if api_name not in results[scenario_name]:
        results[scenario_name][api_name] = {}

    # Convert index to string keys "1", "2", ...
    test_index_key = str(test_index + 1)

    # Store response
    results[scenario_name][api_name][test_index_key] = response_data

    # Save back to file
    with open(results_file, "w") as f:
        json.dump(results, f, indent=4)



def update_response(scenario_name, api_name, api_interactions, response_data, test_index):
    initialize_api(api_name, api_interactions)
    api_interactions[api_name]["response"] = response_data
    update_result(scenario_name, api_name, test_index, response_data)



def show_message(title, message, level="info"):
    """
    level: "info", "warning", "critical", "error", "question"
    Returns:
        For question → True (Yes), False (No)
        For others  → None
    """
    msg = QMessageBox()
    msg.setWindowTitle(title)
    msg.setTextFormat(Qt.PlainText)
    msg.setText(message)

    # Set icon
    lvl = level.lower()
    if lvl in ("info", "information"):
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)

    elif lvl in ("warn", "warning"):
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Ok)

    elif lvl in ("error", "critical"):
        msg.setIcon(QMessageBox.Critical)
        msg.setStandardButtons(QMessageBox.Ok)

    elif lvl == "question":
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    else:
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)

    result = msg.exec_()

    # For QUESTION dialogs → return True/False
    if lvl == "question":
        if result == QMessageBox.Yes:
            return QMessageBox.Yes

    return None
