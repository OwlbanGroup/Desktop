# JPMorgan Payment Integration

## Overview

The JPMorgan payment functionality has been successfully integrated into the main Flask backend through proxy routes. This allows seamless access to JPMorgan payment APIs from the main application without needing to directly interact with the separate Node.js OSCAR-BROOME-REVENUE server.

## Architecture

- **Main Backend**: Flask server running on port 5000 (`backend/app_server.py`)
- **OSCAR-BROOME-REVENUE**: Node.js Express server running on port 4000
- **Integration**: Proxy routes in Flask forward requests to the Node.js server

## Available Proxy Endpoints

All JPMorgan payment endpoints are available through the Flask backend at `/api/jpmorgan-payment/`:

### Core Payment Operations
- `POST /api/jpmorgan-payment/create-payment` - Create a new payment
- `GET /api/jpmorgan-payment/payment-status/<payment_id>` - Check payment status
- `POST /api/jpmorgan-payment/refund` - Process a refund
- `POST /api/jpmorgan-payment/capture` - Capture an authorized payment
- `POST /api/jpmorgan-payment/void` - Void a payment

### Additional Operations
- `GET /api/jpmorgan-payment/transactions` - Get transaction history
- `POST /api/jpmorgan-payment/webhook` - Handle webhooks
- `GET /api/jpmorgan-payment/health` - Health check

## Configuration

The integration uses environment variables for configuration:

- `OSCAR_BROOME_URL`: URL of the OSCAR-BROOME-REVENUE server (default: `http://localhost:4000`)

## Usage Examples

### Python Client
```python
import requests

# Create a payment
response = requests.post('http://localhost:5000/api/jpmorgan-payment/create-payment', json={
    'amount': 100.00,
    'currency': 'USD',
    'description': 'Test payment'
})

# Check payment status
response = requests.get('http://localhost:5000/api/jpmorgan-payment/payment-status/12345')
```

### JavaScript Client
```javascript
// Create a payment
fetch('/api/jpmorgan-payment/create-payment', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        amount: 100.00,
        currency: 'USD',
        description: 'Test payment'
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

## Running the Integration

1. Start the OSCAR-BROOME-REVENUE server:
   ```bash
   cd OSCAR-BROOME-REVENUE
   npm start
   ```

2. Start the main Flask backend:
   ```bash
   cd backend
   python app_server.py
   ```

3. Access the frontend at: `http://localhost:5000`

## Benefits

- **Seamless Integration**: All payment functionality accessible through single API
- **Unified Architecture**: No need to manage multiple server endpoints
- **Error Handling**: Centralized error handling and logging
- **Scalability**: Easy to add load balancing or caching at the Flask level
- **Security**: Single point of access control

## Testing

Use the provided test script to verify the integration:

```bash
python test_jpmorgan_proxy.py
```

This will test the health check and create payment endpoints.

## Troubleshooting

- Ensure both servers are running (Flask on 5000, Node.js on 4000)
- Check environment variables if using custom URLs
- Verify network connectivity between servers
- Check server logs for detailed error messages

## Future Enhancements

- Add authentication/authorization to proxy routes
- Implement request/response caching
- Add rate limiting
- Implement circuit breaker pattern for resilience
- Add comprehensive monitoring and metrics
