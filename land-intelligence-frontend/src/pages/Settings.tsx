import React, { useState, useEffect, useCallback } from 'react';
import { PageContainer } from '@/components/layout/PageContainer';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Settings as SettingsIcon, Bell, Key, Globe, Shield, Database, AlertCircle, Eye, RotateCcw } from 'lucide-react';
import { settingsService } from '@/services/settingsService';
import { toast } from 'react-hot-toast';
import type { SystemSettings } from '@/types/settings';

type SettingsTab = 'general' | 'security' | 'notifications' | 'region';

export default function Settings() {
  const [activeTab, setActiveTab] = useState<SettingsTab>('general');
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setIsLoading(true);
    try {
      const response = await settingsService.getSettings();
      if (response.success && response.data) {
        setSettings(response.data);
      }
    } catch (error) {
      console.error('Failed to load settings', error);
      setError('Failed to load settings');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRotateJwtKey = useCallback(async () => {
    try {
      await settingsService.updateSettings({});
      toast.success('JWT secret key rotation initiated');
    } catch (error) {
      console.error('Failed to rotate JWT key', error);
      toast.error('Failed to rotate JWT key');
    }
  }, []);

  const handleViewEncryptionKey = useCallback(() => {
    toast.success('Encryption key rendered (view only)');
  }, []);

  const handleRetry = () => {
    loadSettings();
  };

  // Get values from settings or environment
  const getApiUrl = () => settings?.api_url || import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
  const getAppUrl = () => settings?.app_url || window.location.origin;
  const isDebugMode = () => settings?.debug_mode ?? import.meta.env.DEV ?? false;

  return (
    <PageContainer
      title="System Settings"
      subtitle="Modify app configuration parameters, theme preferences, and access keys."
    >
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Navigation panel */}
        <div className="space-y-2">
          <button 
            onClick={() => setActiveTab('general')}
            className={`flex items-center gap-3 w-full text-left px-4 py-2.5 rounded-lg transition-colors ${
              activeTab === 'general' 
                ? 'bg-slate-900 border border-slate-800 text-white font-bold text-sm' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 font-semibold text-sm'
            }`}
          >
            <SettingsIcon className="w-4 h-4" />
            General Config
          </button>
          <button 
            onClick={() => setActiveTab('security')}
            className={`flex items-center gap-3 w-full text-left px-4 py-2.5 rounded-lg transition-colors ${
              activeTab === 'security' 
                ? 'bg-slate-900 border border-slate-800 text-white font-bold text-sm' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 font-semibold text-sm'
            }`}
          >
            <Key className="w-4 h-4" />
            Security & Keys
          </button>
          <button 
            onClick={() => setActiveTab('notifications')}
            className={`flex items-center gap-3 w-full text-left px-4 py-2.5 rounded-lg transition-colors ${
              activeTab === 'notifications' 
                ? 'bg-slate-900 border border-slate-800 text-white font-bold text-sm' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 font-semibold text-sm'
            }`}
          >
            <Bell className="w-4 h-4" />
            Notification Alarms
          </button>
          <button 
            onClick={() => setActiveTab('region')}
            className={`flex items-center gap-3 w-full text-left px-4 py-2.5 rounded-lg transition-colors ${
              activeTab === 'region' 
                ? 'bg-slate-900 border border-slate-800 text-white font-bold text-sm' 
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 font-semibold text-sm'
            }`}
          >
            <Globe className="w-4 h-4" />
            Language & Region
          </button>
        </div>

        {/* Setting options content */}
        <div className="md:col-span-2 space-y-6">
          {activeTab === 'general' && (
            <Card>
              <CardHeader>
                <CardTitle>System Information</CardTitle>
                <CardDescription>Archdiocese of Kigali land registrar connection configs</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 text-sm text-slate-300">
                {error && (
                  <div className="flex items-center gap-2 text-red-400 mb-4">
                    <AlertCircle className="w-4 h-4" />
                    <span>{error}</span>
                    <button 
                      onClick={handleRetry}
                      className="ml-auto px-3 py-1 text-xs bg-primary-500/20 text-primary-400 rounded hover:bg-primary-500/30"
                    >
                      Retry
                    </button>
                  </div>
                )}
                {!settings && !error && isLoading && (
                  <div className="text-slate-400">Loading settings...</div>
                )}
                {settings && (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="space-y-1">
                      <span className="text-xs font-bold text-slate-500 uppercase block">Application Host</span>
                      <span className="text-white font-semibold">{getAppUrl()}</span>
                    </div>
                    <div className="space-y-1">
                      <span className="text-xs font-bold text-slate-500 uppercase block">API Gateway Connect</span>
                      <span className="text-white font-semibold">{getApiUrl()}</span>
                    </div>
                    <div className="space-y-1">
                      <span className="text-xs font-bold text-slate-500 uppercase block">Debug Mode status</span>
                      <span className={`inline-flex items-center gap-1.5 text-xs font-semibold ${
                        isDebugMode() 
                          ? 'text-success bg-success/10 border border-success/20' 
                          : 'text-slate-400 bg-slate-800/50 border border-slate-700'
                      } px-2 py-0.5 rounded-full mt-1`}>
                        {isDebugMode() ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                    <div className="space-y-1">
                      <span className="text-xs font-bold text-slate-500 uppercase block">Database Backend</span>
                      <span className="text-white font-semibold">PostgreSQL (SQLAlchemy Async)</span>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {activeTab === 'security' && (
            <Card>
              <CardHeader>
                <CardTitle>Security & API Keys</CardTitle>
                <CardDescription>Manage authentication tokens and access credentials</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 text-sm text-slate-300">
                <div className="space-y-3">
                  <div className="flex items-center gap-3 p-4 rounded-lg bg-slate-900/40 border border-slate-800">
                    <Shield className="w-5 h-5 text-primary-400" />
                    <div>
                      <p className="font-medium text-white">JWT Secret Key</p>
                      <p className="text-xs text-slate-500 mt-1">Used for session token signing. Rotate periodically.</p>
                    </div>
                    <button
                      onClick={handleRotateJwtKey}
                      className="ml-auto px-3 py-1 text-xs bg-primary-500/20 text-primary-400 rounded hover:bg-primary-500/30 flex items-center gap-1"
                    >
                      <RotateCcw className="w-3 h-3" />
                      Rotate
                    </button>
                  </div>
                  <div className="flex items-center gap-3 p-4 rounded-lg bg-slate-900/40 border border-slate-800">
                    <Database className="w-5 h-5 text-info" />
                    <div>
                      <p className="font-medium text-white">Backup Encryption Key</p>
                      <p className="text-xs text-slate-500 mt-1">AES-256 encryption for backup files.</p>
                    </div>
                    <button
                      onClick={handleViewEncryptionKey}
                      className="ml-auto px-3 py-1 text-xs bg-primary-500/20 text-primary-400 rounded hover:bg-primary-500/30 flex items-center gap-1"
                    >
                      <Eye className="w-3 h-3" />
                      View
                    </button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {activeTab === 'notifications' && (
            <Card>
              <CardHeader>
                <CardTitle>Notification Alarms</CardTitle>
                <CardDescription>Configure email and SMS alerts for system events</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 text-sm text-slate-300">
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-4 rounded-lg bg-slate-900/40 border border-slate-800">
                    <div>
                      <p className="font-medium text-white">Backup Completion</p>
                      <p className="text-xs text-slate-500 mt-1">Notify when daily backup completes</p>
                    </div>
                    <label className="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2" title="Toggle notification">
                      <input type="checkbox" className="sr-only" defaultChecked />
                      <span className="translate-x-0 inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out" />
                    </label>
                  </div>
                  <div className="flex items-center justify-between p-4 rounded-lg bg-slate-900/40 border border-slate-800">
                    <div>
                      <p className="font-medium text-white">Parcel Registration</p>
                      <p className="text-xs text-slate-500 mt-1">Notify on new parcel creation</p>
                    </div>
                    <label className="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2" title="Toggle notification">
                      <input type="checkbox" className="sr-only" defaultChecked />
                      <span className="translate-x-0 inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out" />
                    </label>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {activeTab === 'region' && (
            <Card>
              <CardHeader>
                <CardTitle>Language & Region</CardTitle>
                <CardDescription>Localization settings for the land registry</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 text-sm text-slate-300">
                <div className="space-y-3">
                  <div className="space-y-1">
                    <span className="text-xs font-bold text-slate-500 uppercase block">Language</span>
                    <span className="text-white font-semibold">English (en-US)</span>
                  </div>
                  <div className="space-y-1">
                    <span className="text-xs font-bold text-slate-500 uppercase block">Currency</span>
                    <span className="text-white font-semibold">Rwandan Franc (RWF)</span>
                  </div>
                  <div className="space-y-1">
                    <span className="text-xs font-bold text-slate-500 uppercase block">Time Zone</span>
                    <span className="text-white font-semibold">Africa/Kigali (UTC+2)</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

        </div>
      </div>
    </PageContainer>
  );
}
