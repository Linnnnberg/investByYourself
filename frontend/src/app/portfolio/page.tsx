'use client';

export default function PortfolioPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="text-center">
          <div className="text-6xl mb-6">🚧</div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Portfolio Management</h1>
          <p className="text-xl text-gray-600 mb-8">Coming soon...</p>
          <div className="bg-white rounded-lg shadow p-8 max-w-md mx-auto">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">What's Coming</h2>
            <ul className="text-left text-gray-600 space-y-2">
              <li>• Portfolio creation and management</li>
              <li>• Real-time portfolio tracking</li>
              <li>• Performance analytics</li>
              <li>• Risk assessment integration</li>
              <li>• Holdings management</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
