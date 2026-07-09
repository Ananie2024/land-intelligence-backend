// Tax List Page
// Land Intelligence System

import { useState, useEffect } from 'react';
import { reportService } from '@/services/reportService';
import type { TaxRecordSummary } from '@/services/reportService';
import { TaxTable } from '../components/TaxTable';
import { TaxSummaryCard } from '../components/TaxSummaryCard';

export const TaxListPage: React.FC = () => {
  const [records, setRecords] = useState<TaxRecordSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [parcelId, setParcelId] = useState('');

  const loadTaxRecords = async () => {
    if (!parcelId) return;
    
    setIsLoading(true);
    try {
      const response = await reportService.getTaxHistoryReport(parcelId);
      if (response.success && response.data) {
        setRecords(response.data);
      }
    } catch (error) {
      console.error('Failed to load tax records', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = () => {
    loadTaxRecords();
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Tax Records</h1>
        <div className="flex items-center gap-2">
          <input
            type="text"
            placeholder="Enter parcel ID..."
            value={parcelId}
            onChange={(e) => setParcelId(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          />
          <button 
            onClick={handleSearch}
            className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          >
            Search
          </button>
        </div>
      </div>
      
      <TaxSummaryCard 
        summary={{
          total_assessed_value: 0,
          total_tax_amount: 0,
          total_penalties: 0,
          paid_amount: 0,
          pending_amount: 0,
          overdue_amount: 0,
        }}
      />
      
      <div className="mt-6">
        {isLoading ? (
          <div className="text-center py-12">Loading tax records...</div>
        ) : (
          <TaxTable 
            records={records}
            onView={(record) => console.log('View tax record:', record)}
          />
        )}
      </div>
    </div>
  );
};

export default TaxListPage;