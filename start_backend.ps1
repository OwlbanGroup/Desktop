# PowerShell script to start the Flask backend server in a new terminal window

Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd .\backend; python app_server.py'
