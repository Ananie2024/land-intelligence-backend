// Reports Page
// Land Intelligence System

import React, { useState } from 'react';
import { PageContainer } from '@/components/layout/PageContainer';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { FileDown, FileText } from 'lucide-react';
import { reportService, ExportFormat } from '@/services/reportService';
import { toast } from 'react-hot-toast';

export default function ReportsPage() {
  const [isExporting, setIsExporting] = useState(false);
  const [exportType, setExportType] = useState<'dashboard' | 'parcels' | null>(null);

  const downloadBlob = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const handleExport = async (type: 'dashboard' | 'parcels', format: ExportFormat) => {
    setIsExporting(true);
    setExportType(type);
    
    try {
      let blob: Blob;
      let filename: string;

      switch (type) {
        case 'dashboard':
          blob = await reportService.exportDashboardReport(format);
          filename = `dashboard-report.${format}`;
          break;
        case 'parcels':
          blob = await reportService.exportParcelsReport(format);
          filename = `parcels-report.${format}`;
          break;
        default:
          return;
      }

      downloadBlob(blob, filename);
      toast.success(`Report downloaded: ${filename}`);
    } catch (error) {
      console.error('Export failed:', error);
      toast.error('Failed to generate report');
    } finally {
      setIsExporting(false);
      setExportType(null);
    }
  };

  return (
    <PageContainer
      title="Reports"
      subtitle="Generate PDF and Excel reports for system data."
    >
      <div className="space-y-6">
        {/* Dashboard Statistics Report */}
        <Card>
          <CardHeader>
            <CardTitle>Dashboard Statistics</CardTitle>
            <CardDescription>
              Export comprehensive system statistics including parishes, parcels, users, and documents.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-3">
              <Button
                onClick={() => handleExport('dashboard', 'pdf')}
                disabled={isExporting}
                leftIcon={<FileText className="w-4 h-4" />}
              >
                {isExporting && exportType === 'dashboard' ? 'Generating...' : 'Export PDF'}
              </Button>
              <Button
                variant="secondary"
                onClick={() => handleExport('dashboard', 'excel')}
                disabled={isExporting}
                leftIcon={<FileDown className="w-4 h-4" />}
              >
                {isExporting && exportType === 'dashboard' ? 'Generating...' : 'Export Excel'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Parcels Report */}
        <Card>
          <CardHeader>
            <CardTitle>Land Parcels Report</CardTitle>
            <CardDescription>
              Export all land parcels data with area, valuation, and ownership details.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-3">
              <Button
                onClick={() => handleExport('parcels', 'pdf')}
                disabled={isExporting}
                leftIcon={<FileText className="w-4 h-4" />}
              >
                {isExporting && exportType === 'parcels' ? 'Generating...' : 'Export PDF'}
              </Button>
              <Button
                variant="secondary"
                onClick={() => handleExport('parcels', 'excel')}
                disabled={isExporting}
                leftIcon={<FileDown className="w-4 h-4" />}
              >
                {isExporting && exportType === 'parcels' ? 'Generating...' : 'Export Excel'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Tax Report Note - updated to reference working export */}
        <Card>
          <CardHeader>
            <CardTitle>Tax Assessment Reports</CardTitle>
            <CardDescription>
              Generate tax reports for individual parcels from the Tax page.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-400">
              Go to the <strong>Tax</strong> section, enter a parcel UPI, and use the <strong>Export PDF</strong> or <strong>Export Excel</strong> buttons to download its tax assessment report. You can also create new assessments and record payments directly from that page.
            </p>
          </CardContent>
        </Card>
      </div>
    </PageContainer>
  );
}