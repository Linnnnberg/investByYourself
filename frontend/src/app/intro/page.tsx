'use client';

import Link from 'next/link';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function IntroPage() {
  return (
    <div className="fixed inset-0 bg-gradient-to-br from-blue-50 to-indigo-100 overflow-y-auto">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            InvestByYourself
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Your comprehensive investment platform for data-driven portfolio management,
            AI-powered workflows, and intelligent market analysis.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/home">
               <Button size="large" className="text-lg px-8 py-4">
                 Start App
               </Button>
             </Link>
             <Link href="/home">
               <Button variant="outline" size="large" className="text-lg px-8 py-4">
                 View Dashboard
               </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          Why Choose InvestByYourself?
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {/* AI-Powered Workflows */}
          <Card className="text-center">
            <CardHeader>
              <div className="text-4xl mb-4">🤖</div>
              <h3 className="text-xl font-semibold">AI-Powered Workflows</h3>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Intelligent workflow engine that guides you through portfolio creation,
                risk assessment, and investment decisions with AI-driven insights.
              </p>
            </CardContent>
          </Card>

          {/* Comprehensive Data Analysis */}
          <Card className="text-center">
            <CardHeader>
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-xl font-semibold">Comprehensive Data Analysis</h3>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Access 5+ years of historical data, technical indicators, and real-time
                market analysis for informed investment decisions.
              </p>
            </CardContent>
          </Card>

          {/* Portfolio Management */}
          <Card className="text-center">
            <CardHeader>
              <div className="text-4xl mb-4">💼</div>
              <h3 className="text-xl font-semibold">Advanced Portfolio Management</h3>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Create, track, and optimize portfolios with sophisticated allocation
                frameworks and risk management tools.
              </p>
            </CardContent>
          </Card>

          {/* Real-time Market Data */}
          <Card className="text-center">
            <CardHeader>
              <div className="text-4xl mb-4">📈</div>
              <h3 className="text-xl font-semibold">Real-time Market Data</h3>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Stay updated with live market data, price movements, and market
                trends from multiple reliable sources.
              </p>
            </CardContent>
          </Card>

          {/* Risk Assessment */}
          <Card className="text-center">
            <CardHeader>
              <div className="text-4xl mb-4">⚖️</div>
              <h3 className="text-xl font-semibold">Intelligent Risk Assessment</h3>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Get personalized risk profiles and recommendations based on your
                investment goals and risk tolerance.
              </p>
            </CardContent>
          </Card>

          {/* Customizable Workflows */}
          <Card className="text-center">
            <CardHeader>
              <div className="text-4xl mb-4">⚙️</div>
              <h3 className="text-xl font-semibold">Customizable Workflows</h3>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Create custom investment workflows tailored to your specific
                strategies and preferences.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Call to Action */}
      <div className="container mx-auto px-4 py-16 text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-6">
          Ready to Take Control of Your Investments?
        </h2>
        <p className="text-xl text-gray-600 mb-8">
          Join InvestByYourself today and empower your financial journey.
        </p>
        <Link href="/home">
           <Button size="large" className="text-lg px-8 py-4">
             Sign Up Now
           </Button>
        </Link>
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8 mt-auto">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; 2025 InvestByYourself. All rights reserved.</p>
          <div className="flex justify-center space-x-4 mt-4">
            <Link href="/privacy" className="hover:underline">Privacy Policy</Link>
            <Link href="/terms" className="hover:underline">Terms of Service</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
