# Organizational Leadership Project

A Python project simulating organizational leadership concepts with different leadership styles, team management, and decision making.

## Features

- Define leaders with various leadership styles (Autocratic, Democratic, Transformational, Laissez-Faire, Servant)
- Manage teams with members and roles
- Simulate leadership actions and decision-making processes
- Command-line interfaces: argument-based and interactive CLI
- Basic unit tests for core functionality

## Installation

This project requires Python 3.7 or higher. No external dependencies are needed.

Clone the repository and navigate to the project directory:

```bash
git clone <repository-url>
cd <project-directory>
```

## Usage

### Argument-based CLI

Run the main CLI with command-line arguments:

```bash
python app.py --leader-name Alice --leadership-style DEMOCRATIC --team-members "Bob:Developer" "Charlie:Designer" --decision "Implement new project strategy"
```

Use `--help` to see all options:

```bash
python app.py --help
```

### Interactive CLI

Run the interactive CLI interface:

```bash
python interface.py
```

Follow the prompts to enter leader name, leadership style, team members, and decisions.

## Testing

Run the unit tests with:

```bash
python -m unittest discover tests
```

## Project Structure

- `organizational_leadership/`: Core module with leadership classes and functions
- `app.py`: Argument-based CLI entry point
- `interface.py`: Interactive CLI interface
- `tests/`: Unit tests
- `README.md`: Project documentation
- `requirements.txt`: Project dependencies (none)

## Contributing

Contributions are welcome. Please open issues or submit pull requests.

## License

This project is licensed under the MIT License.
