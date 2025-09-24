# Branch Management Strategy
## InvestByYourself Platform

**Date**: January 24, 2025
**Status**: Production Ready
**Default Branch**: `master`

---

## 🎯 **Branch Structure**

### **Primary Branches**
- **`master`** - ✅ **DEFAULT BRANCH** - Clean, security-compliant, production-ready
- **`main-legacy`** - ❌ **QUARANTINED** - Contains secrets, read-only

### **Development Branches**
- **`feature/*`** - Feature development branches
- **`Story-*`** - Story-based development branches
- **`Tech-*`** - Technical implementation branches

---

## 🔒 **Branch Protection Rules**

### **Master Branch Protection**
- ✅ **Require pull request reviews** (2 reviewers)
- ✅ **Require status checks to pass** (CI/CD)
- ✅ **Require branches to be up to date**
- ✅ **Restrict pushes that create files**
- ✅ **Block force pushes**
- ✅ **Require linear history**

### **Main-Legacy Branch Protection**
- ✅ **Block all pushes** (read-only)
- ✅ **Require admin review for changes**
- ✅ **Mark as archived/legacy**

---

## 🚀 **Development Workflow**

### **For New Features**
1. **Create feature branch** from `master`
   ```bash
   git checkout master
   git pull origin master
   git checkout -b feature/your-feature-name
   ```

2. **Develop and commit** changes
   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

3. **Push and create PR** to `master`
   ```bash
   git push origin feature/your-feature-name
   # Create PR via GitHub UI
   ```

### **For Bug Fixes**
1. **Create hotfix branch** from `master`
   ```bash
   git checkout master
   git pull origin master
   git checkout -b hotfix/your-bug-fix
   ```

2. **Fix and commit** changes
   ```bash
   git add .
   git commit -m "fix: your bug fix description"
   ```

3. **Push and create PR** to `master`

---

## 🛡️ **Security Guidelines**

### **Environment Variables**
- ✅ **Use environment variables** for all secrets
- ✅ **Never commit hardcoded passwords**
- ✅ **Use `.env.example` templates**
- ✅ **Follow security best practices**

### **Pre-commit Hooks**
- ✅ **Security scanning** (GitGuardian compliance)
- ✅ **Code formatting** (Black, isort)
- ✅ **Linting** (ESLint, Prettier)
- ✅ **Type checking** (TypeScript)

---

## 📋 **Team Communication**

### **Branch Transition Notice**
> **IMPORTANT**: Default branch is now `master`. All new development should:
> - Create branches from `master`
> - Create PRs against `master`
> - `main-legacy` is read-only (contains security issues)
> - Follow the new development workflow

### **Migration Checklist**
- [ ] Update CI/CD branch filters to use `master`
- [ ] Update release pipelines to deploy from `master`
- [ ] Update CODEOWNERS to reference `master`
- [ ] Update documentation to reference `master`
- [ ] Update contribution guidelines
- [ ] Update infrastructure scripts

---

## 🔧 **Tooling Updates Required**

### **CI/CD Configuration**
```yaml
# Update branch filters
branches:
  - master
  - feature/*
  - hotfix/*
```

### **Release Pipeline**
```yaml
# Update deploy rules
deploy:
  branch: master
  environment: production
```

### **CODEOWNERS**
```
# Update default branch references
* @team-lead
/master @security-team
```

---

## 📚 **Documentation Updates**

### **Files to Update**
- [ ] `README.md` - Update branch references
- [ ] `CONTRIBUTING.md` - Update workflow
- [ ] `docs/DEVELOPMENT_SETUP.md` - Update instructions
- [ ] CI/CD documentation
- [ ] Deployment guides

### **New Documentation**
- [ ] `docs/BRANCH_MANAGEMENT.md` - This file
- [ ] `docs/SECURITY_GUIDELINES.md` - Security best practices
- [ ] `docs/DEVELOPMENT_WORKFLOW.md` - Development process

---

## 🎯 **Success Metrics**

### **Security Compliance**
- ✅ **0 hardcoded secrets** in `master` branch
- ✅ **GitGuardian approval** for all commits
- ✅ **Environment variables** for all configuration
- ✅ **Security scanning** passes

### **Development Efficiency**
- ✅ **Clean git history** in `master`
- ✅ **Protected branch** prevents direct pushes
- ✅ **PR-based workflow** ensures code review
- ✅ **Automated testing** on all PRs

---

## 🚨 **Emergency Procedures**

### **If Security Issues Found**
1. **Immediately create hotfix branch** from `master`
2. **Fix security issue** following guidelines
3. **Create PR** with security team review
4. **Deploy immediately** after approval

### **If Branch Protection Issues**
1. **Contact repository admins**
2. **Temporarily disable protection** if needed
3. **Re-enable protection** after fix
4. **Audit changes** for security compliance

---

**Last Updated**: January 24, 2025
**Maintained By**: Development Team
**Next Review**: After team migration completion
