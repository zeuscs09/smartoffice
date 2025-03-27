# Frappe Framework API Documentation

## Table of Contents
1. [Authentication](#1-authentication)
2. [Basic CRUD Operations](#2-basic-crud-operations)
3. [Document Operations](#3-document-operations)
4. [File Operations](#4-file-operations)
5. [Advanced Queries](#5-advanced-queries)
6. [Error Handling](#6-error-handling)
7. [Utility Classes](#7-utility-classes)
8. [Next.js Integration](#8-nextjs-integration)
9. [Frappe Utility Functions](#9-frappe-utility-functions)
10. [Frappe Hooks](#10-frappe-hooks)

## 1. Authentication

การยืนยันตัวตนเพื่อเข้าถึง Frappe API

### 1.1 Login Authentication

**Python**
```python
import requests

def login_auth():
    session = requests.Session()  # ใช้ session เพื่อจัดการ cookies
    url = "https://your-site.com/api/method/login"
    data = {
        "usr": "username",
        "pwd": "password"
    }
    response = session.post(url, json=data)
    
    # เก็บ session ไว้ใช้ต่อไป
    # session จะเก็บ cookies ไว้ให้โดยอัตโนมัติ
    
    return response.json()
```

**JavaScript**
```javascript
async function loginAuth() {
    const response = await fetch('https://your-site.com/api/method/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            usr: 'username',
            pwd: 'password'
        }),
        credentials: 'include'  // สำคัญเพื่อให้ browser รับ cookies
    });
    return await response.json();
}
```

**Login Response Format**
```json
{
  "message": "Logged In",
  "home_page": "/app",
  "full_name": "User Name"
}
```

**หมายเหตุ:**
- ผลลัพธ์การ login จะได้รับข้อมูลในรูปแบบ JSON จำกัด ไม่ได้รวม sid และข้อมูลอื่นตามที่ระบุในเอกสารเดิม
- Session ID (sid) จะถูกตั้งค่าเป็น HTTP cookie โดยอัตโนมัติ ไม่ได้อยู่ในผลลัพธ์ JSON
- การเรียกใช้ API ต่อไปจะใช้ cookie ที่ได้รับโดยอัตโนมัติ

### 1.2 Token Authentication (API Key)

Token Authentication เป็นวิธีการยืนยันตัวตนที่ปลอดภัยและแนะนำสำหรับการเชื่อมต่อระหว่างแอปพลิเคชัน

**Python**
```python
import requests

def token_auth():
    # ใช้ API Key และ API Secret ที่สร้างจากระบบ
    api_key = "your_api_key"
    api_secret = "your_api_secret"
    headers = {
        "Authorization": f"token {api_key}:{api_secret}"
    }
    response = requests.get(
        "https://your-site.com/api/resource/User", 
        headers=headers
    )
    return response.json()
```

**JavaScript**
```javascript
async function tokenAuth() {
    // ใช้ API Key และ API Secret ที่สร้างจากระบบ
    const apiKey = "your_api_key";
    const apiSecret = "your_api_secret";
    const headers = {
        'Authorization': `token ${apiKey}:${apiSecret}`
    };
    const response = await fetch('https://your-site.com/api/resource/User', {
        headers
    });
    return await response.json();
}
```

**หมายเหตุ:**
- ไม่สามารถใช้ sid จาก login เป็น token ได้โดยตรง เนื่องจาก sid จะถูกจัดการผ่าน cookies 
- API Key มีความปลอดภัยและเหมาะสมสำหรับการเชื่อมต่อระหว่างแอปพลิเคชัน

### 1.3 How to Get Authentication Token

Frappe Framework รองรับการยืนยันตัวตน 2 วิธีหลัก: Session Authentication และ Token Authentication

#### 1.3.1 Session Authentication (Using Cookies)

Session Authentication ใช้ cookies ซึ่งได้รับโดยอัตโนมัติหลังจาก login

**Python**
```python
import requests

def login_and_use_cookies():
    # 1. Login โดยใช้ session ที่เก็บ cookies
    session = requests.Session()
    login_url = "https://your-site.com/api/method/login"
    login_data = {
        "usr": "username",
        "pwd": "password"
    }
    response = session.post(login_url, json=login_data)
    result = response.json()
    
    # 2. ใช้งาน session เดิมในการเรียก API ถัดไป (cookies จะถูกส่งอัตโนมัติ)
    api_response = session.get(
        "https://your-site.com/api/resource/User", 
        headers={"Accept": "application/json"}
    )
    
    return api_response.json()
```

**JavaScript**
```javascript
async function loginAndUseCookies() {
    // 1. Login เพื่อรับ cookies
    const loginResponse = await fetch('https://your-site.com/api/method/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            usr: 'username',
            pwd: 'password'
        }),
        credentials: 'include'  // ส่วนสำคัญเพื่อให้ browser รับ cookies
    });
    
    const loginData = await loginResponse.json();
    console.log('Login successful:', loginData);
    
    // 2. เรียกใช้ API ต่อไปโดยใช้ cookies ที่ได้รับ
    const apiResponse = await fetch('https://your-site.com/api/resource/User', {
        headers: {
            'Accept': 'application/json'
        },
        credentials: 'include'  // ส่วนสำคัญเพื่อให้ browser ส่ง cookies
    });
    
    return await apiResponse.json();
}
```

**ข้อควรระวัง:**
- `credentials: 'include'` จำเป็นเพื่อให้ browser รับ/ส่ง cookies
- กรณีมีการเรียกข้าม domain (CORS) จะต้องมีการตั้งค่า `Access-Control-Allow-Credentials: true` ที่ฝั่ง server
- Session จะหมดอายุหลังจากไม่ได้ใช้งานระยะหนึ่ง (ขึ้นอยู่กับการตั้งค่าของ server)

#### 1.3.2 Token Authentication (Using API Key)

API Key เป็นวิธีที่แนะนำสำหรับแอปพลิเคชันที่ต้องการเชื่อมต่อกับ Frappe API โดยไม่ต้อง login ทุกครั้ง

**วิธีสร้าง API Key:**

1. Login เข้าสู่ Frappe / ERPNext ด้วย User ที่มีสิทธิ์เพียงพอ
2. ไปที่ User > Settings > API Access
3. คลิก "Generate Keys"
4. ระบบจะสร้าง API Key และ API Secret ให้อัตโนมัติ
5. บันทึก API Key และ API Secret ไว้ในที่ปลอดภัย (จะไม่สามารถดู API Secret ได้อีกหลังจากปิดหน้าจอนี้)

**Python**
```python
import requests

def use_api_key():
    # ข้อมูล API Key และ Secret ที่ได้จากขั้นตอนการสร้าง
    api_key = "your_api_key_here"
    api_secret = "your_api_secret_here"
    
    # สร้าง Authorization header
    headers = {
        "Authorization": f"token {api_key}:{api_secret}",
        "Content-Type": "application/json"
    }
    
    # เรียกใช้ API
    response = requests.get(
        "https://your-site.com/api/resource/User",
        headers=headers
    )
    
    return response.json()
```

**JavaScript**
```javascript
async function useApiKey() {
    // ข้อมูล API Key และ Secret ที่ได้จากขั้นตอนการสร้าง
    const apiKey = "your_api_key_here";
    const apiSecret = "your_api_secret_here";
    
    // สร้าง Authorization header
    const headers = {
        'Authorization': `token ${apiKey}:${apiSecret}`,
        'Content-Type': 'application/json'
    };
    
    // เรียกใช้ API
    const response = await fetch('https://your-site.com/api/resource/User', {
        headers
    });
    
    return await response.json();
}
```

#### 1.3.3 การใช้งานกับ Next.js

ในการใช้งานกับ Next.js ควรเก็บ API Key และ Secret ไว้ใน Environment Variables:

**.env.local**
```
NEXT_PUBLIC_FRAPPE_URL=https://your-site.com
NEXT_PUBLIC_API_KEY=your_api_key
NEXT_PUBLIC_API_SECRET=your_api_secret
```

**หมายเหตุ:** ไม่ควรใช้ `NEXT_PUBLIC_` prefix กับ sensitive information หากใช้ข้อมูลนี้ใน client-side component ควรสร้าง API Route เพื่อเป็นตัวกลางแทน:

**pages/api/frappe-proxy.js**
```javascript
export default async function handler(req, res) {
  const apiKey = process.env.API_KEY; // ไม่มี NEXT_PUBLIC_ prefix
  const apiSecret = process.env.API_SECRET;
  
  const response = await fetch(`${process.env.FRAPPE_URL}${req.query.endpoint}`, {
    method: req.method,
    headers: {
      'Authorization': `token ${apiKey}:${apiSecret}`,
      'Content-Type': 'application/json'
    },
    body: req.method !== 'GET' ? JSON.stringify(req.body) : undefined
  });
  
  const data = await response.json();
  res.status(response.status).json(data);
}
```

**การเรียกใช้งานใน Component**
```javascript
// client-side component
const fetchData = async () => {
  const response = await fetch('/api/frappe-proxy?endpoint=/api/resource/User');
  return await response.json();
};
```

**ข้อควรระวัง:** เก็บ API keys, secrets และ session IDs ไว้ในที่ปลอดภัย และไม่ควรเปิดเผยในโค้ดที่เข้าถึงได้จากฝั่ง client โดยตรง

## 2. Basic CRUD Operations

การดำเนินการพื้นฐานกับข้อมูล

### 2.1 Create (POST)

#### การใช้ Session Authentication (Cookies)

**Python**
```python
import requests

def create_document_with_session(doctype, data):
    # ใช้ session ที่ login แล้ว
    session = requests.Session()
    
    # 1. Login
    login_url = "https://your-site.com/api/method/login"
    login_data = {"usr": "username", "pwd": "password"}
    session.post(login_url, json=login_data)
    
    # 2. Create document
    response = session.post(
        f"https://your-site.com/api/resource/{doctype}",
        json=data
    )
    return response.json()

# ตัวอย่างการใช้งาน
todo = create_document_with_session("Todo", {
    "description": "New Task",
    "status": "Open"
})
```

**JavaScript**
```javascript
async function createDocumentWithSession(doctype, data) {
    // 1. Login
    await fetch('https://your-site.com/api/method/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            usr: 'username',
            pwd: 'password'
        }),
        credentials: 'include'
    });
    
    // 2. Create document
    const response = await fetch(`https://your-site.com/api/resource/${doctype}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data),
        credentials: 'include'
    });
    return await response.json();
}

// ตัวอย่างการใช้งาน
const todo = await createDocumentWithSession('Todo', {
    description: 'New Task',
    status: 'Open'
});
```

#### การใช้ API Key Authentication

**Python**
```python
import requests

def create_document_with_api_key(doctype, data):
    api_key = "your_api_key"
    api_secret = "your_api_secret"
    headers = {
        "Authorization": f"token {api_key}:{api_secret}",
        "Content-Type": "application/json"
    }
    response = requests.post(
        f"https://your-site.com/api/resource/{doctype}",
        json=data,
        headers=headers
    )
    return response.json()

# ตัวอย่างการใช้งาน
todo = create_document_with_api_key("Todo", {
    "description": "New Task",
    "status": "Open"
})
```

**JavaScript**
```javascript
async function createDocumentWithApiKey(doctype, data) {
    const apiKey = "your_api_key";
    const apiSecret = "your_api_secret";
    const headers = {
        'Authorization': `token ${apiKey}:${apiSecret}`,
        'Content-Type': 'application/json'
    };
    const response = await fetch(`https://your-site.com/api/resource/${doctype}`, {
        method: 'POST',
        headers,
        body: JSON.stringify(data)
    });
    return await response.json();
}

// ตัวอย่างการใช้งาน
const todo = await createDocumentWithApiKey('Todo', {
    description: 'New Task',
    status: 'Open'
});
```

### 2.2 Read (GET)

#### การใช้ Session Authentication (Cookies)

**Python**
```python
import requests
import json

def get_document_with_session(doctype, name=None, filters=None):
    # ใช้ session ที่ login แล้ว
    session = requests.Session()
    
    # 1. Login
    login_url = "https://your-site.com/api/method/login"
    login_data = {"usr": "username", "pwd": "password"}
    session.post(login_url, json=login_data)
    
    # 2. Get document
    if name:
        url = f"https://your-site.com/api/resource/{doctype}/{name}"
    else:
        url = f"https://your-site.com/api/resource/{doctype}"
        if filters:
            url += f"?filters={json.dumps(filters)}"
    
    response = session.get(url)
    return response.json()

# ตัวอย่างการใช้งาน
todo = get_document_with_session("Todo", "TODO0001")
todos = get_document_with_session("Todo", filters=[["status", "=", "Open"]])
```

**JavaScript**
```javascript
async function getDocumentWithSession(doctype, name = null, filters = null) {
    // 1. Login
    await fetch('https://your-site.com/api/method/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            usr: 'username',
            pwd: 'password'
        }),
        credentials: 'include'
    });
    
    // 2. Get document
    let url = `https://your-site.com/api/resource/${doctype}`;
    if (name) {
        url += `/${name}`;
    } else if (filters) {
        url += `?filters=${JSON.stringify(filters)}`;
    }
    
    const response = await fetch(url, { 
        credentials: 'include' 
    });
    return await response.json();
}

// ตัวอย่างการใช้งาน
const todo = await getDocumentWithSession('Todo', 'TODO0001');
const todos = await getDocumentWithSession('Todo', null, [['status', '=', 'Open']]);
```

#### การใช้ API Key Authentication

**Python**
```python
import requests
import json

def get_document_with_api_key(doctype, name=None, filters=None):
    api_key = "your_api_key"
    api_secret = "your_api_secret"
    headers = {
        "Authorization": f"token {api_key}:{api_secret}"
    }
    
    if name:
        url = f"https://your-site.com/api/resource/{doctype}/{name}"
    else:
        url = f"https://your-site.com/api/resource/{doctype}"
        if filters:
            url += f"?filters={json.dumps(filters)}"
    
    response = requests.get(url, headers=headers)
    return response.json()

# ตัวอย่างการใช้งาน
todo = get_document_with_api_key("Todo", "TODO0001")
todos = get_document_with_api_key("Todo", filters=[["status", "=", "Open"]])
```

**JavaScript**
```javascript
async function getDocumentWithApiKey(doctype, name = null, filters = null) {
    const apiKey = "your_api_key";
    const apiSecret = "your_api_secret";
    const headers = {
        'Authorization': `token ${apiKey}:${apiSecret}`
    };
    
    let url = `https://your-site.com/api/resource/${doctype}`;
    if (name) {
        url += `/${name}`;
    } else if (filters) {
        url += `?filters=${JSON.stringify(filters)}`;
    }
    
    const response = await fetch(url, { headers });
    return await response.json();
}

// ตัวอย่างการใช้งาน
const todo = await getDocumentWithApiKey('Todo', 'TODO0001');
const todos = await getDocumentWithApiKey('Todo', null, [['status', '=', 'Open']]);
```

### 2.3 Update (PUT)

#### การใช้ Session Authentication (Cookies)

**Python**
```python
import requests

def update_document_with_session(doctype, name, data):
    # ใช้ session ที่ login แล้ว
    session = requests.Session()
    
    # 1. Login
    login_url = "https://your-site.com/api/method/login"
    login_data = {"usr": "username", "pwd": "password"}
    session.post(login_url, json=login_data)
    
    # 2. Update document
    response = session.put(
        f"https://your-site.com/api/resource/{doctype}/{name}",
        json=data
    )
    return response.json()

# ตัวอย่างการใช้งาน
updated_todo = update_document_with_session("Todo", "TODO0001", {
    "status": "Completed"
})
```

**JavaScript**
```javascript
async function updateDocumentWithSession(doctype, name, data) {
    // 1. Login
    await fetch('https://your-site.com/api/method/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            usr: 'username',
            pwd: 'password'
        }),
        credentials: 'include'
    });
    
    // 2. Update document
    const response = await fetch(
        `https://your-site.com/api/resource/${doctype}/${name}`,
        {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
            credentials: 'include'
        }
    );
    return await response.json();
}

// ตัวอย่างการใช้งาน
const updatedTodo = await updateDocumentWithSession('Todo', 'TODO0001', {
    status: 'Completed'
});
```

#### การใช้ API Key Authentication

**Python**
```python
import requests

def update_document_with_api_key(doctype, name, data):
    api_key = "your_api_key"
    api_secret = "your_api_secret"
    headers = {
        "Authorization": f"token {api_key}:{api_secret}",
        "Content-Type": "application/json"
    }
    response = requests.put(
        f"https://your-site.com/api/resource/{doctype}/{name}",
        json=data,
        headers=headers
    )
    return response.json()

# ตัวอย่างการใช้งาน
updated_todo = update_document_with_api_key("Todo", "TODO0001", {
    "status": "Completed"
})
```

**JavaScript**
```javascript
async function updateDocumentWithApiKey(doctype, name, data) {
    const apiKey = "your_api_key";
    const apiSecret = "your_api_secret";
    const headers = {
        'Authorization': `token ${apiKey}:${apiSecret}`,
        'Content-Type': 'application/json'
    };
    const response = await fetch(
        `https://your-site.com/api/resource/${doctype}/${name}`,
        {
            method: 'PUT',
            headers,
            body: JSON.stringify(data)
        }
    );
    return await response.json();
}

// ตัวอย่างการใช้งาน
const updatedTodo = await updateDocumentWithApiKey('Todo', 'TODO0001', {
    status: 'Completed'
});
```

### 2.4 Delete (DELETE)

#### การใช้ Session Authentication (Cookies)

**Python**
```python
import requests

def delete_document_with_session(doctype, name):
    # ใช้ session ที่ login แล้ว
    session = requests.Session()
    
    # 1. Login
    login_url = "https://your-site.com/api/method/login"
    login_data = {"usr": "username", "pwd": "password"}
    session.post(login_url, json=login_data)
    
    # 2. Delete document
    response = session.delete(
        f"https://your-site.com/api/resource/{doctype}/{name}"
    )
    return response.json()

# ตัวอย่างการใช้งาน
delete_document_with_session("Todo", "TODO0001")
```

**JavaScript**
```javascript
async function deleteDocumentWithSession(doctype, name) {
    // 1. Login
    await fetch('https://your-site.com/api/method/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            usr: 'username',
            pwd: 'password'
        }),
        credentials: 'include'
    });
    
    // 2. Delete document
    const response = await fetch(
        `https://your-site.com/api/resource/${doctype}/${name}`,
        {
            method: 'DELETE',
            credentials: 'include'
        }
    );
    return await response.json();
}

// ตัวอย่างการใช้งาน
await deleteDocumentWithSession('Todo', 'TODO0001');
```

#### การใช้ API Key Authentication

**Python**
```python
import requests

def delete_document_with_api_key(doctype, name):
    api_key = "your_api_key"
    api_secret = "your_api_secret"
    headers = {
        "Authorization": f"token {api_key}:{api_secret}"
    }
    response = requests.delete(
        f"https://your-site.com/api/resource/{doctype}/{name}",
        headers=headers
    )
    return response.json()

# ตัวอย่างการใช้งาน
delete_document_with_api_key("Todo", "TODO0001")
```

**JavaScript**
```javascript
async function deleteDocumentWithApiKey(doctype, name) {
    const apiKey = "your_api_key";
    const apiSecret = "your_api_secret";
    const headers = {
        'Authorization': `token ${apiKey}:${apiSecret}`
    };
    const response = await fetch(
        `https://your-site.com/api/resource/${doctype}/${name}`,
        {
            method: 'DELETE',
            headers
        }
    );
    return await response.json();
}

// ตัวอย่างการใช้งาน
await deleteDocumentWithApiKey('Todo', 'TODO0001');
```

## 3. Document Operations

การดำเนินการกับเอกสาร

### 3.1 Submit Document

#### การใช้ Session Authentication (Cookies)

**Python**
```python
import requests

def submit_document_with_session(doctype, name):
    # ใช้ session ที่ login แล้ว
    session = requests.Session()
    
    # 1. Login
    login_url = "https://your-site.com/api/method/login"
    login_data = {"usr": "username", "pwd": "password"}
    session.post(login_url, json=login_data)
    
    # 2. Submit document
    response = session.post(
        f"https://your-site.com/api/resource/{doctype}/{name}/submit"
    )
    return response.json()

# ตัวอย่างการใช้งาน
submit_document_with_session("Sales Order", "SO-0001")
```

**JavaScript**
```javascript
async function submitDocumentWithSession(doctype, name) {
    // 1. Login
    await fetch('https://your-site.com/api/method/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            usr: 'username',
            pwd: 'password'
        }),
        credentials: 'include'
    });
    
    // 2. Submit document
    const response = await fetch(
        `https://your-site.com/api/resource/${doctype}/${name}/submit`,
        {
            method: 'POST',
            credentials: 'include'
        }
    );
    return await response.json();
}

// ตัวอย่างการใช้งาน
await submitDocumentWithSession('Sales Order', 'SO-0001');
```

#### การใช้ API Key Authentication

**Python**
```python
import requests

def submit_document_with_api_key(doctype, name):
    api_key = "your_api_key"
    api_secret = "your_api_secret"
    headers = {
        "Authorization": f"token {api_key}:{api_secret}"
    }
    response = requests.post(
        f"https://your-site.com/api/resource/{doctype}/{name}/submit",
        headers=headers
    )
    return response.json()

# ตัวอย่างการใช้งาน
submit_document_with_api_key("Sales Order", "SO-0001")
```

**JavaScript**
```javascript
async function submitDocumentWithApiKey(doctype, name) {
    const apiKey = "your_api_key";
    const apiSecret = "your_api_secret";
    const headers = {
        'Authorization': `token ${apiKey}:${apiSecret}`
    };
    const response = await fetch(
        `https://your-site.com/api/resource/${doctype}/${name}/submit`,
        {
            method: 'POST',
            headers
        }
    );
    return await response.json();
}

// ตัวอย่างการใช้งาน
await submitDocumentWithApiKey('Sales Order', 'SO-0001');
```

### 3.2 Cancel Document

#### การใช้ Session Authentication (Cookies)

**Python**
```python
import requests

def cancel_document_with_session(doctype, name):
    # ใช้ session ที่ login แล้ว
    session = requests.Session()
    
    # 1. Login
    login_url = "https://your-site.com/api/method/login"
    login_data = {"usr": "username", "pwd": "password"}
    session.post(login_url, json=login_data)
    
    # 2. Cancel document
    response = session.post(
        f"https://your-site.com/api/resource/{doctype}/{name}/cancel"
    )
    return response.json()

# ตัวอย่างการใช้งาน
cancel_document_with_session("Sales Order", "SO-0001")
```

**JavaScript**
```javascript
async function cancelDocumentWithSession(doctype, name) {
    // 1. Login
    await fetch('https://your-site.com/api/method/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            usr: 'username',
            pwd: 'password'
        }),
        credentials: 'include'
    });
    
    // 2. Cancel document
    const response = await fetch(
        `https://your-site.com/api/resource/${doctype}/${name}/cancel`,
        {
            method: 'POST',
            credentials: 'include'
        }
    );
    return await response.json();
}

// ตัวอย่างการใช้งาน
await cancelDocumentWithSession('Sales Order', 'SO-0001');
```

#### การใช้ API Key Authentication

**Python**
```python
import requests

def cancel_document_with_api_key(doctype, name):
    api_key = "your_api_key"
    api_secret = "your_api_secret"
    headers = {
        "Authorization": f"token {api_key}:{api_secret}"
    }
    response = requests.post(
        f"https://your-site.com/api/resource/{doctype}/{name}/cancel",
        headers=headers
    )
    return response.json()

# ตัวอย่างการใช้งาน
cancel_document_with_api_key("Sales Order", "SO-0001")
```

**JavaScript**
```javascript
async function cancelDocumentWithApiKey(doctype, name) {
    const apiKey = "your_api_key";
    const apiSecret = "your_api_secret";
    const headers = {
        'Authorization': `token ${apiKey}:${apiSecret}`
    };
    const response = await fetch(
        `https://your-site.com/api/resource/${doctype}/${name}/cancel`,
        {
            method: 'POST',
            headers
        }
    );
    return await response.json();
}

// ตัวอย่างการใช้งาน
await cancelDocumentWithApiKey('Sales Order', 'SO-0001');
```

### 3.3 Amend Document

#### การใช้ Session Authentication (Cookies)

**Python**
```python
import requests

def amend_document_with_session(doctype, name):
    # ใช้ session ที่ login แล้ว
    session = requests.Session()
    
    # 1. Login
    login_url = "https://your-site.com/api/method/login"
    login_data = {"usr": "username", "pwd": "password"}
    session.post(login_url, json=login_data)
    
    # 2. Amend document
    response = session.post(
        f"https://your-site.com/api/resource/{doctype}/{name}/amend"
    )
    return response.json()

# ตัวอย่างการใช้งาน
amend_document_with_session("Sales Order", "SO-0001")
```

**JavaScript**
```javascript
async function amendDocumentWithSession(doctype, name) {
    // 1. Login
    await fetch('https://your-site.com/api/method/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            usr: 'username',
            pwd: 'password'
        }),
        credentials: 'include'
    });
    
    // 2. Amend document
    const response = await fetch(
        `https://your-site.com/api/resource/${doctype}/${name}/amend`,
        {
            method: 'POST',
            credentials: 'include'
        }
    );
    return await response.json();
}

// ตัวอย่างการใช้งาน
await amendDocumentWithSession('Sales Order', 'SO-0001');
```

#### การใช้ API Key Authentication

**Python**
```python
import requests

def amend_document_with_api_key(doctype, name):
    api_key = "your_api_key"
    api_secret = "your_api_secret"
    headers = {
        "Authorization": f"token {api_key}:{api_secret}"
    }
    response = requests.post(
        f"https://your-site.com/api/resource/{doctype}/{name}/amend",
        headers=headers
    )
    return response.json()

# ตัวอย่างการใช้งาน
amend_document_with_api_key("Sales Order", "SO-0001")
```

**JavaScript**
```javascript
async function amendDocumentWithApiKey(doctype, name) {
    const apiKey = "your_api_key";
    const apiSecret = "your_api_secret";
    const headers = {
        'Authorization': `token ${apiKey}:${apiSecret}`
    };
    const response = await fetch(
        `https://your-site.com/api/resource/${doctype}/${name}/amend`,
        {
            method: 'POST',
            headers
        }
    );
    return await response.json();
}

// ตัวอย่างการใช้งาน
await amendDocumentWithApiKey('Sales Order', 'SO-0001');
```

## 4. File Operations

การดำเนินการกับไฟล์

### 4.1 Get Document Version

**Python**
```python
import requests

def get_document_versions(doctype, name):
    headers = {"Authorization": "token api_key:api_secret"}
    response = requests.get(
        f"https://your-site.com/api/resource/{doctype}/{name}/versions",
        headers=headers
    )
    return response.json()

# ตัวอย่างการใช้งาน
versions = get_document_versions("Sales Order", "SO-0001")
```

**JavaScript**
```javascript
async function getDocumentVersions(doctype, name) {
    const headers = {
        'Authorization': 'token api_key:api_secret'
    };
    const response = await fetch(
        `https://your-site.com/api/resource/${doctype}/${name}/versions`,
        { headers }
    );
    return await response.json();
}

// ตัวอย่างการใช้งาน
const versions = await getDocumentVersions('Sales Order', 'SO-0001');
```

### 4.2 Get Document Attachments

**Python**
```python
import requests

def get_document_attachments(doctype, name):
    headers = {"Authorization": "token api_key:api_secret"}
    response = requests.get(
        f"https://your-site.com/api/resource/{doctype}/{name}/attachments",
        headers=headers
    )
    return response.json()

# ตัวอย่างการใช้งาน
attachments = get_document_attachments("Sales Order", "SO-0001")
```

**JavaScript**
```javascript
async function getDocumentAttachments(doctype, name) {
    const headers = {
        'Authorization': 'token api_key:api_secret'
    };
    const response = await fetch(
        `https://your-site.com/api/resource/${doctype}/${name}/attachments`,
        { headers }
    );
    return await response.json();
}

// ตัวอย่างการใช้งาน
const attachments = await getDocumentAttachments('Sales Order', 'SO-0001');
```

### 4.3 Upload File

**Python**
```python
import requests

def upload_file(file_path, doctype=None, name=None):
    headers = {"Authorization": "token api_key:api_secret"}
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {}
        if doctype and name:
            data = {
                'doctype': doctype,
                'name': name
            }
        
        response = requests.post(
            "https://your-site.com/api/method/upload_file",
            files=files,
            data=data,
            headers=headers
        )
    return response.json()

# ตัวอย่างการใช้งาน
upload_file("path/to/file.pdf", "Sales Order", "SO-0001")
```

**JavaScript**
```javascript
async function uploadFile(file, doctype = null, name = null) {
    const formData = new FormData();
    formData.append('file', file);
    
    if (doctype && name) {
        formData.append('doctype', doctype);
        formData.append('name', name);
    }
    
    const headers = {
        'Authorization': 'token api_key:api_secret'
        // Don't set Content-Type here, let the browser set it with boundary
    };
    
    const response = await fetch('/api/method/upload_file', {
        method: 'POST',
        body: formData,
        headers
    });
    return await response.json();
}

// ตัวอย่างการใช้งาน
const fileInput = document.querySelector('input[type="file"]');
const file = fileInput.files[0];
await uploadFile(file, 'Sales Order', 'SO-0001');
```

## 5. Advanced Queries

การค้นหาข้อมูลขั้นสูง

### 5.1 Count Records

**Python**
```python
import requests
import json

def get_count(doctype, filters=None):
    headers = {"Authorization": "token api_key:api_secret"}
    params = f"?filters={json.dumps(filters)}" if filters else ""
    
    response = requests.get(
        f"https://your-site.com/api/resource/{doctype}/count{params}",
        headers=headers
    )
    return response.json()

# ตัวอย่างการใช้งาน
count = get_count("Todo", [["status", "=", "Open"]])
```

**JavaScript**
```javascript
async function getCount(doctype, filters = null) {
    const headers = {
        'Authorization': 'token api_key:api_secret'
    };
    const params = filters ? `?filters=${JSON.stringify(filters)}` : '';
    
    const response = await fetch(
        `/api/resource/${doctype}/count${params}`,
        { headers }
    );
    return await response.json();
}

// ตัวอย่างการใช้งาน
const count = await getCount('Todo', [['status', '=', 'Open']]);
```

### 5.2 Get List with Pagination

**Python**
```python
import requests
import json

def get_list(doctype, params):
    headers = {"Authorization": "token api_key:api_secret"}
    
    query_params = {
        'fields': json.dumps(params.get('fields', [])),
        'filters': json.dumps(params.get('filters', [])),
        'order_by': params.get('order_by'),
        'limit_start': params.get('limit_start'),
        'limit_page_length': params.get('limit_page_length')
    }
    
    response = requests.get(
        f"https://your-site.com/api/resource/{doctype}",
        params=query_params,
        headers=headers
    )
    return response.json()

# ตัวอย่างการใช้งาน
todos = get_list("Todo", {
    "fields": ["name", "description", "status"],
    "filters": [["status", "=", "Open"]],
    "order_by": "creation desc",
    "limit_start": 0,
    "limit_page_length": 20
})
```

**JavaScript**
```javascript
async function getList(doctype, params) {
    const headers = {
        'Authorization': 'token api_key:api_secret'
    };
    const queryParams = new URLSearchParams();
    
    if (params.fields) {
        queryParams.append('fields', JSON.stringify(params.fields));
    }
    if (params.filters) {
        queryParams.append('filters', JSON.stringify(params.filters));
    }
    if (params.order_by) {
        queryParams.append('order_by', params.order_by);
    }
    if (params.limit_start !== undefined) {
        queryParams.append('limit_start', params.limit_start.toString());
    }
    if (params.limit_page_length !== undefined) {
        queryParams.append('limit_page_length', params.limit_page_length.toString());
    }

    const response = await fetch(
        `/api/resource/${doctype}?${queryParams}`,
        { headers }
    );
    return await response.json();
}

// ตัวอย่างการใช้งาน
const todos = await getList('Todo', {
    fields: ['name', 'description', 'status'],
    filters: [['status', '=', 'Open']],
    order_by: 'creation desc',
    limit_start: 0,
    limit_page_length: 20
});
```

## 6. Error Handling

การจัดการข้อผิดพลาด

### 6.1 HTTP Status Codes
- 200: Success
- 401: Authentication Error
- 403: Permission Error
- 404: Not Found
- 417: Validation Error
- 500: Server Error

### 6.2 Error Handling Examples

**Python**
```python
def handle_api_error(response):
    if response.status_code != 200:
        error_data = response.json()
        raise Exception(f"API Error: {error_data.get('message', 'Unknown error')}")
    return response.json()
```

**JavaScript**
```javascript
async function handleApiError(response) {
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Unknown error');
    }
    return await response.json();
}
```

### 6.3 Error Response Format
```json
{
    "exc": "Exception details",
    "exc_type": "ValidationError",
    "message": "Error message"
}
```

## 7. Utility Classes

เครื่องมือที่ช่วยในการพัฒนา

### 7.1 API Response Handler

**Python**
```python
class APIResponseHandler:
    @staticmethod
    def handle(response):
        if response.status_code != 200:
            error = response.json()
            raise Exception(error.get('message', 'API Error'))
        return response.json()
```

**JavaScript**
```javascript
class APIResponseHandler {
    static async handle(response) {
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'API Error');
        }
        return await response.json();
    }
}
```

### 7.2 Document Operations Utility

**Python**
```python
class DocTypeOperations:
    def __init__(self, doctype):
        self.doctype = doctype
        self.headers = {"Authorization": "token api_key:api_secret"}

    def submit(self, name):
        response = requests.post(
            f"https://your-site.com/api/resource/{self.doctype}/{name}/submit",
            headers=self.headers
        )
        return APIResponseHandler.handle(response)

    def cancel(self, name):
        response = requests.post(
            f"https://your-site.com/api/resource/{self.doctype}/{name}/cancel",
            headers=self.headers
        )
        return APIResponseHandler.handle(response)

    def delete(self, name):
        response = requests.delete(
            f"https://your-site.com/api/resource/{self.doctype}/{name}",
            headers=self.headers
        )
        return APIResponseHandler.handle(response)

    def update(self, name, data):
        response = requests.put(
            f"https://your-site.com/api/resource/{self.doctype}/{name}",
            json=data,
            headers=self.headers
        )
        return APIResponseHandler.handle(response)

# ตัวอย่างการใช้งาน
sales_order = DocTypeOperations('Sales Order')
sales_order.submit('SO-0001')
```

**JavaScript**
```javascript
class DocTypeOperations {
    constructor(doctype) {
        this.doctype = doctype;
        this.headers = {
            'Authorization': 'token api_key:api_secret'
        };
    }

    async submit(name) {
        const response = await fetch(
            `https://your-site.com/api/resource/${this.doctype}/${name}/submit`,
            {
                method: 'POST',
                headers: this.headers
            }
        );
        return APIResponseHandler.handle(response);
    }

    async cancel(name) {
        const response = await fetch(
            `https://your-site.com/api/resource/${this.doctype}/${name}/cancel`,
            {
                method: 'POST',
                headers: this.headers
            }
        );
        return APIResponseHandler.handle(response);
    }

    async delete(name) {
        const response = await fetch(
            `https://your-site.com/api/resource/${this.doctype}/${name}`,
            {
                method: 'DELETE',
                headers: this.headers
            }
        );
        return APIResponseHandler.handle(response);
    }

    async update(name, data) {
        const response = await fetch(
            `https://your-site.com/api/resource/${this.doctype}/${name}`,
            {
                method: 'PUT',
                headers: this.headers,
                body: JSON.stringify(data)
            }
        );
        return APIResponseHandler.handle(response);
    }
}

// ตัวอย่างการใช้งาน
const salesOrder = new DocTypeOperations('Sales Order');
await salesOrder.submit('SO-0001');
```

## 8. Next.js Integration

การใช้งานร่วมกับ Next.js

### 8.1 API Service Setup

```typescript
// services/api.ts
export class FrappeAPI {
  private baseUrl: string;
  private token: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_FRAPPE_URL || '';
    this.token = `token ${process.env.NEXT_PUBLIC_API_KEY}:${process.env.NEXT_PUBLIC_API_SECRET}`;
  }

  private async fetchAPI(endpoint: string, options: RequestInit = {}) {
    const headers = {
      'Authorization': this.token,
      'Content-Type': 'application/json',
      ...options.headers,
    };

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers,
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // ตัวอย่างเมธอดสำหรับดึงข้อมูล
  async getTodos(filters?: object) {
    return this.fetchAPI('/api/resource/Todo', {
      method: 'GET',
      body: filters ? JSON.stringify(filters) : undefined,
    });
  }

  // ตัวอย่างเมธอดสำหรับสร้างข้อมูล
  async createTodo(data: any) {
    return this.fetchAPI('/api/resource/Todo', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

export const frappeAPI = new FrappeAPI();
```

### 8.2 Custom Hooks

```typescript
// hooks/useFrappeQuery.ts
import { useState, useEffect } from 'react';

export function useFrappeQuery<T>(endpoint: string, options?: RequestInit) {
    const [data, setData] = useState<T | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const response = await fetch(endpoint, {
                    ...options,
                    headers: {
                        'Authorization': 'token api_key:api_secret',
                        ...options?.headers
                    }
                });
                
                if (!response.ok) {
                    throw new Error('API Error');
                }
                
                const result = await response.json();
                setData(result);
                setError(null);
            } catch (err) {
                setError(err instanceof Error ? err : new Error('An error occurred'));
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [endpoint]);

    return { data, loading, error };
}
```

### 8.3 Document Operations Hook

```typescript
// hooks/useDocumentOperations.ts
import { useState } from 'react';
import { DocTypeOperations } from '../utils/DocTypeOperations';

export function useDocumentOperations(doctype: string) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<Error | null>(null);
    const operations = new DocTypeOperations(doctype);

    const submitDoc = async (name: string) => {
        try {
            setLoading(true);
            await operations.submit(name);
            // Handle success
        } catch (err) {
            setError(err instanceof Error ? err : new Error('Failed to submit document'));
        } finally {
            setLoading(false);
        }
    };

    const cancelDoc = async (name: string) => {
        try {
            setLoading(true);
            await operations.cancel(name);
            // Handle success
        } catch (err) {
            setError(err instanceof Error ? err : new Error('Failed to cancel document'));
        } finally {
            setLoading(false);
        }
    };

    return {
        submitDoc,
        cancelDoc,
        loading,
        error
    };
}
```

### 8.4 Example Component

```typescript
// components/SalesOrder.tsx
import { useDocumentOperations } from '../hooks/useDocumentOperations';
import { useFrappeQuery } from '../hooks/useFrappeQuery';

export function SalesOrder({ name }: { name: string }) {
    const { submitDoc, cancelDoc, loading, error } = useDocumentOperations('Sales Order');
    const { data, loading: dataLoading } = useFrappeQuery(`/api/resource/Sales Order/${name}`);

    if (dataLoading) return <div>Loading...</div>;
    if (error) return <div>Error: {error.message}</div>;

    return (
        <div>
            <h2>Sales Order: {name}</h2>
            <div>
                <button 
                    onClick={() => submitDoc(name)}
                    disabled={loading}
                >
                    Submit
                </button>
                <button 
                    onClick={() => cancelDoc(name)}
                    disabled={loading}
                >
                    Cancel
                </button>
            </div>
        </div>
    );
}
```

### 8.5 Environment Variables Setup
```env
# .env.local
NEXT_PUBLIC_FRAPPE_URL=https://your-site.com
NEXT_PUBLIC_API_KEY=your_api_key
NEXT_PUBLIC_API_SECRET=your_api_secret
```

## 9. Frappe Utility Functions

Frappe Framework มี utility functions ที่ช่วยให้การพัฒนาทำได้ง่ายขึ้น

### 9.1 การทำงานกับวันที่และเวลา

**Python**
```python
import frappe
from frappe.utils import now, today, add_days, add_months, getdate, get_datetime

# รับวันที่-เวลาปัจจุบัน 
current_datetime = now()  # เช่น "2023-01-01 12:00:00"

# รับวันที่ปัจจุบัน 
current_date = today()  # เช่น "2023-01-01"

# เพิ่ม/ลด วัน
tomorrow = add_days(today(), 1)
yesterday = add_days(today(), -1)

# เพิ่ม/ลด เดือน
next_month = add_months(today(), 1)

# แปลงข้อความเป็นวันที่
date_obj = getdate("2023-01-01")

# แปลงข้อความเป็นวันที่-เวลา
datetime_obj = get_datetime("2023-01-01 12:00:00")
```

### 9.2 การแปลงข้อมูล (Data Conversion)

**Python**
```python
from frappe.utils import cint, flt, cstr, safe_encode

# แปลงค่าเป็น integer (คืนค่า 0 ถ้าแปลงไม่ได้)
integer_value = cint("123")  # ได้ 123

# แปลงค่าเป็น float (คืนค่า 0.0 ถ้าแปลงไม่ได้)
float_value = flt("123.45")  # ได้ 123.45

# แปลงค่าเป็น string
string_value = cstr(123)  # ได้ "123"

# encode ข้อความเป็น UTF-8 อย่างปลอดภัย
encoded = safe_encode("ข้อความภาษาไทย")
```

### 9.3 การจัดรูปแบบข้อมูล (Formatting)

**Python**
```python
from frappe.utils import fmt_money, format_date, format_time, format_datetime

# จัดรูปแบบจำนวนเงิน
formatted_money = fmt_money(1000, precision=2, currency="THB")  # ได้ "THB 1,000.00"

# จัดรูปแบบวันที่
formatted_date = format_date("2023-01-01")  # ได้ "01-01-2023" (ขึ้นอยู่กับการตั้งค่าระบบ)

# จัดรูปแบบเวลา
formatted_time = format_time("14:30:00")  # ได้ "2:30 PM" (ขึ้นอยู่กับการตั้งค่าระบบ)

# จัดรูปแบบวันที่-เวลา
formatted_datetime = format_datetime("2023-01-01 14:30:00")
```

### 9.4 การทำงานกับฐานข้อมูล

**Python**
```python
import frappe

# รับข้อมูลหลายรายการ
users = frappe.db.get_list(
    "User",
    fields=["name", "email", "user_type"],
    filters={"enabled": 1},
    order_by="creation desc",
    limit=10
)

# รับค่าฟิลด์เดียว
email = frappe.db.get_value("User", "administrator", "email")

# รับค่าหลายฟิลด์จากเอกสารเดียว
user_info = frappe.db.get_value(
    "User", 
    "administrator", 
    ["email", "first_name", "last_name"], 
    as_dict=True
)

# รับข้อมูลแบบ SQL query ตรงๆ
results = frappe.db.sql("""
    SELECT name, email FROM `tabUser`
    WHERE user_type = 'System User'
    ORDER BY creation DESC
    LIMIT 10
""", as_dict=True)
```

### 9.5 การทำงานกับ Transaction

**Python**
```python
import frappe

# เริ่ม transaction
frappe.db.begin()

try:
    # ดำเนินการต่างๆ กับฐานข้อมูล
    frappe.get_doc({
        "doctype": "Todo",
        "description": "New task"
    }).insert()
    
    # อัปเดตข้อมูล
    frappe.db.set_value("User", "administrator", "enabled", 1)
    
    # Commit การเปลี่ยนแปลง
    frappe.db.commit()
except Exception as e:
    # Rollback กรณีเกิดข้อผิดพลาด
    frappe.db.rollback()
    frappe.log_error(f"Error: {str(e)}")
```

## 10. Frappe Hooks

Frappe Framework มี hook system ที่ช่วยให้นักพัฒนาสามารถเพิ่มฟังก์ชันการทำงานได้โดยไม่ต้องแก้ไขโค้ดหลัก

### 10.1 การกำหนด Hooks ใน hooks.py

ทุก Frappe app จะมีไฟล์ `hooks.py` ที่ใช้กำหนด hook ต่างๆ

```python
# ตัวอย่าง hooks.py
app_name = "myapp"
app_title = "My App"
app_publisher = "My Company"
app_description = "My Application"
app_email = "info@example.com"
app_license = "MIT"

# Document Events
doc_events = {
    "User": {
        "after_insert": "myapp.events.user_after_insert",
        "on_update": "myapp.events.user_on_update",
        "on_submit": "myapp.events.user_on_submit"
    }
}

# Scheduled Tasks
scheduler_events = {
    "daily": [
        "myapp.tasks.daily_tasks"
    ],
    "hourly": [
        "myapp.tasks.hourly_tasks"
    ],
    "weekly": [
        "myapp.tasks.weekly_tasks"
    ]
}

# Website Route Rules
website_route_rules = [
    {"from_route": "/blog", "to_route": "Blog Post"}
]
```

### 10.2 Document Events

Document Events ช่วยให้สามารถกำหนดฟังก์ชันที่จะทำงานเมื่อมีการดำเนินการกับเอกสาร

```python
# ไฟล์ hooks.py
doc_events = {
    "Doctype Name": {
        "before_insert": "module.function",
        "after_insert": "module.function",
        "before_validate": "module.function",
        "validate": "module.function",
        "on_update": "module.function",
        "before_submit": "module.function",
        "on_submit": "module.function",
        "before_cancel": "module.function",
        "on_cancel": "module.function",
        "on_trash": "module.function",
        "after_delete": "module.function"
    }
}

# ตัวอย่างการใช้งาน
# myapp/events.py
def user_after_insert(doc, method):
    # doc คือเอกสารที่ถูกสร้าง
    print(f"User {doc.name} has been created!")
```

### 10.3 Scheduler Events

Scheduler Events ช่วยให้สามารถกำหนดงานที่จะทำตามรอบเวลาที่กำหนด

```python
# ไฟล์ hooks.py
scheduler_events = {
    "daily": [
        "myapp.tasks.daily"
    ],
    "hourly": [
        "myapp.tasks.hourly"
    ],
    "weekly": [
        "myapp.tasks.weekly"
    ],
    "monthly": [
        "myapp.tasks.monthly"
    ],
    "cron": {
        "*/15 * * * *": [
            "myapp.tasks.every_fifteen_minutes"
        ]
    }
}

# ตัวอย่างการใช้งาน
# myapp/tasks.py
def daily():
    print("This runs daily")
    
    # สร้างรายงานประจำวัน
    frappe.get_doc({
        "doctype": "Daily Report",
        "date": frappe.utils.today(),
        "status": "Generated"
    }).insert()
```

### 10.4 API Endpoints

การกำหนด API Endpoints เพื่อสร้าง API ที่กำหนดเอง

```python
# ไฟล์ที่เก็บ API endpoints (เช่น myapp/api.py)
import frappe
from frappe import _

@frappe.whitelist()
def get_user_info():
    """รับข้อมูลผู้ใช้ปัจจุบัน"""
    user = frappe.session.user
    user_doc = frappe.get_doc("User", user)
    
    return {
        "username": user,
        "email": user_doc.email,
        "full_name": user_doc.full_name,
        "roles": [r.role for r in user_doc.roles]
    }

@frappe.whitelist()
def create_task(description, due_date=None):
    """สร้าง Todo ใหม่"""
    if not description:
        frappe.throw(_("Description is required"))
    
    todo = frappe.get_doc({
        "doctype": "Todo",
        "description": description,
        "priority": "Medium"
    })
    
    if due_date:
        todo.date = due_date
    
    todo.insert()
    return todo
```

การเรียกใช้ API ที่สร้างขึ้น:

**Python**
```python
import requests

def call_custom_api():
    session = requests.Session()
    
    # Login
    login_url = "https://your-site.com/api/method/login"
    login_data = {"usr": "username", "pwd": "password"}
    session.post(login_url, json=login_data)
    
    # เรียกใช้ API ที่สร้างขึ้น
    response = session.get(
        "https://your-site.com/api/method/myapp.api.get_user_info"
    )
    
    # สร้าง task ใหม่
    task_response = session.post(
        "https://your-site.com/api/method/myapp.api.create_task",
        json={
            "description": "New Task via API",
            "due_date": "2023-12-31"
        }
    )
    
    return {
        "user_info": response.json(),
        "new_task": task_response.json()
    }
```

**JavaScript**
```javascript
async function callCustomApi() {
    // Login
    await fetch('https://your-site.com/api/method/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            usr: 'username',
            pwd: 'password'
        }),
        credentials: 'include'
    });
    
    // เรียกใช้ API ที่สร้างขึ้น
    const userInfoResponse = await fetch(
        'https://your-site.com/api/method/myapp.api.get_user_info',
        { credentials: 'include' }
    );
    
    // สร้าง task ใหม่
    const taskResponse = await fetch(
        'https://your-site.com/api/method/myapp.api.create_task',
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                description: 'New Task via API',
                due_date: '2023-12-31'
            }),
            credentials: 'include'
        }
    );
    
    return {
        userInfo: await userInfoResponse.json(),
        newTask: await taskResponse.json()
    };
}
```

## เพิ่มเติม
- [Frappe REST API Documentation](https://frappeframework.com/docs/user/en/api/rest)
- [Authentication](https://frappeframework.com/docs/user/en/api/authentication)
- [Common Issues & Solutions](https://frappeframework.com/docs/user/en/api/common-issues)
- [Frappe Hooks Documentation](https://frappeframework.com/docs/user/en/python-api/hooks)
- [Frappe Utilities Documentation](https://frappeframework.com/docs/user/en/api/utils)

---
*เอกสารนี้เป็นคู่มือเบื้องต้น สำหรับข้อมูลเพิ่มเติมกรุณาอ้างอิงจากเอกสารอย่างเป็นทางการของ Frappe Framework*
