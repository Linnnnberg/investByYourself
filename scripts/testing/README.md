# ETL Pipeline Testing Scripts

This directory contains comprehensive testing scripts for the investByYourself ETL pipeline, specifically designed to validate functionality after security fixes.

## 🎯 **Purpose**

These scripts were created to verify that the ETL pipeline continues to work correctly after removing all hardcoded credentials and implementing environment variable-based configuration.

## 📁 **Scripts Overview**

### 1. **test_env_loading.py**
- **Purpose**: Tests environment variable loading from configuration files
- **What it tests**:
  - Loading credentials from `.env` files
  - Database, Redis, MinIO, and API key configuration
  - Environment variable accessibility
- **Usage**: `python test_env_loading.py`

### 2. **test_config_classes.py**
- **Purpose**: Tests configuration classes and their environment loading methods
- **What it tests**:
  - `DatabaseConfig` class functionality
  - `CacheConfig` class functionality
  - `DatabaseLoader.DatabaseConfig` class functionality
  - Environment variable integration
- **Usage**: `python test_config_classes.py`

### 3. **test_etl_core.py**
- **Purpose**: Tests core ETL components that are known to work
- **What it tests**:
  - Data collection framework imports
  - Data processing engine imports
  - Data loading framework imports
  - Configuration loading with environment variables
  - Data transformation functionality
  - File operations (mock)
- **Usage**: `python test_etl_core.py`

### 4. **test_etl_functionality.py**
- **Purpose**: Comprehensive ETL functionality testing
- **What it tests**:
  - All major ETL components
  - Configuration loading
  - Mock cache and database operations
  - Component instantiation
- **Usage**: `python test_etl_functionality.py`

### 5. **test_etl_workflow.py**
- **Purpose**: Tests complete ETL workflow end-to-end
- **What it tests**:
  - Complete data flow: Collect → Transform → Load
  - File-based data loading (JSON, CSV)
  - Data transformation with calculated fields
  - Data integrity verification
  - Security validation (no hardcoded credentials)
- **Usage**: `python test_etl_workflow.py`

## 🔧 **Setup Requirements**

### Environment File
- **File**: `test.env`
- **Purpose**: Contains test credentials and configuration
- **Note**: Uses dummy credentials for testing only

### Dependencies
```bash
pip install python-dotenv
```

### Python Path
All scripts automatically add the `src` directory to the Python path for imports.

## 🚀 **Running Tests**

### Individual Tests
```bash
cd scripts/testing
python test_env_loading.py
python test_config_classes.py
python test_etl_core.py
python test_etl_functionality.py
python test_etl_workflow.py
```

### Complete Test Suite
```bash
cd scripts/testing
python test_etl_workflow.py  # Most comprehensive test
```

## 📊 **Expected Results**

### ✅ **All Tests Should Pass**
- Environment variable loading: ✅
- Configuration classes: ✅
- Core ETL components: ✅
- ETL functionality: ✅
- Complete workflow: ✅
- Security validation: ✅

### 🔒 **Security Validation**
- No hardcoded passwords found
- All credentials loaded from environment variables
- Configuration classes properly secured

## 🎉 **Success Indicators**

When all tests pass, you'll see:
```
🎉 SUCCESS: ETL pipeline fully functional and secure!
🔒 Security fixes working correctly
✅ Ready for production use with proper environment configuration
```

## 🔄 **Reusability**

These scripts can be reused for:
- **Development**: Testing new features
- **CI/CD**: Automated testing in pipelines
- **Debugging**: Isolating component issues
- **Security Audits**: Validating credential management
- **Onboarding**: New developer setup validation

## 📝 **Customization**

### Adding New Tests
1. Create new test script in this directory
2. Follow the naming convention: `test_*.py`
3. Include proper error handling and reporting
4. Add to this README

### Modifying Test Data
- Update sample data in `test_etl_workflow.py`
- Modify test credentials in `test.env`
- Adjust test parameters as needed

## 🚨 **Troubleshooting**

### Common Issues
1. **Import Errors**: Ensure `src` directory is accessible
2. **Environment Issues**: Check `test.env` file exists and is readable
3. **Path Issues**: Run from `scripts/testing` directory

### Debug Mode
Most scripts include detailed logging and error reporting for troubleshooting.

---

**Created**: August 21, 2025
**Purpose**: Post-security-fix validation
**Status**: All tests passing ✅
**Maintainer**: investByYourself Development Team
