'use client';

import React from 'react';
import {
  ChartBarIcon,
  UserGroupIcon,
  AcademicCapIcon,
  ClockIcon,
  TrophyIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
} from '@heroicons/react/24/outline';

export default function AdminDashboard() {
  const companyStats = {
    totalEmployees: 245,
    activeEmployees: 198,
    completionRate: 87,
    averageScore: 91,
    totalTrainingHours: 1247,
    modulesCompleted: 3456,
  };

  const departmentPerformance = [
    { name: 'Sales', employees: 45, completion: 95, score: 94, trend: 'up' },
    { name: 'Customer Service', employees: 32, completion: 89, score: 88, trend: 'up' },
    { name: 'Engineering', employees: 78, completion: 82, score: 95, trend: 'down' },
    { name: 'Marketing', employees: 28, completion: 91, score: 87, trend: 'up' },
    { name: 'HR', employees: 15, completion: 100, score: 92, trend: 'up' },
    { name: 'Finance', employees: 22, completion: 77, score: 89, trend: 'down' },
  ];

  const popularModules = [
    { name: 'Sales Communication Skills', completions: 156, rating: 4.8, duration: '45 min' },
    { name: 'Customer Service Excellence', completions: 143, rating: 4.7, duration: '30 min' },
    { name: 'Leadership Fundamentals', completions: 128, rating: 4.9, duration: '60 min' },
    { name: 'Technical Skills Assessment', completions: 112, rating: 4.6, duration: '40 min' },
    { name: 'Compliance Training', completions: 98, rating: 4.5, duration: '25 min' },
  ];

  const recentActivity = [
    { user: 'Sarah Johnson', action: 'Completed Sales Communication Skills', score: 95, time: '2 hours ago' },
    { user: 'Mike Chen', action: 'Started Leadership Fundamentals', score: null, time: '3 hours ago' },
    { user: 'Lisa Rodriguez', action: 'Achieved Customer Service Expert badge', score: null, time: '5 hours ago' },
    { user: 'David Kim', action: 'Completed Technical Assessment', score: 88, time: '6 hours ago' },
    { user: 'Emma Wilson', action: 'Started Compliance Training', score: null, time: '8 hours ago' },
  ];

  const alerts = [
    { type: 'warning', message: 'Engineering department completion rate below target (82%)', time: '1 hour ago' },
    { type: 'info', message: 'New module "Cybersecurity Awareness" has been published', time: '2 hours ago' },
    { type: 'success', message: 'Sales department achieved 95% completion rate', time: '4 hours ago' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="text-gray-600">Manage training programs and track employee progress</p>
            </div>
            <div className="flex space-x-4">
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                Add New Module
              </button>
              <button className="border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50">
                Export Report
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="flex items-center">
              <UserGroupIcon className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Employees</p>
                <p className="text-2xl font-bold text-gray-900">{companyStats.totalEmployees}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="flex items-center">
              <CheckCircleIcon className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Learners</p>
                <p className="text-2xl font-bold text-gray-900">{companyStats.activeEmployees}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="flex items-center">
              <TrophyIcon className="h-8 w-8 text-yellow-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Completion Rate</p>
                <p className="text-2xl font-bold text-gray-900">{companyStats.completionRate}%</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="flex items-center">
              <ChartBarIcon className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Avg Score</p>
                <p className="text-2xl font-bold text-gray-900">{companyStats.averageScore}%</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="flex items-center">
              <ClockIcon className="h-8 w-8 text-indigo-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Training Hours</p>
                <p className="text-2xl font-bold text-gray-900">{companyStats.totalTrainingHours.toLocaleString()}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="flex items-center">
              <AcademicCapIcon className="h-8 w-8 text-red-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Modules Done</p>
                <p className="text-2xl font-bold text-gray-900">{companyStats.modulesCompleted.toLocaleString()}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Department Performance */}
          <div className="lg:col-span-2">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Department Performance</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Department</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Employees</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Completion</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Avg Score</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Trend</th>
                    </tr>
                  </thead>
                  <tbody>
                    {departmentPerformance.map((dept) => (
                      <tr key={dept.name} className="border-b border-gray-100">
                        <td className="py-3 px-4 font-medium text-gray-900">{dept.name}</td>
                        <td className="py-3 px-4 text-gray-600">{dept.employees}</td>
                        <td className="py-3 px-4">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            dept.completion >= 90 ? 'bg-green-100 text-green-800' :
                            dept.completion >= 80 ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {dept.completion}%
                          </span>
                        </td>
                        <td className="py-3 px-4 text-gray-600">{dept.score}%</td>
                        <td className="py-3 px-4">
                          {dept.trend === 'up' ? (
                            <ArrowTrendingUpIcon className="h-5 w-5 text-green-600" />
                          ) : (
                            <ArrowTrendingDownIcon className="h-5 w-5 text-red-600" />
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Alerts & Notifications */}
          <div>
            <div className="bg-white p-6 rounded-lg shadow-sm mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Alerts & Notifications</h3>
              <div className="space-y-4">
                {alerts.map((alert, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    {alert.type === 'warning' && (
                      <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600 mt-0.5" />
                    )}
                    {alert.type === 'info' && (
                      <ChartBarIcon className="h-5 w-5 text-blue-600 mt-0.5" />
                    )}
                    {alert.type === 'success' && (
                      <CheckCircleIcon className="h-5 w-5 text-green-600 mt-0.5" />
                    )}
                    <div className="flex-1">
                      <p className="text-sm text-gray-900">{alert.message}</p>
                      <p className="text-xs text-gray-500 mt-1">{alert.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
          {/* Popular Training Modules */}
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Most Popular Modules</h3>
            <div className="space-y-4">
              {popularModules.map((module, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{module.name}</h4>
                    <div className="flex items-center space-x-4 mt-1">
                      <span className="text-sm text-gray-600">{module.completions} completions</span>
                      <span className="text-sm text-gray-600">⭐ {module.rating}</span>
                      <span className="text-sm text-gray-600">{module.duration}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
            <div className="space-y-4">
              {recentActivity.map((activity, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-xs font-medium text-blue-600">
                      {activity.user.split(' ').map(n => n[0]).join('')}
                    </span>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-gray-900">
                      <span className="font-medium">{activity.user}</span> {activity.action}
                      {activity.score && (
                        <span className="ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                          {activity.score}%
                        </span>
                      )}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* AI Integration Notice */}
        <div className="mt-8 bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Universal AI Platform Integration</h3>
              <p className="text-gray-600 mt-1">
                This dashboard is powered by the Universal AI Agent Platform, providing real-time analytics, 
                AI-driven insights, and intelligent training recommendations.
              </p>
              <div className="mt-3 flex space-x-4 text-sm">
                <span className="flex items-center text-green-600">
                  <CheckCircleIcon className="h-4 w-4 mr-1" />
                  Real-time AI coaching
                </span>
                <span className="flex items-center text-green-600">
                  <CheckCircleIcon className="h-4 w-4 mr-1" />
                  Voice & vision analysis
                </span>
                <span className="flex items-center text-green-600">
                  <CheckCircleIcon className="h-4 w-4 mr-1" />
                  Automated assessments
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}