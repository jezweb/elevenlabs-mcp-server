# ElevenLabs Tools & Integrations Guide
*Complete Reference for Extending Agent Capabilities*

## Table of Contents
1. [System Tools Overview](#system-tools-overview)
2. [Webhook Tools (Server-Side)](#webhook-tools-server-side)
3. [Client Tools (Local Execution)](#client-tools-local-execution)
4. [n8n Integration](#n8n-integration)
5. [Make/Zapier Integration](#makezapier-integration)
6. [Custom API Integration](#custom-api-integration)
7. [Database Connections](#database-connections)
8. [CRM Integration](#crm-integration)
9. [Calendar & Scheduling](#calendar--scheduling)
10. [Knowledge Base & RAG](#knowledge-base--rag)
11. [Tool Chaining & Workflows](#tool-chaining--workflows)
12. [Error Handling & Fallbacks](#error-handling--fallbacks)

---

## System Tools Overview

### Core System Tools

#### end_call
Allows agent to end conversation naturally.

```json
{
  "tool_type": "end_call",
  "enabled": true,
  "trigger_phrases": [
    "goodbye",
    "bye",
    "talk to you later",
    "have a good day"
  ],
  "confirmation_required": false
}
```

**Best Practices:**
- Always enable for natural conversation flow
- Agent can decide when conversation is complete
- Prevents awkward endless loops

#### transfer_to_ai_agent
Seamless handoff between AI agents.

```json
{
  "tool_type": "transfer_to_ai_agent",
  "rules": [
    {
      "agent_id": "agent_8801k2px9ch5ee2bs65xwwhdzcjq",
      "condition": "User wants to book an appointment or schedule service",
      "transfer_message": "I'll connect you with our booking specialist.",
      "enable_first_message": true,
      "pass_context": true
    }
  ]
}
```

**Configuration Options:**
- `agent_id`: Target agent's unique ID
- `condition`: Natural language trigger condition
- `transfer_message`: What to say during transfer
- `enable_first_message`: Allow target agent to speak first
- `pass_context`: Share conversation history

#### transfer_to_number
Transfer to human via phone number.

```json
{
  "tool_type": "transfer_to_number",
  "rules": [
    {
      "phone_number": "+61411234567",
      "condition": "Emergency or urgent situation",
      "transfer_message": "This needs immediate attention. Connecting you now.",
      "transfer_mode": "warm",  // warm or cold
      "play_hold_music": true
    }
  ]
}
```

**Transfer Modes:**
- **Warm Transfer**: Agent introduces before connecting
- **Cold Transfer**: Direct connection without introduction

#### language_detection
Automatic language switching.

```json
{
  "tool_type": "language_detection",
  "enabled": true,
  "supported_languages": ["en", "es", "fr", "de", "zh"],
  "detection_threshold": 0.8,
  "switch_message": "I've detected you prefer {language}. Let me switch."
}
```

#### skip_turn
Let user continue speaking without interruption.

```json
{
  "tool_type": "skip_turn",
  "enabled": true,
  "trigger_silence_duration": 2.0,
  "max_skips": 3
}
```

---

## Webhook Tools (Server-Side)

### Basic Webhook Configuration

```json
{
  "tool_type": "webhook",
  "name": "check_availability",
  "description": "Check available appointment slots. Use when user asks about availability or wants to book.",
  "url": "https://your-api.com/webhook/availability",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer ${API_KEY}",
    "Content-Type": "application/json"
  },
  "parameters": [
    {
      "name": "date",
      "type": "string",
      "description": "Requested date in YYYY-MM-DD format",
      "required": true
    },
    {
      "name": "service_type",
      "type": "string",
      "description": "Type of service needed",
      "required": true,
      "enum": ["consultation", "repair", "installation"]
    },
    {
      "name": "duration",
      "type": "integer",
      "description": "Appointment duration in minutes",
      "required": false,
      "default": 60
    }
  ],
  "response_format": {
    "type": "json",
    "schema": {
      "available_slots": "array",
      "next_available": "string",
      "message": "string"
    }
  }
}
```

### Advanced Webhook Features

#### Retry Configuration
```json
{
  "retry_config": {
    "max_attempts": 3,
    "retry_delay_ms": 1000,
    "exponential_backoff": true,
    "retry_on_status_codes": [500, 502, 503, 504]
  }
}
```

#### Timeout Settings
```json
{
  "timeout_config": {
    "connection_timeout_ms": 5000,
    "read_timeout_ms": 10000,
    "total_timeout_ms": 15000
  }
}
```

#### Authentication Methods

**Bearer Token:**
```json
{
  "auth": {
    "type": "bearer",
    "token": "${BEARER_TOKEN}"
  }
}
```

**API Key:**
```json
{
  "auth": {
    "type": "api_key",
    "header_name": "X-API-Key",
    "key": "${API_KEY}"
  }
}
```

**Basic Auth:**
```json
{
  "auth": {
    "type": "basic",
    "username": "${USERNAME}",
    "password": "${PASSWORD}"
  }
}
```

**OAuth 2.0:**
```json
{
  "auth": {
    "type": "oauth2",
    "token_url": "https://auth.example.com/token",
    "client_id": "${CLIENT_ID}",
    "client_secret": "${CLIENT_SECRET}",
    "scope": "read write"
  }
}
```

---

## Client Tools (Local Execution)

### Python SDK Implementation

```python
from elevenlabs import ConversationAgent
import asyncio

class ClientToolHandler:
    def __init__(self):
        self.agent = None
    
    async def setup_agent(self, agent_id):
        """Initialize the conversation agent with client tools"""
        self.agent = ConversationAgent(
            agent_id=agent_id,
            api_key="your_api_key"
        )
        
        # Register client tools
        self.agent.register_tool("capture_screen", self.capture_screen)
        self.agent.register_tool("open_file", self.open_file)
        self.agent.register_tool("process_payment", self.process_payment)
        self.agent.register_tool("scan_qr_code", self.scan_qr_code)
    
    async def capture_screen(self, params):
        """Capture screenshot or camera feed"""
        import cv2
        import base64
        
        # Capture from camera
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            # Convert to base64
            _, buffer = cv2.imencode('.jpg', frame)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return {
                "success": True,
                "image": image_base64,
                "timestamp": datetime.now().isoformat()
            }
        
        return {"success": False, "error": "Failed to capture"}
    
    async def open_file(self, params):
        """Open a local file"""
        import subprocess
        import platform
        
        file_path = params.get("file_path")
        
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', file_path])
            elif platform.system() == 'Windows':
                subprocess.call(['start', file_path], shell=True)
            else:  # Linux
                subprocess.call(['xdg-open', file_path])
            
            return {"success": True, "opened": file_path}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def process_payment(self, params):
        """Process payment locally"""
        # Integration with local payment terminal
        amount = params.get("amount")
        currency = params.get("currency", "USD")
        
        # Simulate payment processing
        payment_result = await self.local_payment_api(amount, currency)
        
        return {
            "success": payment_result["status"] == "approved",
            "transaction_id": payment_result.get("transaction_id"),
            "amount": amount,
            "currency": currency
        }
    
    async def scan_qr_code(self, params):
        """Scan QR code using camera"""
        import cv2
        from pyzbar import pyzbar
        
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect QR codes
            qr_codes = pyzbar.decode(frame)
            
            if qr_codes:
                for qr in qr_codes:
                    data = qr.data.decode('utf-8')
                    cap.release()
                    
                    return {
                        "success": True,
                        "data": data,
                        "type": qr.type
                    }
            
            # Timeout after 10 seconds
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        return {"success": False, "error": "No QR code found"}

# Usage
async def main():
    handler = ClientToolHandler()
    await handler.setup_agent("agent_123")
    await handler.agent.start_conversation()

asyncio.run(main())
```

### JavaScript SDK Implementation

```javascript
import { ElevenLabsConvai } from '@elevenlabs/convai-sdk';

class ClientToolHandler {
  constructor() {
    this.agent = null;
  }

  async setupAgent(agentId) {
    this.agent = await ElevenLabsConvai.create({
      agentId: agentId,
      apiKey: process.env.ELEVEN_LABS_API_KEY
    });

    // Register client tools
    this.agent.registerTool('getUserLocation', this.getUserLocation.bind(this));
    this.agent.registerTool('takePhoto', this.takePhoto.bind(this));
    this.agent.registerTool('saveToLocal', this.saveToLocal.bind(this));
    this.agent.registerTool('openWebpage', this.openWebpage.bind(this));
  }

  async getUserLocation() {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject({ success: false, error: 'Geolocation not supported' });
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            success: true,
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy
          });
        },
        (error) => {
          reject({ success: false, error: error.message });
        }
      );
    });
  }

  async takePhoto() {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    const video = document.createElement('video');
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');

    video.srcObject = stream;
    await video.play();

    // Wait for video to be ready
    await new Promise(resolve => {
      video.onloadedmetadata = resolve;
    });

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);

    // Stop the stream
    stream.getTracks().forEach(track => track.stop());

    // Convert to base64
    const imageData = canvas.toDataURL('image/jpeg');

    return {
      success: true,
      image: imageData,
      timestamp: new Date().toISOString()
    };
  }

  async saveToLocal(params) {
    const { filename, content } = params;
    
    try {
      // Create blob from content
      const blob = new Blob([content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      
      // Create download link
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      
      URL.revokeObjectURL(url);
      
      return { success: true, filename };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async openWebpage(params) {
    const { url } = params;
    
    try {
      window.open(url, '_blank');
      return { success: true, url };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }
}

// Usage
const handler = new ClientToolHandler();
await handler.setupAgent('agent_123');
await handler.agent.start();
```

---

## n8n Integration

### n8n Webhook Workflow

#### Step 1: Create Webhook Trigger
```json
{
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "elevenlabs-agent",
        "method": "POST",
        "responseMode": "lastNode",
        "authentication": "headerAuth"
      }
    }
  ]
}
```

#### Step 2: Process Agent Request
```javascript
// n8n Function Node
const agentData = items[0].json;
const action = agentData.action;
const parameters = agentData.parameters;

let response = {};

switch(action) {
  case 'check_availability':
    // Database lookup
    const availability = await checkDatabase(parameters.date);
    response = {
      available: availability.slots.length > 0,
      slots: availability.slots,
      message: `Found ${availability.slots.length} available slots`
    };
    break;
    
  case 'create_booking':
    // Create booking
    const booking = await createBooking(parameters);
    response = {
      success: true,
      booking_id: booking.id,
      confirmation: `Booking confirmed for ${booking.date}`
    };
    break;
    
  case 'send_email':
    // Send email
    const email = await sendEmail(parameters);
    response = {
      success: true,
      message: 'Email sent successfully'
    };
    break;
}

return [{ json: response }];
```

#### Step 3: Database Integration
```json
{
  "name": "Postgres",
  "type": "n8n-nodes-base.postgres",
  "parameters": {
    "operation": "executeQuery",
    "query": "SELECT * FROM appointments WHERE date = $1 AND status = 'available'",
    "additionalFields": {
      "queryParams": "={{ $json.date }}"
    }
  }
}
```

#### Step 4: Return Response
```json
{
  "name": "Webhook Response",
  "type": "n8n-nodes-base.respondToWebhook",
  "parameters": {
    "responseCode": 200,
    "responseHeaders": {
      "Content-Type": "application/json"
    },
    "responseData": "={{ $json }}"
  }
}
```

### Complete n8n Workflow Examples

#### Customer Support Ticket Creation
```javascript
// Complete n8n workflow for support ticket
{
  "name": "ElevenLabs Support Ticket",
  "nodes": [
    {
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300]
    },
    {
      "name": "Validate Data",
      "type": "n8n-nodes-base.if",
      "position": [450, 300],
      "parameters": {
        "conditions": {
          "string": [{
            "value1": "={{ $json.customer_email }}",
            "operation": "isNotEmpty"
          }]
        }
      }
    },
    {
      "name": "Create Zendesk Ticket",
      "type": "n8n-nodes-base.zendesk",
      "position": [650, 200],
      "parameters": {
        "operation": "create",
        "subject": "={{ $json.issue_summary }}",
        "description": "={{ $json.issue_details }}",
        "priority": "={{ $json.priority }}"
      }
    },
    {
      "name": "Send Slack Notification",
      "type": "n8n-nodes-base.slack",
      "position": [650, 400],
      "parameters": {
        "channel": "#support",
        "text": "New ticket created: {{ $json.ticket_id }}"
      }
    },
    {
      "name": "Return Response",
      "type": "n8n-nodes-base.respondToWebhook",
      "position": [850, 300]
    }
  ]
}
```

---

## Make/Zapier Integration

### Make (Integromat) Scenario

```json
{
  "scenario": {
    "name": "ElevenLabs Agent Integration",
    "trigger": {
      "type": "webhook",
      "instant": true,
      "data_structure": {
        "action": "string",
        "parameters": "object",
        "agent_id": "string",
        "conversation_id": "string"
      }
    },
    "modules": [
      {
        "name": "Router",
        "type": "router",
        "routes": [
          {
            "condition": "action == 'check_crm'",
            "modules": ["Salesforce Lookup"]
          },
          {
            "condition": "action == 'send_sms'",
            "modules": ["Twilio SMS"]
          }
        ]
      },
      {
        "name": "Salesforce Lookup",
        "type": "salesforce",
        "operation": "search",
        "object": "Contact",
        "query": "Email = '{{parameters.email}}'"
      },
      {
        "name": "Webhook Response",
        "type": "webhook_response",
        "status": 200,
        "body": "{{output}}"
      }
    ]
  }
}
```

### Zapier Zap Configuration

```yaml
trigger:
  app: Webhooks by Zapier
  event: Catch Hook
  
actions:
  - app: Filter by Zapier
    action: Only continue if...
    conditions:
      - field: action
        condition: equals
        value: create_lead
  
  - app: Salesforce
    action: Create Lead
    fields:
      first_name: "{{parameters.first_name}}"
      last_name: "{{parameters.last_name}}"
      email: "{{parameters.email}}"
      phone: "{{parameters.phone}}"
      company: "{{parameters.company}}"
  
  - app: Gmail
    action: Send Email
    fields:
      to: "{{parameters.email}}"
      subject: "Welcome to our service"
      body: "Thank you for your interest..."
  
  - app: Webhooks by Zapier
    action: Custom Request
    method: POST
    url: "{{webhook_response_url}}"
    data:
      success: true
      lead_id: "{{salesforce.id}}"
      message: "Lead created successfully"
```

---

## Custom API Integration

### Direct API Integration Pattern

```python
import aiohttp
import asyncio
from typing import Dict, Any

class CustomAPIIntegration:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
    
    async def handle_agent_request(self, action: str, params: Dict[str, Any]):
        """Main handler for agent tool requests"""
        
        handlers = {
            'search_products': self.search_products,
            'check_inventory': self.check_inventory,
            'create_order': self.create_order,
            'get_customer': self.get_customer,
            'update_ticket': self.update_ticket
        }
        
        handler = handlers.get(action)
        if not handler:
            return {'error': f'Unknown action: {action}'}
        
        try:
            return await handler(params)
        except Exception as e:
            return {'error': str(e)}
    
    async def search_products(self, params: Dict[str, Any]):
        """Search product catalog"""
        query = params.get('query', '')
        category = params.get('category')
        
        endpoint = f'{self.base_url}/products/search'
        data = {
            'q': query,
            'category': category,
            'limit': 10
        }
        
        async with self.session.post(endpoint, json=data) as response:
            results = await response.json()
            
            # Format for agent response
            return {
                'found': len(results['products']),
                'products': [
                    {
                        'name': p['name'],
                        'price': p['price'],
                        'availability': p['in_stock']
                    }
                    for p in results['products'][:5]
                ]
            }
    
    async def check_inventory(self, params: Dict[str, Any]):
        """Check product inventory"""
        product_id = params.get('product_id')
        location = params.get('location', 'all')
        
        endpoint = f'{self.base_url}/inventory/{product_id}'
        
        async with self.session.get(endpoint) as response:
            inventory = await response.json()
            
            return {
                'in_stock': inventory['total'] > 0,
                'quantity': inventory['total'],
                'locations': inventory['by_location']
            }
    
    async def create_order(self, params: Dict[str, Any]):
        """Create a new order"""
        endpoint = f'{self.base_url}/orders'
        
        order_data = {
            'customer_id': params.get('customer_id'),
            'items': params.get('items', []),
            'shipping_address': params.get('shipping_address'),
            'payment_method': params.get('payment_method')
        }
        
        async with self.session.post(endpoint, json=order_data) as response:
            if response.status == 201:
                order = await response.json()
                return {
                    'success': True,
                    'order_id': order['id'],
                    'total': order['total'],
                    'estimated_delivery': order['estimated_delivery']
                }
            else:
                error = await response.text()
                return {
                    'success': False,
                    'error': error
                }

# FastAPI webhook endpoint
from fastapi import FastAPI, Request
import json

app = FastAPI()

@app.post("/webhook/elevenlabs-agent")
async def handle_agent_webhook(request: Request):
    """Webhook endpoint for ElevenLabs agent"""
    
    body = await request.json()
    action = body.get('action')
    parameters = body.get('parameters', {})
    
    async with CustomAPIIntegration(
        base_url='https://api.yourcompany.com',
        api_key='your_api_key'
    ) as api:
        result = await api.handle_agent_request(action, parameters)
    
    return result
```

---

## Database Connections

### PostgreSQL Integration

```python
import asyncpg
from datetime import datetime

class DatabaseIntegration:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.pool = None
    
    async def connect(self):
        self.pool = await asyncpg.create_pool(self.db_url)
    
    async def disconnect(self):
        await self.pool.close()
    
    async def check_appointment_availability(self, date: str, service: str):
        """Check available appointment slots"""
        
        query = """
            SELECT time_slot, duration_minutes
            FROM appointment_slots
            WHERE date = $1
            AND service_type = $2
            AND is_available = true
            ORDER BY time_slot
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, date, service)
            
            return {
                'date': date,
                'available_slots': [
                    {
                        'time': row['time_slot'].strftime('%H:%M'),
                        'duration': row['duration_minutes']
                    }
                    for row in rows
                ]
            }
    
    async def create_appointment(self, customer_data: dict):
        """Create new appointment"""
        
        query = """
            INSERT INTO appointments 
            (customer_name, customer_email, customer_phone, 
             service_type, date, time_slot, notes)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id, confirmation_code
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                customer_data['name'],
                customer_data['email'],
                customer_data['phone'],
                customer_data['service'],
                customer_data['date'],
                customer_data['time'],
                customer_data.get('notes', '')
            )
            
            return {
                'success': True,
                'appointment_id': row['id'],
                'confirmation_code': row['confirmation_code']
            }
```

### MongoDB Integration

```python
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

class MongoDBIntegration:
    def __init__(self, connection_string: str, database: str):
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client[database]
    
    async def search_knowledge_base(self, query: str):
        """Search knowledge base articles"""
        
        # Text search
        cursor = self.db.articles.find(
            {'$text': {'$search': query}},
            {'score': {'$meta': 'textScore'}}
        ).sort([('score', {'$meta': 'textScore'})])
        
        articles = []
        async for doc in cursor.limit(5):
            articles.append({
                'title': doc['title'],
                'excerpt': doc['excerpt'],
                'url': doc['url'],
                'relevance': doc['score']
            })
        
        return {
            'found': len(articles),
            'articles': articles
        }
    
    async def log_conversation(self, conversation_data: dict):
        """Log conversation for analytics"""
        
        doc = {
            'conversation_id': conversation_data['id'],
            'agent_id': conversation_data['agent_id'],
            'timestamp': datetime.utcnow(),
            'duration': conversation_data['duration'],
            'transcript': conversation_data['transcript'],
            'tools_used': conversation_data['tools'],
            'outcome': conversation_data['outcome']
        }
        
        result = await self.db.conversations.insert_one(doc)
        return {'logged': True, 'id': str(result.inserted_id)}
```

---

## CRM Integration

### Salesforce Integration

```python
from simple_salesforce import Salesforce
import asyncio

class SalesforceIntegration:
    def __init__(self, username, password, security_token):
        self.sf = Salesforce(
            username=username,
            password=password,
            security_token=security_token
        )
    
    async def create_lead(self, lead_data):
        """Create a new lead in Salesforce"""
        
        lead = {
            'FirstName': lead_data.get('first_name'),
            'LastName': lead_data.get('last_name'),
            'Email': lead_data.get('email'),
            'Phone': lead_data.get('phone'),
            'Company': lead_data.get('company', 'Unknown'),
            'LeadSource': 'AI Agent',
            'Description': lead_data.get('notes', '')
        }
        
        result = await asyncio.to_thread(
            self.sf.Lead.create,
            lead
        )
        
        return {
            'success': result['success'],
            'lead_id': result['id'],
            'message': f"Lead created with ID: {result['id']}"
        }
    
    async def search_contact(self, email):
        """Search for existing contact"""
        
        query = f"SELECT Id, FirstName, LastName, AccountId FROM Contact WHERE Email = '{email}'"
        
        results = await asyncio.to_thread(
            self.sf.query,
            query
        )
        
        if results['totalSize'] > 0:
            contact = results['records'][0]
            return {
                'found': True,
                'contact_id': contact['Id'],
                'name': f"{contact['FirstName']} {contact['LastName']}",
                'account_id': contact['AccountId']
            }
        
        return {'found': False}
```

### HubSpot Integration

```python
import aiohttp

class HubSpotIntegration:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.hubapi.com'
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    async def create_contact(self, contact_data):
        """Create or update contact in HubSpot"""
        
        endpoint = f'{self.base_url}/crm/v3/objects/contacts'
        
        properties = {
            'email': contact_data['email'],
            'firstname': contact_data.get('first_name'),
            'lastname': contact_data.get('last_name'),
            'phone': contact_data.get('phone'),
            'company': contact_data.get('company'),
            'ai_agent_interaction': 'true',
            'last_agent_contact': datetime.now().isoformat()
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                endpoint,
                headers=self.headers,
                json={'properties': properties}
            ) as response:
                if response.status == 201:
                    result = await response.json()
                    return {
                        'success': True,
                        'contact_id': result['id']
                    }
                elif response.status == 409:
                    # Contact exists, update instead
                    return await self.update_contact(
                        contact_data['email'],
                        properties
                    )
```

---

## Calendar & Scheduling

### Google Calendar Integration

```python
from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime

class GoogleCalendarIntegration:
    def __init__(self, credentials_file):
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_file,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        self.service = build('calendar', 'v3', credentials=self.credentials)
    
    async def check_availability(self, date, duration_minutes=60):
        """Check calendar availability"""
        
        # Set time range
        start_time = datetime.datetime.fromisoformat(date)
        end_time = start_time + datetime.timedelta(days=1)
        
        # Get busy times
        body = {
            'timeMin': start_time.isoformat(),
            'timeMax': end_time.isoformat(),
            'items': [{'id': 'primary'}]
        }
        
        events = await asyncio.to_thread(
            self.service.freebusy().query(body=body).execute
        )
        
        busy_times = events['calendars']['primary']['busy']
        
        # Find available slots
        available_slots = self.find_available_slots(
            start_time,
            end_time,
            busy_times,
            duration_minutes
        )
        
        return {
            'date': date,
            'available_slots': available_slots
        }
    
    async def create_event(self, event_data):
        """Create calendar event"""
        
        event = {
            'summary': event_data['title'],
            'description': event_data.get('description', ''),
            'start': {
                'dateTime': event_data['start_time'],
                'timeZone': event_data.get('timezone', 'UTC')
            },
            'end': {
                'dateTime': event_data['end_time'],
                'timeZone': event_data.get('timezone', 'UTC')
            },
            'attendees': [
                {'email': email} for email in event_data.get('attendees', [])
            ]
        }
        
        result = await asyncio.to_thread(
            self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute
        )
        
        return {
            'success': True,
            'event_id': result['id'],
            'link': result['htmlLink']
        }
```

### Calendly Integration

```python
class CalendlyIntegration:
    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = 'https://api.calendly.com'
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
    
    async def get_event_types(self):
        """Get available event types"""
        
        endpoint = f'{self.base_url}/event_types'
        
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint, headers=self.headers) as response:
                data = await response.json()
                
                return {
                    'event_types': [
                        {
                            'name': et['name'],
                            'duration': et['duration'],
                            'url': et['scheduling_url']
                        }
                        for et in data['collection']
                    ]
                }
    
    async def get_availability(self, event_type_uri, date_range):
        """Get availability for specific event type"""
        
        endpoint = f'{self.base_url}/availability'
        
        params = {
            'event_type': event_type_uri,
            'start_time': date_range['start'],
            'end_time': date_range['end']
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                endpoint,
                headers=self.headers,
                params=params
            ) as response:
                data = await response.json()
                
                return {
                    'available_times': data['collection']
                }
```

---

## Knowledge Base & RAG

### Knowledge Base Configuration

```json
{
  "knowledge_base": {
    "enabled": true,
    "use_rag": true,
    "files": [
      {
        "name": "product_catalog.txt",
        "type": "products",
        "update_frequency": "daily"
      },
      {
        "name": "faq.txt",
        "type": "support",
        "update_frequency": "weekly"
      },
      {
        "name": "policies.txt",
        "type": "compliance",
        "update_frequency": "monthly"
      }
    ],
    "rag_settings": {
      "search_threshold": 0.7,
      "max_results": 3,
      "include_source": true,
      "chunk_size": 500,
      "overlap": 50
    }
  }
}
```

### Dynamic Knowledge Base Updates

```python
class KnowledgeBaseManager:
    def __init__(self, agent_id, api_key):
        self.agent_id = agent_id
        self.api_key = api_key
        self.base_url = 'https://api.elevenlabs.io/v1'
    
    async def update_knowledge_base(self, file_content, filename):
        """Update knowledge base file"""
        
        endpoint = f'{self.base_url}/agents/{self.agent_id}/knowledge-base'
        
        headers = {
            'Authorization': f'Bearer {self.api_key}'
        }
        
        files = {
            'file': (filename, file_content, 'text/plain')
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                endpoint,
                headers=headers,
                data={'action': 'update'},
                files=files
            ) as response:
                return await response.json()
    
    async def sync_from_database(self):
        """Sync knowledge base from database"""
        
        # Fetch latest data
        products = await self.fetch_products()
        faqs = await self.fetch_faqs()
        
        # Format as text
        products_text = self.format_products(products)
        faqs_text = self.format_faqs(faqs)
        
        # Update knowledge base
        await self.update_knowledge_base(products_text, 'products.txt')
        await self.update_knowledge_base(faqs_text, 'faqs.txt')
        
        return {'synced': True, 'timestamp': datetime.now()}
```

---

## Tool Chaining & Workflows

### Sequential Tool Execution

```python
class ToolChainOrchestrator:
    def __init__(self):
        self.tools = {}
        self.workflows = {}
    
    def register_tool(self, name, handler):
        """Register a tool handler"""
        self.tools[name] = handler
    
    def define_workflow(self, name, steps):
        """Define a workflow with multiple steps"""
        self.workflows[name] = steps
    
    async def execute_workflow(self, workflow_name, initial_params):
        """Execute a complete workflow"""
        
        workflow = self.workflows.get(workflow_name)
        if not workflow:
            return {'error': f'Unknown workflow: {workflow_name}'}
        
        context = {'params': initial_params, 'results': {}}
        
        for step in workflow:
            tool_name = step['tool']
            tool_params = self.prepare_params(step.get('params', {}), context)
            
            # Check conditions
            if 'condition' in step:
                if not self.evaluate_condition(step['condition'], context):
                    continue
            
            # Execute tool
            tool_handler = self.tools.get(tool_name)
            if not tool_handler:
                return {'error': f'Unknown tool: {tool_name}'}
            
            try:
                result = await tool_handler(tool_params)
                context['results'][step.get('name', tool_name)] = result
                
                # Check for early exit
                if step.get('exit_on_success') and result.get('success'):
                    break
                if step.get('exit_on_failure') and not result.get('success'):
                    break
                    
            except Exception as e:
                if step.get('required', True):
                    return {'error': str(e)}
                context['results'][step.get('name', tool_name)] = {'error': str(e)}
        
        return context['results']

# Example workflow definition
orchestrator = ToolChainOrchestrator()

# Register tools
orchestrator.register_tool('check_inventory', check_inventory_handler)
orchestrator.register_tool('create_order', create_order_handler)
orchestrator.register_tool('send_confirmation', send_confirmation_handler)

# Define workflow
orchestrator.define_workflow('complete_purchase', [
    {
        'name': 'inventory_check',
        'tool': 'check_inventory',
        'params': {'product_id': '{{params.product_id}}'},
        'required': True
    },
    {
        'name': 'order_creation',
        'tool': 'create_order',
        'params': {
            'product_id': '{{params.product_id}}',
            'quantity': '{{params.quantity}}',
            'customer_id': '{{params.customer_id}}'
        },
        'condition': 'results.inventory_check.in_stock',
        'required': True
    },
    {
        'name': 'confirmation',
        'tool': 'send_confirmation',
        'params': {
            'order_id': '{{results.order_creation.order_id}}',
            'email': '{{params.customer_email}}'
        },
        'condition': 'results.order_creation.success',
        'required': False
    }
])
```

---

## Error Handling & Fallbacks

### Comprehensive Error Handling

```python
from enum import Enum
import logging

class ToolError(Enum):
    NETWORK_ERROR = "network_error"
    AUTHENTICATION_ERROR = "auth_error"
    VALIDATION_ERROR = "validation_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    TIMEOUT_ERROR = "timeout_error"
    UNKNOWN_ERROR = "unknown_error"

class ToolErrorHandler:
    def __init__(self):
        self.retry_config = {
            ToolError.NETWORK_ERROR: {'max_retries': 3, 'delay': 1000},
            ToolError.RATE_LIMIT_ERROR: {'max_retries': 5, 'delay': 5000},
            ToolError.TIMEOUT_ERROR: {'max_retries': 2, 'delay': 2000}
        }
        self.fallback_responses = {}
        self.logger = logging.getLogger(__name__)
    
    def register_fallback(self, tool_name, fallback_response):
        """Register fallback response for tool"""
        self.fallback_responses[tool_name] = fallback_response
    
    async def execute_with_retry(self, tool_handler, params, tool_name):
        """Execute tool with retry logic"""
        
        retries = 0
        last_error = None
        
        while retries < 3:
            try:
                result = await tool_handler(params)
                return result
                
            except NetworkError as e:
                last_error = e
                retries += 1
                await asyncio.sleep(1 * retries)
                self.logger.warning(f"Network error on {tool_name}, retry {retries}")
                
            except RateLimitError as e:
                last_error = e
                wait_time = e.retry_after or (5 * retries)
                await asyncio.sleep(wait_time)
                retries += 1
                self.logger.warning(f"Rate limit on {tool_name}, waiting {wait_time}s")
                
            except AuthenticationError as e:
                self.logger.error(f"Auth error on {tool_name}: {e}")
                return self.get_fallback_response(tool_name, ToolError.AUTHENTICATION_ERROR)
                
            except ValidationError as e:
                self.logger.error(f"Validation error on {tool_name}: {e}")
                return {
                    'error': 'Invalid parameters provided',
                    'details': str(e),
                    'success': False
                }
                
            except Exception as e:
                last_error = e
                retries += 1
                if retries >= 3:
                    self.logger.error(f"Tool {tool_name} failed after {retries} retries: {e}")
                    return self.get_fallback_response(tool_name, ToolError.UNKNOWN_ERROR)
        
        return self.get_fallback_response(tool_name, ToolError.UNKNOWN_ERROR)
    
    def get_fallback_response(self, tool_name, error_type):
        """Get appropriate fallback response"""
        
        if tool_name in self.fallback_responses:
            return self.fallback_responses[tool_name]
        
        # Default fallback responses by error type
        default_fallbacks = {
            ToolError.NETWORK_ERROR: {
                'success': False,
                'message': 'I\'m having trouble connecting right now. Can I help you with something else?',
                'require_human': False
            },
            ToolError.AUTHENTICATION_ERROR: {
                'success': False,
                'message': 'There\'s an authentication issue. Let me transfer you to support.',
                'require_human': True
            },
            ToolError.RATE_LIMIT_ERROR: {
                'success': False,
                'message': 'The system is very busy right now. Please try again in a few moments.',
                'require_human': False
            },
            ToolError.UNKNOWN_ERROR: {
                'success': False,
                'message': 'I encountered an unexpected issue. Let me get someone to help you.',
                'require_human': True
            }
        }
        
        return default_fallbacks.get(error_type, {
            'success': False,
            'message': 'Something went wrong. Please try again.',
            'require_human': True
        })

# Usage example
error_handler = ToolErrorHandler()

# Register fallback responses
error_handler.register_fallback('check_availability', {
    'success': False,
    'message': 'I cannot check availability right now, but you can call us at 1-800-EXAMPLE',
    'alternative_action': 'phone_transfer'
})

# Execute with error handling
result = await error_handler.execute_with_retry(
    check_availability_tool,
    {'date': '2024-01-15'},
    'check_availability'
)
```

---

## Tool Testing Framework

```python
import pytest
from unittest.mock import Mock, patch

class ToolTestFramework:
    """Framework for testing agent tools"""
    
    @pytest.fixture
    def mock_agent_context(self):
        """Mock agent context for testing"""
        return {
            'agent_id': 'test_agent_123',
            'conversation_id': 'conv_456',
            'user_data': {
                'name': 'Test User',
                'email': 'test@example.com'
            }
        }
    
    @pytest.mark.asyncio
    async def test_webhook_tool(self, mock_agent_context):
        """Test webhook tool execution"""
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            # Mock response
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json.return_value = {
                'success': True,
                'data': 'test_data'
            }
            mock_post.return_value.__aenter__.return_value = mock_response
            
            # Execute tool
            result = await webhook_tool_handler({
                'action': 'test_action',
                'params': {'test': 'value'}
            }, mock_agent_context)
            
            # Assertions
            assert result['success'] == True
            assert 'data' in result
            mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_tool_error_handling(self):
        """Test tool error handling"""
        
        with patch('tool_handler') as mock_handler:
            mock_handler.side_effect = NetworkError('Connection failed')
            
            error_handler = ToolErrorHandler()
            result = await error_handler.execute_with_retry(
                mock_handler,
                {},
                'test_tool'
            )
            
            assert result['success'] == False
            assert 'message' in result
```

---

*Last Updated: 2025-08-15*
*Version: 2.0*
*Maintainer: jeremy@jezweb.net*