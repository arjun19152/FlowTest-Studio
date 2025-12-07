import requests

def make_request(api_data):
    method = api_data["method"]
    url = api_data["url"] + api_data["path"]
    headers = api_data.get("headers", {})
    params = api_data.get("params", {})
    body = api_data.get("body", {})

    try:
        response = requests.request(method, url, headers=headers, params=params, json=body)
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error calling {url}: {e}")
        return f"Error calling {url}: {e}"