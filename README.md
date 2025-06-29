# Multi-Service MCP Server

A comprehensive Model Context Protocol (MCP) server that provides unified API access to multiple services including GitHub, Jira, and Slack. Built with FastAPI and designed for modern application integrations.

## 🚀 Features

- **GitHub Integration**: Repository management, issue tracking, and more
- **Jira Integration**: Issue creation, retrieval, and project management
- **Slack Integration**: Channel management, message sending, and chat history
- **RESTful API**: Clean, documented endpoints for all services
- **Async Support**: Built with FastAPI for high-performance async operations
- **CORS Enabled**: Ready for web application integrations
- **Environment-based Configuration**: Secure credential management
- **Docker Ready**: Includes Render deployment configuration

## 📋 Prerequisites

- Python 3.11+
- Active accounts and API tokens for:
  - GitHub (Personal Access Token)
  - Jira (API Token)
  - Slack (Bot Token and App Token)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd MCP
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   GITHUB_TOKEN=your_github_personal_access_token
   
   JIRA_URL=https://your-domain.atlassian.net
   JIRA_USERNAME=your_email@example.com
   JIRA_API_TOKEN=your_jira_api_token
   
   SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
   SLACK_APP_TOKEN=xapp-your-slack-app-token
   
   PORT=8000
   HOST=0.0.0.0
   ```

## 🚦 Running the Server

### Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`

## 📚 API Documentation

Once the server is running, you can access:
- **Interactive API Docs**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## 🔌 API Endpoints

### GitHub Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/github/repos/{username}` | Get user's repositories |
| GET | `/github/issues/{repo_name}` | Get repository issues |

### Jira Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/jira/issues` | Get Jira issues (optional project filter) |
| POST | `/jira/issues` | Create a new Jira issue |

### Slack Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/slack/channels` | Get Slack channels |
| POST | `/slack/messages` | Send a message to Slack |
| GET | `/slack/messages/{channel}` | Get messages from a channel |

### General Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Server status and information |

## 🏗️ Project Structure

```
MCP/
├── main.py              # FastAPI application and routes
├── config.py            # Configuration and settings
├── models.py            # Pydantic models for API requests/responses
├── services.py          # Service classes for external API integrations
├── requirements.txt     # Python dependencies
├── render.yaml          # Render deployment configuration
├── .env                 # Environment variables (not in version control)
└── README.md           # Project documentation
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_TOKEN` | GitHub Personal Access Token | Yes |
| `JIRA_URL` | Your Jira instance URL | Yes |
| `JIRA_USERNAME` | Your Jira username/email | Yes |
| `JIRA_API_TOKEN` | Jira API token | Yes |
| `SLACK_BOT_TOKEN` | Slack Bot User OAuth Token | Yes |
| `SLACK_APP_TOKEN` | Slack App-Level Token | Yes |
| `PORT` | Server port (default: 8000) | No |
| `HOST` | Server host (default: 0.0.0.0) | No |

### Setting Up API Tokens

#### GitHub
1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Generate a new token with appropriate scopes (repo, read:user)

#### Jira
1. Go to Jira Settings > Products > Application access
2. Create an API token for your account

#### Slack
1. Create a new Slack app at https://api.slack.com/apps
2. Enable necessary scopes (channels:read, chat:write, etc.)
3. Install the app to your workspace

## 🚀 Deployment

### Render Deployment

This project includes a `render.yaml` file for easy deployment to Render:

1. Connect your GitHub repository to Render
2. Set up environment variables in Render dashboard
3. Deploy using the provided configuration

### Docker Deployment

```dockerfile
# Example Dockerfile (create as needed)
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🧪 Testing

You can test the API endpoints using:

- **curl**: Command-line HTTP client
- **Postman**: API development environment
- **httpx**: Python HTTP client

Example:
```bash
# Test server status
curl http://localhost:8000/

# Get GitHub repositories
curl "http://localhost:8000/github/repos/octocat"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔒 Security

- Never commit your `.env` file or API tokens to version control
- Use environment variables for all sensitive configuration
- Regularly rotate your API tokens
- Follow the principle of least privilege for API token scopes

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Errors**: Verify your API tokens are correct and have sufficient permissions
2. **CORS Issues**: The server includes CORS middleware; check your client configuration
3. **Rate Limiting**: External APIs may have rate limits; implement appropriate retry logic

### Debug Mode

Set `DEBUG=True` in your environment to enable detailed error messages.

## 📞 Support

For issues, questions, or contributions, please open an issue in the GitHub repository.

---

Built with ❤️ using FastAPI and modern Python
