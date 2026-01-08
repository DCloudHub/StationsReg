
## **5. README File (`README.md`)**

```markdown
# 📍 Station Location Registration System

A Streamlit web application to register clients, share personalized WhatsApp links, and automatically record their GPS locations at stations.

## ✨ Features

### 🔗 WhatsApp Integration
- Generate personalized WhatsApp messages with unique links
- QR code generation for easy scanning
- One-click WhatsApp sharing

### 👤 Client Management
- Unique client ID generation (Format: STN-YYMMDD-001)
- Client details storage (name, phone, email)
- Station assignment

### 📍 Location Recording
- Automatic GPS location capture
- Manual entry option for testing
- Accuracy reporting
- Timestamp recording

### 📊 Data Analytics
- Real-time dashboard
- Filter by station/status/date
- Export to CSV/Excel
- Visual charts and reports

## 🚀 Quick Start

### Local Development
```bash
git clone <your-repo>
cd station-tracker
pip install -r requirements.txt
streamlit run app.py
