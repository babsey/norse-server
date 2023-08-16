# Norse execution server

A server that executes arbitrary PyTorch and Norse code.

## Usage

```bash
# Install via pip
pip install git+https://github.com/norse/norse_server

# Run with gunicorn for production
gunicorn norse_server.server.app

# Or locally with flask for development
flask --app src/server.py --debug run -h 0.0.0.0
```

## Authors