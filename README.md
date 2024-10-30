# Norse execution server

A server that executes arbitrary PyTorch and Norse code.

## Usage

```bash
# Install via pip
pip install git+https://github.com/norse/norse_server

# Run with gunicorn for production
norse-server start

# Or locally with flask for development
flask --app src/main.py --debug run -h 0.0.0.0
```

## Acknowledgements

This project has received funding from the European Union’s Horizon 2020 Framework Programme for Research and Innovation
under Specific Grant Agreement No. 785907 (Human Brain Project SGA2) and No. 945539 (Human Brain Project SGA3).
