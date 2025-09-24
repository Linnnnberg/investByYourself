# Frontend Setup Guide

## 🚀 Quick Setup

### Prerequisites
- Node.js 18+ installed
- npm or yarn package manager
- Git for version control

### Installation Steps

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Environment Setup**
   ```bash
   # Copy environment template
   cp env.template .env.local

   # Edit .env.local with your values
   # At minimum, set the ETL service URL:
   NEXT_PUBLIC_ETL_SERVICE_URL='http://localhost:8001'
   ```

3. **Start Development Server**
   ```bash
   npm run dev
   ```

4. **Open Browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🔧 Development Commands

```bash
# Development
npm run dev          # Start dev server
npm run build        # Build for production
npm run start        # Start production server

# Code Quality
npm run lint         # Run ESLint
npm run type-check   # TypeScript type checking

# Testing
npm run test         # Run tests
npm run test:watch   # Run tests in watch mode
npm run test:coverage # Run tests with coverage

# Storybook (optional)
npm run storybook    # Start Storybook dev server
npm run build-storybook # Build Storybook
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── globals.css         # Global styles
│   │   ├── layout.tsx          # Root layout
│   │   └── page.tsx            # Home page
│   ├── components/             # Reusable components
│   │   └── ui/                 # shadcn/ui components
│   ├── lib/                    # Utility functions
│   │   └── utils.ts            # Main utilities
│   ├── types/                  # TypeScript types
│   └── hooks/                  # Custom React hooks
├── public/                     # Static assets
├── package.json                # Dependencies
├── tailwind.config.js          # Tailwind configuration
├── tsconfig.json               # TypeScript configuration
├── next.config.js              # Next.js configuration
└── components.json             # shadcn/ui configuration
```

## 🎨 Design System

The project uses:
- **Tailwind CSS** for styling
- **shadcn/ui** for component library
- **Custom CSS variables** for theming
- **Responsive design** with mobile-first approach

## 🔗 API Integration

The frontend integrates with:
- **ETL Service** (localhost:8001) for financial data
- **Main API** (localhost:8000) for business logic
- **Real-time updates** via WebSockets (future)

## 🚨 Troubleshooting

### Common Issues

1. **Port 3000 already in use**
   ```bash
   # Kill process on port 3000
   npx kill-port 3000
   # Or use different port
   npm run dev -- -p 3001
   ```

2. **TypeScript errors**
   ```bash
   npm run type-check
   # Fix any type issues
   ```

3. **Tailwind not working**
   ```bash
   # Rebuild CSS
   npm run build
   # Check tailwind.config.js
   ```

4. **Dependencies issues**
   ```bash
   # Clear cache and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

### Getting Help

- Check the [README.md](README.md) for detailed information
- Review [Next.js documentation](https://nextjs.org/docs)
- Check [Tailwind CSS docs](https://tailwindcss.com/docs)
- Review [shadcn/ui components](https://ui.shadcn.com/)

## 📱 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🔒 Security Notes

- Never commit `.env.local` files
- Use environment variables for sensitive data
- Validate all user inputs
- Implement proper authentication (Auth0 recommended)

## 🚀 Deployment

### Vercel (Recommended)
```bash
npm install -g vercel
vercel
```

### Docker
```bash
docker build -t investbyyourself-frontend .
docker run -p 3000:3000 investbyyourself-frontend
```

### Manual
```bash
npm run build
npm run start
```

---

**Status**: 🚀 **Ready for Development**
**Next Step**: Start building components and pages
**Target**: Functional MVP in 6 weeks
