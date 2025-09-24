#!/usr/bin/env python3
"""
Development Environment Setup Script
Tech-028: API Implementation - Secure Environment Configuration

This script creates a proper development environment configuration
that follows security best practices and will pass security checks.
"""

import os
import secrets
import string
from pathlib import Path


def generate_secure_key(length: int = 32) -> str:
    """Generate a cryptographically secure random key."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def create_dev_env_file():
    """Create a secure development environment file."""

    # Generate secure development keys
    secret_key = generate_secure_key(32)
    jwt_secret = generate_secure_key(32)

    env_content = f"""# InvestByYourself API Development Environment Configuration
# Tech-028: API Implementation - Development Settings
# Generated on: {os.popen('date').read().strip()}
#
# SECURITY NOTE: This file contains development keys only.
# These keys are NOT suitable for production use.
# For production, use proper secret management.

# Application Configuration
APP_NAME=InvestByYourself API
VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true
API_PORT=8000
API_HOST=0.0.0.0

# Security Configuration (Development Keys)
# WARNING: These are development keys only - NOT for production!
SECRET_KEY={secret_key}
JWT_SECRET_KEY={jwt_secret}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Configuration (Development)
CORS_ORIGINS=http://localhost:3000,http://localhost:8000,http://localhost:3001,http://127.0.0.1:3000
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Configuration (SQLite for Development)
DATABASE_TYPE=sqlite
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=investbyyourself
POSTGRES_USER=postgres
POSTGRES_PASSWORD=dev_password_placeholder
SQLITE_DATABASE=investbyyourself_dev.db

# Redis Configuration (Optional for Development)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# External API Keys (Development Placeholders)
# Replace these with real keys when needed for testing
ALPHA_VANTAGE_API_KEY=dev_alpha_vantage_key_placeholder
FRED_API_KEY=dev_fred_key_placeholder
FMP_API_KEY=dev_fmp_key_placeholder

# Supabase Configuration (Development Placeholders)
# Replace these with real keys when needed for testing
SUPABASE_URL=https://dev-project-placeholder.supabase.co
SUPABASE_ANON_KEY=dev_supabase_anon_key_placeholder
SUPABASE_SERVICE_ROLE_KEY=dev_supabase_service_role_key_placeholder

# Rate Limiting (Disabled for Development)
RATE_LIMIT_ENABLED=false
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=60

# Logging Configuration (Verbose for Development)
LOG_LEVEL=DEBUG
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Monitoring Configuration (Disabled for Development)
SENTRY_DSN=
PROMETHEUS_ENABLED=false
PROMETHEUS_PORT=8001
"""

    # Write the development environment file
    with open(".env.development", "w") as f:
        f.write(env_content)

    print("✅ Created .env.development file with secure development keys")
    return True


def create_env_loader():
    """Create an environment loader that supports multiple environments."""

    loader_content = '''#!/usr/bin/env python3
"""
Environment Loader for Multiple Environments
Tech-028: API Implementation - Secure Environment Management

This module loads the appropriate environment configuration
based on the ENVIRONMENT variable or default to development.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def load_environment():
    """Load environment variables based on the current environment."""

    # Get the current environment
    env = os.getenv('ENVIRONMENT', 'development')

    # Define environment file paths
    env_files = {
        'development': '.env.development',
        'staging': '.env.staging',
        'production': '.env.production',
        'test': '.env.test'
    }

    # Get the appropriate environment file
    env_file = env_files.get(env, '.env.development')
    env_path = Path(env_file)

    # Check if the environment file exists
    if env_path.exists():
        print(f"Loading environment from: {env_file}")
        load_dotenv(env_path)
    else:
        print(f"Environment file {env_file} not found, using system environment variables")
        # Fallback to system environment variables
        load_dotenv()

    # Validate required environment variables
    required_vars = [
        'SECRET_KEY',
        'JWT_SECRET_KEY',
        'ENVIRONMENT'
    ]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    print(f"Environment loaded successfully: {env}")
    return True


if __name__ == "__main__":
    load_environment()
'''

    with open("env_loader.py", "w") as f:
        f.write(loader_content)

    print("✅ Created env_loader.py for environment management")
    return True


def update_gitignore():
    """Update .gitignore to properly handle environment files."""

    gitignore_additions = """
# Environment files - Security
.env
.env.local
.env.development
.env.staging
.env.production
.env.test
*.env
.env.*

# But allow templates
!.env.template
!.env.*.template
"""

    gitignore_path = Path(".gitignore")

    if gitignore_path.exists():
        with open(".gitignore", "r") as f:
            content = f.read()

        if ".env" not in content:
            with open(".gitignore", "a") as f:
                f.write(gitignore_additions)
            print("✅ Updated .gitignore to exclude environment files")
        else:
            print("✅ .gitignore already properly configured")
    else:
        with open(".gitignore", "w") as f:
            f.write(gitignore_additions)
        print("✅ Created .gitignore with environment file exclusions")

    return True


def create_env_template():
    """Create a comprehensive environment template."""

    template_content = """# InvestByYourself API Environment Configuration Template
# Tech-028: API Implementation - Environment Template
#
# Copy this file to .env.development, .env.staging, .env.production, etc.
# and fill in the appropriate values for each environment.
#
# SECURITY WARNING: Never commit actual .env files to version control!

# Application Configuration
APP_NAME=InvestByYourself API
VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true
API_PORT=8000
API_HOST=0.0.0.0

# Security Configuration (REQUIRED)
# Generate secure keys using: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE_TYPE=sqlite
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=investbyyourself
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_postgres_password
SQLITE_DATABASE=investbyyourself_dev.db

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_DB=0

# External API Keys
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
FRED_API_KEY=your_fred_api_key
FMP_API_KEY=your_fmp_api_key

# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Monitoring
SENTRY_DSN=your_sentry_dsn_here
PROMETHEUS_ENABLED=false
PROMETHEUS_PORT=8001
"""

    with open(".env.template", "w") as f:
        f.write(template_content)

    print("✅ Updated .env.template with comprehensive configuration")
    return True


def main():
    """Main setup function."""
    print("🔧 Setting up secure development environment...")
    print("=" * 50)

    try:
        # Create development environment file
        create_dev_env_file()

        # Create environment loader
        create_env_loader()

        # Update gitignore
        update_gitignore()

        # Create/update template
        create_env_template()

        print("=" * 50)
        print("✅ Development environment setup complete!")
        print("")
        print("📋 Next steps:")
        print("1. Review the generated .env.development file")
        print("2. Update any placeholder values as needed")
        print(
            "3. Run: python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload"
        )
        print("")
        print("🔒 Security notes:")
        print("- Development keys are generated securely")
        print("- Environment files are excluded from git")
        print("- Template file is safe to commit")
        print("- Production keys should be managed separately")

    except Exception as e:
        print(f"❌ Error setting up development environment: {e}")
        return False

    return True


if __name__ == "__main__":
    main()
