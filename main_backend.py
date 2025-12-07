import json
from execute import execute_api_sequence
import os

class startEngine:
    @staticmethod
    def runBackend(scenario_name, api_blocks, project_path):
        # Load configurations
        with open("configs/api_config_new.json") as f:
            api_config = json.load(f)

        # with open("configs/env_config_sample.json") as f:
        #     env_config = json.load(f)
        env_config = None
        
        file_path = os.path.join("interactions",scenario_name + "_interactions.json")
        with open(file_path) as f:
            api_interactions = json.load(f)

        for block in api_blocks:
            block.reset_status()

        # Execute the API sequence
        updated_api_interactions = execute_api_sequence(api_config, env_config, api_interactions, scenario_name, api_blocks, project_path)

        
        with open(file_path, "w") as f:
            json.dump(updated_api_interactions, f, indent=4)
