# durl-py

A lightweight Python library for working with Data URLs (RFC 2397).

## Installation

```bash
pip install durl-py
```

## Usage

### DataURL Class

The `durl.DataURL` class provides a convenient way to create, parse, and manipulate Data URLs.

**Creating a DataURL from raw data:**

```python
from durl import DataURL, MIMEType

# From bytes
data_url = DataURL.from_data(MIMEType.TEXT_PLAIN, b"Hello, World!")
print(data_url.url)
# data:text/plain;base64,SGVsbG8sIFdvcmxkIQ==

# From string
data_url = DataURL.from_data(MIMEType.TEXT_PLAIN, "Hello, World!")
print(data_url.url)
# data:text/plain;base64,SGVsbG8sIFdvcmxkIQ==
```

**Parsing a DataURL string:**

```python
from durl import DataURL

data_url_string = "data:text/plain;base64,SGVsbG8sIFdvcmxkIQ=="
data_url = DataURL.from_url(data_url_string)

print(data_url.mime_type)
# text/plain

print(data_url.data_decoded)
# Hello, World!
```

### `message_contents_from_text` function

The `durl.message_contents_from_text` function allows you to extract Data URLs from a string.

```python
from durl import message_contents_from_text, DataURL

text = "Here is an image: data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg== and some text."

contents = message_contents_from_text(text)

print(contents[0])
# Here is an image:

assert isinstance(contents[1], DataURL)
print(contents[1].mime_type)
# image/png

print(contents[2])
# and some text.
```

## Development

To install the development dependencies, run:

```bash
pip install -r requirements-all.txt
```

To run the tests, run:

```bash
pytest
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
