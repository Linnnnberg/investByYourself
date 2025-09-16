'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Building2,
  TrendingUp,
  Users,
  Briefcase,
  Settings,
  Database,
  FileText,
  BarChart3,
  Wrench
} from 'lucide-react';

const ENTITY_SECTIONS = [
  {
    title: 'Data Management',
    entities: [
      { id: 'companies', name: 'Companies', icon: Building2, count: 35, description: 'Company profiles and information' },
      { id: 'sectors', name: 'Sectors', icon: BarChart3, count: 10, description: 'Sector classifications and data' },
      { id: 'ratios', name: 'Financial Ratios', icon: TrendingUp, count: 490, description: 'Financial metrics and ratios' },
    ]
  },
  {
    title: 'User Management',
    entities: [
      { id: 'users', name: 'Users', icon: Users, count: 0, description: 'User accounts and profiles' },
      { id: 'sessions', name: 'Sessions', icon: Database, count: 0, description: 'Active user sessions' },
    ]
  },
  {
    title: 'Portfolio Management',
    entities: [
      { id: 'portfolios', name: 'Portfolios', icon: Briefcase, count: 0, description: 'User investment portfolios' },
      { id: 'strategies', name: 'Strategies', icon: FileText, count: 0, description: 'Investment strategies' },
    ]
  },
  {
    title: 'System',
    entities: [
      { id: 'logs', name: 'System Logs', icon: FileText, count: 0, description: 'Application and error logs' },
      { id: 'settings', name: 'Settings', icon: Settings, count: 0, description: 'System configuration' },
    ]
  }
];

export default function OperationsPage() {
  const [selectedEntity, setSelectedEntity] = useState('companies');

  const handleEntitySelect = (entityId: string) => {
    setSelectedEntity(entityId);
  };

  const handleCRUDOperation = (operation: string, entityId: string) => {
    console.log(`${operation} operation for ${entityId}`);
    // TODO: Implement CRUD operations
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Operations Dashboard</h1>
              <p className="text-gray-600">Manage all database entities with full CRUD operations</p>
            </div>
            <div className="flex items-center space-x-3">
              <Button variant="outline" size="sm">
                <Database className="h-4 w-4 mr-2" />
                Database Status
              </Button>
              <Button variant="outline" size="sm">
                <Wrench className="h-4 w-4 mr-2" />
                System Tools
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="flex h-screen">
        {/* Sidebar */}
        <div className="w-80 bg-white shadow-lg h-full overflow-y-auto">
          <div className="p-4">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Entity Management</h2>

            {ENTITY_SECTIONS.map((section) => (
              <div key={section.title} className="mb-6">
                <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-3">
                  {section.title}
                </h3>
                <div className="space-y-1">
                  {section.entities.map((entity) => (
                    <button
                      key={entity.id}
                      onClick={() => handleEntitySelect(entity.id)}
                      className={`w-full flex items-center justify-between p-3 text-left rounded-lg transition-colors ${
                        selectedEntity === entity.id
                          ? 'bg-blue-100 text-blue-700 border border-blue-200'
                          : 'text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      <div className="flex items-center">
                        <entity.icon className="h-5 w-5 mr-3" />
                        <div>
                          <div className="font-medium">{entity.name}</div>
                          <div className="text-sm text-gray-500">{entity.description}</div>
                        </div>
                      </div>
                      <div className="text-sm font-medium text-gray-400">
                        {entity.count}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-xl capitalize">
                    {selectedEntity.replace('-', ' ')} Management
                  </CardTitle>
                  <p className="text-gray-600 mt-1">
                    Manage {selectedEntity} data with full CRUD operations
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <Button
                    onClick={() => handleCRUDOperation('create', selectedEntity)}
                    size="sm"
                  >
                    Add New
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleCRUDOperation('export', selectedEntity)}
                    size="sm"
                  >
                    Export
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleCRUDOperation('import', selectedEntity)}
                    size="sm"
                  >
                    Import
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <Wrench className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Operations Panel Coming Soon
                </h3>
                <p className="text-gray-600 mb-6">
                  The {selectedEntity} management panel is currently under development.
                  This will include full CRUD operations, data tables, and advanced filtering.
                </p>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 max-w-md mx-auto">
                  <h4 className="font-medium text-blue-900 mb-2">Planned Features:</h4>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• Full CRUD operations (Create, Read, Update, Delete)</li>
                    <li>• Advanced search and filtering</li>
                    <li>• Bulk operations (import/export)</li>
                    <li>• Real-time data updates</li>
                    <li>• Audit logging and security controls</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
