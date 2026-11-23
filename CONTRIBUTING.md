# Contributing

Thanks for your interest in improving this repository.

## Getting set up

```bash
git clone https://github.com/aidless/kaggle-science-exam.git
cd kaggle-science-exam
pip install -r requirements.txt   # if present
```

## Verifying your change

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
make check
```

`make check` is the same offline gate CI runs. Please run it before opening a pull request.

## Pull requests

- One logical change per pull request.
- Explain what breaks or is missing without the change.
- State how you verified it, and paste the command output.
- Keep unrelated reformatting out of the diff.

## Security

Do not open a public issue for a security problem. Use the private channel described
in [SECURITY.md](SECURITY.md).

## Code of conduct

Participation is governed by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
