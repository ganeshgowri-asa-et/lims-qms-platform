# LIMS QMS Platform - Quick Setup Guide

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Dependencies

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Setup Database

**Option A: Using SQLite (Quick Test)**
```bash
# In .env file, use:
DATABASE_URL=sqlite:///./lims_qms.db
```

**Option B: Using PostgreSQL (Recommended for Production)**
```bash
# Install PostgreSQL, then create database
createdb lims_qms_db

# In .env file, use:
DATABASE_URL=postgresql://user:password@localhost:5432/lims_qms_db
```

### Step 3: Configure Environment

Create `.env` file:

```env
DATABASE_URL=sqlite:///./lims_qms.db
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=dev-secret-key-change-in-production
APP_NAME=LIMS QMS Platform
ORGANIZATION_NAME=My Organization
DEBUG=True

# Optional - for AI features
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
```

### Step 4: Start Services

**Terminal 1 - Backend API:**
```bash
python main.py
```

**Terminal 2 - Frontend UI:**
```bash
cd frontend
streamlit run app.py
```

### Step 5: Access Application

- **Frontend UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

## 📝 First Time Usage

### 1. Register Your First NC

1. Go to http://localhost:8501
2. Click "📝 Register NC"
3. Fill in the form:
   - **Title**: "Test calibration failed for equipment XYZ"
   - **Description**: "Equipment XYZ calibration results exceeded tolerance limits"
   - **Source**: Testing
   - **Severity**: Major
   - **Detected By**: Your Name
   - **Registered By**: Your Name
4. Click "🚀 Register NC"
5. Note the NC number generated (e.g., NC-2024-001)

### 2. Perform Root Cause Analysis

1. Click "🎯 Root Cause Analysis" from menu
2. Select your NC from the dropdown
3. Click "🚀 Get AI Suggestions" (optional, requires API key)
4. Choose method:
   - **5-Why**: For simple, linear problems
   - **Fishbone**: For complex, multi-factor problems
5. Fill in the analysis
6. Click "💾 Save Analysis"

### 3. Create CAPA Action

1. Click "✅ CAPA Management" from menu
2. Go to "➕ Create CAPA" tab
3. Select your NC
4. Fill in:
   - **Type**: Corrective (fix the problem)
   - **Title**: "Recalibrate equipment and update procedure"
   - **Description**: Detailed action plan
   - **Assigned To**: Technician name
   - **Due Date**: 30 days from now
5. Click "🚀 Create CAPA Action"

### 4. View Dashboard

1. Click "📊 Dashboard" from menu
2. See real-time metrics:
   - Total NCs and CAPAs
   - Status distribution
   - Overdue actions
   - Trends and charts

## 🔧 Configuration Options

### Database Options

**SQLite** (Development/Testing)
```env
DATABASE_URL=sqlite:///./lims_qms.db
```

**PostgreSQL** (Production)
```env
DATABASE_URL=postgresql://username:password@host:port/database
```

**PostgreSQL with Docker**
```bash
docker run -d \
  --name lims-postgres \
  -e POSTGRES_USER=limsuser \
  -e POSTGRES_PASSWORD=limspass \
  -e POSTGRES_DB=lims_qms_db \
  -p 5432:5432 \
  postgres:14

# Then use:
DATABASE_URL=postgresql://limsuser:limspass@localhost:5432/lims_qms_db
```

### AI Configuration

**Anthropic Claude** (Recommended)
```env
ANTHROPIC_API_KEY=sk-ant-...
```
- Get key from: https://console.anthropic.com/
- Provides high-quality root cause suggestions

**OpenAI GPT-4**
```env
OPENAI_API_KEY=sk-...
```
- Get key from: https://platform.openai.com/
- Alternative AI provider

**No AI** (Rule-based fallback)
- Leave both keys empty
- System will use rule-based suggestions
- Still functional, but less intelligent

## 🐳 Docker Deployment (Optional)

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000 8501

CMD ["sh", "-c", "python main.py & cd frontend && streamlit run app.py"]
```

### Build and Run

```bash
docker build -t lims-qms-platform .
docker run -p 8000:8000 -p 8501:8501 lims-qms-platform
```

## 🔍 Troubleshooting

### Problem: "Module not found" errors
**Solution**: Ensure virtual environment is activated and dependencies installed
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Problem: "Database connection failed"
**Solution**: Check DATABASE_URL in .env file
```bash
# For SQLite - use relative path
DATABASE_URL=sqlite:///./lims_qms.db

# For PostgreSQL - verify credentials
psql -U username -d lims_qms_db -h localhost
```

### Problem: "Port already in use"
**Solution**: Change ports in .env
```env
API_PORT=8001  # Instead of 8000
```

Then run Streamlit on different port:
```bash
streamlit run app.py --server.port 8502
```

### Problem: AI suggestions not working
**Solution**:
1. Check API keys are set in .env
2. Verify API key validity
3. System will fall back to rule-based suggestions if AI fails

### Problem: Frontend can't connect to backend
**Solution**:
1. Ensure backend is running (`python main.py`)
2. Check API_HOST and API_PORT in config
3. Verify http://localhost:8000/health is accessible

## 📊 Sample Data

To test the system with sample data:

```python
# Run this script to create sample data
python scripts/create_sample_data.py  # (Create this script if needed)
```

Or manually create via UI:
1. Register 3-5 NCs with different severities
2. Perform RCA on 2-3 of them
3. Create CAPA actions
4. Update some CAPA statuses
5. View dashboard for populated charts

## 🎓 Training Resources

### Video Tutorials
- [Coming Soon] NC Registration Walkthrough
- [Coming Soon] Root Cause Analysis Guide
- [Coming Soon] CAPA Management Best Practices

### Documentation
- `README.md` - Full system documentation
- `API_REFERENCE.md` - API endpoint details
- In-app help - Click "?" icons in UI

## 📞 Getting Help

1. **Documentation**: Read README.md
2. **API Docs**: http://localhost:8000/docs
3. **Issues**: Create GitHub issue
4. **Email**: [your-email@example.com]

## ✅ Verification Checklist

- [ ] Dependencies installed
- [ ] Database configured and accessible
- [ ] .env file created with correct values
- [ ] Backend API starts successfully
- [ ] Frontend UI accessible
- [ ] Can register an NC
- [ ] Can perform RCA
- [ ] Can create CAPA
- [ ] Dashboard shows data
- [ ] AI suggestions work (if configured)

---

**Happy Quality Managing! 🎉**
