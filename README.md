# echo

![GitHub.](https://img.shields.io/github/license/skkuinit/echo?logo=github)

## Dependencies

- Flask
- slack-bolt

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

```bash
export `sed -e 's/[[:space:]]*:[[:space:]]*/=/g' .env.yaml;echo;echo ENV=dev`
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
├── actions/
│   ├── __init__.py
│   ├── _actions.py
│   └── _vote.py
├── commands/
│   ├── __init__.py
│   └── _commands.py
├── events/
│   ├── __init__.py
│   └── _events.py
├── poll/
│   ├── actions.py
│   ├── command.py
│   └── shortcut.py
├── tests/
│   └── test_filters.py
├── utils/
│   ├── __init__.py
│   ├── filters.py
│   ├── params.yaml
│   ├── random.py
│   └── text.py
├── views/
│   ├── __init__.py
│   └── _views.py
├── LICENSE
├── README.md
├── app.py
├── listeners.py
├── main.py
├── payloads.yaml
└── requirements.txt

7 directories, 25 files
```

## License

[MIT](LICENSE)
