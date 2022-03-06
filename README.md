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
├── utils/
│   ├── random.py
│   └── text.py
├── LICENSE
├── README.md
├── commands.py
├── listeners.py
├── main.py
└── requirements.txt

1 directory, 8 files
```

## License

[MIT](LICENSE)
