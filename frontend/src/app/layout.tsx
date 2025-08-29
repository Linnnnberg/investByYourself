import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'InvestByYourself - Financial Analysis Platform',
  description: 'Comprehensive investment analysis and portfolio management platform with real-time financial data and advanced analytics.',
  keywords: ['investment', 'financial analysis', 'portfolio management', 'stock analysis', 'ETL', 'financial data'],
  authors: [{ name: 'InvestByYourself Development Team' }],
  creator: 'InvestByYourself Development Team',
  publisher: 'InvestByYourself',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL('https://investbyyourself.com'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    title: 'InvestByYourself - Financial Analysis Platform',
    description: 'Comprehensive investment analysis and portfolio management platform with real-time financial data and advanced analytics.',
    url: 'https://investbyyourself.com',
    siteName: 'InvestByYourself',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'InvestByYourself Platform',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'InvestByYourself - Financial Analysis Platform',
    description: 'Comprehensive investment analysis and portfolio management platform with real-time financial data and advanced analytics.',
    images: ['/og-image.png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'your-google-verification-code',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <div className="min-h-screen bg-background">
          {children}
        </div>
      </body>
    </html>
  )
}
