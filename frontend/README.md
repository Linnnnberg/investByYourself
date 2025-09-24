# Frontend MVP Development

**Story-026: Frontend MVP Development** 🚀 **IMMEDIATE PRIORITY**

## 🎯 Overview

This is the frontend application for the investByYourself platform, built with Next.js, React, and TypeScript. The frontend will integrate with our existing ETL service to provide users with a comprehensive investment analysis and portfolio management interface.

## 🚀 Quick Start

### Prerequisites

1. **Node.js 18+** - [Download here](https://nodejs.org/)
2. **npm or yarn** - Package managers
3. **Git** - Version control

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js 13+ App Router
│   │   ├── (auth)/            # Authentication routes
│   │   ├── (dashboard)/       # Dashboard routes
│   │   ├── companies/         # Company analysis routes
│   │   ├── portfolio/         # Portfolio management routes
│   │   ├── api/               # API routes
│   │   ├── globals.css        # Global styles
│   │   ├── layout.tsx         # Root layout
│   │   └── page.tsx           # Home page
│   ├── components/            # Reusable components
│   │   ├── ui/                # shadcn/ui components
│   │   ├── charts/            # Chart components
│   │   ├── forms/             # Form components
│   │   └── layout/            # Layout components
│   ├── lib/                   # Utility functions
│   │   ├── utils.ts           # General utilities
│   │   ├── auth.ts            # Authentication utilities
│   │   └── api.ts             # API client utilities
│   ├── hooks/                 # Custom React hooks
│   ├── types/                 # TypeScript type definitions
│   └── styles/                # Additional styles
├── public/                    # Static assets
├── components.json            # shadcn/ui configuration
├── tailwind.config.js         # Tailwind CSS configuration
├── tsconfig.json              # TypeScript configuration
├── next.config.js             # Next.js configuration
├── package.json               # Dependencies and scripts
└── README.md                  # This file
```

## 🎨 Design System

### Technology Stack

- **Framework**: Next.js 13+ with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui
- **Charts**: TradingView Lightweight Charts + Recharts
- **State Management**: Zustand
- **Forms**: React Hook Form + Zod
- **Data Fetching**: TanStack Query (React Query)

### Key Features

1. **Authentication System**
   - Auth0 integration
   - Magic link authentication
   - User profile management
   - Session handling

2. **Core Dashboard**
   - Watchlist with real-time data
   - Portfolio overview and P&L
   - Quick filters and search
   - Responsive design

3. **Company Analysis Interface**
   - Company overview pages
   - Financial statements (IS/BS/CF)
   - Ratio analysis and peer comparison
   - Interactive charts

4. **Portfolio Management**
   - Portfolio creation and CSV import
   - Holdings view with cost basis
   - Performance tracking vs benchmarks
   - Basic rebalancing suggestions

5. **Data Export & Reporting**
   - CSV export for portfolio data
   - PDF generation for reports
   - One-click export functionality
   - Basic alerting system

## 🔧 Development

### Environment Variables

Create a `.env.local` file:

```bash
# Auth0 Configuration
AUTH0_SECRET='your-auth0-secret'
AUTH0_BASE_URL='http://localhost:3000'
AUTH0_ISSUER_BASE_URL='https://your-domain.auth0.com'
AUTH0_CLIENT_ID='your-auth0-client-id'
AUTH0_CLIENT_SECRET='your-auth0-client-secret'

# API Configuration
NEXT_PUBLIC_API_BASE_URL='http://localhost:8000'
NEXT_PUBLIC_ETL_SERVICE_URL='http://localhost:8001'

# Database (if needed)
DATABASE_URL='postgresql://...'
```

### Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript type checking
npm run test         # Run tests
npm run test:watch   # Run tests in watch mode
```

## 📱 Responsive Design

The application is designed with a **desktop-first** approach:

- **Desktop**: Full-featured interface with advanced tools
- **Tablet**: Optimized for touch with simplified navigation
- **Mobile**: Essential features with touch-friendly controls

## 🔗 API Integration

### ETL Service Integration

The frontend integrates with our ETL service for:

- Company profile data
- Financial statements and ratios
- Market data and pricing
- Portfolio data management

### Data Flow

1. **User Request** → Frontend Component
2. **API Call** → ETL Service
3. **Data Processing** → ETL Service
4. **Response** → Frontend Component
5. **State Update** → UI Rendering

## 🚀 Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Docker

```bash
# Build image
docker build -t investbyyourself-frontend .

# Run container
docker run -p 3000:3000 investbyyourself-frontend
```

## 📊 Performance Targets

- **Dashboard TTI**: < 3s on 4G
- **Chart Interactivity**: < 100ms on hover/zoom
- **Data Refresh**: ≤ 15 min for equities, ≤ 24h for macro
- **Page Load**: < 2s for company pages

## 🧪 Testing

### Testing Stack

- **Unit Tests**: Jest + React Testing Library
- **E2E Tests**: Playwright
- **Component Tests**: Storybook (optional)

### Test Coverage Goals

- **Unit Tests**: >90% coverage
- **Component Tests**: >80% coverage
- **E2E Tests**: Critical user journeys

## 🔒 Security

- **Authentication**: Auth0 OIDC/OAuth2
- **API Security**: HTTPS, JWT tokens, rate limiting
- **Data Protection**: GDPR compliance, no PII exposure
- **Input Validation**: Zod schema validation

## 📈 Monitoring

- **Error Tracking**: Sentry
- **Performance**: Web Vitals, Core Web Vitals
- **Analytics**: Google Analytics 4
- **Uptime**: Vercel Analytics

## 🎯 Success Criteria

- [ ] Functional MVP with core user journeys
- [ ] Users can explore companies, manage portfolios
- [ ] Real-time data integration working
- [ ] Export and reporting functional
- [ ] Responsive design for desktop use

## 📚 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [shadcn/ui Components](https://ui.shadcn.com/)
- [React Query Documentation](https://tanstack.com/query/latest)
- [TradingView Charts](https://www.tradingview.com/lightweight-charts/)

## 🤝 Contributing

1. Follow the established code patterns
2. Write tests for new features
3. Update documentation as needed
4. Use conventional commits for messages

---

**Status**: 🚀 **IN PROGRESS** - Frontend Infrastructure Setup
**Next Milestone**: Authentication System Implementation
**Target Completion**: 6 weeks
