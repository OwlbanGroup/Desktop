"""
Swagger/OpenAPI documentation setup for Flask application
"""

from flask import Flask, jsonify, request
from flasgger import Swagger, swag_from
import json
from datetime import datetime

def setup_swagger(app: Flask) -> Swagger:
    """
    Setup Swagger documentation for the Flask application

    Args:
        app: Flask application instance

    Returns:
        Swagger instance
    """

    # Swagger configuration
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,  # all in
                "model_filter": lambda tag: True,  # all in
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/",
        "title": "Owlban Group Integrated Platform API",
        "description": """
        # Owlban Group Integrated Leadership & Revenue Platform

        A comprehensive API for organizational leadership simulation, revenue tracking,
        NVIDIA AI integration, and earnings dashboard functionality.

        ## Features

        - **Leadership Simulation**: Simulate team leadership with various leadership styles
        - **Revenue Tracking**: Track and analyze revenue streams and performance
        - **NVIDIA AI Integration**: Advanced GPU-accelerated AI capabilities
        - **Payment Processing**: Integrated payment processing with JPMorgan and Chase
        - **Earnings Dashboard**: Real-time earnings monitoring and reporting
        - **Login Overrides**: Emergency and administrative access controls

        ## Authentication

        Some endpoints require authentication. Use the `/api/auth/login` endpoint to obtain a JWT token,
        then include it in the Authorization header as `Bearer <token>`.

        ## Rate Limiting

        API endpoints are rate-limited to prevent abuse. Check the response headers for rate limit information.
        """,
        "version": "1.0.0",
        "termsOfService": "/terms",
        "contact": {
            "name": "Owlban Group Support",
            "email": "support@owlban.group",
            "url": "https://owlban.group/support"
        },
        "license": {
            "name": "Proprietary",
            "url": "https://owlban.group/license"
        },
        "schemes": ["http", "https"],
        "host": "localhost:5000",
        "basePath": "/",
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
            }
        },
        "security": [
            {
                "Bearer": []
            }
        ]
    }

    # Initialize Swagger
    swagger = Swagger(app, config=swagger_config)

    return swagger

# API specification templates for documentation
LEADERSHIP_API_SPEC = {
    "tags": ["Leadership"],
    "summary": "Simulate team leadership",
    "description": "Simulate a leadership session with specified leadership style and team members",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "leader_name": {
                        "type": "string",
                        "example": "Alice",
                        "description": "Name of the leader"
                    },
                    "leadership_style": {
                        "type": "string",
                        "enum": ["DEMOCRATIC", "AUTHORITATIVE", "LAISSEZ_FAIRE", "TRANSACTIONAL", "TRANSFORMATIONAL"],
                        "example": "DEMOCRATIC",
                        "description": "Leadership style to use"
                    },
                    "team_members": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "example": ["Bob:Developer", "Charlie:Designer"],
                        "description": "List of team members in format 'Name:Role'"
                    }
                },
                "required": ["leader_name", "leadership_style", "team_members"]
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Leadership simulation successful",
            "schema": {
                "type": "object",
                "properties": {
                    "lead_result": {"type": "string"},
                    "team_status": {"type": "object"}
                }
            }
        },
        "400": {
            "description": "Invalid input parameters"
        },
        "500": {
            "description": "Internal server error"
        }
    }
}

GPU_STATUS_SPEC = {
    "tags": ["System"],
    "summary": "Get NVIDIA GPU status",
    "description": "Retrieve current NVIDIA GPU settings and performance metrics",
    "responses": {
        "200": {
            "description": "GPU status retrieved successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "gpu_count": {"type": "integer"},
                    "gpus": {
                        "type": "array",
                        "items": {"type": "object"}
                    },
                    "total_memory": {"type": "string"},
                    "driver_version": {"type": "string"}
                }
            }
        },
        "500": {
            "description": "Failed to retrieve GPU status"
        }
    }
}

PAYMENT_SPEC = {
    "tags": ["Payments"],
    "summary": "Create payment transaction",
    "description": "Process a payment through JPMorgan payment gateway",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "format": "float",
                        "example": 100.00,
                        "description": "Payment amount"
                    },
                    "currency": {
                        "type": "string",
                        "example": "USD",
                        "description": "Currency code"
                    },
                    "payment_method": {
                        "type": "string",
                        "enum": ["credit_card", "bank_transfer", "digital_wallet"],
                        "example": "credit_card",
                        "description": "Payment method"
                    },
                    "description": {
                        "type": "string",
                        "example": "Service payment",
                        "description": "Payment description"
                    }
                },
                "required": ["amount", "currency"]
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Payment created successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "payment_id": {"type": "string"},
                    "status": {"type": "string"},
                    "amount": {"type": "number"},
                    "currency": {"type": "string"},
                    "created_at": {"type": "string", "format": "date-time"}
                }
            }
        },
        "400": {
            "description": "Invalid payment data"
        },
        "500": {
            "description": "Payment processing failed"
        }
    }
}

LOGIN_OVERRIDE_SPEC = {
    "tags": ["Security"],
    "summary": "Create emergency login override",
    "description": "Create an emergency login override for system access",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "example": "System maintenance required",
                        "description": "Reason for override"
                    },
                    "target_user_id": {
                        "type": "string",
                        "example": "user123",
                        "description": "Target user ID"
                    },
                    "emergency_code": {
                        "type": "string",
                        "example": "EMERG-2024-001",
                        "description": "Emergency authorization code"
                    }
                },
                "required": ["reason", "target_user_id", "emergency_code"]
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Override created successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "override_id": {"type": "string"},
                    "status": {"type": "string"},
                    "expires_at": {"type": "string", "format": "date-time"}
                }
            }
        },
        "400": {
            "description": "Invalid override request"
        },
        "403": {
            "description": "Insufficient permissions"
        },
        "500": {
            "description": "Override creation failed"
        }
    }
}

HEALTH_SPEC = {
    "tags": ["System"],
    "summary": "System health check",
    "description": "Check the health status of all system components",
    "responses": {
        "200": {
            "description": "System is healthy",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "example": "healthy"},
                    "timestamp": {"type": "string", "format": "date-time"},
                    "services": {
                        "type": "object",
                        "properties": {
                            "flask": {"type": "string"},
                            "database": {"type": "string"},
                            "redis": {"type": "string"},
                            "node_proxy": {"type": "string"}
                        }
                    },
                    "version": {"type": "string"}
                }
            }
        },
        "503": {
            "description": "System is unhealthy",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "example": "unhealthy"},
                    "issues": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        }
    }
}

def generate_openapi_spec():
    """
    Generate OpenAPI specification as JSON

    Returns:
        dict: OpenAPI specification
    """
    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "Owlban Group Integrated Platform API",
            "description": "Comprehensive API for leadership simulation, revenue tracking, and AI integration",
            "version": "1.0.0",
            "contact": {
                "name": "Owlban Group Support",
                "email": "support@owlban.group"
            }
        },
        "servers": [
            {
                "url": "http://localhost:5000",
                "description": "Development server"
            },
            {
                "url": "https://api.owlban.group",
                "description": "Production server"
            }
        ],
        "security": [
            {
                "BearerAuth": []
            }
        ],
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            },
            "schemas": {
                "Error": {
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "description": "Error message"
                        },
                        "code": {
                            "type": "integer",
                            "description": "Error code"
                        }
                    }
                },
                "LeadershipResult": {
                    "type": "object",
                    "properties": {
                        "lead_result": {"type": "string"},
                        "team_status": {"type": "object"},
                        "revenue_impact": {"type": "number", "format": "float"}
                    }
                },
                "GPUStatus": {
                    "type": "object",
                    "properties": {
                        "gpu_count": {"type": "integer"},
                        "gpus": {"type": "array", "items": {"type": "object"}},
                        "total_memory": {"type": "string"},
                        "driver_version": {"type": "string"}
                    }
                }
            }
        },
        "paths": {
            "/api/leadership/lead_team": {
                "post": LEADERSHIP_API_SPEC
            },
            "/api/gpu/status": {
                "get": GPU_STATUS_SPEC
            },
            "/api/jpmorgan-payment/create-payment": {
                "post": PAYMENT_SPEC
            },
            "/api/override/emergency": {
                "post": LOGIN_OVERRIDE_SPEC
            },
            "/health": {
                "get": HEALTH_SPEC
            }
        },
        "tags": [
            {
                "name": "Leadership",
                "description": "Leadership simulation and team management"
            },
            {
                "name": "System",
                "description": "System status and GPU monitoring"
            },
            {
                "name": "Payments",
                "description": "Payment processing and transactions"
            },
            {
                "name": "Security",
                "description": "Security and access control"
            }
        ]
    }

    return spec
