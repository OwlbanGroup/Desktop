# Organizational Leadership Project

A Python project simulating organizational leadership concepts with different leadership styles, team management, and decision making.

## Features

- Define leaders with various leadership styles (Autocratic, Democratic, Transformational, Laissez-Faire, Servant)
- Manage teams with members and roles
- Simulate leadership actions and decision-making processes
- Command-line interfaces: argument-based and interactive CLI
- Basic unit tests for core functionality
- Revenue tracking with live updates
- NVIDIA technologies and NIM services integration (placeholders)

## Installation

This project requires Python 3.7 or higher.

### Dependencies

Install required dependencies using pip:

```bash
pip install -r requirements.txt
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

Integration and end-to-end tests cover leadership, revenue tracking, and NVIDIA integration modules.

## Deployment

This project is a CLI application and can be run on any system with Python 3.7+ and the required dependencies installed.

For deployment:

1. Clone the repository.
2. Install dependencies as above.
3. Run the CLI application as needed.

No additional deployment scripts or containers are provided at this time.

## Contributing

Contributions are welcome. Please open issues or submit pull requests.

## License

This project is licensed under the MIT License.
