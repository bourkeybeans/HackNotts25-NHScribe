# Raspberry Pi Deployment Guide

## Overview
This guide will help you deploy the NHScribe application on a Raspberry Pi server with local network IP: `10.249.84.213`

## Prerequisites
- Raspberry Pi with Raspbian/Ubuntu installed
- Python 3.8+ installed
- Node.js 16+ and npm installed
- Network access to the Raspberry Pi

## Configuration Complete ✓

The application has been pre-configured to work with your Raspberry Pi at `10.249.84.213`:

### Backend (FastAPI)
- ✅ CORS configured to allow network access
- ✅ Server configured to run on `0.0.0.0:8000` (accessible from network)
- ✅ Static file serving configured for letters

### Frontend (React)
- ✅ API base URL centralized in `src/config.js`
- ✅ All API endpoints updated to use `API_BASE_URL`
- ✅ Configuration supports environment variables

## Deployment Steps

### 1. Transfer Files to Raspberry Pi

```bash
# From your local machine, transfer the project to the Pi
scp -r /Users/farhan/Documents/HackNotts25/HackNotts25 pi@10.249.84.213:~/
```

### 2. Backend Setup (Python/FastAPI)

SSH into your Raspberry Pi:
```bash
ssh pi@10.249.84.213
```

Navigate to the project directory:
```bash
cd ~/HackNotts25
```

Install Python dependencies:
```bash
pip install -r requirements.txt
```

Start the backend server:
```bash
python app.py
```

The backend will be accessible at:
- Local: `http://localhost:8000`
- Network: `http://10.249.84.213:8000`

### 3. Frontend Setup (React)

In a new terminal/SSH session on the Raspberry Pi:

```bash
cd ~/HackNotts25/front-end
```

Install Node.js dependencies:
```bash
npm install
```

**Optional:** Create a `.env` file to override the default API URL:
```bash
# Create .env file
echo "REACT_APP_API_URL=http://10.249.84.213:8000" > .env
```

Start the React development server:
```bash
npm start
```

The frontend will be accessible at:
- Local: `http://localhost:3000`
- Network: `http://10.249.84.213:3000`

## Production Deployment

For production use, build the React app and serve it:

### Build Frontend
```bash
cd ~/HackNotts25/front-end
REACT_APP_API_URL=http://10.249.84.213:8000 npm run build
```

### Serve with Python
```bash
# Install a simple HTTP server
pip install whitenoise

# Or use Python's built-in server
cd build
python -m http.server 3000
```

### Using PM2 for Process Management

Install PM2:
```bash
npm install -g pm2
```

Create ecosystem file `ecosystem.config.js`:
```javascript
module.exports = {
  apps: [{
    name: 'nhscribe-backend',
    script: 'app.py',
    interpreter: 'python3',
    cwd: '/home/pi/HackNotts25',
    env: {
      PYTHONUNBUFFERED: 1
    }
  }, {
    name: 'nhscribe-frontend',
    script: 'serve',
    args: '-s build -l 3000',
    cwd: '/home/pi/HackNotts25/front-end'
  }]
}
```

Start services:
```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

## Network Access

Once deployed, the application will be accessible from any device on the same network:

- **Frontend:** http://10.249.84.213:3000
- **Backend API:** http://10.249.84.213:8000
- **API Documentation:** http://10.249.84.213:8000/docs

## Configuration Files

### Backend CORS Settings
Location: `app.py` lines 37-50

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",           # Local React dev server
        "http://10.249.84.213:3000",       # React app on Pi
        "http://10.249.84.213:8000",       # Backend on Pi
        "*"                                 # Allow all origins for local network
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Frontend API Configuration
Location: `front-end/src/config.js`

```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://10.249.84.213:8000';
```

## Troubleshooting

### Cannot connect to backend
1. Check if backend is running: `curl http://10.249.84.213:8000`
2. Check firewall: `sudo ufw status`
3. Ensure port 8000 is open: `sudo ufw allow 8000`

### CORS errors
- CORS is already configured to allow all origins with `"*"`
- If issues persist, check browser console for specific error messages

### Frontend cannot fetch data
1. Verify API_BASE_URL in browser console: `console.log(window.location)`
2. Check network connectivity to Pi
3. Verify backend is responding: `curl http://10.249.84.213:8000/patients/`

### Database issues
- Database file location: `scribe.db` in project root
- Check permissions: `ls -la scribe.db`
- Reset database: `rm scribe.db` then restart backend

## Updating Configuration

### Change IP Address
If your Raspberry Pi IP changes, update:

1. Frontend config:
```bash
cd ~/HackNotts25/front-end
# Update src/config.js or set environment variable
export REACT_APP_API_URL=http://NEW_IP:8000
```

2. Backend CORS (if needed):
```python
# Edit app.py and add new IP to allow_origins list
```

## System Requirements

### Minimum
- Raspberry Pi 3B+ or newer
- 1GB RAM
- 8GB SD card
- Network connection

### Recommended
- Raspberry Pi 4 (4GB RAM) or newer
- 16GB+ SD card
- Ethernet connection for stability

## Security Notes

⚠️ **Important:** This configuration allows open network access and is suitable for:
- Local network deployments
- Development environments
- Trusted network environments

For production deployments with internet access, consider:
- Adding authentication
- Implementing proper CORS restrictions
- Using HTTPS
- Setting up a reverse proxy (nginx)
- Implementing rate limiting

## Support

For issues or questions:
1. Check the logs: `pm2 logs` (if using PM2)
2. Check backend logs: Look at terminal output where `python app.py` is running
3. Check frontend console: Open browser developer tools (F12)

## Quick Test

After deployment, test all endpoints:

```bash
# Test backend health
curl http://10.249.84.213:8000/

# Test patient endpoint
curl http://10.249.84.213:8000/patients/

# Test letters endpoint
curl http://10.249.84.213:8000/letters/recent
```

Visit in browser:
- Frontend: http://10.249.84.213:3000
- API Docs: http://10.249.84.213:8000/docs

