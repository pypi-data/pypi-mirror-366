# COESI CLI

A command-line interface for managing COESI Platform Docker deployments.

## Installation

### From PyPI (Recommended)

```bash
pip install coesi
```

### From Source

```bash
git clone https://github.com/coesi/coesi-cli.git
cd coesi-cli
pip install -e .
```

## Usage

After installation, you can use the `coesi` command globally:

```bash
# Deploy development environment
coesi dev

# Deploy production with default IP
coesi prod

# Deploy production with custom IP
coesi prod 10.0.0.100

# Restart services
coesi restart dev
coesi restart prod

# Stop services
coesi stop dev
coesi stop prod
coesi stop all

# Check status
coesi status
coesi status dev
coesi status prod

# View logs
coesi logs
coesi logs core-api

# Clean environments
coesi clean dev
coesi clean prod
coesi clean all

# Update production IP
coesi ip 192.168.1.100

# Show help
coesi --help
```

## Commands

### `coesi dev`

Deploy development environment with localhost (no IP parameter allowed).

### `coesi prod [IP]`

Deploy production environment with optional IP address. Uses default IP if not specified.

### `coesi restart [PROFILE]`

Restart services without rebuilding (dev or prod).

### `coesi stop [PROFILE]`

Stop services (dev, prod, or all).

### `coesi status [PROFILE]`

Show service status (dev, prod, or all).

### `coesi logs [SERVICE]`

View logs for specific service or all services.

### `coesi clean [PROFILE]`

Remove containers and volumes (dev, prod, or all).

### `coesi ip [IP]`

Change production IP in .env.prod file.

## Requirements

- Docker
- Docker Compose
- Python 3.8+

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/rezathriii/coesi-cli.git
cd coesi-cli

# Install in development mode
pip install -e .[dev]
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
flake8 src/
mypy src/
```

### Publishing to PyPI

```bash
# Build the package
python -m build

# Upload to PyPI
twine upload dist/*
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## Support

For issues and questions, please visit: https://github.com/rezathriii/coesi-cli/issues

## Author

**Reza Taheri**

- GitHub: [@rezathriii](https://github.com/rezathriii)
- Email: taheri.reza94@gmail.com
