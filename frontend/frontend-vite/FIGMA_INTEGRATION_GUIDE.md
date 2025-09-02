# 🎨 Figma Integration Guide for investByYourself

## Overview
This guide will help you extract design values from your Figma design and integrate them into your codebase using the `figma-tokens.ts` file.

## 🚀 Quick Start

### Step 1: Open Your Figma Design
1. Open your Figma file
2. Identify the main components (dashboard, cards, buttons, etc.)
3. Select a component to extract values from

### Step 2: Extract Design Values
For each component, extract these values:

#### **Colors**
- **Primary colors**: Main brand colors
- **Surface colors**: Background colors for cards, sections
- **Text colors**: Primary, secondary, tertiary text
- **Border colors**: Lines and dividers
- **Semantic colors**: Success, warning, danger states

#### **Typography**
- **Font family**: What fonts are you using?
- **Font sizes**: From smallest (xs) to largest (9xl)
- **Font weights**: Light, normal, medium, semibold, bold
- **Line heights**: How much space between lines
- **Letter spacing**: Space between characters

#### **Spacing**
- **Padding**: Internal spacing within components
- **Margins**: External spacing between components
- **Grid system**: Base spacing unit (usually 4px or 8px)

#### **Layout**
- **Border radius**: How rounded are your corners?
- **Shadows**: Drop shadows and elevation
- **Borders**: Line thickness and styles

## 📋 Step-by-Step Extraction

### 1. Extract Colors

#### **Primary Brand Colors**
1. **Select your main brand color** (e.g., primary button)
2. **Copy the hex code** (e.g., #3b82f6)
3. **Update in `figma-tokens.ts`**:

```typescript
// In figma-tokens.ts
primary: {
  500: '#3b82f6',  // Replace with your Figma color
  // ... other shades
}
```

#### **Surface Colors**
1. **Select a card or section background**
2. **Copy the hex code**
3. **Update in `figma-tokens.ts`**:

```typescript
surface: {
  default: '#ffffff',    // Replace with your Figma color
  elevated: '#f8fafc',   // Replace with your Figma color
  // ... other surfaces
}
```

### 2. Extract Typography

#### **Font Family**
1. **Select any text element**
2. **Note the font name** (e.g., Inter, Roboto, SF Pro)
3. **Update in `figma-tokens.ts`**:

```typescript
fontFamily: {
  primary: 'Inter, system-ui, sans-serif',  // Replace with your Figma font
  // ... other fonts
}
```

#### **Font Sizes**
1. **Select different text elements** (headings, body, captions)
2. **Note the font sizes** (in px or rem)
3. **Update in `figma-tokens.ts`**:

```typescript
fontSize: {
  xs: '0.75rem',      // Replace with your Figma size
  sm: '0.875rem',     // Replace with your Figma size
  base: '1rem',       // Replace with your Figma size
  lg: '1.125rem',     // Replace with your Figma size
  xl: '1.25rem',      // Replace with your Figma size
  '2xl': '1.5rem',    // Replace with your Figma size
  // ... other sizes
}
```

### 3. Extract Spacing

#### **Base Spacing Unit**
1. **Look for consistent spacing patterns**
2. **Identify the base unit** (usually 4px, 8px, or 16px)
3. **Update in `figma-tokens.ts`**:

```typescript
spacing: {
  xs: '0.25rem',    // 4px - Replace with your Figma unit
  sm: '0.5rem',     // 8px - Replace with your Figma unit
  md: '1rem',       // 16px - Replace with your Figma unit
  lg: '1.5rem',     // 24px - Replace with your Figma unit
  xl: '2rem',       // 32px - Replace with your Figma unit
  // ... other spacing
}
```

### 4. Extract Layout Values

#### **Border Radius**
1. **Select a card or button**
2. **Note the corner radius** (in px or rem)
3. **Update in `figma-tokens.ts`**:

```typescript
borderRadius: {
  sm: '0.125rem',    // 2px - Replace with your Figma value
  md: '0.375rem',    // 6px - Replace with your Figma value
  lg: '0.5rem',      // 8px - Replace with your Figma value
  xl: '0.75rem',     // 12px - Replace with your Figma value
  '2xl': '1rem',     // 16px - Replace with your Figma value
  // ... other radius values
}
```

#### **Shadows**
1. **Select an elevated component** (card, button)
2. **Note the shadow properties** (offset, blur, color, opacity)
3. **Update in `figma-tokens.ts`**:

```typescript
shadows: {
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',  // Replace with your Figma shadow
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)', // Replace with your Figma shadow
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)', // Replace with your Figma shadow
  // ... other shadows
}
```

## 🎯 Example: Extract Dashboard Card Values

### 1. Select Your Dashboard Card in Figma
- Click on the main dashboard card/section

### 2. Extract Values
```typescript
// Example values from a Figma dashboard card
{
  // Colors
  backgroundColor: '#ffffff',        // Card background
  borderColor: '#e5e7eb',          // Card border
  textColor: '#111827',             // Card title

  // Spacing
  padding: '24px',                  // Internal spacing
  margin: '32px',                   // External spacing

  // Layout
  borderRadius: '12px',             // Corner radius
  shadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)', // Drop shadow

  // Typography
  titleFontSize: '24px',            // Title size
  titleFontWeight: '600',           // Title weight
  bodyFontSize: '16px',             // Body text size
}
```

### 3. Update Your Tokens
```typescript
// In figma-tokens.ts
export const figmaTokens = {
  colors: {
    surface: {
      default: '#ffffff',    // Your Figma card background
    },
    border: {
      default: '#e5e7eb',   // Your Figma card border
    },
    text: {
      primary: '#111827',    // Your Figma card title
    }
  },
  spacing: {
    lg: '1.5rem',           // 24px - Your Figma padding
    xl: '2rem',             // 32px - Your Figma margin
  },
  borderRadius: {
    xl: '0.75rem',          // 12px - Your Figma radius
  },
  shadows: {
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)', // Your Figma shadow
  },
  typography: {
    fontSize: {
      '2xl': '1.5rem',      // 24px - Your Figma title size
      base: '1rem',          // 16px - Your Figma body size
    },
    fontWeight: {
      semibold: '600',       // Your Figma title weight
    }
  }
};
```

## 🔄 Update Components

### 1. Import Tokens
```typescript
import { figmaTokens } from '../styles/figma-tokens';
```

### 2. Apply to Components
```typescript
<div
  style={{
    backgroundColor: figmaTokens.colors.surface.default,
    borderRadius: figmaTokens.borderRadius.xl,
    border: `1px solid ${figmaTokens.colors.border.default}`,
    boxShadow: figmaTokens.shadows.md,
    padding: figmaTokens.spacing.lg
  }}
>
  <h2 style={{
    color: figmaTokens.colors.text.primary,
    fontSize: figmaTokens.typography.fontSize['2xl'],
    fontWeight: figmaTokens.typography.fontWeight.semibold
  }}>
    Your Title
  </h2>
</div>
```

## 🧪 Testing Your Changes

### 1. Start Development Server
```bash
npm run dev
```

### 2. View Changes
- Open `http://localhost:3000`
- Navigate to your dashboard
- See your Figma styles applied!

### 3. Iterate
- Make changes in Figma
- Update `figma-tokens.ts`
- Refresh browser to see updates

## 🎨 Best Practices

### 1. Start Small
- Begin with one component (e.g., dashboard card)
- Extract all values for that component
- Test and iterate

### 2. Be Consistent
- Use the same spacing scale throughout
- Maintain consistent color usage
- Follow typography hierarchy

### 3. Document Changes
- Note which Figma components you've extracted
- Keep track of any custom values
- Update this guide as you learn

## 🚀 Next Steps

1. **Extract values** from your main dashboard card
2. **Update `figma-tokens.ts`** with those values
3. **Test the changes** in your browser
4. **Move to the next component** (buttons, tables, etc.)
5. **Create a complete design system** from your Figma

## 📚 Resources

- [Figma Design Tokens Plugin](https://www.figma.com/community/plugin/843461159747178978/Design-Tokens)
- [Figma to Code Tools](https://www.figma.com/community/plugin/843461159747178978/Design-Tokens)
- [Design System Best Practices](https://www.designsystems.com/)

---

**Happy designing! 🎨✨**

Your Figma designs will now be perfectly integrated with your codebase!
