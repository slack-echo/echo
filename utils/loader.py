def read_yaml(path: str) -> dict:
    import yaml
    from yaml.loader import SafeLoader

    if path.startswith("http"):
        import os
        import requests

        headers = {
            "Accept": "application/vnd.github.v3.raw",
            "Authorization": os.environ.get("GITHUB_ACCESS_TOKEN"),
        }
        r = requests.get(path, headers=headers)
        return yaml.load(r.text, Loader=SafeLoader)
    else:
        with open(path) as f:
            return yaml.load(f, Loader=SafeLoader)


def read_json(path: str) -> dict:
    import json

    if path.startswith("http"):
        import os
        import requests

        headers = {
            "Accept": "application/vnd.github.v3.raw",
            "Authorization": os.environ.get("GITHUB_ACCESS_TOKEN"),
        }
        r = requests.get(path, headers=headers)
        return r.json()
    else:
        with open(path) as f:
            return json.load(f)
