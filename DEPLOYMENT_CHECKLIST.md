# 🚀 Raspberry Pi Deployment Checklist

**Target IP:** `10.249.84.213`
**Backend Port:** `8000`
**Frontend Port:** `3000`

## ✅ Pre-Deployment (Completed)

- [X] Backend CORS configured for network access
- [X] Backend server set to listen on `0.0.0.0`
- [X] Frontend API URLs centralized in config file
- [X] All frontend components updated to use config
- [X] Start scripts created and made executable
- [X] Documentation created

## 📋 Deployment Steps

### Step 1: Transfer Files to Raspberry Pi

```bash
scp -r /Users/farhan/Documents/HackNotts25/HackNotts25 pi@10.249.84.213:~/
```

- [ ] Files transferred successfully
- [ ] SSH access to Pi confirmed

### Step 2: Prepare Raspberry Pi Environment

```bash
ssh pi@10.249.84.213
cd ~/HackNotts25
```

- [ ] Connected to Raspberry Pi
- [ ] In correct directory

### Step 3: Backend Setup

```bash
# Make start script executable
chmod +x start_backend.sh

# Start backend
./start_backend.sh
```

- [ ] Python dependencies installed
- [ ] Backend server running
- [ ] Accessible at http://10.249.84.213:8000

### Step 4: Frontend Setup (New Terminal/SSH Session)

```bash
ssh pi@10.249.84.213
cd ~/HackNotts25/front-end

# Make start script executable
chmod +x start_frontend.sh

# Start frontend
./start_frontend.sh
```

- [ ] Node.js dependencies installed
- [ ] Frontend server running
- [ ] Accessible at http://10.249.84.213:3000

## 🧪 Testing Checklist

### Backend API Tests

From any terminal:

```bash
# Test 1: API is responding
curl http://10.249.84.213:8000/

# Test 2: Patients endpoint
curl http://10.249.84.213:8000/patients/

# Test 3: Letters endpoint
curl http://10.249.84.213:8000/letters/recent
```

- [ ] API root responds
- [ ] Patients endpoint responds (empty array OK)
- [ ] Letters endpoint responds (empty array OK)

### Frontend Tests

From web browser:

- [ ] Navigate to http://10.249.84.213:3000
- [ ] Dashboard loads correctly
- [ ] "New Letter" button works
- [ ] Can access http://10.249.84.213:8000/docs

### Integration Tests

- [ ] Create new patient works
- [ ] Upload CSV works
- [ ] Generate letter works
- [ ] View letter in dashboard
- [ ] Edit letter works
- [ ] Download PDF works

## 🔍 Verification Points

### Network Connectivity

- [ ] Raspberry Pi is on network 10.249.84.x
- [ ] Other devices can ping 10.249.84.213
- [ ] Firewall allows ports 8000 and 3000

### Service Status

- [ ] Backend process is running (check with `ps aux | grep python`)
- [ ] Frontend process is running (check with `ps aux | grep node`)
- [ ] No error messages in terminal outputs

### Database

- [ ] `scribe.db` file exists in project root
- [ ] File has read/write permissions
- [ ] Can query database (backend starts successfully)

## 🚨 Troubleshooting Checklist

If something doesn't work:

### Backend Issues

- [ ] Check Python version: `python3 --version` (need 3.8+)
- [ ] Check if port 8000 is in use: `sudo netstat -tulpn | grep 8000`
- [ ] Check backend logs in terminal
- [ ] Verify requirements.txt installed: `pip list`
- [ ] Check file permissions: `ls -la scribe.db`

### Frontend Issues

- [ ] Check Node version: `node --version` (need 16+)
- [ ] Check if port 3000 is in use: `sudo netstat -tulpn | grep 3000`
- [ ] Check frontend logs in terminal
- [ ] Verify node_modules installed: `ls -la node_modules/`
- [ ] Clear cache: `rm -rf node_modules package-lock.json && npm install`

### Network Issues

- [ ] Verify IP address: `hostname -I`
- [ ] Check firewall: `sudo ufw status`
- [ ] Test from Pi itself: `curl http://localhost:8000`
- [ ] Test from another device on network
- [ ] Check CORS settings in app.py

### CORS Issues

- [ ] Open browser console (F12)
- [ ] Check for CORS error messages
- [ ] Verify API_BASE_URL in config.js
- [ ] Check CORS settings in app.py line 37-50

## 📊 Configuration Summary

### Files Modified/Created

| File                                    | Purpose              | Status     |
| --------------------------------------- | -------------------- | ---------- |
| `app.py`                              | CORS + Server config | ✅ Updated |
| `front-end/src/config.js`             | API base URL         | ✅ Created |
| `front-end/src/NewLetter.jsx`         | Use config           | ✅ Updated |
| `front-end/src/NHScribeDashboard.jsx` | Use config           | ✅ Updated |
| `front-end/src/ReviewLetter.jsx`      | Use config           | ✅ Updated |
| `start_backend.sh`                    | Backend launcher     | ✅ Created |
| `front-end/start_frontend.sh`         | Frontend launcher    | ✅ Created |
| `DEPLOYMENT.md`                       | Full guide           | ✅ Created |
| `QUICKSTART.md`                       | Quick reference      | ✅ Created |

### Key Configuration Values

```javascript
// Frontend: front-end/src/config.js
const API_BASE_URL = 'http://10.249.84.213:8000';
```

```python
# Backend: app.py line 451
uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
```

## 🎯 Success Criteria

Your deployment is successful when:

✅ Backend responds at http://10.249.84.213:8000
✅ Frontend loads at http://10.249.84.213:3000
✅ API docs accessible at http://10.249.84.213:8000/docs
✅ Can create patients from any device on network
✅ Can upload CSV files
✅ Can generate letters
✅ Can view and edit letters
✅ Can download PDFs
✅ No CORS errors in browser console
✅ Both services run without crashing

## 📱 Access URLs

**From Raspberry Pi:**

- Frontend: http://localhost:3000
- Backend: http://localhost:8000

**From Other Devices on Network:**

- Frontend: http://10.249.84.213:3000
- Backend: http://10.249.84.213:8000
- API Docs: http://10.249.84.213:8000/docs

## 🔄 Post-Deployment

### Optional: Set Up Automatic Startup

Using PM2:

```bash
npm install -g pm2
pm2 start app.py --name nhscribe-backend --interpreter python3
cd front-end && npm run build
pm2 serve build 3000 --name nhscribe-frontend
pm2 save
pm2 startup
```

- [ ] PM2 installed
- [ ] Services added to PM2
- [ ] Auto-start configured

### Regular Maintenance

- [ ] Set up database backups
- [ ] Monitor disk space
- [ ] Check logs periodically
- [ ] Update dependencies monthly

## 📞 Support Resources

- **Full Guide:** DEPLOYMENT.md
- **Quick Reference:** QUICKSTART.md
- **API Documentation:** http://10.249.84.213:8000/docs
- **Project README:** README.md

---

**Date Prepared:** October 26, 2025
**Target System:** Raspberry Pi at 10.249.84.213
**Configuration Status:** ✅ Complete and Ready for Deployment
