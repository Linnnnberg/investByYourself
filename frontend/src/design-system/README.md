# investByYourself Design System

A comprehensive design system for the investByYourself financial platform, built with consistency, accessibility, and scalability in mind.

## 🎯 Overview

The investByYourself Design System provides a unified foundation for building consistent, professional user interfaces across the platform. It includes design tokens, component libraries, and utilities that ensure visual consistency and improve development velocity.

## 🏗️ Architecture

```
design-system/
├── tokens/           # Design tokens (colors, typography, spacing)
├── components/       # Reusable UI components
├── layouts/          # Layout patterns and grids
├── utilities/        # Helper functions and utilities
├── index.ts         # Main export file
└── README.md        # This file
```

## 🎨 Design Tokens

### Colors
- **Primary Colors**: Brand blue palette with 10 shades (50-900)
- **Secondary Colors**: Professional gray palette
- **Semantic Colors**: Success (green), warning (yellow), danger (red)
- **Financial Colors**: Profit, loss, neutral, alert, info
- **Background Colors**: Primary, secondary, tertiary, card, overlay
- **Text Colors**: Primary, secondary, tertiary, inverse, disabled, link
- **Border Colors**: Light, medium, dark, focus, error, success

### Typography
- **Font Families**: Inter (primary), JetBrains Mono (monospace)
- **Font Sizes**: 12px to 128px (xs to 9xl)
- **Font Weights**: 100 to 900 (thin to black)
- **Line Heights**: None, tight, snug, normal, relaxed, loose
- **Letter Spacing**: Tighter, tight, normal, wide, wider, widest
- **Text Styles**: Predefined combinations for display, headings, body, captions, buttons, financial data

### Spacing
- **Base Scale**: 4px grid system (xs: 4px to 6xl: 192px)
- **Component Spacing**: Button, card, form, navigation, layout, table, modal
- **Layout Spacing**: Container, grid, section, page
- **Responsive Spacing**: Mobile, tablet, desktop breakpoints
- **Utility Spacing**: Auto, none, full, screen dimensions

## 🧩 Components

### Button
- **Variants**: Primary, secondary, outline, ghost, danger, success
- **Sizes**: Small, medium, large
- **States**: Default, hover, active, disabled, loading
- **Features**: Icons, full width, loading spinner

### Card
- **Variants**: Default, elevated, outlined, interactive, financial
- **Sizes**: Small, medium, large
- **Features**: Header, footer, hoverable, selected, disabled
- **Padding**: None, small, medium, large, custom

## 🚀 Usage

### Basic Import
```typescript
import { Button, Card } from '@/design-system/components';
import { colors, typography, spacing } from '@/design-system';
```

### Using Components
```typescript
// Button with variants
<Button variant="primary" size="large">
  Click Me
</Button>

// Card with header and footer
<Card variant="elevated">
  <CardHeader>
    <h3>Card Title</h3>
  </CardHeader>
  <CardContent>
    <p>Card content goes here</p>
  </CardContent>
  <CardFooter>
    <Button size="small">Action</Button>
  </CardFooter>
</Card>
```

### Using Design Tokens
```typescript
// Colors
const primaryColor = colors.primary[500];
const successColor = colors.financial.profit;

// Typography
const headingStyle = typography.textStyles.heading.h1;
const bodyStyle = typography.textStyles.body.medium;

// Spacing
const buttonPadding = spacing.component.button.padding.medium;
const cardGap = spacing.component.card.gap;
```

### Custom Styling
```typescript
// Inline styles with tokens
const customStyle = {
  backgroundColor: colors.primary[100],
  padding: spacing.lg,
  fontSize: typography.textStyles.body.large.fontSize,
  fontWeight: typography.textStyles.body.large.fontWeight,
};

// CSS custom properties
const cssVariables = designSystemUtils.generateCSSVariables();
```

## 🎨 Design Principles

1. **Consistency**: Maintain visual consistency across all components
2. **Accessibility**: Ensure designs meet WCAG 2.1 AA standards
3. **Scalability**: Design system should scale with platform growth
4. **Performance**: Optimize for fast loading and smooth interactions
5. **User Experience**: Prioritize intuitive and efficient user workflows

## 🔧 Development

### Adding New Components
1. Create component file in `components/` directory
2. Use design system tokens for styling
3. Export from `components/index.ts`
4. Add to component library
5. Update documentation

### Adding New Tokens
1. Create token file in `tokens/` directory
2. Export from main `index.ts`
3. Add to design system configuration
4. Update types and utilities
5. Document usage examples

### Testing Components
1. Create component in design system demo page
2. Test all variants and states
3. Verify responsive behavior
4. Check accessibility compliance
5. Validate design token usage

## 📱 Responsive Design

The design system supports responsive design with:
- **Breakpoints**: Mobile (320px), tablet (768px), desktop (1024px), wide (1280px), ultra (1536px)
- **Responsive Spacing**: Different spacing values for different screen sizes
- **Mobile-First**: Components designed with mobile-first approach
- **Flexible Layouts**: Grid systems that adapt to screen size

## ♿ Accessibility

- **WCAG 2.1 AA Compliance**: Meets accessibility standards
- **Keyboard Navigation**: Full keyboard support for interactive components
- **Screen Reader Support**: Proper ARIA labels and semantic HTML
- **Focus Management**: Clear focus indicators and logical tab order
- **Color Contrast**: Meets minimum contrast requirements

## 🎯 Best Practices

### Component Usage
- Use semantic variants (e.g., `danger` for destructive actions)
- Maintain consistent spacing between components
- Follow established patterns for similar functionality
- Test components in different contexts and states

### Token Usage
- Use semantic color tokens over hardcoded values
- Apply consistent spacing using the spacing scale
- Use typography styles for consistent text hierarchy
- Leverage design system utilities for common operations

### Customization
- Extend components rather than overriding styles
- Use design tokens for custom styling
- Maintain consistency with existing patterns
- Document custom implementations

## 🔄 Versioning

- **Current Version**: 1.0.0
- **Breaking Changes**: Will be documented in release notes
- **Migration Guide**: Provided for major version updates
- **Deprecation Policy**: Components marked as deprecated before removal

## 📚 Resources

- **Demo Page**: `/design-system` - Interactive showcase of all components
- **Storybook**: Component documentation and examples (planned)
- **Figma Integration**: Design tokens sync with Figma (planned)
- **Component Library**: Reusable components for rapid development

## 🤝 Contributing

1. Follow established patterns and conventions
2. Use design system tokens for all styling
3. Test components across different contexts
4. Update documentation for new features
5. Maintain accessibility and performance standards

## 📞 Support

For questions or issues with the design system:
1. Check the demo page for examples
2. Review component documentation
3. Consult design system principles
4. Reach out to the design team

---

**Built with ❤️ for the investByYourself platform**
