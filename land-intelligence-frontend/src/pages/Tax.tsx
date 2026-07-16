import React, { useState, useCallback } from 'react';
import { PageContainer } from '@/components/layout/PageContainer';
import { DollarSign, FileDown, Plus, CreditCard, Search, MapPin } from 'lucide-react';
import { reportService, ExportFormat, TaxReportSummary } from '@/services/reportService';
import { taxService } from '@/services/taxService';
import { useResourceQuery } from '@/hooks/useResourceList';
import { toast } from 'react-hot-toast';
import { Pagination } from '@/components/ui/Pagination';

export default function Tax() {
  const [error, setError] = useState<string | null>(null);
  const [parcelId, setParcelId] = useState('');
  const [isExporting, setIsExporting] = useState(false);
  const [isAssessing, setIsAssessing] = useState(false);
  const [isPaying, setIsPaying] = useState(false);
  const [assessmentYear, setAssessmentYear] = useState(new Date().getFullYear().toString());
  const [paymentAmount, setPaymentAmount] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('bank_transfer');
  const [paymentReference, setPaymentReference] = useState('');
  const [showPaymentForm, setShowPaymentForm] = useState(false);

  // Parcel search state
  const [parcelSearch, setParcelSearch] = useState('');
  const [parcelSuggestions, setParcelSuggestions] = useState<{ id: string; upi: string }[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isSearchingParcels, setIsSearchingParcels] = useState(false);

  // Tax records pagination state
  const [recordsPage, setRecordsPage] = useState(1);
  const [recordsPageSize, setRecordsPageSize] = useState(10);

  // Load tax report reactively based on selected parcelId
  const { data: taxReport, isLoading, refetch } = useResourceQuery<TaxReportSummary>(
    ['tax-report', parcelId],
    () => reportService.getTaxReport(parcelId),
    { enabled: !!parcelId }
  );

  // Search parcels by UPI or number
  const searchParcels = useCallback(async (query: string) => {
    if (!query || query.length < 2) {
      setParcelSuggestions([]);
      setShowSuggestions(false);
      return;
    }
    setIsSearchingParcels(true);
    try {
      const response = await taxService.searchParcels(query, 10);
      if (response.success && response.data) {
        setParcelSuggestions(response.data.items);
        setShowSuggestions(true);
      }
    } catch {
      setParcelSuggestions([]);
    } finally {
      setIsSearchingParcels(false);
    }
  }, []);

  const handleParcelSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setParcelSearch(value);
    searchParcels(value);
  };

  const selectParcel = (id: string, upi: string) => {
    setParcelId(upi);
    setParcelSearch(upi);
    setShowSuggestions(false);
  };

  const handleExport = useCallback(async (format: ExportFormat) => {
    if (!parcelId) {
      toast.error('Enter a UPI first');
      return;
    }
    setIsExporting(true);
    try {
      const blob = await reportService.exportTaxReport(parcelId, format);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `tax-report-${parcelId}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success(`Tax report exported as ${format.toUpperCase()}`);
    } catch (err) {
      console.error('Failed to export tax report', err);
      toast.error('Failed to export tax report');
    } finally {
      setIsExporting(false);
    }
  }, [parcelId]);

  const handleAssess = useCallback(async () => {
    if (!parcelId) {
      toast.error('Enter a UPI first');
      return;
    }
    setIsAssessing(true);
    try {
      const response = await taxService.createAssessment({
        parcel_upi: parcelId,
        assessment_year: assessmentYear,
        land_use_category_id: null,
        include_penalties: true,
      });
      if (response.success) {
        toast.success(`Assessment for ${parcelId} (${assessmentYear}) created`);
        refetch();
      } else {
        toast.error(response.message || 'Failed to create assessment');
      }
    } catch (err) {
      console.error('Failed to create tax assessment', err);
      toast.error('Failed to create tax assessment');
    } finally {
      setIsAssessing(false);
    }
  }, [parcelId, assessmentYear, refetch]);

  const handleRecordPayment = useCallback(async () => {
    if (!taxReport || taxReport.records.length === 0) {
      toast.error('No tax records found for this parcel');
      return;
    }
    const amount = parseFloat(paymentAmount);
    if (isNaN(amount) || amount <= 0) {
      toast.error('Enter a valid payment amount');
      return;
    }
    setIsPaying(true);
    try {
      const response = await taxService.recordPayment({
        tax_record_id: taxReport.records[0].id,
        payment_amount: amount,
        payment_method: paymentMethod,
        payment_reference: paymentReference || undefined,
        payment_date: new Date().toISOString().split('T')[0],
      });
      if (response.success) {
        toast.success(`Payment of RWF ${amount.toLocaleString()} recorded`);
        setShowPaymentForm(false);
        setPaymentAmount('');
        setPaymentReference('');
        refetch();
      } else {
        toast.error(response.message || 'Failed to record payment');
      }
    } catch (err) {
      console.error('Failed to record payment', err);
      toast.error('Failed to record payment');
    } finally {
      setIsPaying(false);
    }
  }, [taxReport, paymentAmount, paymentMethod, paymentReference, refetch]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && parcelId) {
      refetch();
    }
  };

  const handleRetry = () => {
    refetch();
  };

  // Client-side pagination logic
  const allRecords = taxReport?.records ?? [];
  const totalRecords = allRecords.length;
  const totalPages = Math.max(1, Math.ceil(totalRecords / recordsPageSize));
  const safePage = Math.min(recordsPage, totalPages);
  const startIdx = (safePage - 1) * recordsPageSize;
  const endIdx = Math.min(startIdx + recordsPageSize, totalRecords);
  const paginatedRecords = allRecords.slice(startIdx, endIdx);

  const handleRecordsPageChange = (page: number) => {
    setRecordsPage(page);
  };

  const handleRecordsPageSizeChange = (size: number) => {
    setRecordsPageSize(size);
    setRecordsPage(1);
  };

  // Derive error from local + query state
  const displayError = error || (!isLoading && !taxReport && parcelId ? 'No tax data found' : null);

  return (
    <PageContainer
      title="Tax Calculations"
      subtitle="Automated land tax computations and diocese tax assessment registries."
    >
      <div className="flex items-center gap-3 p-6 rounded-xl border border-slate-800/80 bg-slate-900/30 mb-6 flex-wrap">
        <DollarSign className="w-6 h-6 text-success flex-shrink-0" />
        <div className="text-sm flex-1 min-w-[200px]">
          <p className="text-white font-bold">Tax Assessment</p>
          <p className="text-slate-400 mt-0.5">Integrated calculations for diocese land tax rates, exemptions, and payment histories.</p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <div className="relative">
            <input
              type="text"
              placeholder="Search parcels by UPI or number..."
              value={parcelSearch}
              onChange={handleParcelSearchChange}
              onKeyDown={handleKeyDown}
              className="pl-9 pr-3 py-2 w-64 bg-slate-900/50 border border-slate-700 rounded-md text-sm text-white placeholder-slate-500"
            />
            <Search className="absolute left-3 top-2 w-4 h-4 text-slate-500" />
            {showSuggestions && parcelSuggestions.length > 0 && (
              <div className="absolute top-full mt-1 w-64 bg-slate-800 border border-slate-700 rounded-md shadow-lg z-10 max-h-48 overflow-auto">
                {parcelSuggestions.map((parcel) => (
                  <button
                    key={parcel.id}
                    onClick={() => selectParcel(parcel.id, parcel.upi)}
                    className="w-full text-left px-3 py-2 text-sm text-slate-200 hover:bg-slate-700 transition-colors flex items-center gap-2"
                  >
                    <MapPin className="w-3 h-3 text-slate-400" />
                    {parcel.upi}
                  </button>
                ))}
              </div>
            )}
          </div>
          <button
            onClick={() => refetch()}
            disabled={!parcelId || isLoading}
            className="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 disabled:opacity-50 transition-colors"
          >
            {isLoading ? 'Loading...' : 'Lookup'}
          </button>
          {taxReport && (
            <>
              <button
                onClick={() => handleExport('pdf')}
                disabled={isExporting}
                className="px-3 py-2 bg-success/20 text-success rounded-md hover:bg-success/30 transition-colors text-sm flex items-center gap-1"
              >
                <FileDown className="w-4 h-4" />
                {isExporting ? '...' : 'Export PDF'}
              </button>
              <button
                onClick={() => handleExport('excel')}
                disabled={isExporting}
                className="px-3 py-2 bg-info/20 text-info rounded-md hover:bg-info/30 transition-colors text-sm flex items-center gap-1"
              >
                <FileDown className="w-4 h-4" />
                {isExporting ? '...' : 'Export Excel'}
              </button>
            </>
          )}
        </div>
      </div>

      {displayError && !isLoading && (
        <div className="text-center py-8">
          <p className="text-red-400 mb-4">{displayError}</p>
          <button
            onClick={handleRetry}
            className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
          >
            Try Again
          </button>
        </div>
      )}

      {isLoading && (
        <div className="text-center py-12 text-slate-400">Loading tax report...</div>
      )}

      {taxReport && !isLoading && (
        <div className="space-y-6">
          {/* Summary cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-slate-900/40 p-4 rounded-lg border border-slate-800">
              <p className="text-sm text-slate-400">UPI</p>
              <p className="text-xl font-bold text-white break-all">
                {taxReport.upi}
              </p>
            </div>
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

          {/* Action buttons */}
          <div className="flex gap-3 flex-wrap">
            <div className="flex items-center gap-2">
              <input
                type="text"
                placeholder="Year (e.g. 2025)"
                value={assessmentYear}
                onChange={(e) => setAssessmentYear(e.target.value)}
                className="px-3 py-2 bg-slate-900/50 border border-slate-700 rounded-md text-sm text-white placeholder-slate-500 w-24"
              />
              <button
                onClick={handleAssess}
                disabled={isAssessing}
                className="px-4 py-2 bg-warning/20 text-warning rounded-md hover:bg-warning/30 transition-colors text-sm flex items-center gap-1"
              >
                <Plus className="w-4 h-4" />
                {isAssessing ? 'Assessing...' : 'New Assessment'}
              </button>
            </div>
            <button
              onClick={() => setShowPaymentForm(!showPaymentForm)}
              className="px-4 py-2 bg-success/20 text-success rounded-md hover:bg-success/30 transition-colors text-sm flex items-center gap-1"
            >
              <CreditCard className="w-4 h-4" />
              Record Payment
            </button>
          </div>

          {/* Payment form */}
          {showPaymentForm && (
            <div className="bg-slate-900/40 p-4 rounded-lg border border-slate-800 space-y-3">
              <h4 className="text-sm font-medium text-white">Record Payment</h4>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="text-xs text-slate-500 block mb-1">Amount (RWF)</label>
                  <input
                    type="number"
                    placeholder="Amount"
                    value={paymentAmount}
                    onChange={(e) => setPaymentAmount(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-900/50 border border-slate-700 rounded-md text-sm text-white placeholder-slate-500"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-500 block mb-1">Method</label>
                  <select
                    value={paymentMethod}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-900/50 border border-slate-700 rounded-md text-sm text-white"
                  >
                    <option value="bank_transfer">Bank Transfer</option>
                    <option value="cash">Cash</option>
                    <option value="mobile_money">Mobile Money</option>
                    <option value="cheque">Cheque</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs text-slate-500 block mb-1">Reference (optional)</label>
                  <input
                    type="text"
                    placeholder="Ref No."
                    value={paymentReference}
                    onChange={(e) => setPaymentReference(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-900/50 border border-slate-700 rounded-md text-sm text-white placeholder-slate-500"
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleRecordPayment}
                  disabled={isPaying}
                  className="px-4 py-2 bg-success text-white rounded-md hover:bg-success/80 transition-colors text-sm"
                >
                  {isPaying ? 'Processing...' : 'Submit Payment'}
                </button>
                <button
                  onClick={() => setShowPaymentForm(false)}
                  className="px-4 py-2 bg-slate-700 text-slate-300 rounded-md hover:bg-slate-600 transition-colors text-sm"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {/* Tax records table */}
          <div>
            <h3 className="text-lg font-medium text-white mb-2">Tax Records</h3>
            {allRecords.length === 0 ? (
              <div className="text-center py-8 text-slate-400 bg-slate-900/40 rounded-lg border border-slate-800">
                No tax records found for this parcel.
              </div>
            ) : (
              <>
                <div className="overflow-x-auto border border-slate-800 rounded-lg">
                  <table className="min-w-full divide-y divide-slate-800">
                    <thead className="bg-slate-900/60">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-slate-400">Year</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-slate-400">Status</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-slate-400">Due Date</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-slate-400">Assessed</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-slate-400">Tax</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-slate-400">Total</th>
                      </tr>
                    </thead>
                    <tbody className="bg-slate-900/40 divide-y divide-slate-800">
                      {paginatedRecords.map((record) => (
                        <tr key={record.id} className="hover:bg-slate-900/60 transition-colors">
                          <td className="px-4 py-2 text-sm text-slate-200 whitespace-nowrap">{record.assessment_year}</td>
                          <td className="px-4 py-2 text-sm text-slate-400 whitespace-nowrap">
                            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                              record.status === 'paid'
                                ? 'bg-success/10 text-success'
                                : record.status === 'overdue'
                                ? 'bg-red-500/10 text-red-400'
                                : 'bg-warning/10 text-warning'
                            }`}>
                              {record.status}
                            </span>
                          </td>
                          <td className="px-4 py-2 text-sm text-slate-400 whitespace-nowrap">
                            {new Date(record.due_date).toLocaleDateString()}
                          </td>
                          <td className="px-4 py-2 text-sm text-slate-400 whitespace-nowrap">
                            RWF {record.assessed_value.toLocaleString()}
                          </td>
                          <td className="px-4 py-2 text-sm text-slate-400 whitespace-nowrap">
                            RWF {record.base_tax_amount.toLocaleString()}
                          </td>
                          <td className="px-4 py-2 text-sm font-medium text-slate-200 whitespace-nowrap">
                            RWF {record.total_amount.toLocaleString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {totalPages > 1 && (
                  <div className="mt-4">
                    <Pagination
                      currentPage={safePage}
                      totalPages={totalPages}
                      totalItems={totalRecords}
                      pageSize={recordsPageSize}
                      onPageChange={handleRecordsPageChange}
                      onPageSizeChange={handleRecordsPageSizeChange}
                    />
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}
    </PageContainer>
  );
}