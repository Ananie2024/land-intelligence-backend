import React, { useState, useEffect } from 'react';
import { PageContainer } from '@/components/layout/PageContainer';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Map, Users, FileText, Database, CheckCircle2, Loader2 } from 'lucide-react';
import { dashboardService } from '@/services/dashboardService';
import type { SystemStats } from '@/types/dashboard';

export default function Dashboard() {
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const response = await dashboardService.getSystemStats();
        if (response.success && response.data) {
          setStats(response.data);
        }
      } catch (error) {
        console.error('Failed to load dashboard stats', error);
      } finally {
        setIsLoading(false);
      }
    };
    loadStats();
  }, []);

  const formatFileSize = (bytes: number): string => {
    const gb = bytes / (1024 * 1024 * 1024);
    return `${gb.toFixed(1)} GB`;
  };

  const formatCurrency = (value: number): string => {
    return `RWF ${value.toLocaleString()}`;
  };

  const statCards = stats ? [
    { 
      title: 'Total Parcels', 
      value: stats.parcels.total_parcels.toLocaleString(), 
      desc: `${formatCurrency(stats.parcels.total_valuation)} valuation`, 
      icon: Map, 
      color: 'text-primary-400 bg-primary-500/10' 
    },
    { 
      title: 'Registrars', 
      value: stats.users.client_count.toLocaleString(), 
      desc: `${stats.users.total_users} total users`, 
      icon: Users, 
      color: 'text-accent-400 bg-accent-500/10' 
    },
    { 
      title: 'Documents', 
      value: stats.documents.total_documents.toLocaleString(), 
      desc: formatFileSize(stats.documents.total_size_bytes), 
      icon: FileText, 
      color: 'text-info bg-info/10' 
    },
    { 
      title: 'Parishes', 
      value: stats.parishes.total_parishes.toLocaleString(), 
      desc: `${stats.parishes.total_parcels} total parcels`, 
      icon: Database, 
      color: 'text-success bg-success/10' 
    },
  ] : [];

  return (
    <PageContainer
      title="System Dashboard"
      subtitle="Digital Land Registry System overview for the Archdiocese of Kigali."
    >
      <div className="space-y-8">
        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-center py-12">
            <Loader2 className="w-8 h-8 text-primary-400 animate-spin" />
          </div>
        )}

        {/* Stats Grid */}
        {!isLoading && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {statCards.map((card, idx) => {
              const Icon = card.icon;
              return (
                <Card key={idx} variant="interactive">
                  <CardHeader className="flex flex-row items-center justify-between pb-2">
                    <CardTitle className="text-slate-400 text-xs font-bold uppercase tracking-wider">
                      {card.title}
                    </CardTitle>
                    <div className={`p-2 rounded-lg ${card.color}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                  </CardHeader>
                  <CardContent className="pt-2">
                    <p className="text-3xl font-extrabold text-white tracking-tight leading-none">
                      {card.value}
                    </p>
                    <CardDescription className="mt-2 text-xs">
                      {card.desc}
                    </CardDescription>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
        {!isLoading && statCards.length === 0 && (
          <div className="text-center py-12 text-slate-400">No statistics available</div>
        )}

        {/* Informational Alerts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>System Log Status</CardTitle>
              <CardDescription>Recent service log synchronizations</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3 p-3.5 rounded-lg bg-slate-950/40 border border-slate-900">
                <CheckCircle2 className="w-4 h-4 text-success flex-shrink-0" />
                <div className="text-xs">
                  <p className="text-white font-semibold">Automatic Database Backup Completed</p>
                  <p className="text-slate-500 mt-0.5">Database snapshot synced with GCS cold store bucket.</p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3.5 rounded-lg bg-slate-950/40 border border-slate-900">
                <CheckCircle2 className="w-4 h-4 text-success flex-shrink-0" />
                <div className="text-xs">
                  <p className="text-white font-semibold">GIS Layer Loaded</p>
                  <p className="text-slate-500 mt-0.5">Spatial boundary overlay successfully refreshed.</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Archdiocese Administration</CardTitle>
              <CardDescription>System access permissions and roles</CardDescription>
            </CardHeader>
            <CardContent className="text-xs text-slate-400 leading-relaxed space-y-3">
              <p>
                Welcome to the digital registration panel. This interface provides integrated monitoring, location tracking, and tax calculation utilities.
              </p>
              <p className="font-semibold text-slate-300">Available Actions:</p>
              <ul className="list-disc pl-4 space-y-1 text-slate-400">
                <li>Register new parcels under Parish scopes.</li>
                <li>Archive scanned deeds and land tenure forms.</li>
                <li>Calculate municipal and diocese land tax rates.</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </PageContainer>
  );
}
