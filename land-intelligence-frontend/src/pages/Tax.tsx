import React, { useState, useEffect } from 'react';
import { PageContainer } from '@/components/layout/PageContainer';
import { DollarSign } from 'lucide-react';
import { reportService } from '@/services/reportService';
import type { TaxRecordSummary, TaxReportSummary } from '@/services/reportService';

export default function Tax() {
  const [taxReport, setTaxReport] = useState<TaxReportSummary | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [parcelId, setParcelId] = useState('');

  const loadTaxReport = async () => {
    if (!parcelId) return;
    
    setIsLoading(true);
    try {
      const response = await reportService.getTaxReport(parcelId);
      if (response.success && response.data) {
        setTaxReport(response.data);
      }
    } catch (error) {
      console.error('Failed to load tax report', error);
    } finally {
      setIsLoading(false);
    }
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
          <p className="text-slate-400 mt-1">Integrated calculations for diocese land tax rates, exemptions, and payment histories.</p>
        </div>
        <div className="flex items-center gap-2">
          <input
            type="text"
            placeholder="Enter parcel ID..."
            value={parcelId}
            onChange={(e) => setParcelId(e.target.value)}
            className="px-3 py-2 bg-slate-900/50 border border-slate-700 rounded-md text-sm text-white placeholder-slate-500"
          />
          <button 
            onClick={loadTaxReport}
            disabled={!parcelId || isLoading}
            className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
          >
            {isLoading ? 'Loading...' : 'Calculate'}
          </button>
        </div>
      </div>

      {taxReport && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-lg shadow">
              <p className="text-sm text-gray-500">Total Outstanding</p>
              <p className="text-2xl font-bold text-gray-900">
                ${taxReport.total_outstanding.toLocaleString()}
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <p className="text-sm text-gray-500">Overdue Amount</p>
              <p className="text-2xl font-bold text-red-600">
                ${taxReport.overdue_amount.toLocaleString()}
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <p className="text-sm text-gray-500">Upcoming</p>
              <p className="text-2xl font-bold text-yellow-600">
                ${taxReport.upcoming_amount.toLocaleString()}
              </p>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Tax Records</h3>
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Year</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Assessed</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Tax</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Total</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {taxReport.records.map((record) => (
                  <tr key={record.id}>
                    <td className="px-4 py-2 text-sm text-gray-900">{record.assessment_year}</td>
                    <td className="px-4 py-2 text-sm text-gray-500">
                      ${record.assessed_value.toLocaleString()}
                    </td>
                    <td className="px-4 py-2 text-sm text-gray-500">
                      ${record.base_tax_amount.toLocaleString()}
                    </td>
                    <td className="px-4 py-2 text-sm font-medium text-gray-900">
                      ${record.total_amount.toLocaleString()}
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