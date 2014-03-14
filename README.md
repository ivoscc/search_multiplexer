### Installation

```
pip install -r requirements.txt
```

### Usage

By default the configuration will be loaded from a file named 'config.ini'
from the same directory unless specified by the --config option.
Also, any configurable value might be explicitly supplied by passing the
desired option, i.e: --port 9999

For default options:

```
python run.py
```

Or to use a specific configuration:

```
python run.py --config /path/to/your/ini
```

And you may also specify a section for a multi-tier ini file (See sample-config.ini):

```
python run.py --config /path/to/your/ini --section production
```

For a full list of parameters, see ```python run.py --help```
