# 🔗 Shared Components - InvestByYourself

*This directory contains shared libraries, utilities, and configurations used across all microservices*

## 📁 **Directory Structure**

### **`common/`**
- **Utilities**: Common helper functions and utilities
- **Models**: Shared data models and DTOs
- **Exceptions**: Common exception classes
- **Constants**: Shared constants and enums
- **Validators**: Common validation logic

### **`database/`**
- **Schemas**: Database schema definitions
- **Migrations**: Database migration scripts
- **Models**: Shared database models
- **Connections**: Database connection utilities

### **`config/`**
- **Settings**: Configuration management
- **Environment**: Environment-specific configs
- **Secrets**: Secure credential handling
- **Feature Flags**: Runtime configuration

## 🚀 **Usage Guidelines**

### **Import Patterns**
```python
# From common utilities
from shared.common.utils import format_currency
from shared.common.models import CompanyProfile

# From database
from shared.database.models import BaseModel
from shared.database.connections import get_db_connection

# From configuration
from shared.config.settings import get_settings
from shared.config.features import is_feature_enabled
```

### **Dependency Management**
- Shared components should have minimal external dependencies
- Use dependency injection for service-specific configurations
- Maintain backward compatibility during updates

### **Versioning Strategy**
- Semantic versioning for shared components
- Backward compatibility for minor versions
- Clear migration guides for breaking changes

## 📋 **Current Status**

- **Phase**: Foundation & Structure (Week 1)
- **Next**: Extract common utilities from existing codebase
- **Timeline**: Week 2-3 for utility extraction

## 🔗 **Related Documentation**

- [Microservices Architecture Plan](../docs/microservices_architecture_plan.md)
- [Master TODO](../MASTER_TODO.md)
- [Development Plan](../docs/investbyyourself_plan.md)

---

*Shared components should be designed for reuse across all services while maintaining clear boundaries*
