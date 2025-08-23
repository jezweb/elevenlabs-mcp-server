# Deployment Guide

This guide covers deploying the ElevenLabs MCP servers to FastMCP Cloud.

## Prerequisites

1. **ElevenLabs API Key**
   - Get your API key from [ElevenLabs Dashboard](https://elevenlabs.io/api-keys)
   - Keep it secure - you'll need it for deployment

2. **GitHub Repository**
   - Push this code to a GitHub repository
   - Ensure it's public or FastMCP has access

3. **FastMCP Cloud Account**
   - Sign up at [FastMCP Cloud](https://fastmcp.com)
   - Verify your account

## Pre-Deployment Checklist

### 1. Test Locally
```bash
# Set environment variable
export ELEVENLABS_API_KEY=your-key-here

# Test agents server
cd elevenlabs-agents
python src/server.py --test

# Test knowledge server
cd elevenlabs-knowledge
python src/server.py --test
```

### 2. Verify Server Objects
```bash
# Check that server objects are at module level
python -c "from elevenlabs_agents.src.server import mcp; print('✅ Agents server OK')"
python -c "from elevenlabs_knowledge.src.server import mcp; print('✅ Knowledge server OK')"
```

## FastMCP Cloud Deployment

### Step 1: Push to GitHub

```bash
# Add all files
git add .

# Commit with descriptive message
git commit -m "feat: initial ElevenLabs MCP servers implementation"

# Push to GitHub
git push origin main
```

### Step 2: Deploy Agents Server

1. Go to [FastMCP Cloud Dashboard](https://fastmcp.com/dashboard)
2. Click "New Server"
3. Configure:

```yaml
Name: elevenlabs-agents-{your-username}
Repository: {your-github-username}/elevenlabs-mcp-server
Branch: main
Entrypoint: elevenlabs-agents/src/server.py
Requirements: elevenlabs-agents/requirements.txt
```

4. Add Environment Variables:
```
ELEVENLABS_API_KEY=your-api-key-here
LOG_LEVEL=INFO
```

5. Resource Configuration:
   - Build: 2 vCPU / 4GB RAM
   - Runtime: 1 vCPU / 2GB RAM

6. Click "Deploy"

### Step 3: Deploy Knowledge Server

1. Click "New Server" again
2. Configure:

```yaml
Name: elevenlabs-knowledge-{your-username}
Repository: {your-github-username}/elevenlabs-mcp-server
Branch: main
Entrypoint: elevenlabs-knowledge/src/server.py
Requirements: elevenlabs-knowledge/requirements.txt
```

3. Add same Environment Variables:
```
ELEVENLABS_API_KEY=your-api-key-here
LOG_LEVEL=INFO
```

4. Same Resource Configuration
5. Click "Deploy"

## Post-Deployment Verification

### 1. Check Server Status
Both servers should show "Running" status in the dashboard.

### 2. Test Endpoints
```bash
# Test agents server
curl https://elevenlabs-agents-{username}.fastmcp.app/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'

# Test knowledge server
curl https://elevenlabs-knowledge-{username}.fastmcp.app/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

### 3. Check Logs
View logs in FastMCP Cloud dashboard to ensure no errors.

## Client Configuration

### Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "elevenlabs-agents": {
      "url": "https://elevenlabs-agents-{username}.fastmcp.app/mcp",
      "transport": "http"
    },
    "elevenlabs-knowledge": {
      "url": "https://elevenlabs-knowledge-{username}.fastmcp.app/mcp",
      "transport": "http"
    }
  }
}
```

### Other MCP Clients

Use the server URLs:
- Agents: `https://elevenlabs-agents-{username}.fastmcp.app/mcp`
- Knowledge: `https://elevenlabs-knowledge-{username}.fastmcp.app/mcp`

## Updating Deployments

### Code Updates
1. Make changes locally
2. Run `./scripts/copy-shared.sh`
3. Test locally
4. Commit and push to GitHub
5. FastMCP Cloud auto-deploys on push

### Environment Variable Updates
1. Go to server settings in FastMCP Cloud
2. Update environment variables
3. Restart server

## Troubleshooting

### "No server object found"
- Ensure `mcp` object is at module level in server.py
- Run `./scripts/copy-shared.sh` before deployment
- Check that server.py doesn't wrap server creation in functions

### "Failed to install dependencies"
- Check requirements.txt has only PyPI packages
- Remove any `-e` or local path references
- Ensure all package names are correct

### "Import error: shared module not found"
- Run `./scripts/copy-shared.sh`
- Verify shared/ was copied to each server's src/
- Check .gitignore isn't excluding the copied shared/ directories

### "API connection failed"
- Verify ELEVENLABS_API_KEY is set correctly
- Check API key has proper permissions
- Ensure API key is active and not expired

### Server Not Starting
1. Check logs in FastMCP Cloud dashboard
2. Verify all imports work locally
3. Ensure Python version compatibility
4. Check for syntax errors

### High Response Times
- Increase runtime resources (2 vCPU / 4GB RAM)
- Check if API rate limits are being hit
- Review logs for timeout errors
- Consider implementing caching

## Monitoring

### Health Checks
FastMCP Cloud automatically monitors:
- Server availability
- Response times
- Error rates
- Resource usage

### Custom Monitoring
View metrics in the dashboard:
- Request count
- Average response time
- Error logs
- Resource utilization

## Cost Optimization

### Tips for Reducing Costs
1. Start with minimal resources (1 vCPU / 2GB RAM)
2. Scale up only if needed
3. Implement response caching
4. Batch API requests when possible
5. Use connection pooling

### Resource Scaling
Monitor these metrics to decide on scaling:
- Response time > 2 seconds: Scale up
- Memory usage > 80%: Add more RAM
- CPU usage > 70%: Add more vCPU
- Frequent timeouts: Increase both

## Security Best Practices

1. **Never commit .env files**
2. **Rotate API keys regularly**
3. **Use environment variables for all secrets**
4. **Monitor access logs**
5. **Keep dependencies updated**

## Rollback Procedure

If deployment fails:
1. Check error logs in dashboard
2. Revert to previous Git commit
3. Push to trigger re-deployment
4. Or use "Rollback" button in FastMCP Cloud

## Support

### FastMCP Cloud Issues
- Documentation: [docs.fastmcp.com](https://docs.fastmcp.com)
- Support: support@fastmcp.com

### ElevenLabs API Issues
- Documentation: [elevenlabs.io/docs](https://elevenlabs.io/docs)
- Discord: [discord.gg/elevenlabs](https://discord.gg/elevenlabs)

### This Project
- GitHub Issues: Create issue in your repository
- Check TROUBLESHOOTING.md for common problems

## Deployment Checklist Summary

- [ ] API key obtained and tested
- [ ] Code pushed to GitHub
- [ ] `./scripts/copy-shared.sh` executed
- [ ] Local tests passing
- [ ] Server objects at module level verified
- [ ] FastMCP Cloud servers created
- [ ] Environment variables configured
- [ ] Deployment successful
- [ ] Endpoints responding
- [ ] Client configured
- [ ] Monitoring active

Remember: Always run `./scripts/copy-shared.sh` before deployment!