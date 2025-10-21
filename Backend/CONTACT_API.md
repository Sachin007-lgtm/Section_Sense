# Contact Form API Documentation

## Overview
Backend API endpoints for handling contact form submissions in the Criminal Law Knowledge Base application.

## Features
- ✅ Submit contact messages
- ✅ Retrieve all messages (admin)
- ✅ Get specific message by ID
- ✅ Mark messages as read
- ✅ Delete messages
- ✅ Get unread message count
- ✅ Email validation
- ✅ Input validation and sanitization
- ✅ Timestamp tracking
- ✅ PostgreSQL/SQLite support

## Database Schema

### ContactMessage Table
```sql
CREATE TABLE contact_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(200) NOT NULL,
    subject VARCHAR(300),
    message TEXT NOT NULL,
    phone VARCHAR(20),
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

### 1. Submit Contact Form
**Endpoint:** `POST /api/v1/contact`

**Description:** Submit a new contact form message

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "subject": "Question about legal services",
  "message": "I would like to know more about...",
  "phone": "+1234567890"
}
```

**Validation Rules:**
- `name`: Required, 2-200 characters
- `email`: Required, valid email format
- `subject`: Optional, max 300 characters
- `message`: Required, min 10 characters
- `phone`: Optional, max 20 characters

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "subject": "Question about legal services",
  "message": "I would like to know more about...",
  "phone": "+1234567890",
  "is_read": false,
  "created_at": "2025-10-22T10:30:00.000Z"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/contact" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "subject": "Legal Query",
    "message": "I need help with a criminal law case."
  }'
```

---

### 2. Get All Contact Messages (Admin)
**Endpoint:** `GET /api/v1/contact/messages`

**Description:** Retrieve all contact messages with pagination

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100, max: 500)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "subject": "Legal Query",
    "message": "I need help...",
    "phone": "+1234567890",
    "is_read": false,
    "created_at": "2025-10-22T10:30:00.000Z"
  },
  {
    "id": 2,
    "name": "Jane Smith",
    "email": "jane@example.com",
    "subject": "Case Information",
    "message": "Can you provide...",
    "phone": null,
    "is_read": true,
    "created_at": "2025-10-21T15:20:00.000Z"
  }
]
```

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/contact/messages?skip=0&limit=50"
```

---

### 3. Get Specific Contact Message
**Endpoint:** `GET /api/v1/contact/messages/{message_id}`

**Description:** Retrieve a specific contact message by ID

**Path Parameters:**
- `message_id`: Integer ID of the message

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Legal Query",
  "message": "I need help with a criminal law case.",
  "phone": "+1234567890",
  "is_read": false,
  "created_at": "2025-10-22T10:30:00.000Z"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Message not found"
}
```

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/contact/messages/1"
```

---

### 4. Mark Message as Read
**Endpoint:** `PATCH /api/v1/contact/messages/{message_id}/read`

**Description:** Mark a contact message as read

**Path Parameters:**
- `message_id`: Integer ID of the message

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Legal Query",
  "message": "I need help...",
  "phone": "+1234567890",
  "is_read": true,
  "created_at": "2025-10-22T10:30:00.000Z"
}
```

**cURL Example:**
```bash
curl -X PATCH "http://localhost:8000/api/v1/contact/messages/1/read"
```

---

### 5. Delete Contact Message
**Endpoint:** `DELETE /api/v1/contact/messages/{message_id}`

**Description:** Delete a contact message

**Path Parameters:**
- `message_id`: Integer ID of the message

**Response (200 OK):**
```json
{
  "message": "Contact message deleted successfully",
  "id": 1
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Message not found"
}
```

**cURL Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/contact/messages/1"
```

---

### 6. Get Unread Count
**Endpoint:** `GET /api/v1/contact/unread-count`

**Description:** Get count of unread contact messages

**Response (200 OK):**
```json
{
  "unread_count": 5
}
```

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/contact/unread-count"
```

---

## Frontend Integration Examples

### JavaScript/TypeScript (Fetch API)

```typescript
// Submit contact form
async function submitContactForm(formData: {
  name: string;
  email: string;
  subject?: string;
  message: string;
  phone?: string;
}) {
  try {
    const response = await fetch('http://localhost:8000/api/v1/contact', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    });

    if (!response.ok) {
      throw new Error('Failed to submit contact form');
    }

    const result = await response.json();
    console.log('Message submitted:', result);
    return result;
  } catch (error) {
    console.error('Error submitting contact form:', error);
    throw error;
  }
}

// Get all messages (admin)
async function getAllMessages(skip = 0, limit = 100) {
  try {
    const response = await fetch(
      `http://localhost:8000/api/v1/contact/messages?skip=${skip}&limit=${limit}`
    );

    if (!response.ok) {
      throw new Error('Failed to fetch messages');
    }

    const messages = await response.json();
    return messages;
  } catch (error) {
    console.error('Error fetching messages:', error);
    throw error;
  }
}

// Mark as read
async function markAsRead(messageId: number) {
  try {
    const response = await fetch(
      `http://localhost:8000/api/v1/contact/messages/${messageId}/read`,
      { method: 'PATCH' }
    );

    if (!response.ok) {
      throw new Error('Failed to mark message as read');
    }

    const updatedMessage = await response.json();
    return updatedMessage;
  } catch (error) {
    console.error('Error marking message as read:', error);
    throw error;
  }
}

// Get unread count
async function getUnreadCount() {
  try {
    const response = await fetch('http://localhost:8000/api/v1/contact/unread-count');
    
    if (!response.ok) {
      throw new Error('Failed to fetch unread count');
    }

    const { unread_count } = await response.json();
    return unread_count;
  } catch (error) {
    console.error('Error fetching unread count:', error);
    throw error;
  }
}
```

### React Example

```tsx
import React, { useState } from 'react';

interface ContactFormData {
  name: string;
  email: string;
  subject: string;
  message: string;
  phone: string;
}

export const ContactForm: React.FC = () => {
  const [formData, setFormData] = useState<ContactFormData>({
    name: '',
    email: '',
    subject: '',
    message: '',
    phone: '',
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/v1/contact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to submit form');
      }

      setSuccess(true);
      setFormData({ name: '', email: '', subject: '', message: '', phone: '' });
    } catch (err) {
      setError('Failed to submit contact form. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Name"
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        required
      />
      <input
        type="email"
        placeholder="Email"
        value={formData.email}
        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        required
      />
      <input
        type="text"
        placeholder="Subject"
        value={formData.subject}
        onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
      />
      <textarea
        placeholder="Message"
        value={formData.message}
        onChange={(e) => setFormData({ ...formData, message: e.target.value })}
        required
        minLength={10}
      />
      <input
        type="tel"
        placeholder="Phone (optional)"
        value={formData.phone}
        onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Submitting...' : 'Submit'}
      </button>
      {success && <p>Message sent successfully!</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </form>
  );
};
```

---

## Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

**404 Not Found:**
```json
{
  "detail": "Message not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Failed to submit contact form: Database connection error"
}
```

---

## Testing

### Test with cURL

```bash
# Submit a test message
curl -X POST "http://localhost:8000/api/v1/contact" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "subject": "Test Subject",
    "message": "This is a test message from the contact form API."
  }'

# Get all messages
curl -X GET "http://localhost:8000/api/v1/contact/messages"

# Get unread count
curl -X GET "http://localhost:8000/api/v1/contact/unread-count"
```

### Test with Python

```python
import requests

# Submit contact form
response = requests.post(
    "http://localhost:8000/api/v1/contact",
    json={
        "name": "Test User",
        "email": "test@example.com",
        "subject": "Test Subject",
        "message": "This is a test message"
    }
)
print(response.json())
```

---

## Security Considerations

1. **Input Validation:** All inputs are validated using Pydantic schemas
2. **Email Validation:** Email addresses are validated using EmailStr
3. **SQL Injection Prevention:** SQLAlchemy ORM prevents SQL injection
4. **Length Limits:** All string fields have maximum length constraints
5. **Rate Limiting:** Consider adding rate limiting in production
6. **Authentication:** Add authentication for admin endpoints in production
7. **CORS:** Configure CORS properly for production deployment

---

## Deployment Notes

### Environment Variables
No additional environment variables needed - uses existing DATABASE_URL

### Database Migration
The contact_messages table will be automatically created when the app starts.

### Production Checklist
- [ ] Add authentication for admin endpoints
- [ ] Implement rate limiting (e.g., 5 submissions per hour per IP)
- [ ] Add email notifications for new contact submissions
- [ ] Set up CORS whitelist for allowed origins
- [ ] Add spam protection (e.g., reCAPTCHA)
- [ ] Enable HTTPS for all endpoints
- [ ] Add logging and monitoring
- [ ] Set up backup strategy for contact messages

---

## Future Enhancements

1. **Email Notifications:** Send email to admin when new message is received
2. **Auto-reply:** Send confirmation email to user after submission
3. **Spam Detection:** Integrate spam detection service
4. **File Attachments:** Allow users to attach files
5. **Categories:** Add message categories (Support, Sales, Feedback, etc.)
6. **Priority Levels:** Mark urgent messages
7. **Response Tracking:** Track admin responses to messages
8. **Analytics:** Dashboard showing message statistics

---

## Support

For issues or questions, please contact the development team or create an issue in the repository.
