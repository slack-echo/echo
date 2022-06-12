# echo

[![GitHub.](https://img.shields.io/github/license/skkuinit/echo?logo=github)](LICENSE)

## Dependencies

- Flask
- PyYAML
- requests
- slack_bolt
- slack_sdk

### Install packages

```bash
pip3 install -r requirements.txt
```

## Development

### Open localhost

```bash
ssh -R 80:localhost:3000 localhost.run
```

### Set Environment Variables

On single workspace

```bash
export `sed -e 's/[[:space:]]*:[[:space:]]*/=/g' auth/.env.yaml`
```

### Run [main.py](main.py)

```bash
python3 main.py
```

## File Structure

```bash
tree --dirsfirst -vFI "$(grep -hvE '^$|^#' {,$(git rev-parse --show-toplevel)/}.gitignore|sed 's:/$::'|tr \\n '\|')"
```

```bash
echo/
├── auth/
│   ├── .env.yaml.sample
│   ├── SECRETS.sample -> .env.yaml.sample
│   └── __init__.py
├── listeners/
│   ├── __init__.py
│   ├── commands.py
│   └── shortcuts.py
├── utils/
│   ├── blocks.py
│   ├── loader.py
│   └── text.py
├── LICENSE
├── README.md
├── config.yaml
├── main.py
└── requirements.txt

3 directories, 13 files

```

## License

[MIT](LICENSE)
