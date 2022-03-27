def read_yaml(path: str) -> dict:
    import yaml
    from yaml.loader import SafeLoader

    if path.startswith("http"):
        import requests

        r = requests.get(path)
        return yaml.load(r.text, Loader=SafeLoader)
    else:
        with open(path) as f:
            return yaml.load(f, Loader=SafeLoader)


def read_json(path: str) -> dict:
    import json

    if path.startswith("http"):
        import requests

        r = requests.get(path)
        return r.json()
    else:
        with open(path) as f:
            return json.load(f)
