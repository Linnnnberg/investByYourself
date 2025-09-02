/**
 * Design System Components Index for investByYourself Platform
 * Central export point for all design system components
 */

// Core Components
export { default as Button, type ButtonProps, type ButtonVariant, type ButtonSize } from './Button';
export { default as Card, type CardProps, type CardVariant, type CardSize, CardHeader, CardContent, CardFooter } from './Card';

// Component Library
export const componentLibrary = {
  Button,
  Card,
} as const;

// Component variants for easy access
export const buttonVariants = {
  primary: 'primary',
  secondary: 'secondary',
  outline: 'outline',
  ghost: 'ghost',
  danger: 'danger',
  success: 'success',
} as const;

export const buttonSizes = {
  small: 'small',
  medium: 'medium',
  large: 'large',
} as const;

export const cardVariants = {
  default: 'default',
  elevated: 'elevated',
  outlined: 'outlined',
  interactive: 'interactive',
  financial: 'financial',
} as const;

export const cardSizes = {
  small: 'small',
  medium: 'medium',
  large: 'large',
} as const;

// Component composition helpers
export const createComponentVariant = <T extends Record<string, any>>(
  component: React.ComponentType<T>,
  variant: keyof T
) => {
  return (props: Omit<T, keyof typeof variant>) => {
    return React.createElement(component, { ...props, variant } as T);
  };
};

// Export default
export default componentLibrary;
