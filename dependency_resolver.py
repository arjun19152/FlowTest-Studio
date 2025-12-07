from utils import find_nested_value

def resolve_dependencies_test(api_name, api_config, api_interactions, env_config, input_values):
    """
    Resolves dependencies for the given API using the relationship matrix.
    """
    api_data = None
    
    if api_name != "ENV":
        api_data = api_config.get(api_name, {}).copy()

    # Get the first dependency list from level, if it exists
    if api_name in api_interactions and "level" in api_interactions[api_name] and api_interactions[api_name]["level"]:
        dependencies_to_resolve = api_interactions[api_name]["level"].pop(0)  # Remove after fetching

        for output_api in dependencies_to_resolve:

            dependency_types = api_interactions[api_name].get(output_api, {})

            for injection_type, params in dependency_types.items():
                for param in params:  # Note: Param is eq.id
                    postgress_flag = False

                    if "eq." in param:
                        postgress_flag = True
                        param = param.replace("eq.", "")

                    value = None

                    if output_api == "ENV":
                        value = env_config["ENV_VARIABLES"].get(param)
                    else:
                        # Fetch value from previous stored API response
                        value = find_nested_value(api_interactions[output_api]["response"], param)

                    # Inject into the appropriate section
                    if value:
                        if injection_type == "H":
                            for key, val in api_data["headers"].items():
                                if val == param or val == f"eq.{param}":
                                    api_data["headers"][key] = f"eq.{value}" if postgress_flag else value
                                    break
                        elif injection_type == "P":
                            for key, val in api_data["params"].items():
                                if val == param or val == f"eq.{param}":
                                    api_data["params"][key] = f"eq.{value}" if postgress_flag else value
                                    break
                        elif injection_type == "B":
                            for key, val in api_data["body"].items():
                                if val == param or val == f"eq.{param}":
                                    api_data["body"][key] = f"eq.{value}" if postgress_flag else value
                                    break
                        elif injection_type == "FI":
                            for key, val in env_config["ENV_VARIABLES"].items():
                                if val == param or val == f"eq.{param}":
                                    env_config["ENV_VARIABLES"][key] = f"eq.{value}" if postgress_flag else value
                                    break
    if api_name != "ENV":
        
        # Replace values in headers
        for k1,v1 in input_values.items():
            for key1, val1 in api_data.get("headers", {}).items():
                if val1 == k1 or val1 == f"eq.{k1}":
                    api_data["headers"][key1] = f"eq.{v1}" if (val1 == f"eq.{k1}") else v1
                    break
        
        # Replace values in params
        for k1,v1 in input_values.items():
            for key1, val1 in api_data.get("params", {}).items():
                if val1 == k1 or val1 == f"eq.{k1}":
                    api_data["params"][key1] = f"eq.{v1}" if (val1 == f"eq.{k1}") else v1
                    break
        
        # Replace values in body
        for k2,v2 in input_values.items():
            for key2, val2 in api_data.get("body", {}).items():
                if val2 == k2 or val2 == f"eq.{k2}":
                    api_data["body"][key2] = f"eq.{v2}" if (val2 == f"eq.{k2}") else v2
                    break

    return api_data