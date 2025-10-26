# NHScribe - Quick Start Guide for Raspberry Pi

## 🚀 One-Command Start

### On Raspberry Pi (After transferring files):

**Terminal 1 - Start Backend:**
```bash
cd ~/HackNotts25
./start_backend.sh
```

**Terminal 2 - Start Frontend:**
```bash
cd ~/HackNotts25/front-end
./start_frontend.sh
```

## 🌐 Access the Application

Once both services are running:

- **Main Application:** http://10.249.84.213:3000
- **API Documentation:** http://10.249.84.213:8000/docs
- **API Endpoint:** http://10.249.84.213:8000

## ✅ Pre-Configured Settings

Your application is already configured for Raspberry Pi deployment:

| Component | Configuration | Status |
|-----------|--------------|--------|
| Backend Host | 0.0.0.0:8000 | ✅ Ready |
| CORS | Network Access Enabled | ✅ Ready |
| Frontend API | http://10.249.84.213:8000 | ✅ Ready |
| Static Files | /letters directory | ✅ Ready |

## 📦 First-Time Setup on Raspberry Pi

```bash
# 1. Transfer project
scp -r /Users/farhan/Documents/HackNotts25/HackNotts25 pi@10.249.84.213:~/

# 2. SSH into Raspberry Pi
ssh pi@10.249.84.213

# 3. Navigate to project
cd ~/HackNotts25

# 4. Make scripts executable
chmod +x start_backend.sh
chmod +x front-end/start_frontend.sh

# 5. Start backend (in terminal 1)
./start_backend.sh

# 6. Start frontend (in terminal 2 - new SSH session)
cd front-end
./start_frontend.sh
```

## 🔧 Configuration Files

### API Configuration
**File:** `front-end/src/config.js`
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://10.249.84.213:8000';
```

### Backend Server
**File:** `app.py` (line 451)
```python
uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
```

## 🧪 Test Your Deployment

```bash
# Test backend is running
curl http://10.249.84.213:8000/

# Test patients endpoint
curl http://10.249.84.213:8000/patients/

# Test recent letters
curl http://10.249.84.213:8000/letters/recent
```

## 📱 Access from Other Devices

From any device on the same network (10.249.84.x):

1. Open web browser
2. Navigate to: http://10.249.84.213:3000
3. Start using NHScribe!

## 🐛 Quick Troubleshooting

### Backend not accessible?
```bash
# Check if running
curl http://10.249.84.213:8000

# Check port is open
sudo netstat -tulpn | grep 8000

# Restart backend
pkill -f "python app.py"
./start_backend.sh
```

### Frontend not loading?
```bash
# Check Node.js process
ps aux | grep node

# Restart frontend
pkill -f "react-scripts"
cd front-end && ./start_frontend.sh
```

### Network access issues?
```bash
# Check Raspberry Pi IP
hostname -I

# Check firewall
sudo ufw status

# Allow ports if needed
sudo ufw allow 8000
sudo ufw allow 3000
```

## 🔄 Update IP Address

If your Raspberry Pi IP changes, update:

```bash
# 1. Update frontend config
nano ~/HackNotts25/front-end/src/config.js
# Change: const API_BASE_URL = 'http://NEW_IP:8000';

# 2. Rebuild frontend (optional, for production)
cd ~/HackNotts25/front-end
npm run build
```

## 📊 Production Deployment

For 24/7 operation, use PM2:

```bash
# Install PM2
npm install -g pm2

# Start backend
pm2 start app.py --name nhscribe-backend --interpreter python3

# Start frontend (after building)
cd front-end
npm run build
pm2 serve build 3000 --name nhscribe-frontend

# Save PM2 configuration
pm2 save
pm2 startup
```

## 📚 Additional Resources

- Full deployment guide: `DEPLOYMENT.md`
- API documentation: http://10.249.84.213:8000/docs
- Project README: `README.md`

## 🎯 Key Features Verified

✅ Patient management  
✅ CSV upload for test results  
✅ AI-powered letter generation  
✅ Letter review and editing  
✅ PDF export  
✅ Status tracking  
✅ Network accessibility  

## 💡 Tips

1. **Always start backend before frontend** - Frontend needs backend API
2. **Use tmux/screen** - Run services in persistent sessions
3. **Check logs** - Look at terminal output for errors
4. **Test locally first** - Use localhost before network access
5. **Keep backups** - Backup `scribe.db` regularly

---

**Need help?** Check the detailed `DEPLOYMENT.md` guide or review the configuration in `front-end/src/config.js` and `app.py`.

