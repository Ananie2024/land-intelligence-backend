import React from 'react';
import { PageContainer } from '@/components/layout/PageContainer';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Settings as SettingsIcon, Bell, Key, Globe } from 'lucide-react';

export default function Settings() {
  return (
    <PageContainer
      title="System Settings"
      subtitle="Modify app configuration parameters, theme preferences, and access keys."
    >
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Navigation panel */}
        <div className="space-y-2">
          <button className="flex items-center gap-3 w-full text-left px-4 py-2.5 rounded-lg bg-slate-900 border border-slate-800 text-white font-bold text-sm">
            <SettingsIcon className="w-4 h-4 text-primary-400" />
            General Config
          </button>
          <button className="flex items-center gap-3 w-full text-left px-4 py-2.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 font-semibold text-sm">
            <Key className="w-4 h-4" />
            Security & Keys
          </button>
          <button className="flex items-center gap-3 w-full text-left px-4 py-2.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 font-semibold text-sm">
            <Bell className="w-4 h-4" />
            Notification Alarms
          </button>
          <button className="flex items-center gap-3 w-full text-left px-4 py-2.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 font-semibold text-sm">
            <Globe className="w-4 h-4" />
            Language & Region
          </button>
        </div>

        {/* Setting options content */}
        <div className="md:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>System Information</CardTitle>
              <CardDescription>Archdiocese of Kigali land registrar connection configs</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 text-sm text-slate-300">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1">
                  <span className="text-xs font-bold text-slate-500 uppercase block">Application Host</span>
                  <span className="text-white font-semibold">http://localhost:5173</span>
                </div>
                <div className="space-y-1">
                  <span className="text-xs font-bold text-slate-500 uppercase block">API Gateway Connect</span>
                  <span className="text-white font-semibold">http://localhost:8000/api/v1</span>
                </div>
                <div className="space-y-1">
                  <span className="text-xs font-bold text-slate-500 uppercase block">Debug Mode status</span>
                  <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-success bg-success/10 border border-success/20 px-2 py-0.5 rounded-full mt-1">
                    Enabled
                  </span>
                </div>
                <div className="space-y-1">
                  <span className="text-xs font-bold text-slate-500 uppercase block">Database Backend</span>
                  <span className="text-white font-semibold">PostgreSQL (SQLAlchemy Async)</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </PageContainer>
  );
}
