# 🚀 investByYourself Frontend

A modern, professional investment platform built with React, TypeScript, and Vite.

## 🏗️ Project Structure

```
src/
├── components/          # React components
│   ├── ui/             # Reusable UI components (shadcn/ui)
│   └── ...             # Feature-specific components
├── constants/           # Application constants
├── hooks/              # Custom React hooks
├── services/           # API and external service integrations
├── styles/             # Design tokens and global styles
├── types/              # TypeScript type definitions
├── utils/              # Utility functions and helpers
├── App.tsx             # Main application component
├── main.tsx            # Application entry point
└── index.css           # Global CSS styles
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation
```bash
npm install
```

### Development
```bash
npm run dev
```

Visit `http://localhost:3000` to view the application.

### Build
```bash
npm run build
```

## 🎨 Design System

This project uses a comprehensive design system with:
- **Figma Integration**: Design tokens extracted from Figma
- **shadcn/ui**: High-quality, accessible UI components
- **Tailwind CSS**: Utility-first CSS framework
- **TypeScript**: Full type safety

## 🔧 Key Features

- **Dashboard**: Portfolio overview and market insights
- **Portfolio Management**: Track holdings and performance
- **Watchlist**: Monitor favorite stocks
- **Market Analysis**: Technical and fundamental analysis tools
- **Real-time Data**: Live market updates via Supabase
- **Responsive Design**: Mobile-first approach

## 📚 Documentation

- [Figma Integration Guide](./FIGMA_INTEGRATION_GUIDE.md) - How to integrate Figma designs
- [Component Library](./src/components/ui/) - Available UI components
- [Design Tokens](./src/styles/figma-tokens.ts) - Design system tokens

## 🏗️ Architecture

### **Type Safety**
- Centralized type definitions in `src/types/`
- Full TypeScript coverage
- Interface-driven development

### **State Management**
- React hooks for local state
- Custom hooks for common patterns
- Context for global state (when needed)

### **API Integration**
- Centralized API service in `src/services/`
- Supabase integration for real-time data
- Error handling and retry logic

### **Styling**
- Tailwind CSS for utility classes
- Figma design tokens for consistency
- CSS modules for component-specific styles

## 🧪 Development

### **Code Quality**
- ESLint configuration
- Prettier formatting
- TypeScript strict mode

### **Testing**
- Unit tests with Vitest
- Component testing with React Testing Library
- E2E testing with Playwright (planned)

### **Performance**
- Code splitting with React.lazy
- Optimized bundle with Vite
- Image optimization

## 📦 Dependencies

### **Core**
- React 18
- TypeScript 5
- Vite 5

### **UI & Styling**
- Tailwind CSS
- shadcn/ui components
- Lucide React icons

### **Data & State**
- Supabase client
- React Query (planned)
- Zustand (planned)

### **Development**
- ESLint
- Prettier
- Vitest

## 🌟 Contributing

1. Follow the established project structure
2. Use TypeScript for all new code
3. Follow the design system guidelines
4. Write tests for new features
5. Update documentation as needed

## 📄 License

This project is proprietary software. All rights reserved.

---

**Built with ❤️ by the investByYourself Team**
