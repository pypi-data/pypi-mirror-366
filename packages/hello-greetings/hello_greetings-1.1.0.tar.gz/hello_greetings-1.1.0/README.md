# Halo

A simple command line tool that greets the user.

## Description

Halo is a lightweight CLI tool that provides interactive greetings. It can accept names as command line arguments or prompt for input interactively.

## Installation

```bash
pip install halo
```

## Usage

### Command Line Arguments

```bash
# Greet a specific name
halo World

# Interactive mode (prompts for input)
halo

# Show version
halo --version

# Show help
halo --help
```

### Examples

```bash
$ halo Python
hello Python

$ halo
Enter something: Universe
hello Universe
```

## Features

- Simple command-line interface
- Interactive input mode
- Version information
- Cross-platform compatibility

## Requirements

- Python 3.8+

## Development

### Installation for Development

```bash
# Clone the repository
git clone https://github.com/AaronOET/halo.git
cd halo

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
