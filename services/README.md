# 🏗️ Microservices Architecture - InvestByYourself

*This directory contains all microservices for the InvestByYourself platform*

## 📁 **Service Structure**

### **Business Services**
- **`financial-analysis-service/`** - Financial ratios, charts, metrics, and risk assessment
- **`company-analysis-service/`** - Company profiles, screening, sector analysis, and research
- **`portfolio-service/`** - Portfolio management, risk assessment, and performance tracking

### **Infrastructure Services**
- **`etl-service/`** - Data collection, transformation, and loading pipeline
- **`data-service/`** - Database, cache, and storage management
- **`api-gateway/`** - Request routing, authentication, and API management

## 🚀 **Development Guidelines**

### **Service Independence**
- Each service should be independently deployable
- Services communicate via well-defined APIs
- No direct database access between services

### **Technology Stack**
- **Language**: Python 3.9+
- **Framework**: FastAPI for REST APIs
- **Database**: PostgreSQL (primary), Redis (cache)
- **Containerization**: Docker

### **Communication Patterns**
- **Synchronous**: REST APIs for real-time requests
- **Asynchronous**: Message queues for background tasks
- **Events**: Event-driven architecture for data consistency

## 📋 **Current Status**

- **Phase**: Foundation & Structure (Week 1)
- **Next**: Service extraction and code migration
- **Timeline**: 4-6 weeks for complete migration

## 🔗 **Related Documentation**

- [Microservices Architecture Plan](../docs/microservices_architecture_plan.md)
- [Master TODO](../MASTER_TODO.md)
- [Development Plan](../docs/investbyyourself_plan.md)

---

*Each service directory should contain its own README, requirements.txt, and Dockerfile*
