'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import AppLayout from '@/components/layouts/AppLayout';

export default function OperationsPage() {
  const [activeTab, setActiveTab] = useState('data-collection');

  // Mock operations data
  const dataCollectionJobs = [
    { id: 1, name: 'Historical Price Data Collection', status: 'completed', lastRun: '2 hours ago', nextRun: 'In 6 hours' },
    { id: 2, name: 'Technical Indicators Calculation', status: 'running', lastRun: '1 hour ago', nextRun: 'In 5 hours' },
    { id: 3, name: 'Company Fundamentals Update', status: 'pending', lastRun: '1 day ago', nextRun: 'In 2 hours' },
  ];

  const systemHealth = [
    { name: 'API Status', status: 'healthy', value: '99.9%' },
    { name: 'Database', status: 'healthy', value: 'Connected' },
    { name: 'Data Sources', status: 'warning', value: '2/3 Active' },
    { name: 'Storage', status: 'healthy', value: '78% Used' },
  ];

  const recentActivities = [
    { id: 1, action: 'Data collection completed', time: '2 hours ago', status: 'success' },
    { id: 2, action: 'Technical indicators updated', time: '3 hours ago', status: 'success' },
    { id: 3, action: 'Failed to fetch market data', time: '5 hours ago', status: 'error' },
    { id: 4, action: 'Portfolio rebalancing triggered', time: '1 day ago', status: 'success' },
  ];

  return (
    <AppLayout>
      <div className="mb-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Operations Center</h1>
          <p className="text-gray-600 mt-2">
            Monitor and manage data collection, system health, and automated processes
          </p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList>
            <TabsTrigger value="data-collection">Data Collection</TabsTrigger>
            <TabsTrigger value="system-health">System Health</TabsTrigger>
            <TabsTrigger value="activities">Recent Activities</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          <TabsContent value="data-collection" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Data Collection Jobs</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {dataCollectionJobs.map((job) => (
                    <div key={job.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <h3 className="font-semibold">{job.name}</h3>
                        <div className="flex items-center space-x-4 text-sm text-gray-600">
                          <span>Last run: {job.lastRun}</span>
                          <span>Next run: {job.nextRun}</span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge
                          variant={job.status === 'completed' ? 'default' : job.status === 'running' ? 'secondary' : 'outline'}
                        >
                          {job.status}
                        </Badge>
                        <Button size="small" variant="outline">Run Now</Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="system-health" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {systemHealth.map((item) => (
                <Card key={item.name}>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">{item.name}</p>
                        <p className="text-2xl font-bold">{item.value}</p>
                      </div>
                      <Badge
                        variant={item.status === 'healthy' ? 'default' : item.status === 'warning' ? 'secondary' : 'destructive'}
                      >
                        {item.status}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <Card>
              <CardHeader>
                <CardTitle>System Overview</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <div className="text-4xl mb-4">📊</div>
                  <p className="text-gray-600">System monitoring dashboard coming soon...</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="activities" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Recent Activities</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentActivities.map((activity) => (
                    <div key={activity.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className={`w-2 h-2 rounded-full ${
                          activity.status === 'success' ? 'bg-green-500' :
                          activity.status === 'error' ? 'bg-red-500' : 'bg-yellow-500'
                        }`}></div>
                        <div>
                          <p className="font-medium">{activity.action}</p>
                          <p className="text-sm text-gray-600">{activity.time}</p>
                        </div>
                      </div>
                      <Badge
                        variant={activity.status === 'success' ? 'default' : activity.status === 'error' ? 'destructive' : 'secondary'}
                      >
                        {activity.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="settings" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Operation Settings</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <div className="text-4xl mb-4">⚙️</div>
                  <p className="text-gray-600">Settings panel coming soon...</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </AppLayout>
  );
}
