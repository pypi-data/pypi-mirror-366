# Hello Greetings

A simple command line tool that greets the user.

## Description

Hello Greetings is a lightweight CLI tool that provides interactive greetings. It can accept names as command line arguments or prompt for input interactively.

## Installation

```bash
pip install hello-greetings
```

## Usage

### Command Line Arguments

```bash
# Greet a specific name
hello-greetings world

# Interactive mode (prompts for input)
hello-greetings

# Show version
hello-greetings --version

# Show help
hello-greetings --help
```

### Examples

```bash
$ hello-greetings Python
hello Python

$ hello-greetings
Enter something: Universe
hello Universe
```

## Features

- Simple command-line interface
- Interactive input mode
- Version information
- Cross-platform compatibility

## Requirements

- Python 3.9+

## Development

### Installation for Development

```bash
# Clone the repository
git clone https://github.com/AaronOET/hello-greetings.git
cd hello-greetings

# Install in development mode
pip install -e .
```

### Running Tests

```bash
python -m pytest tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.
