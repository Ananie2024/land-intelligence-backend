import React, { useState } from 'react';
import { X, Calendar, DollarSign, User, FileText, CheckCircle2 } from 'lucide-react';
import { leaseService } from '@/services/leaseService';
import { LeaseAgreementCreate, PaymentFrequency } from '@/types/lease';
import { taxService } from '@/services/taxService';
import { toast } from 'react-hot-toast';

interface CreateLeaseModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const CreateLeaseModal: React.FC<CreateLeaseModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [parcelSearch, setParcelSearch] = useState('');
  const [selectedParcel, setSelectedParcel] = useState<{ id: string; upi: string; owner_name?: string } | null>(null);
  const [parcelSuggestions, setParcelSuggestions] = useState<{ id: string; upi: string; owner_name?: string }[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  const [leaseNumber, setLeaseNumber] = useState('');
  const [tenantName, setTenantName] = useState('');
  const [tenantContact, setTenantContact] = useState('');
  const [tenantIdNumber, setTenantIdNumber] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [annualRent, setAnnualRent] = useState('');
  const [frequency, setFrequency] = useState<PaymentFrequency>('annually');
  const [purposeUse, setPurposeUse] = useState('');
  const [notes, setNotes] = useState('');
  const [autoGenerate, setAutoGenerate] = useState(true);

  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSearchParcels = async (query: string) => {
    setParcelSearch(query);
    if (!query || query.length < 2) {
      setParcelSuggestions([]);
      setShowSuggestions(false);
      return;
    }
    try {
      const res = await taxService.searchParcels(query, 10);
      if (res.success && res.data) {
        setParcelSuggestions(res.data.items);
        setShowSuggestions(true);
      }
    } catch {
      setParcelSuggestions([]);
    }
  };

  const handleSelectParcel = (p: { id: string; upi: string; owner_name?: string }) => {
    setSelectedParcel(p);
    setParcelSearch(p.upi);
    setShowSuggestions(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedParcel) {
      toast.error('Please select a land parcel (UPI).');
      return;
    }
    if (!tenantName.trim()) {
      toast.error('Tenant name is required.');
      return;
    }
    if (!startDate || !endDate) {
      toast.error('Start date and end date are required.');
      return;
    }
    if (new Date(startDate) >= new Date(endDate)) {
      toast.error('Start date must be before end date.');
      return;
    }
    if (!annualRent || parseFloat(annualRent) <= 0) {
      toast.error('Valid annual rent amount is required.');
      return;
    }

    setIsSubmitting(true);
    try {
      const payload: LeaseAgreementCreate = {
        parcel_id: selectedParcel.id,
        lease_number: leaseNumber.trim() || undefined,
        tenant_name: tenantName.trim(),
        tenant_contact: tenantContact.trim() || undefined,
        tenant_id_number: tenantIdNumber.trim() || undefined,
        start_date: startDate,
        end_date: endDate,
        annual_rent_amount: parseFloat(annualRent),
        payment_frequency: frequency,
        purpose_use: purposeUse.trim() || undefined,
        notes: notes.trim() || undefined,
        auto_generate_schedules: autoGenerate,
      };

      const res = await leaseService.createLease(payload);
      if (res.success) {
        toast.success('Lease agreement created successfully!');
        onSuccess();
        onClose();
      } else {
        toast.error(res.message || 'Failed to create lease agreement.');
      }
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || err?.message || 'Error creating lease.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden border border-slate-200 dark:border-slate-700">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 bg-slate-50 dark:bg-slate-800/80 border-b border-slate-200 dark:border-slate-700">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 rounded-lg">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-900 dark:text-white">Create Lease Agreement</h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">Register new tenant lease contract & payment terms</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {/* Parcel Search */}
          <div className="relative">
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1">
              Select Land Parcel (UPI) *
            </label>
            <input
              type="text"
              placeholder="Search UPI (e.g. 1/02/02/03/1390)..."
              value={parcelSearch}
              onChange={(e) => handleSearchParcels(e.target.value)}
              className="w-full px-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
            />
            {showSuggestions && parcelSuggestions.length > 0 && (
              <div className="absolute z-20 left-0 right-0 mt-1 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                {parcelSuggestions.map((p) => (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => handleSelectParcel(p)}
                    className="w-full text-left px-4 py-2 text-sm hover:bg-indigo-50 dark:hover:bg-slate-700 border-b border-slate-100 dark:border-slate-700 text-slate-800 dark:text-slate-200 flex justify-between items-center"
                  >
                    <span className="font-mono font-medium">{p.upi}</span>
                    <span className="text-xs text-slate-400">{p.owner_name || 'Church Parcel'}</span>
                  </button>
                ))}
              </div>
            )}
            {selectedParcel && (
              <p className="mt-1 text-xs text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Selected: <span className="font-mono font-semibold">{selectedParcel.upi}</span>
              </p>
            )}
          </div>

          {/* Tenant Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1">
                Tenant Name *
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                <input
                  type="text"
                  required
                  placeholder="e.g. Kigali Telecom Ltd"
                  value={tenantName}
                  onChange={(e) => setTenantName(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1">
                Tenant Contact (Phone / Email)
              </label>
              <input
                type="text"
                placeholder="+250 788 123 456"
                value={tenantContact}
                onChange={(e) => setTenantContact(e.target.value)}
                className="w-full px-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1">
                National ID / Reg No
              </label>
              <input
                type="text"
                placeholder="1199880011223344"
                value={tenantIdNumber}
                onChange={(e) => setTenantIdNumber(e.target.value)}
                className="w-full px-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1">
                Lease Reference Code (Optional)
              </label>
              <input
                type="text"
                placeholder="Auto-generated if blank"
                value={leaseNumber}
                onChange={(e) => setLeaseNumber(e.target.value)}
                className="w-full px-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 font-mono"
              />
            </div>
          </div>

          {/* Dates & Financials */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1">
                Start Date *
              </label>
              <div className="relative">
                <Calendar className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                <input
                  type="date"
                  required
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1">
                End Date *
              </label>
              <div className="relative">
                <Calendar className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                <input
                  type="date"
                  required
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1">
                Annual Rental Amount (RWF) *
              </label>
              <div className="relative">
                <DollarSign className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                <input
                  type="number"
                  step="0.01"
                  required
                  placeholder="1200000"
                  value={annualRent}
                  onChange={(e) => setAnnualRent(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 font-mono"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1">
                Payment Frequency *
              </label>
              <select
                value={frequency}
                onChange={(e) => setFrequency(e.target.value as PaymentFrequency)}
                className="w-full px-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
              >
                <option value="annually">Annually (1x per year)</option>
                <option value="semi_annually">Semi-Annually (2x per year)</option>
                <option value="quarterly">Quarterly (4x per year)</option>
                <option value="monthly">Monthly (12x per year)</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1">
              Purpose / Intended Use
            </label>
            <input
              type="text"
              placeholder="e.g. Commercial farming, Telecom mast site, Retail store"
              value={purposeUse}
              onChange={(e) => setPurposeUse(e.target.value)}
              className="w-full px-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div className="flex items-center space-x-2 pt-1">
            <input
              type="checkbox"
              id="autoGenerate"
              checked={autoGenerate}
              onChange={(e) => setAutoGenerate(e.target.checked)}
              className="w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500"
            />
            <label htmlFor="autoGenerate" className="text-xs text-slate-700 dark:text-slate-300 font-medium">
              Automatically generate installment payment schedule items across contract term
            </label>
          </div>

          {/* Footer actions */}
          <div className="flex items-center justify-end space-x-3 pt-4 border-t border-slate-200 dark:border-slate-700">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-sm disabled:opacity-50 flex items-center gap-2"
            >
              {isSubmitting ? 'Creating...' : 'Create Agreement'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
