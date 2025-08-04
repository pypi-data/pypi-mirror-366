---
title: "Troubleshooting Guide"
layout: single
permalink: /troubleshooting/
sidebar:
  nav: "docs"
toc: true
toc_label: "Troubleshooting"
toc_icon: "wrench"
---

This guide helps you resolve common issues when setting up and using Insight Ingenious - an enterprise-grade Python library for quickly setting up APIs to interact with AI Agents. The library includes comprehensive debugging utilities to help diagnose and resolve deployment issues.

## Quick Test Commands

### Hello World Test (bike-insights)
```bash
# The "Hello World" of Ingenious - try this first!
# Note: Default port is 80, but use 8000 for development to avoid permission issues
curl -X POST http://localhost:80/api/v1/chat \
   -H "Content-Type: application/json" \
   -d '{
   "user_prompt": "{\"stores\": [{\"name\": \"Hello Store\", \"location\": \"NSW\", \"bike_sales\": [{\"product_code\": \"HELLO-001\", \"quantity_sold\": 1, \"sale_date\": \"2023-04-01\", \"year\": 2023, \"month\": \"April\", \"customer_review\": {\"rating\": 5.0, \"comment\": \"Perfect introduction!\"}}], \"bike_stock\": []}], \"revision_id\": \"hello-1\", \"identifier\": \"world\"}",
   "conversation_flow": "bike-insights"
   }'
```

### Simple Alternative Test (classification-agent)
```bash
# If bike-insights seems too complex, try this simpler workflow
curl -X POST http://localhost:80/api/v1/chat \
   -H "Content-Type: application/json" \
   -d '{
   "user_prompt": "Analyze this feedback: Great product!",
   "conversation_flow": "classification-agent"
   }'
```

---

## Important Configuration Notes

### Environment Variable Prefix
All Ingenious configuration uses the `INGENIOUS_` prefix with double underscores (`__`) for nested settings:
- ✅ `INGENIOUS_WEB_CONFIGURATION__PORT=8080`
- ❌ `WEB_PORT=8080` (legacy, not recommended)
- ✅ `INGENIOUS_MODELS__0__API_KEY=your-key`
- ❌ `AZURE_OPENAI_API_KEY=your-key` (not used by Ingenious)

## Common Setup Issues

### 1. Profile Validation Errors

**Symptoms**:
```
ValidationError: validation error for IngeniousSettings
models.0.api_key
  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
```

**Causes**:
- Environment variables not set or empty
- Missing required INGENIOUS_ prefixed variables
- Incorrect environment variable syntax

**Solutions**:

1. **Check your .env file**:
   ```bash
   # Make sure .env exists and has these minimum variables
   cat .env
   ```
   Should contain:
   ```env
   # Model configuration (required)
   INGENIOUS_MODELS__0__MODEL=gpt-4o-mini
   INGENIOUS_MODELS__0__API_TYPE=rest
   INGENIOUS_MODELS__0__API_VERSION=2024-12-01-preview
   INGENIOUS_MODELS__0__DEPLOYMENT=gpt-4o-mini
   INGENIOUS_MODELS__0__API_KEY=your-actual-key
   INGENIOUS_MODELS__0__BASE_URL=https://your-resource.openai.azure.com/
   INGENIOUS_CHAT_SERVICE__TYPE=multi_agent
   ```

2. **Create minimal .env file**:
   ```bash
   # Create .env with minimal configuration
   cat > .env << 'EOF'
   INGENIOUS_MODELS__0__API_KEY=your-api-key
   INGENIOUS_MODELS__0__BASE_URL=https://your-resource.openai.azure.com/
   INGENIOUS_MODELS__0__MODEL=gpt-4o-mini
   INGENIOUS_CHAT_SERVICE__TYPE=multi_agent
   EOF
   ```

3. **Load environment variables**:
   ```bash
   # Source the .env file or export variables
   # For bash/zsh
   export $(grep -v '^#' .env | xargs)

   # Or use dotenv to load .env automatically
   # The .env file is loaded automatically by Ingenious
   ```

---

### 2. Server Port Issues

**Symptoms**:
- "Permission denied" when starting server on port 80
- Server ignores `--port` parameter
- "Address already in use" errors
- Connection refused when testing API

**Solutions**:

1. **Use alternative port (Recommended for development)**:
   ```bash
   # Use port 8000 for development (no admin privileges required)
   uv run ingen serve --port 8000

   # Update your test commands to use the new port
   curl http://localhost:8000/api/v1/health
   ```

2. **Set port in environment variables (PREFERRED METHOD)**:
   ```bash
   # The correct environment variable is INGENIOUS_WEB_CONFIGURATION__PORT
   export INGENIOUS_WEB_CONFIGURATION__PORT=8080
   uv run ingen serve
   ```

3. **Or set in .env file (RECOMMENDED)**:
   ```bash
   # Add to your .env file
   INGENIOUS_WEB_CONFIGURATION__PORT=8080
   ```

4. **Check if port is available**:
   ```bash
   # Check what's using port 80
   lsof -i :80

   # Check what's using your target port
   lsof -i :8080

   # Kill processes if needed (be careful!)
   sudo kill -9 $(lsof -t -i:80)
   ```

5. **For production deployments on port 80**:
   ```bash
   # Run with elevated privileges (Linux/macOS)
   sudo uv run ingen serve

   # Or use a reverse proxy (nginx, apache)
   ```

**Note**: Port 80 requires administrative privileges on most systems. For development, use ports 8080, 8000, or 3000.

---

### 3. Module Import Errors

**Symptoms**:
```
ModuleNotFoundError: No module named 'ingenious_extensions'
```

**Solutions**:

1. **Make sure you're in the project root**:
   ```bash
   pwd  # Should be your project directory
   ls   # Should see ingenious_extensions/ folder
   ```

2. **Reinstall the library**:
   ```bash
   uv add ingenious
   ```

3. **Check Python path**:
   ```bash
   uv run python -c "import sys; print('\n'.join(sys.path))"
   ```

---

### 4. Workflow Execution Errors

**Symptoms**:
- "Class ConversationFlow not found"
- "Expecting value: line 1 column 1 (char 0)"

**Solutions**:

1. **Use correct workflow names**:
   ```bash
   #  Correct formats (both work)
   "conversation_flow": "bike-insights"  # Hyphenated (recommended)
   "conversation_flow": "bike_insights"   # Underscore (also supported)
   ```

2. **Check bike-insights input format**:
   ```bash
   # bike-insights needs JSON in user_prompt
   curl -X POST http://localhost:80/api/v1/chat \
     -H "Content-Type: application/json" \
     -d '{
       "user_prompt": "{\"stores\": [...], \"revision_id\": \"test\", \"identifier\": \"test\"}",
       "conversation_flow": "bike-insights"
     }'
   ```

---

### 5. Azure SQL Database Issues

**Symptoms**:
- "pyodbc.InterfaceError: ('IM002', '[IM002] [Microsoft][ODBC Driver Manager] Data source name not found..."
- "Module pyodbc not found"
- Chat history not persisting between sessions
- Connection timeout errors

**Prerequisites Check**:

1. **Verify ODBC Driver is installed**:
   ```bash
   odbcinst -q -d
   # Should show: [ODBC Driver 18 for SQL Server]
   # If not, install using the instructions below
   ```

2. **Install ODBC Driver (if missing)**:

   **On macOS**:
   ```bash
   brew tap microsoft/mssql-release
   brew install msodbcsql18 mssql-tools18
   ```

   **On Ubuntu/Debian**:
   ```bash
   curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
   curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
   apt-get update
   ACCEPT_EULA=Y apt-get install msodbcsql18
   ```

**Configuration Solutions**:

1. **Install required dependencies**:
   ```bash
   # pyodbc is required for Azure SQL
   uv add pyodbc
   # python-dotenv is included with ingenious
   ```

2. **Check environment variable is set**:
   ```bash
   echo $AZURE_SQL_CONNECTION_STRING
   # Should show your connection string

   # Or check if .env file is properly formatted
   cat .env | grep AZURE_SQL
   ```

3. **Configure Azure SQL connection** (critical):
   ```bash
   # Method 1: Using AZURE_SQL_CONNECTION_STRING environment variable
   # Add to .env file (NO SPACES around = and use quotes for complex values)
   AZURE_SQL_CONNECTION_STRING="Driver={ODBC Driver 18 for SQL Server};Server=tcp:your-server.database.windows.net,1433;Database=your-database;Uid=your-username;Pwd=your-password;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

   # Method 2: Using INGENIOUS_ prefixed variables
   INGENIOUS_CHAT_HISTORY__DATABASE_TYPE=azuresql
   INGENIOUS_CHAT_HISTORY__DATABASE_CONNECTION_STRING="Driver={ODBC Driver 18 for SQL Server};Server=tcp:your-server.database.windows.net,1433;Database=your-database;Uid=your-username;Pwd=your-password;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
   INGENIOUS_CHAT_HISTORY__DATABASE_NAME=your_database_name
   ```

4. **Verify environment variables are loaded**:
   ```bash
   # Check if environment variables are set correctly
   echo $INGENIOUS_CHAT_HISTORY__DATABASE_TYPE
   # Should output: azuresql

   echo $INGENIOUS_CHAT_HISTORY__DATABASE_CONNECTION_STRING
   # Should output your connection string
   ```

5. **Test environment variable loading**:
   ```bash
   uv run python -c "
   from dotenv import load_dotenv
   import os
   load_dotenv()
   conn_str = os.getenv('AZURE_SQL_CONNECTION_STRING')
   if not conn_str:
       print(' AZURE_SQL_CONNECTION_STRING not set')
   else:
       print(' Environment variable loaded successfully')
       print(f'Connection string length: {len(conn_str)} characters')
   "
   ```

6. **Test connection directly**:
   ```bash
   uv run python -c "
   import pyodbc
   import os
   conn_str = os.getenv('AZURE_SQL_CONNECTION_STRING')
   if not conn_str:
       print(' AZURE_SQL_CONNECTION_STRING not set')
   else:
       try:
           conn = pyodbc.connect(conn_str)
           print(' Azure SQL connection successful')
           conn.close()
       except Exception as e:
           print(f' Connection failed: {e}')
   "
   ```

4. **Test through Ingenious repository**:
   ```bash
   uv run python -c "
   import asyncio
   from ingenious.config import get_config
   from ingenious.db.chat_history_repository import ChatHistoryRepository
   from ingenious.models.database_client import DatabaseClientType

   async def test():
       config = get_config()
       db_type = DatabaseClientType(config.chat_history.database_type)
       repo = ChatHistoryRepository(db_type=db_type, config=config)
       try:
           messages = await repo.get_thread_messages('test-thread')
           print(f' Azure SQL repository working! (Found {len(messages)} messages)')
       except Exception as e:
           print(f' Repository error: {e}')

   asyncio.run(test())
   "
   ```

**Common Connection String Issues**:

- **Missing driver**: Ensure `Driver={ODBC Driver 18 for SQL Server}` is in the connection string
- **Port issues**: Use `Server=tcp:your-server.database.windows.net,1433`
- **Encryption**: Include `Encrypt=yes;TrustServerCertificate=no`
- **Timeout**: Add `Connection Timeout=30` for slow networks
- **Environment variable substitution**: The `$AZURE_SQL_CONNECTION_STRING` syntax works in .env files but may not work in all shells

**Security Notes**:
- Never commit connection strings to version control
- Always use environment variables for database credentials
- Rotate passwords regularly for production deployments

---

### 6. Azure Blob Storage Issues

**Symptoms**:
- "BlobServiceClient cannot be constructed from connection string"
- "Storage account not found" or authentication errors
- Memory/prompts not persisting between sessions
- File operations failing silently
- "Container does not exist" errors

**Prerequisites Check**:

1. **Verify Azure Storage SDK is installed**:
   ```bash
   uv tree | grep azure-storage-blob
   # Should show: azure-storage-blob==12.24.0
   ```

2. **Install Azure Storage SDK (if missing)**:
   ```bash
   uv add azure-storage-blob
   ```

**Configuration Steps**:

1. **Set up Azure Storage Account** (via Azure Portal):
   - Create a Storage Account (General Purpose v2)
   - Note the Account Name and Account Key
   - Get the Connection String from "Access keys" section

2. **Configure Azure Blob Storage**:
   ```bash
   # Method 1: Using connection string in token field (RECOMMENDED)
   # The library detects connection strings automatically
   INGENIOUS_FILE_STORAGE__REVISIONS__STORAGE_TYPE=azure
   INGENIOUS_FILE_STORAGE__REVISIONS__URL=https://yourstorageaccount.blob.core.windows.net/
   INGENIOUS_FILE_STORAGE__REVISIONS__CONTAINER_NAME=ingenious-revisions
   INGENIOUS_FILE_STORAGE__REVISIONS__TOKEN="DefaultEndpointsProtocol=https;AccountName=yourstorageaccount;AccountKey=your_key;EndpointSuffix=core.windows.net"

   # Method 2: Using DefaultAzureCredential (for production)
   INGENIOUS_FILE_STORAGE__REVISIONS__STORAGE_TYPE=azure
   INGENIOUS_FILE_STORAGE__REVISIONS__URL=https://yourstorageaccount.blob.core.windows.net/
   INGENIOUS_FILE_STORAGE__REVISIONS__AUTHENTICATION_METHOD=default_credential
   INGENIOUS_FILE_STORAGE__REVISIONS__CONTAINER_NAME=ingenious-revisions

   # Also configure DATA storage similarly
   INGENIOUS_FILE_STORAGE__DATA__STORAGE_TYPE=azure
   INGENIOUS_FILE_STORAGE__DATA__URL=https://yourstorageaccount.blob.core.windows.net/
   INGENIOUS_FILE_STORAGE__DATA__CONTAINER_NAME=ingenious-data
   INGENIOUS_FILE_STORAGE__DATA__TOKEN="<same-connection-string>"
   ```

3. **Set AZURE_STORAGE_CONNECTION_STRING (if using environment variable reference)**:
   ```bash
   # If you want to reference $AZURE_STORAGE_CONNECTION_STRING in your config
   # Add this to your .env file
   AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=yourstorageaccount;AccountKey=your_key;EndpointSuffix=core.windows.net"
   ```

4. **Test environment variable loading**:
   ```bash
   uv run python -c "
   from dotenv import load_dotenv
   import os
   load_dotenv()
   conn_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
   if not conn_str:
       print(' AZURE_STORAGE_CONNECTION_STRING not set')
   else:
       print(' Environment variable loaded successfully')
       print(f'Connection string length: {len(conn_str)} characters')
   "
   ```

5. **Test Azure Blob Storage connectivity**:
   ```bash
   uv run python -c "
   from azure.storage.blob import BlobServiceClient
   import os
   from dotenv import load_dotenv
   load_dotenv()

   # Try to get connection string from environment
   conn_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
   if not conn_str:
       # Try from INGENIOUS settings
       token = os.getenv('INGENIOUS_FILE_STORAGE__REVISIONS__TOKEN')
       if token and 'DefaultEndpointsProtocol' in token:
           conn_str = token

   if not conn_str:
       print(' Azure Storage connection string not found')
       print(' Set either AZURE_STORAGE_CONNECTION_STRING or')
       print(' INGENIOUS_FILE_STORAGE__REVISIONS__TOKEN')
   else:
       try:
           client = BlobServiceClient.from_connection_string(conn_str)
           account_info = client.get_account_information()
           print(' Azure Blob Storage connection successful')
           print(f'Account kind: {account_info[\"account_kind\"]}')
       except Exception as e:
           print(f' Connection failed: {e}')
   "
   ```

6. **Test through Ingenious FileStorage**:
   ```bash
   uv run python -c "
   from ingenious.files import get_file_storage
   from ingenious.config import get_config

   try:
       config = get_config()
       file_storage = get_file_storage()
       print(f' FileStorage initialized: {type(file_storage).__name__}')

       # Test basic operations
       test_path = 'test/hello.txt'
       file_storage.save_text(test_path, 'Hello Azure!')
       content = file_storage.load_text(test_path)
       print(f' File operations working: {content}')

       # Cleanup
       if file_storage.exists(test_path):
           file_storage.delete(test_path)
           print(' Cleanup successful')
   except Exception as e:
       print(f' FileStorage error: {e}')
   "
   ```

7. **Container naming requirements**:
   - Container names must be lowercase
   - Use only letters, numbers, and hyphens
   - Must start with a letter or number
   - Examples: `ingenious-data`, `ingenious-revisions`

8. **Test Memory and Prompts Integration**:
   ```bash
   uv run python -c "
   from ingenious.services.memory_manager import MemoryManager
   import json

   try:
       memory_manager = MemoryManager()
       test_data = {'test': 'memory_data', 'timestamp': '2024-01-01'}

       # Test memory operations
       memory_manager.save_memory('test_conversation', test_data)
       loaded_data = memory_manager.load_memory('test_conversation')
       print(f' Memory operations working: {loaded_data == test_data}')

       # Test prompts API (adjust port as needed)
       import requests
       response = requests.get('http://localhost:80/api/v1/prompts')
       if response.status_code == 200:
           print(' Prompts API accessible')
       else:
           print(f'  Prompts API returned: {response.status_code}')

   except Exception as e:
       print(f' Memory/Prompts error: {e}')
   "
   ```

**Common Connection String Issues**:

- **Malformed connection string**: Ensure all required fields are present:
  ```
  DefaultEndpointsProtocol=https;AccountName=name;AccountKey=key;EndpointSuffix=core.windows.net
  ```
- **Missing EndpointSuffix**: Required for proper endpoint resolution
- **Wrong account name/key**: Verify credentials in Azure Portal
- **Network access**: Ensure storage account allows access from your IP/network

**Container Management**:

- **Auto-creation**: Ingenious automatically creates containers if they don't exist
- **Naming conventions**: Use lowercase, hyphens only (e.g., `ingenious-data-dev`)
- **Environment separation**: Use different containers for dev/staging/prod

**Performance Considerations**:

- **Connection reuse**: BlobServiceClient instances are reused automatically
- **Batch operations**: For high-volume scenarios, consider batching operations
- **Timeout settings**: Adjust timeout in configuration for slow networks

**Security Best Practices**:

- **Connection strings**: Never commit to version control
- **Access keys**: Rotate regularly
- **Network access**: Configure firewall rules in Azure Portal
- **Shared Access Signatures**: Consider using SAS tokens for limited access

**Troubleshooting Storage Type Conflicts**:

If you're switching from local to Azure Blob Storage:

1. **Clear local data** (if safe to do so):
   ```bash
   rm -rf ./data/conversations
   rm -rf ./data/prompts
   ```

2. **Verify configuration precedence**:
   - Environment variables with `INGENIOUS_` prefix are the primary configuration method
   - `.env` files are loaded automatically for local development

3. **Test with minimal configuration**:
   ```bash
   # Minimal .env for testing
   INGENIOUS_FILE_STORAGE__REVISIONS__STORAGE_TYPE=azure
   INGENIOUS_FILE_STORAGE__REVISIONS__URL=https://your-storage.blob.core.windows.net/
   INGENIOUS_FILE_STORAGE__DATA__STORAGE_TYPE=azure
   INGENIOUS_FILE_STORAGE__DATA__URL=https://your-storage.blob.core.windows.net/
   ```

---

##  Debugging Commands

### Check System Status
```bash
uv run ingen status
```

### List Available Workflows
```bash
uv run ingen workflows
```

### Check Specific Workflow Requirements
```bash
uv run ingen workflows bike-insights
```

### Test Installation
```bash
uv run python -c "import ingenious; print(' Ingenious imported successfully')"
```

### Check Configuration Loading
```bash
# Check environment variables are loaded
uv run python -c "
from ingenious.config import get_config
try:
    cfg = get_config()
    print(' Configuration loaded successfully')
    print(f'Models: {len(cfg.models)}')
    print(f'Database type: {cfg.chat_history.database_type}')
except Exception as e:
    print(f' Configuration error: {e}')
"
```

---

##  Log Analysis

### Enable Debug Logging

1. **In .env file**:
   ```bash
   INGENIOUS_LOGGING__ROOT_LOG_LEVEL=debug
   INGENIOUS_LOGGING__LOG_LEVEL=debug
   ```

2. **Or via environment**:
   ```bash
   export LOGLEVEL=DEBUG
   export ROOTLOGLEVEL=DEBUG
   ```

### Common Log Messages

** Good Signs**:
```
Profile loaded from file
Module ingenious_extensions.services.chat_services.multi_agent.conversation_flows.bike_insights.bike_insights found.
DEBUG: Successfully loaded conversation flow class
INFO:     Uvicorn running on http://0.0.0.0:80
```

** Warning Signs**:
```
Environment variables not found or .env file missing
Template directory not found. Skipping...
Validation error in field
```

** Error Signs**:
```
ModuleNotFoundError: No module named
ValidationError: 9 validation errors
Class ConversationFlow not found in module
```

---

##  Testing & Verification

### Minimal Test
```bash
# Test server is running
curl -s http://localhost:80/api/v1/health || echo "Server not responding"

# Test bike-insights workflow
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "{\"stores\": [], \"revision_id\": \"test\", \"identifier\": \"test\"}",
    "conversation_flow": "bike-insights"
  }' | jq '.message_id // "ERROR"'
```

### Full Integration Test
```bash
#!/bin/bash
set -e

echo " Running full integration test..."

# 1. Check environment
echo "1. Checking environment..."
[ -n "$AZURE_OPENAI_API_KEY" ] || { echo " AZURE_OPENAI_API_KEY not set"; exit 1; }
[ -f ".env" ] || { echo " .env not found"; exit 1; }

# 2. Test import
echo "2. Testing Python import..."
uv run python -c "import ingenious; print(' Import OK')"

# 3. Test configuration
echo "3. Testing configuration..."
# Environment variables are loaded from .env automatically
uv run ingen status

# 4. Test workflows
echo "4. Testing workflows..."
uv run ingen workflows | grep -q "bike-insights" && echo " bike-insights available"

echo " All tests passed!"
```

---

##  Environment Checklist

Before running Ingenious, ensure:

- [ ] Python 3.13+ installed
- [ ] uv package manager available
- [ ] Ingenious library installed: `uv add ingenious`
- [ ] Project initialized: `uv run ingen init`
- [ ] .env file created with Azure OpenAI credentials
- [ ] Environment variables set:
  - [ ] `INGENIOUS_MODELS__0__API_KEY`
  - [ ] `INGENIOUS_MODELS__0__BASE_URL`
  - [ ] `INGENIOUS_CHAT_SERVICE__TYPE`
- [ ] Port available (default 80)
- [ ] Network access to Azure OpenAI endpoint

---

## 🆘 Getting Help

### Self-Help Commands
```bash
# Get general help
uv run ingen --help

# Get command-specific help
uv run ingen serve --help
uv run ingen workflows --help

# Check system status
uv run ingen status

# List all workflows
uv run ingen workflows
```

### Common Solutions Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| Import errors | `uv add ingenious` |
| Configuration validation | Check INGENIOUS_ prefixed env vars |
| Port not working | Set `INGENIOUS_WEB_CONFIGURATION__PORT` |
| Workflow not found | Use `bike-insights` (recommended) or `bike_insights` (also supported) |
| JSON parse error | Escape quotes in `user_prompt` for bike-insights |
| Server won't start | Check port availability and .env file |

### Still Need Help?

1. Check the logs for specific error messages
2. Review configuration files against templates
3. Test with minimal configuration first
4. Check the API documentation: `/docs/api/workflows.md`
5. Verify environment variables are loaded correctly

---

##  Reset Instructions

If everything is broken, start fresh:

```bash
# 1. Clean slate
rm -rf ingenious_extensions/ tmp/ .env

# 2. Reinstall
uv add ingenious

# 3. Initialize
uv run ingen init

# 4. Configure
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

# 5. Create minimal .env
cat > .env << 'EOF'
INGENIOUS_MODELS__0__API_KEY=your-api-key
INGENIOUS_MODELS__0__BASE_URL=https://your-resource.openai.azure.com/
INGENIOUS_CHAT_SERVICE__TYPE=multi_agent
EOF

# 6. Test
uv run ingen status
uv run ingen serve
```
