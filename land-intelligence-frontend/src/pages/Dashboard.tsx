import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { PageContainer } from '@/components/layout/PageContainer';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Map, Users, FileText, Database, CheckCircle2, Loader2, ArrowRight, LandPlot, Scan, Receipt } from 'lucide-react';
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
        } else {
          toast.error('Failed to load dashboard statistics');
        }
      } catch (error) {
        console.error('Failed to load dashboard stats', error);
        toast.error('Failed to load dashboard statistics');
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
      color: 'text-primary-400 bg-primary-500/10',
      gradient: 'from-primary-500 to-primary-600'
    },
    { 
      title: 'Registrars', 
      value: stats.users.client_count.toLocaleString(), 
      desc: `${stats.users.total_users} total users`, 
      icon: Users, 
      color: 'text-gold-400 bg-gold-500/10',
      gradient: 'from-gold-500 to-gold-600'
    },
    { 
      title: 'Documents', 
      value: stats.documents.total_documents.toLocaleString(), 
      desc: formatFileSize(stats.documents.total_size_bytes), 
      icon: FileText, 
      color: 'text-info bg-info/10',
      gradient: 'from-info to-primary-500'
    },
    { 
      title: 'Parishes', 
      value: stats.parishes.total_parishes.toLocaleString(), 
      desc: `${stats.parishes.total_parcels} total parcels`, 
      icon: Database, 
      color: 'text-success bg-success/10',
      gradient: 'from-success to-gold-600'
    },
  ] : [];

  const quickActions = [
    { 
      name: 'Register Parcel', 
      path: '/parcels', 
      icon: LandPlot, 
      color: 'from-primary-500 to-primary-600',
      desc: 'Add new land parcel registration'
    },
    { 
      name: 'Scan Documents', 
      path: '/documents', 
      icon: Scan, 
      color: 'from-gold-500 to-gold-600',
      desc: 'Upload and archive deeds'
    },
    { 
      name: 'Calculate Tax', 
      path: '/tax', 
      icon: Receipt, 
      color: 'from-burgundy-500 to-burgundy-600',
      desc: 'Process land tax calculations'
    },
  ];

  return (
    <PageContainer
      title=""
      subtitle=""
      className="p-6 md:p-8 lg:p-10"
    >
      <div className="space-y-10">
        {/* Hero Section with Large Logo */}
        <section className="relative overflow-hidden rounded-2xl border border-slate-800/60 bg-gradient-to-br from-slate-900/80 via-slate-950/90 to-primary-950/50">
          {/* Background decorative elements */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute top-10 right-10 w-32 h-32 bg-gold-500/10 rounded-full blur-2xl pointer-events-none" />
          <div className="absolute bottom-10 left-10 w-24 h-24 bg-burgundy-500/10 rounded-full blur-xl pointer-events-none" />
          
          <div className="relative z-10 p-8 md:p-12 lg:p-16 flex flex-col lg:flex-row items-center gap-8 lg:gap-12">
            {/* Large Logo Display */}
            <div className="flex-shrink-0">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-primary-500 via-gold-500 to-burgundy-500 rounded-full blur-xl opacity-30 animate-pulse-glow" />
                <img 
                  src="/archidiocese-logo.png" 
                  alt="Archdiocese of Kigali" 
                  className="relative h-32 w-auto md:h-40 lg:h-48 object-contain drop-shadow-2xl"
                />
              </div>
            </div>
            
            {/* Hero Text */}
            <div className="flex-1 text-center lg:text-left">
              <h1 className="text-3xl md:text-4xl lg:text-5xl font-extrabold text-white tracking-tight leading-tight mb-4">
                <span className="bg-gradient-to-r from-primary-400 via-gold-400 to-burgundy-400 bg-clip-text text-transparent">
                  Digital Land Registry
                </span>
                <br />
                <span className="text-slate-100">Archdiocese of Kigali</span>
              </h1>
              <p className="text-lg md:text-xl text-slate-400 font-medium max-w-2xl leading-relaxed">
                Secure and comprehensive land management system for parishes and administrative oversight. 
                Track parcels, manage documents, and calculate taxes with precision.
              </p>
              <div className="mt-6 flex flex-wrap gap-3 justify-center lg:justify-start">
                <a href="/parcels">
                  <Button variant="primary" size="lg" rightIcon={<ArrowRight className="w-4 h-4" />}>
                    View Parcels
                  </Button>
                </a>
                <a href="/documents">
                  <Button variant="glass" size="lg">
                    Browse Documents
                  </Button>
                </a>
              </div>
            </div>
          </div>
        </section>

        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-center py-12">
            <Loader2 className="w-8 h-8 text-primary-400 animate-spin" />
          </div>
        )}

        {/* Stats Grid */}
        {!isLoading && statCards.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {statCards.map((card, idx) => {
              const Icon = card.icon;
              return (
                <Card key={idx} variant="interactive" className="group">
                  <CardHeader className="flex flex-row items-center justify-between pb-3">
                    <CardTitle className="text-slate-400 text-xs font-bold uppercase tracking-wider group-hover:text-white transition-colors">
                      {card.title}
                    </CardTitle>
                    <div className={`p-2.5 rounded-xl ${card.color} group-hover:scale-110 transition-transform`}>
                      <Icon className="w-5 h-5" />
                    </div>
                  </CardHeader>
                  <CardContent className="pt-1">
                    <p className="text-3xl md:text-4xl font-extrabold text-white tracking-tight leading-none mb-1">
                      {card.value}
                    </p>
                    <CardDescription className="text-xs">
                      {card.desc}
                    </CardDescription>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}

        {/* Quick Actions Section */}
        <div>
          <h2 className="text-xl font-bold text-white mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {quickActions.map((action, idx) => {
              const Icon = action.icon;
              return (
                <a key={idx} href={action.path}>
                  <Card variant="interactive" className="h-full group cursor-pointer">
                    <CardContent className="flex items-center gap-4 p-5">
                      <div className={`p-3 rounded-xl bg-gradient-to-br ${action.color} shadow-lg group-hover:scale-110 transition-transform`}>
                        <Icon className="w-6 h-6 text-white" />
                      </div>
                      <div className="flex-1">
                        <p className="font-bold text-white text-sm mb-0.5 group-hover:text-gold-300 transition-colors">{action.name}</p>
                        <p className="text-xs text-slate-400">{action.desc}</p>
                      </div>
                      <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-gold-400 group-hover:translate-x-1 transition-all" />
                    </CardContent>
                  </Card>
                </a>
              );
            })}
          </div>
        </div>

        {/* Informational Alerts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="overflow-hidden">
            <CardHeader>
              <CardTitle>System Log Status</CardTitle>
              <CardDescription>Recent service log synchronizations</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3 p-3.5 rounded-lg bg-slate-950/40 border border-slate-900 hover:bg-slate-950/60 transition-colors">
                <div className="p-1.5 rounded-full bg-success/20">
                  <CheckCircle2 className="w-4 h-4 text-success flex-shrink-0" />
                </div>
                <div className="text-xs">
                  <p className="text-white font-semibold">Automatic Database Backup Completed</p>
                  <p className="text-slate-500 mt-0.5">Database snapshot synced with GCS cold store bucket.</p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3.5 rounded-lg bg-slate-950/40 border border-slate-900 hover:bg-slate-950/60 transition-colors">
                <div className="p-1.5 rounded-full bg-primary-500/20">
                  <CheckCircle2 className="w-4 h-4 text-primary-400 flex-shrink-0" />
                </div>
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