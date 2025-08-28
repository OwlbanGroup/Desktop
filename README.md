# Organizational Leadership Project with NVIDIA NeMo-Agent-Toolkit Integration

A Python project simulating organizational leadership concepts with advanced NVIDIA AI integration, including NeMo framework, NIM services, and multi-agent systems.

## Features

- Define leaders with various leadership styles (Autocratic, Democratic, Transformational, Laissez-Faire, Servant)
- Manage teams with members and roles
- Simulate leadership actions and decision-making processes
- Command-line interfaces: argument-based and interactive CLI
- Comprehensive unit tests and integration tests
- Revenue tracking with live updates
- **Advanced NVIDIA NeMo-Agent-Toolkit integration** with real AI capabilities
- Multi-agent system orchestration
- Tool calling and function execution
- Real-time response streaming
- Financial services AI (fraud detection, risk management, data analytics)

## Installation

This project requires Python 3.8 or higher with CUDA support recommended for NVIDIA acceleration.

### Dependencies

Install required dependencies using pip:

```bash
pip install -r requirements.txt
```

### NVIDIA NeMo Framework Setup

For full NVIDIA NeMo functionality, you may need to:

1. Install NVIDIA drivers and CUDA toolkit
2. Set up NVIDIA NGC account for model access
3. Configure environment variables for NVIDIA services

```bash
# Optional: Install NVIDIA PyIndex for optimized packages
pip install nvidia-pyindex
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

### NVIDIA NeMo-Agent-Toolkit Integration

The project includes comprehensive NVIDIA NeMo framework integration with advanced capabilities:

```python
from nvidia_integration import NvidiaIntegration

# Create an instance
nvidia = NvidiaIntegration()

# Check system status
status = nvidia.get_advanced_status()
print(f"NVIDIA Available: {status['nvidia_available']}")

# Load NeMo models
nvidia.load_nemo_model("gpt-3.5b")
nvidia.load_nemo_model("bert-base")

# Create multi-agent systems
agent_config = {
    "agents": ["analyst", "strategist", "executor"],
    "orchestration": "hierarchical"
}
nvidia.create_agent_system(agent_config)

# Use tool calling
result = nvidia.tool_calling("financial_analysis", {"data": quarterly_reports})

# Stream responses in real-time
response = nvidia.stream_response("Analyze Q3 performance trends")
```

### Advanced AI Capabilities

```python
# Financial services AI
fraud_results = nvidia.perform_fraud_detection(transactions)
risk_assessment = nvidia.perform_risk_management(financial_data)
analytics = nvidia.generate_data_analytics(business_metrics)

# Batch processing
prompts = [
    "Analyze market trends",
    "Suggest risk mitigation strategies",
    "Generate quarterly forecast"
]
responses = nvidia.batch_process_prompts(prompts, model_type="colosseum")
```

## Demonstration Scripts

- `demo_deepseek.py` - DeepSeek v3.1 model integration
- `demo_nvidia_aiq.py` - Comprehensive NVIDIA AI capabilities demo
- `test_nvidia_*.py` - Comprehensive test suites

## Testing

Run the comprehensive test suite:

```bash
python -m unittest discover tests

# Run specific NVIDIA integration tests
python -m unittest test_nvidia_integration.py
python -m unittest test_nvidia_comprehensive.py
python -m unittest test_nvidia_performance.py
```

## Deployment

### Local Deployment
```bash
pip install -r requirements.txt
python app.py
```

### Containerized Deployment (Recommended for NVIDIA)
```dockerfile
FROM nvcr.io/nvidia/pytorch:23.05-py3
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

### Cloud Deployment
- NVIDIA NGC containers for optimized performance
- Kubernetes with NVIDIA GPU support
- Cloud platforms with GPU instances (AWS, GCP, Azure)

## Configuration

Set environment variables for NVIDIA services:

```bash
export NVIDIA_API_KEY=your_api_key
export NIM_SERVICE_URL=your_nim_endpoint
export CUDA_VISIBLE_DEVICES=0
```

## Contributing

Contributions are welcome! Please see our contributing guidelines and code of conduct.

1. Fork the repository
2. Create a feature branch
3. Make your changes with comprehensive tests
4. Submit a pull request

## License

This project is licensed under the MIT License. NVIDIA SDKs and models may have separate licensing requirements.

## Support

For NVIDIA-related issues:
- Check [NVIDIA NeMo Documentation](https://docs.nvidia.com/deeplearning/nemo/)
- Visit [NVIDIA Developer Forums](https://forums.developer.nvidia.com/)
- Consult [NVIDIA NGC Catalog](https://catalog.ngc.nvidia.com/)

For project-specific issues, please open a GitHub issue.
