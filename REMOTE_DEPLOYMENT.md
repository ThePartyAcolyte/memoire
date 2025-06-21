# MnemoX Lite - Remote Deployment Guide

This guide covers deploying MnemoX Lite to cloud platforms for centralized access from multiple clients/devices.

## 🚀 Deployment on Render.com

### Prerequisites
- GitHub repository with this code
- Google AI API key
- Render.com account (free tier available)

### Step 1: Setup Repository
```bash
# Ensure you're on the remote-deployment branch
git checkout remote-deployment

# Commit all changes
git add .
git commit -m "Add remote deployment configuration"
git push origin remote-deployment
```

### Step 2: Deploy on Render.com
1. Go to [render.com](https://render.com) and connect your GitHub
2. Create new **Web Service**
3. Select your `mnemox-lite` repository
4. Choose branch: `remote-deployment`
5. Render will automatically detect `render.yaml` configuration

### Step 3: Configure Environment Variables
In Render dashboard, set:
- `GOOGLE_API_KEY`: Your Google AI API key
- `PORT`: `8080` (auto-configured)
- `ENABLE_GUI`: `false` (auto-configured)

### Step 4: Deploy
- Click **Deploy**
- Wait for build to complete
- Note your service URL: `https://your-app-name.onrender.com`

## 🔌 Client Configuration

### For Claude Desktop
Edit your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mnemox-remote": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-websocket", "wss://your-app-name.onrender.com"],
      "env": {}
    }
  }
}
```

### For Multiple Clients
Each client (different computers, users) uses the same configuration pointing to your deployed URL.

**Benefits:**
- ✅ Shared memory across all clients
- ✅ Centralized data storage
- ✅ No local setup required on client machines
- ✅ Automatic scaling and maintenance

## 📊 Monitoring & Management

### Render.com Dashboard
- **Logs**: View server logs and errors
- **Metrics**: CPU, memory, network usage
- **Environment**: Manage environment variables
- **Scaling**: Upgrade to paid plans for better performance

### Health Check
Test your deployment:
```bash
# Test WebSocket connection
wscat -c wss://your-app-name.onrender.com
```

### Data Persistence
- SQLite database and Qdrant vector store persist on Render's disk
- Free tier includes 1GB persistent storage
- Data survives deployments and restarts

## 🛠️ Alternative Deployment Options

### Fly.io
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Deploy
fly deploy
```

### Railway (if using paid plan)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway deploy
```

### Self-hosted (VPS/Raspberry Pi)
```bash
# On your server
git clone https://github.com/your-username/mnemox-lite
cd mnemox-lite
git checkout remote-deployment

# Setup environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export GOOGLE_API_KEY="your-key"
export PORT="8080"
export ENABLE_GUI="false"

# Run server
python run_remote.py
```

## 🔒 Security Considerations

### Environment Variables
- Never commit API keys to git
- Use Render's environment variable system
- Rotate API keys regularly

### Network Security
- HTTPS/WSS encryption by default on Render
- No additional authentication implemented (consider adding if needed)
- Logs may contain sensitive information

### Data Privacy
- Data stored on Render's infrastructure
- Consider data location requirements for your use case
- Regular backups recommended for important data

## 📈 Performance Optimization

### Free Tier Limitations
- **Render.com**: 750 hours/month, sleeps after 15min inactivity
- **Cold starts**: 10-30 seconds wake-up time
- **Memory**: 512MB RAM limit

### Optimization Tips
- Use paid tier for always-on service
- Implement connection pooling for multiple clients
- Consider CDN for static assets if adding web interface

## 🐛 Troubleshooting

### Common Issues

**Connection Refused**
- Check if service is running in Render dashboard
- Verify WebSocket URL format: `wss://your-app.onrender.com`

**Cold Start Delays**
- Normal on free tier - first request takes 10-30s
- Upgrade to paid tier for instant response

**Memory Errors**
- Reduce `max_results` in search configuration
- Clear old data: projects with many fragments

**API Rate Limits**
- Google AI has generous free tier limits
- Monitor usage in Google AI Studio

### Debug Commands
```bash
# Check server logs
# (In Render dashboard -> Logs tab)

# Test connection locally
python -c "import asyncio; import websockets; asyncio.run(websockets.connect('wss://your-app.onrender.com'))"
```

## 🔄 Updates & Maintenance

### Updating Code
```bash
# Make changes in remote-deployment branch
git add .
git commit -m "Update feature"
git push origin remote-deployment

# Render auto-deploys on push
```

### Database Migrations
- SQLite schema changes require careful planning
- Consider backup/restore for major changes
- Test migrations on staging environment

### Monitoring
- Set up Render notifications for deployment failures
- Monitor Google AI API usage quotas
- Regular health checks recommended

---

## 📞 Getting Started Checklist

- [ ] Repository pushed to GitHub
- [ ] Render.com account created
- [ ] Google AI API key obtained
- [ ] Web service created on Render
- [ ] Environment variables configured
- [ ] Deployment successful
- [ ] Client configuration updated
- [ ] Connection tested
- [ ] Memory operations working

**Your centralized MnemoX server is ready! 🎉**

All clients can now share the same semantic memory across devices and conversations.