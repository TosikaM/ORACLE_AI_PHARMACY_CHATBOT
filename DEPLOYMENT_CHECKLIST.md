# DEPLOYMENT CHECKLIST

Use this checklist to ensure you have everything ready for deployment.

## ✅ Pre-Deployment Checklist

### Files Ready
- [ ] .gitignore exists in root folder
- [ ] requirements.txt exists
- [ ] All Python files in correct folders
- [ ] config/.env has all your secrets (but won't be uploaded!)
- [ ] database/wallet/ has wallet files (but won't be uploaded!)

### Test Locally First
- [ ] Chatbot works when running: `streamlit run ui/chatbot_ui.py`
- [ ] Can ask questions and get responses
- [ ] Database connection working
- [ ] SmartClient showing status correctly

### Secrets Prepared
- [ ] All 4 Google API keys copied
- [ ] Oracle ADMIN password copied
- [ ] Oracle DSN copied (e.g., pharmacydb_high)
- [ ] Wallet password copied
- [ ] Ran `encode_wallet.py` and copied encoded wallet

### Git Ready
- [ ] Git installed (`git --version` works)
- [ ] Git configured with your name and email

### GitHub Ready
- [ ] GitHub account created
- [ ] Logged into GitHub
- [ ] Ready to create repository

## 📝 Step-by-Step Deployment

### Phase 1: Push to GitHub
1. Create GitHub repository (Private recommended)
2. Copy repository URL
3. Run these commands in project folder:
   ```
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_REPO_URL
   git branch -M main
   git push -u origin main
   ```
4. Verify on GitHub that .env and wallet files are NOT visible

### Phase 2: Deploy to Streamlit
1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Select repository: YOUR_USERNAME/pharmacy-chatbot
5. Branch: main
6. Main file: ui/chatbot_ui.py
7. Click "Advanced settings"
8. Paste secrets in TOML format
9. Click "Deploy"
10. Wait 2-3 minutes
11. Test your live app!

## 🔐 Secrets Format for Streamlit

```toml
[google_api]
key_1 = "AIzaSy..."
key_2 = "AIzaSy..."
key_3 = "AIzaSy..."
key_4 = "AIzaSy..."

[oracle]
user = "ADMIN"
password = "your_admin_password"
dsn = "pharmacydb_high"

[oracle_wallet]
wallet_password = "your_wallet_password"
cwallet_sso_base64 = "very_long_encoded_string_from_encode_wallet.py"
```

## ⚠️ Common Issues

**Issue:** Can't push to GitHub - "rejected"
**Solution:** Make sure you haven't created README on GitHub. Use empty repository.

**Issue:** Streamlit deployment fails with "Module not found"
**Solution:** Check requirements.txt has all packages with correct spelling.

**Issue:** "Database connection failed" on Streamlit
**Solution:** Double-check all Oracle credentials in secrets, especially the encoded wallet.

**Issue:** "No module named 'config'"
**Solution:** Make sure main file is set to `ui/chatbot_ui.py` not just `chatbot_ui.py`

## 🎉 Success!

When deployment succeeds, you'll have a URL like:
`https://YOUR_USERNAME-pharmacy-chatbot.streamlit.app`

Share this URL to access your chatbot from anywhere!
