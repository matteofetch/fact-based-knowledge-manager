# Fact-Based Knowledge Manager

An autonomous knowledge management system that maintains a fact-based knowledge base by processing Slack messages and updating facts automatically using ChatGPT API.

## 🚀 Project Overview

This system reads project updates from Slack, processes them through ChatGPT API with knowledge management guidelines, and maintains an up-to-date fact-based knowledge base. Built for hackathon rapid development with clean architecture for easy feature expansion.

**Current Phase**: Section 1a - Hardcoded Flow (for testing and prompt iteration)

## 🛠 Tech Stack

- **Backend**: Python (Vercel serverless functions)
- **AI**: ChatGPT API (GPT-4)
- **Storage**: Google Sheets API (planned)
- **Integration**: Zapier (Slack ↔ Vercel webhooks) (planned)
- **Deployment**: Vercel

## 📋 Current Features

### ✅ Implemented (Phase 1a - Hardcoded)
- Hardcoded Slack message processing
- Hardcoded knowledge base guidelines
- Hardcoded current fact-based knowledge base
- ChatGPT API integration with comprehensive logging
- Error handling and health checks
- Vercel serverless deployment ready
- Clean architecture for easy API swapping

### 🔄 Planned (Phase 1b - Full Integration)
- Live Slack message integration via Zapier
- Google Docs integration for guidelines
- Google Sheets integration for knowledge base
- Automatic fact base updates

## 🏗 Project Structure

```
fact-based-knowledge-manager/
├── api/
│   └── process.py              # Vercel serverless function
├── src/
│   ├── __init__.py
│   ├── models.py               # Data models
│   ├── hardcoded_data.py       # Test data (Phase 1a)
│   ├── logger.py               # Comprehensive logging
│   ├── chatgpt_service.py      # ChatGPT API integration
│   └── knowledge_processor.py  # Main orchestration
├── requirements.txt            # Python dependencies
├── vercel.json                # Vercel configuration
├── test_local.py              # Local testing script
├── .gitignore
├── roadmap.md                 # Project roadmap
├── knowledge-guidelines.md    # Knowledge management rules
├── sample-knowledge-base.md   # Example fact structure
└── README.md
```

## 🚦 Quick Start

### 1. Setup Environment

```bash
# Clone or download the project
cd fact-based-knowledge-manager

# Install dependencies
pip install -r requirements.txt

# Create environment file
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
echo "ENVIRONMENT=development" >> .env
```

### 2. Get OpenAI API Key

1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add it to your `.env` file

### 3. Test Locally

```bash
# Run local tests
python test_local.py
```

This will:
- Check your environment setup
- Test ChatGPT API connectivity  
- Run the hardcoded knowledge processing flow
- Show detailed logs for debugging

### 4. Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel deploy

# Set environment variables in Vercel dashboard
# Go to your project settings and add:
# OPENAI_API_KEY=your_key_here
# ENVIRONMENT=production
```

## 📡 API Endpoints

### GET `/api/process`
Returns API information and available endpoints.

### GET `/api/process/health`
System health check - tests all components.

```json
{
  "overall_status": "healthy",
  "components": {
    "chatgpt_api": {
      "status": "healthy",
      "details": "Connection successful"
    },
    "environment": {
      "status": "healthy", 
      "details": "All required environment variables present"
    },
    "hardcoded_data": {
      "status": "healthy",
      "details": "Loaded 10 facts and 6891 character guidelines"
    }
  }
}
```

### POST `/api/process/hardcoded`
Runs the complete hardcoded knowledge processing flow.

**Response:**
```json
{
  "success": true,
  "processing_log": "Processing completed with 8 log entries:\n[12:34:56] INFO: Starting hardcoded knowledge processing flow\n...",
  "updated_knowledge_base": {
    "title": "Current RN Project Facts",
    "facts": [
      {
        "number": 1,
        "description": "Rewards Network (RN) is a network of ~18 000 local restaurants...",
        "last_validated": "2025-01-15"
      }
    ]
  },
  "updated_knowledge_base_markdown": "# Current RN Project Facts\n\n| **#** | **Fact** | **Time Last Validated** |\n..."
}
```

### POST `/api/process/custom`
Process custom knowledge update request (for future integrations).

**Request Body:**
```json
{
  "slack_message": {
    "content": "Your slack message content",
    "channel": "#updates",
    "user": "project-manager"
  },
  "current_knowledge_base": {
    "title": "Current RN Project Facts",
    "facts": [...]
  },
  "guidelines": "Your knowledge management guidelines..."
}
```

## 🔍 Testing the System

### Local Testing
```bash
python test_local.py
```

### Production Testing
```bash
# Health check
curl https://your-domain.vercel.app/api/process/health

# Run hardcoded flow
curl -X POST https://your-domain.vercel.app/api/process/hardcoded
```

## 📊 Logging & Debugging

The system includes comprehensive logging:

- **Request/Response logging**: Full ChatGPT API interactions
- **Processing flow logging**: Step-by-step execution tracking
- **Error logging**: Detailed error context and stack traces
- **Performance logging**: Token usage and timing data

All logs are returned in API responses for easy debugging during development.

## 🎯 Sample Hardcoded Data

The system currently uses these hardcoded inputs for testing:

**Slack Message:**
```
Here's this week's Atlas update:
- 11,156 offers live (last: 11,287)  
- Restaurant coverage: 62.0% (last: 62.7%)
- Card capture rate: 53.8% (last: 54.1%)
- ARR: $8.7M (last: $8.5M)
```

**Knowledge Base:** 10 facts about the RN project (see `sample-knowledge-base.md`)

**Guidelines:** Comprehensive fact management rules (see `knowledge-guidelines.md`)

## 🛣 Next Steps (Roadmap)

### Phase 1b - Full Integration
1. Slack API integration via Zapier
2. Google Docs integration for guidelines
3. Google Sheets integration for knowledge base storage
4. Real-time fact base updates

### Phase 2 - Agentic Knowledge Management
1. Automated task generation
2. Independent task execution
3. Slack-based human-in-the-loop tasks

See `roadmap.md` for detailed development phases.

## 🔧 Development

### Architecture Principles
- **Clean separation**: Data sources (hardcoded → APIs) easily swappable
- **Comprehensive logging**: All ChatGPT interactions logged for prompt iteration
- **Error resilience**: Graceful failures with informative messages
- **Testability**: Local testing before deployment

### Key Components
- **Models**: Pydantic data models for type safety
- **Logger**: Structured logging with different levels
- **ChatGPT Service**: API integration with response parsing
- **Knowledge Processor**: Main orchestration logic
- **Vercel Handler**: HTTP request/response handling

## 🐛 Troubleshooting

### Common Issues

**"OPENAI_API_KEY not found"**
- Create a `.env` file with your API key
- For Vercel, add the environment variable in your project settings

**"Connection failed" in health check**
- Verify your OpenAI API key is valid
- Check your internet connection
- Ensure you have sufficient API credits

**"Failed to parse table row"**
- This indicates ChatGPT returned an unexpected format
- Check the full logs to see the actual response
- May need to adjust the prompt or parsing logic

### Getting Help
1. Check the `processing_log` in API responses
2. Run `python test_local.py` for detailed local diagnostics
3. Use the `/health` endpoint to check system status
4. Review ChatGPT request/response logs for prompt debugging

## 📄 License

This project is built for hackathon use. Feel free to adapt and extend for your needs. 