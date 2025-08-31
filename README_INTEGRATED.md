# Owlban Group - Integrated Leadership & Revenue Platform

A comprehensive Python-based platform that combines organizational leadership simulation, revenue tracking, NVIDIA AI integration, and earnings dashboard functionality into a unified web application.

## 🏗️ Architecture

This integrated project combines:

- **Backend (Python/Flask)**: Leadership simulation, revenue tracking, NVIDIA AI integration
- **Frontend (HTML/CSS/JS)**: Web interface and earnings dashboard
- **Database**: Revenue tracking with SQLAlchemy
- **AI Integration**: NVIDIA NeMo framework for advanced AI capabilities

## 📁 Project Structure

```
owlban-group-integrated/
├── backend/
│   └── app_server.py          # Flask web server with API endpoints
├── frontend/
│   ├── index.html              # Main web interface
│   └── OSCAR-BROOME-REVENUE/   # Earnings dashboard components
├── organizational_leadership/  # Leadership simulation module
├── tests/                      # Test suites
├── requirements.txt            # Python dependencies
├── run.py                      # Application runner script
└── README_INTEGRATED.md        # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- NVIDIA GPU (recommended for AI features)
- CUDA toolkit (for NVIDIA acceleration)

### Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Optional: Setup NVIDIA environment:**
   ```bash
   export CUDA_VISIBLE_DEVICES=0
   ```

### Running the Application

Start the integrated web application:

```bash
python run.py
```

The application will be available at:
- **Main Interface**: http://localhost:5000
- **API Endpoints**: http://localhost:5000/api/*

## 🎯 Features

### Leadership Simulation
- Define leaders with various leadership styles
- Manage teams with members and roles
- Simulate leadership actions and decision-making
- Real-time revenue impact tracking

### NVIDIA AI Integration
- Advanced NVIDIA NeMo-Agent-Toolkit integration
- Multi-agent system orchestration
- Tool calling and function execution
- Real-time response streaming

### Earnings Dashboard
- Comprehensive revenue tracking and reporting
- Payment processing integration
- Executive portal with interactive dashboards
- Real-time earnings updates

### Web Interface
- Modern responsive web UI
- Interactive leadership simulation controls
- GPU status monitoring
- Direct access to earnings dashboard

## 🔧 API Endpoints

### Leadership API
- `POST /api/leadership/lead_team` - Simulate team leadership
- `POST /api/leadership/make_decision` - Simulate decision making

### System API
- `GET /api/gpu/status` - Get NVIDIA GPU status
- `GET /api/earnings` - Get earnings data

## 🧪 Testing

Run the comprehensive test suite:

```bash
python -m pytest tests/
```

## 📊 Usage Examples

### Leadership Simulation
```python
from organizational_leadership import leadership

leader = leadership.Leader("Alice", leadership.LeadershipStyle.DEMOCRATIC)
team = leadership.Team(leader)
result = leader.lead_team()
```

### NVIDIA Integration
```python
from nvidia_integration import NvidiaIntegration

nvidia = NvidiaIntegration()
status = nvidia.get_advanced_status()
```

## 🔐 Configuration

Set environment variables:

```bash
export NVIDIA_API_KEY=your_api_key
export CUDA_VISIBLE_DEVICES=0
```

## 🚀 Deployment

### Development
```bash
python run.py
```

### Production
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app_server:app
```

---

**Built with ❤️ by the Owlban Group**
