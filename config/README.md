# InvestByYourself - Unified Environment Configuration Management

**Tech-026: Unified Environment Configuration Management**

This directory contains the unified environment configuration system for InvestByYourself, designed to provide centralized, secure, and maintainable configuration management across all services and environments.

## 🎯 Overview

The unified configuration system addresses the following challenges:
- **Scattered Configuration**: Multiple `.env` files across different services
- **Security Issues**: Hardcoded secrets and project IDs in templates
- **Inconsistency**: Different naming conventions and structures
- **Maintenance**: Difficult to manage and update configurations
- **Validation**: No automated validation of configuration files

## 📁 Directory Structure

```
config/
├── environments/           # Environment-specific configurations
│   ├── base.env.template          # Base configuration for all environments
│   ├── development.env.template   # Development environment overrides
│   ├── staging.env.template       # Staging environment overrides
│   └── production.env.template    # Production environment overrides
├── services/              # Service-specific configurations
│   ├── backend.env.template       # Backend service configuration
│   ├── frontend.env.template      # Frontend service configuration
│   └── etl.env.template          # ETL service configuration
├── scripts/               # Configuration management scripts
│   ├── generate_env.py           # Generate environment files from templates
│   ├── validate_env.py           # Validate configuration files
│   └── migrate_env.py            # Migrate from old configuration system
├── backups/               # Backup of old configuration files
└── README.md             # This documentation
```

## 🚀 Quick Start

### 1. Generate Configuration Files

Generate configuration for a specific environment and service:

```bash
# Generate development backend configuration
python config/scripts/generate_env.py --environment development --service backend

# Generate production frontend configuration
python config/scripts/generate_env.py --environment production --service frontend

# Generate all services for development environment
python config/scripts/generate_env.py --environment development --all-services
```

### 2. Validate Configuration Files

Validate your configuration files for security and consistency:

```bash
# Validate all configurations
python config/scripts/validate_env.py --all

# Validate specific environment
python config/scripts/validate_env.py --environment development

# Validate specific file
python config/scripts/validate_env.py --file .env.development.backend
```

### 3. Migrate from Old System

If you're migrating from the old configuration system:

```bash
# Backup existing configurations
python config/scripts/migrate_env.py --backup

# Migrate to new system
python config/scripts/migrate_env.py --migrate --environment development

# Clean up old files (after validation)
python config/scripts/migrate_env.py --cleanup
```

## 📋 Configuration Hierarchy

The configuration system uses a hierarchical approach where later configurations override earlier ones:

1. **Base Configuration** (`base.env.template`)
   - Common variables across all environments
   - Default values and placeholders
   - Documentation and examples

2. **Environment Overrides** (`{environment}.env.template`)
   - Environment-specific values
   - Security settings
   - Performance tuning

3. **Service Overrides** (`{service}.env.template`)
   - Service-specific configurations
   - Port numbers and timeouts
   - Feature flags

## 🔒 Security Features

### No Hardcoded Secrets
- All sensitive data uses environment variables
- Templates contain placeholders, not actual values
- Validation prevents hardcoded secrets

### Secure Defaults
- Strong password requirements
- Secure connection settings
- Proper CORS configuration

### Validation
- Automated security checks
- Placeholder detection
- Weak password detection
- Insecure default detection

## 🛠️ Configuration Categories

### Environment & Application
- `ENVIRONMENT`: Current environment (development, staging, production)
- `DEBUG`: Debug mode flag
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Database Configuration
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DATABASE`
- `POSTGRES_USER`, `POSTGRES_PASSWORD`
- Connection pool settings

### Cache & Storage
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`
- `MINIO_HOST`, `MINIO_PORT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`

### External APIs
- `FRED_API_KEY`: Federal Reserve Economic Data API
- `ALPHA_VANTAGE_API_KEY`: Alpha Vantage API
- `FMP_API_KEY`: Financial Modeling Prep API

### Supabase Configuration
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_ANON_KEY`: Public anonymous key
- `SUPABASE_SERVICE_ROLE_KEY`: Service role key

### Security Configuration
- `ENCRYPTION_KEY`: Data encryption key
- `JWT_SECRET`: JWT signing secret
- `CORS_ORIGINS`: Allowed CORS origins

## 📝 Usage Examples

### Development Environment

```bash
# Generate development configuration for all services
python config/scripts/generate_env.py --environment development --all-services

# This creates:
# - .env.development.backend
# - .env.development.frontend
# - .env.development.etl
```

### Production Environment

```bash
# Generate production backend configuration
python config/scripts/generate_env.py --environment production --service backend

# Validate production configuration
python config/scripts/validate_env.py --environment production
```

### Custom Output Location

```bash
# Generate to custom location
python config/scripts/generate_env.py --environment development --service backend --output /path/to/custom.env
```

## 🔍 Validation Features

The validation system checks for:

### Security Issues
- Hardcoded secrets in templates
- Weak passwords
- Insecure default values
- Placeholder values in production

### Consistency Issues
- Missing required variables
- Inconsistent values across environments
- Invalid variable formats

### Format Issues
- Invalid numeric values
- Invalid boolean values
- Invalid URL formats
- Missing quotes around values with spaces

## 🚨 Common Issues and Solutions

### Issue: "Placeholder value detected"
**Solution**: Replace placeholder values with actual values:
```bash
# Instead of:
SUPABASE_URL=https://your-project-id.supabase.co

# Use:
SUPABASE_URL=https://ztxlcatckspsdtkepmwy.supabase.co
```

### Issue: "Weak password detected"
**Solution**: Use strong passwords with 16+ characters, mixed case, numbers, and symbols:
```bash
# Instead of:
POSTGRES_PASSWORD=password

# Use:
POSTGRES_PASSWORD=Str0ng!P@ssw0rd2025
```

### Issue: "Required variable missing"
**Solution**: Add the missing variable to your configuration:
```bash
# Add missing variable:
FRED_API_KEY=your_actual_fred_api_key
```

## 🔄 Migration from Old System

If you're migrating from the old configuration system:

### 1. Backup Existing Files
```bash
python config/scripts/migrate_env.py --backup
```

### 2. Review Backup
Check `config/backups/` for your backed up files.

### 3. Migrate Configurations
```bash
python config/scripts/migrate_env.py --migrate --environment development
```

### 4. Generate New Files
```bash
python config/scripts/generate_env.py --environment development --all-services
```

### 5. Validate New System
```bash
python config/scripts/validate_env.py --all
```

### 6. Update Deployment Scripts
Update your deployment scripts to use the new configuration files.

### 7. Clean Up Old Files
```bash
python config/scripts/migrate_env.py --cleanup
```

## 📚 Script Documentation

### `generate_env.py`
Generates environment configuration files from templates.

**Options:**
- `--environment`: Target environment (development, staging, production)
- `--service`: Target service (backend, frontend, etl)
- `--all-services`: Generate for all services
- `--output`: Custom output file path

### `validate_env.py`
Validates environment configuration files.

**Options:**
- `--file`: Validate specific file
- `--environment`: Validate all files for environment
- `--all`: Validate all configurations
- `--output-format`: Output format (text, json)

### `migrate_env.py`
Migrates from old configuration system.

**Options:**
- `--backup`: Backup existing configurations
- `--migrate`: Migrate to new system
- `--environment`: Target environment for migration
- `--cleanup`: Clean up old files
- `--validate`: Validate migration
- `--guide`: Show migration guide

## 🎯 Best Practices

### 1. Use Environment Variables
Always use environment variables for sensitive data:
```bash
# Good
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

# Bad
POSTGRES_PASSWORD=hardcoded_password
```

### 2. Validate Before Deployment
Always validate configurations before deployment:
```bash
python config/scripts/validate_env.py --environment production
```

### 3. Use Strong Passwords
Use strong, unique passwords for all services:
```bash
# Good: 16+ characters, mixed case, numbers, symbols
POSTGRES_PASSWORD=Str0ng!P@ssw0rd2025

# Bad: Weak password
POSTGRES_PASSWORD=password
```

### 4. Keep Templates Updated
Update templates when adding new configuration options:
```bash
# Add new variable to appropriate template
echo "NEW_FEATURE_ENABLED=true" >> config/environments/base.env.template
```

### 5. Document Changes
Document configuration changes in commit messages and documentation.

## 🔧 Troubleshooting

### Script Not Found
```bash
# Make sure you're in the project root
cd /path/to/InvestByYourself

# Run scripts with full path
python config/scripts/generate_env.py --help
```

### Permission Denied
```bash
# Make scripts executable (Linux/Mac)
chmod +x config/scripts/*.py
```

### Import Errors
```bash
# Install required dependencies
pip install -r requirements.txt
```

## 📞 Support

For issues with the configuration system:

1. Check the validation output for specific errors
2. Review the backup files in `config/backups/`
3. Consult this documentation
4. Check the migration guide: `python config/scripts/migrate_env.py --guide`

## 🔄 Version History

- **v1.0.0**: Initial unified configuration system
- **Tech-026**: Complete rewrite with security improvements and automation

---

**Note**: This configuration system is part of Tech-026: Unified Environment Configuration Management. For more information, see the [MASTER_TODO.md](../MASTER_TODO.md) file.
