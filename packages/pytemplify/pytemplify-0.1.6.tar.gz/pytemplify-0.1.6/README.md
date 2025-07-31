# pytemplify
Text file generator framework using parsed dictionary data and Jinja2 templates.

## How to create your generator using `pytemplify`
Install uv:
```shell
curl -Ls https://astral.sh/uv/install.sh | sh
```
Install `pytemplify`:
```shell
pip install pytemplify
```
Generate the first skeleton of your generator using `mygen-init`:
```shell
cd <your-repo-path>
mygen-init
```
Complete the `TODO`s in modules; main implementation module is `parser_<your-generator-name>.py`.

Try to run:
```shell
uv pip install -r requirements.txt
uv venv
source .venv/bin/activate
<your-generator-name>
```
```shell
uv pip install nox
nox
```

## Running Tests and Linters with nox

To run all sessions (formatting, linting, and tests):

```shell
nox
```

To run only tests:

```shell
nox -s tests
```

To run only linting:

```shell
nox -s lint
```

To run only code formatting:

```shell
nox -s format_code
```

## Publishing to PyPI with uv

1. Build the package:

```shell
uv build
```

2. Publish to PyPI:

```shell
uv publish
```

For test PyPI, use:

```shell
uv publish --repository testpypi
```

## TIPs
Activate uv virtual environment:
```shell
source .venv/bin/activate
```
Deactivate uv virtual environment:
```shell
deactivate
```