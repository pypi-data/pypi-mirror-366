# Simple Data Storage Library (SQLite + Pickle)

This Python library provides an easy way to store and retrieve key-value data using SQLite and `pickle`. It also includes a basic Tkinter GUI that explains how to use the library.

## Features

- Store any Python object with a key
- Uses SQLite as backend with a single-row table
- Serialized using `pickle`
- Simple and unified `save_data()` function
- GUI helper included to show usage instructions

## Installation

No installation required. Just copy the Python files into your project. Make sure to have:

```bash
Python 3.x
```

## Usage

```python
from your_module import save_data, see_data

# Save data
save_data(db_name="mydb", data="1234", data_name="password")

# Retrieve data
print(see_data(db_name="mydb", data_name="password"))
```

- `db_name`: name of the SQLite file (without `.db`)
- `data_name`: the key to store the value under
- `data`: any serializable Python object

## GUI Helper

Run `tkinter_gui_helper.py` to view usage instructions in a simple graphical window.

## License

MIT License
