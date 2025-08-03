# friendly_errors 😇

A Python module that catches errors and displays them in a friendlier, more helpful way — with tips, emojis, and clear explanations!

## ✨ Features

- Friendly error messages with explanations
- Custom traceback location info
- YAML-configured error data
- Automatically sets `sys.excepthook`

## 📦 Installation

```bash
pip install nice-errors
```
## Usage

```python
import nice-errors

#Throw an error here!

print(1/0)
# See the nice result!
```