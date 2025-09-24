# Team Environment Setup Guide
## InvestByYourself Financial Platform

**Purpose**: Secure environment setup for team members without sharing credentials
**Security Level**: High - No credentials in version control
**Last Updated**: 2025-01-27

---

## 🎯 **Overview**

This guide helps team members set up their local development environment securely without exposing credentials or sensitive information. Each developer maintains their own `.env` file with local database credentials.

---

## 🔐 **Security Principles**

### **What We DO:**
- ✅ Keep `env.template` in version control
- ✅ Use `.gitignore` to exclude `.env` files
- ✅ Share configuration structure, not values
- ✅ Use Bitwarden for shared credentials when needed
- ✅ Provide interactive setup scripts

### **What We DON'T:**
- ❌ Commit `.env` files to git
- ❌ Share database passwords in chat/email
- ❌ Use hardcoded credentials in code
- ❌ Store secrets in public repositories

---

## 🚀 **Quick Setup (Recommended)**

### **Step 1: Run the Setup Script**
```bash
cd scripts
python setup_team_environment.py
```

This script will:
- Check your current environment
- Prompt for database credentials interactively
- Create a secure `.env` file
- Validate your connection
- Guide you through next steps

### **Step 2: Verify Setup**
The script will automatically test your database connection and confirm everything is working.

---

## 🔧 **Manual Setup (Alternative)**

If you prefer manual setup:

### **Step 1: Copy Template**
```bash
cp env.template .env
```

### **Step 2: Edit .env File**
Update these key values in your `.env` file:

```env
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=investbyyourself
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_actual_password_here

# Environment
ENVIRONMENT=development
DEBUG=true
```

### **Step 3: Test Connection**
```bash
python scripts/check_and_populate_database.py
```

---

## 🗄️ **Database Setup Requirements**

### **PostgreSQL Installation**
- **Windows**: Download from https://www.postgresql.org/download/windows/
- **macOS**: `brew install postgresql`
- **Linux**: `sudo apt-get install postgresql postgresql-contrib`

### **Database Creation**
```sql
-- Connect as postgres user
CREATE DATABASE investbyyourself;
CREATE USER etl_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE investbyyourself TO etl_user;
```

### **Connection Details**
- **Host**: Usually `localhost` or `127.0.0.1`
- **Port**: Default `5432`
- **User**: Usually `postgres` (superuser) or `etl_user`
- **Password**: What you set during installation

---

## 🔑 **API Keys Management**

### **Optional APIs (Not Required for Basic Setup)**
- **FRED API**: Economic data (free tier available)
- **Alpha Vantage**: Financial data (free tier available)
- **Financial Modeling Prep**: Enhanced financial data (paid)

### **Getting API Keys**
1. **FRED**: https://fred.stlouisfed.org/docs/api/api_key.html
2. **Alpha Vantage**: https://www.alphavantage.co/support/#api-key
3. **FMP**: https://financialmodelingprep.com/developer/docs/

### **Storing API Keys Securely**
- Store in your local `.env` file
- Use Bitwarden for team sharing if needed
- Never commit API keys to version control

---

## 🐳 **Docker Alternative (Optional)**

If you prefer using Docker instead of local installations:

### **Start Services with Docker Compose**
```bash
# Start PostgreSQL, Redis, and MinIO
docker-compose up -d

# Your .env will automatically use Docker service names
POSTGRES_HOST=localhost
REDIS_HOST=localhost
MINIO_HOST=localhost
```

### **Docker Service Credentials**
- **PostgreSQL**: `postgres` / `password`
- **Redis**: No password (default)
- **MinIO**: `minio_admin` / `minio_password`

---

## 🧪 **Testing Your Setup**

### **Step 1: Test Database Connection**
```bash
python scripts/check_and_populate_database.py
```

### **Step 2: Populate Sample Data**
The script will automatically populate your database with sample financial data.

### **Step 3: Test Financial Exploration System**
```bash
# Test basic functionality
python scripts/financial_analysis/data_explorer.py

# Launch interactive dashboard
streamlit run scripts/financial_analysis/financial_dashboard.py
```

---

## 🔍 **Troubleshooting**

### **Common Issues**

#### **1. Database Connection Failed**
```bash
# Check if PostgreSQL is running
# Windows: Services > PostgreSQL
# macOS/Linux: sudo systemctl status postgresql

# Test connection manually
psql -h localhost -U postgres -d investbyyourself
```

#### **2. Permission Denied**
```bash
# Check user permissions
# Make sure your user has access to the database
```

#### **3. Port Already in Use**
```bash
# Check what's using port 5432
# Windows: netstat -an | findstr 5432
# macOS/Linux: lsof -i :5432
```

#### **4. Environment Variables Not Loading**
```bash
# Make sure .env file is in project root
# Check file permissions
# Verify .env file format (no spaces around =)
```

---

## 📋 **Team Collaboration**

### **Sharing Configuration (Not Credentials)**
- Share `env.template` updates in pull requests
- Document new environment variables
- Use Bitwarden for shared service credentials

### **Environment Updates**
When new environment variables are added:
1. Update `env.template`
2. Document changes in this guide
3. Notify team members to update their `.env` files

### **Development vs Production**
- **Development**: Use local `.env` file
- **Production**: Use environment variables or secure secret management
- **CI/CD**: Use GitHub Secrets or similar

---

## 🎯 **Next Steps After Setup**

1. **✅ Environment Configured**: Your `.env` file is ready
2. **📊 Database Populated**: Sample data is loaded
3. **🧪 System Tested**: Financial exploration system is working
4. **🚀 Ready to Develop**: You can now work on the codebase

### **What You Can Do Now:**
- Run financial data queries
- Generate interactive charts
- Explore company profiles
- Test the ETL pipeline
- Contribute to development

---

## 📚 **Additional Resources**

- **Project Documentation**: `docs/` directory
- **Database Schema**: `database/schema.sql`
- **API Documentation**: `docs/api/` directory
- **Testing Guide**: `scripts/testing/README.md`

---

## 🆘 **Getting Help**

### **Team Support**
- Check existing documentation first
- Ask in team chat/meetings
- Create issues for bugs or missing features

### **External Resources**
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Python Environment**: https://docs.python.org/3/tutorial/venv.html
- **Docker**: https://docs.docker.com/get-started/

---

**Remember**: Keep your credentials secure and never share them in public channels or commit them to version control!
