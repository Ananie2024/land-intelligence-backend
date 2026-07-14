import React, { useState, useEffect, useCallback } from 'react';
import { PageContainer } from '@/components/layout/PageContainer';
import { DollarSign } from 'lucide-react';
import { reportService } from '@/services/reportService';
import type { TaxRecordSummary, TaxReportSummary } from '@/services/reportService';
import { toast } from 'react-hot-toast';

export default function Tax() {
  const [taxReport, setTaxReport] = useState<TaxReportSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [parcelId, setParcelId] = useState('');

  const loadTaxReport = useCallback(async () => {
    if (!parcelId) return;
    
    setIsLoading(true);
    setError(null);
    try {
      const response = await reportService.getTaxReport(parcelId);
      if (response.success && response.data) {
        setTaxReport(response.data);
      } else {
        setError(response.message || 'Failed to load tax report');
      }
    } catch (error) {
      console.error('Failed to load tax report', error);
      setError('Failed to load tax report');
      toast.error('Failed to load tax report');
    } finally {
      setIsLoading(false);
    }
  }, [parcelId]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && parcelId) {
      loadTaxReport();
    }
  };

  const handleRetry = () => {
    loadTaxReport();
  };

  return (
    <PageContainer
      title="Tax Calculations"
      subtitle="Automated land tax computations and diocese tax assessment registries."
    >
      <div className="flex items-center gap-3 p-6 rounded-xl border border-slate-800/80 bg-slate-900/30 mb-6">
        <DollarSign className="w-6 h-6 text-success" />
        <div className="text-sm flex-1">
          <p className="text-white font-bold">Tax Assessment</p>
          <p className="text-slate-400 mt-0.5">Integrated calculations for diocese land tax rates, exemptions, and payment histories.</p>
        </div>
        <div className="flex items-center gap-2">
          <input
            type="text"
            placeholder="Enter UPI (e.g., 1/02/02/03/1390)..."
            value={parcelId}
            onChange={(e) => setParcelId(e.target.value)}
            onKeyDown={handleKeyDown}
            className="px-3 py-2 bg-slate-900/50 border border-slate-700 rounded-md text-sm text-white placeholder-slate-500"
          />
          <button 
            onClick={loadTaxReport}
            disabled={!parcelId || isLoading}
            className="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 disabled:opacity-50 transition-colors"
          >
            {isLoading ? 'Loading...' : 'Calculate'}
          </button>
        </div>
      </div>

      {error && (
        <div className="text-center py-8">
          <p className="text-red-400 mb-4">{error}</p>
          <button 
            onClick={handleRetry}
            className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
          >
            Try Again
          </button>
        </div>
      )}

      {taxReport && !error && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-slate-900/40 p-4 rounded-lg border border-slate-800">
              <p className="text-sm text-slate-400">Total Outstanding</p>
              <p className="text-2xl font-bold text-white">
                RWF {taxReport.total_outstanding.toLocaleString()}
              </p>
            </div>
            <div className="bg-slate-900/40 p-4 rounded-lg border border-slate-800">
              <p className="text-sm text-slate-400">Overdue Amount</p>
              <p className="text-2xl font-bold text-red-400">
                RWF {taxReport.overdue_amount.toLocaleString()}
              </p>
            </div>
            <div className="bg-slate-900/40 p-4 rounded-lg border border-slate-800">
              <p className="text-sm text-slate-400">Upcoming</p>
              <p className="text-2xl font-bold text-yellow-400">
                RWF {taxReport.upcoming_amount.toLocaleString()}
              </p>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-medium text-white mb-2">Tax Records</h3>
            <table className="min-w-full divide-y divide-slate-800">
              <thead className="bg-slate-900/60">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-slate-400">Year</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-slate-400">Assessed</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-slate-400">Tax</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-slate-400">Total</th>
                </tr>
              </thead>
              <tbody className="bg-slate-900/40 divide-y divide-slate-800">
                {taxReport.records.map((record) => (
                  <tr key={record.id} className="hover:bg-slate-900/60 transition-colors">
                    <td className="px-4 py-2 text-sm text-slate-200">{record.assessment_year}</td>
                    <td className="px-4 py-2 text-sm text-slate-400">
                      RWF {record.assessed_value.toLocaleString()}
                    </td>
                    <td className="px-4 py-2 text-sm text-slate-400">
                      RWF {record.base_tax_amount.toLocaleString()}
                    </td>
                    <td className="px-4 py-2 text-sm font-medium text-slate-200">
                      RWF {record.total_amount.toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </PageContainer>
  );
}
