# HTML Element Naming Strategy

## Overview
This document outlines the naming strategy for HTML elements to improve debugging, testing, and development experience.

## Naming Convention

### Format
```
[feature]-[component]-[element]-[variant]
```

### Examples
- `watchlist-add-company-button`
- `markets-search-input`
- `watchlist-item-remove-button`
- `company-card-price-display`

## Data Attributes

### Primary Attributes
- `data-testid`: For testing and debugging purposes
- `data-feature`: For feature identification and grouping
- `data-component`: For component identification

### Usage Pattern
```html
<button
  data-testid="watchlist-add-company-button"
  data-feature="watchlist-add-company"
  data-component="button"
>
  Add Company
</button>
```

## Feature Categories

### Navigation
- `navigation-*`: Main navigation elements
- `sidebar-*`: Sidebar navigation items
- `top-navigation-*`: Top navigation elements

### Watchlist
- `watchlist-*`: Watchlist related features
- `watchlist-add-*`: Adding companies to watchlist
- `watchlist-item-*`: Individual watchlist items
- `watchlist-search-*`: Watchlist search functionality

### Markets/Companies
- `markets-*`: Markets page features
- `markets-company-*`: Company cards and details
- `markets-search-*`: Markets search functionality

### Search
- `search-*`: General search functionality
- `search-result-*`: Search result items
- `search-input-*`: Search input fields

### Statistics
- `stats-*`: Statistics displays
- `watchlist-stats-*`: Watchlist statistics
- `markets-stats-*`: Markets statistics

## Implementation Examples

### Watchlist Page
```html
<!-- Page Title -->
<h1 data-testid="watchlist-page-title" data-feature="watchlist-page">Watchlist</h1>

<!-- Add Company Button -->
<button
  data-testid="watchlist-add-company-button"
  data-feature="watchlist-add-company"
>
  Add Company
</button>

<!-- Search Input -->
<input
  data-testid="watchlist-search-input"
  data-feature="watchlist-search"
  placeholder="Search your watchlist..."
/>

<!-- Watchlist Item -->
<div
  data-testid="watchlist-item-sap.de"
  data-feature="watchlist-item"
>
  <!-- Item content -->
</div>

<!-- Remove Button -->
<button
  data-testid="remove-watchlist-item-sap.de-button"
  data-feature="remove-watchlist-item"
>
  ✕
</button>
```

### Markets Page
```html
<!-- Page Title -->
<h1 data-testid="markets-page-title" data-feature="markets-page">Markets</h1>

<!-- Company Card -->
<div
  data-testid="markets-company-card-sap.de"
  data-feature="markets-company-card"
>
  <!-- Company content -->
</div>

<!-- View Details Button -->
<button
  data-testid="markets-company-view-details-sap.de-button"
  data-feature="markets-company-view-details"
>
  View Details
</button>
```

### Navigation
```html
<!-- Sidebar Link -->
<a
  data-testid="sidebar-companies-link"
  data-feature="navigation-companies"
  href="/companies"
>
  Markets
</a>

<!-- Top Navigation Search -->
<input
  data-testid="top-navigation-search-input"
  data-feature="top-navigation-search"
  placeholder="Search markets..."
/>
```

## Benefits

### 1. **Easy Element Selection**
```javascript
// Select by test ID
document.querySelector('[data-testid="watchlist-add-company-button"]')

// Select by feature
document.querySelectorAll('[data-feature="watchlist-item"]')
```

### 2. **Testing Framework Integration**
```javascript
// Playwright/Cypress examples
await page.click('[data-testid="watchlist-add-company-button"]')
await page.fill('[data-testid="watchlist-search-input"]', 'SAP')
```

### 3. **Debugging**
```javascript
// Find all watchlist items
document.querySelectorAll('[data-feature="watchlist-item"]')

// Find specific company
document.querySelector('[data-testid="watchlist-item-sap.de"]')
```

### 4. **Feature Grouping**
```javascript
// Get all watchlist related elements
document.querySelectorAll('[data-feature^="watchlist"]')

// Get all navigation elements
document.querySelectorAll('[data-feature^="navigation"]')
```

## Implementation Guidelines

### 1. **Consistency**
- Always use kebab-case for test IDs
- Use descriptive names that indicate purpose
- Include the feature category in the name

### 2. **Uniqueness**
- Test IDs should be unique within the page
- Use dynamic parts (like company symbols) for uniqueness
- Avoid generic names like "button" or "input"

### 3. **Maintainability**
- Use consistent patterns across similar components
- Document naming conventions for new developers
- Update names when features change

### 4. **Performance**
- Use `data-testid` for primary selection
- Use `data-feature` for grouping and filtering
- Avoid over-using data attributes

## Testing Integration

### Playwright Example
```javascript
test('add company to watchlist', async ({ page }) => {
  await page.click('[data-testid="watchlist-add-company-button"]')
  await page.fill('[data-testid="watchlist-company-search-input"]', 'SAP')
  await page.click('[data-testid="add-company-sap.de-button"]')
  await expect(page.locator('[data-testid="watchlist-item-sap.de"]')).toBeVisible()
})
```

### Cypress Example
```javascript
it('should add company to watchlist', () => {
  cy.get('[data-testid="watchlist-add-company-button"]').click()
  cy.get('[data-testid="watchlist-company-search-input"]').type('SAP')
  cy.get('[data-testid="add-company-sap.de-button"]').click()
  cy.get('[data-testid="watchlist-item-sap.de"]').should('be.visible')
})
```

## Future Enhancements

### 1. **Automated Testing**
- Generate test selectors automatically
- Validate naming conventions in CI/CD
- Create testing utilities based on naming patterns

### 2. **Developer Tools**
- Browser extension for element inspection
- VS Code extension for naming validation
- Automated documentation generation

### 3. **Analytics Integration**
- Track user interactions by feature
- Monitor component usage patterns
- Generate usage reports

## Conclusion

This naming strategy provides:
- **Clear element identification** for debugging
- **Consistent patterns** for development
- **Easy testing integration** with modern frameworks
- **Maintainable codebase** with clear conventions

The strategy is designed to scale with the application and provide long-term benefits for development, testing, and maintenance.
