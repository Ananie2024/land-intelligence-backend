import React, { useState } from 'react';
import { X, Calendar, DollarSign, User, FileText, CheckCircle2, Clock, AlertTriangle, CreditCard } from 'lucide-react';
import { LeaseAgreement, LeasePaymentSchedule } from '@/types/lease';
import { leaseService } from '@/services/leaseService';
import { toast } from 'react-hot-toast';

interface LeaseDetailModalProps {
  lease: LeaseAgreement | null;
  isOpen: boolean;
  onClose: () => void;
  onRefresh: () => void;
}

export const LeaseDetailModal: React.FC<LeaseDetailModalProps> = ({ lease, isOpen, onClose, onRefresh }) => {
  const [selectedSchedule, setSelectedSchedule] = useState<LeasePaymentSchedule | null>(null);
  const [payAmount, setPayAmount] = useState('');
  const [payRef, setPayRef] = useState('');
  const [payNotes, setPayNotes] = useState('');
  const [isSubmittingPay, setIsSubmittingPay] = useState(false);

  if (!isOpen || !lease) return null;

  const handleOpenPay = (sched: LeasePaymentSchedule) => {
    setSelectedSchedule(sched);
    setPayAmount((sched.amount_due - sched.amount_paid).toString());
    setPayRef('');
    setPayNotes('');
  };

  const handleSubmitPayment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSchedule) return;
    const amount = parseFloat(payAmount);
    if (isNaN(amount) || amount <= 0) {
      toast.error('Please enter a valid payment amount.');
      return;
    }

    setIsSubmittingPay(true);
    try {
      const res = await leaseService.recordPayment(lease.id, selectedSchedule.id, {
        amount_paid: amount,
        payment_reference: payRef.trim() || undefined,
        notes: payNotes.trim() || undefined,
      });

      if (res.success) {
        toast.success('Payment recorded successfully!');
        setSelectedSchedule(null);
        onRefresh();
      } else {
        toast.error(res.message || 'Failed to record payment.');
      }
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || err?.message || 'Error recording payment.');
    } finally {
      setIsSubmittingPay(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <span className="px-2.5 py-1 text-xs font-semibold text-emerald-700 bg-emerald-100 dark:bg-emerald-950/60 dark:text-emerald-400 rounded-full">Active</span>;
      case 'expired':
        return <span className="px-2.5 py-1 text-xs font-semibold text-rose-700 bg-rose-100 dark:bg-rose-950/60 dark:text-rose-400 rounded-full">Expired</span>;
      case 'draft':
        return <span className="px-2.5 py-1 text-xs font-semibold text-slate-700 bg-slate-100 dark:bg-slate-800 dark:text-slate-400 rounded-full">Draft</span>;
      default:
        return <span className="px-2.5 py-1 text-xs font-semibold text-amber-700 bg-amber-100 dark:bg-amber-950/60 dark:text-amber-400 rounded-full">{status}</span>;
    }
  };

  const getPaymentStatusBadge = (status: string) => {
    switch (status) {
      case 'paid':
        return <span className="px-2 py-0.5 text-xs font-medium text-emerald-700 bg-emerald-50 dark:bg-emerald-950/50 dark:text-emerald-400 rounded">Paid</span>;
      case 'overdue':
        return <span className="px-2 py-0.5 text-xs font-medium text-rose-700 bg-rose-50 dark:bg-rose-950/50 dark:text-rose-400 rounded">Overdue</span>;
      case 'partial':
        return <span className="px-2 py-0.5 text-xs font-medium text-amber-700 bg-amber-50 dark:bg-amber-950/50 dark:text-amber-400 rounded">Partial</span>;
      default:
        return <span className="px-2 py-0.5 text-xs font-medium text-sky-700 bg-sky-50 dark:bg-sky-950/50 dark:text-sky-400 rounded">Pending</span>;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-3xl overflow-hidden border border-slate-200 dark:border-slate-700">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 bg-slate-50 dark:bg-slate-800/80 border-b border-slate-200 dark:border-slate-700">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 rounded-lg">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h2 className="text-lg font-bold text-slate-900 dark:text-white font-mono">{lease.lease_number}</h2>
                {getStatusBadge(lease.status)}
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400">Lease Details & Payment Schedule</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-6 max-h-[75vh] overflow-y-auto">
          {/* Key Grid Overview */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-slate-50 dark:bg-slate-900/50 rounded-xl border border-slate-200/80 dark:border-slate-700/80">
            <div>
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Tenant Name</span>
              <p className="text-sm font-semibold text-slate-800 dark:text-slate-100 mt-0.5">{lease.tenant_name}</p>
            </div>
            <div>
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Parcel UPI</span>
              <p className="text-sm font-mono font-semibold text-indigo-600 dark:text-indigo-400 mt-0.5">
                {lease.parcel?.upi || lease.parcel_id}
              </p>
            </div>
            <div>
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Annual Rent</span>
              <p className="text-sm font-mono font-bold text-emerald-600 dark:text-emerald-400 mt-0.5">
                {Number(lease.annual_rent_amount).toLocaleString()} RWF
              </p>
            </div>
            <div>
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Payment Frequency</span>
              <p className="text-sm font-medium text-slate-700 dark:text-slate-300 capitalize mt-0.5">
                {lease.payment_frequency.replace('_', ' ')} ({Number(lease.installment_amount).toLocaleString()} RWF)
              </p>
            </div>
          </div>

          {/* Details Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div className="space-y-2">
              <div className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-700">
                <span className="text-slate-500">Contract Term:</span>
                <span className="font-semibold text-slate-700 dark:text-slate-300">
                  {lease.start_date} to {lease.end_date}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-700">
                <span className="text-slate-500">Tenant Contact:</span>
                <span className="font-medium text-slate-700 dark:text-slate-300">{lease.tenant_contact || 'N/A'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-700">
                <span className="text-slate-500">ID / Reg No:</span>
                <span className="font-mono text-slate-700 dark:text-slate-300">{lease.tenant_id_number || 'N/A'}</span>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-700">
                <span className="text-slate-500">Intended Purpose:</span>
                <span className="font-medium text-slate-700 dark:text-slate-300">{lease.purpose_use || 'Standard lease'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-700">
                <span className="text-slate-500">Created Date:</span>
                <span className="text-slate-700 dark:text-slate-300">{new Date(lease.created_at).toLocaleDateString()}</span>
              </div>
              {lease.notes && (
                <div className="py-1">
                  <span className="text-slate-500 block mb-0.5">Notes:</span>
                  <p className="text-slate-600 dark:text-slate-400 italic">{lease.notes}</p>
                </div>
              )}
            </div>
          </div>

          {/* Payment Schedule Table */}
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white mb-3 flex items-center gap-2">
              <CreditCard className="w-4 h-4 text-indigo-500" /> Payment Schedule Installments
            </h3>

            {lease.payment_schedules && lease.payment_schedules.length > 0 ? (
              <div className="overflow-x-auto border border-slate-200 dark:border-slate-700 rounded-xl">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 dark:bg-slate-900 text-slate-500 dark:text-slate-400 uppercase font-semibold">
                    <tr>
                      <th className="px-4 py-2.5">Due Date</th>
                      <th className="px-4 py-2.5">Amount Due</th>
                      <th className="px-4 py-2.5">Paid</th>
                      <th className="px-4 py-2.5">Status</th>
                      <th className="px-4 py-2.5">Reference</th>
                      <th className="px-4 py-2.5 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-700 text-slate-700 dark:text-slate-300">
                    {lease.payment_schedules.map((sched) => (
                      <tr key={sched.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-700/30">
                        <td className="px-4 py-2.5 font-medium">{sched.due_date}</td>
                        <td className="px-4 py-2.5 font-mono font-semibold">{Number(sched.amount_due).toLocaleString()} RWF</td>
                        <td className="px-4 py-2.5 font-mono text-emerald-600 dark:text-emerald-400">
                          {Number(sched.amount_paid).toLocaleString()} RWF
                        </td>
                        <td className="px-4 py-2.5">{getPaymentStatusBadge(sched.status)}</td>
                        <td className="px-4 py-2.5 font-mono text-slate-500">{sched.payment_reference || '-'}</td>
                        <td className="px-4 py-2.5 text-right">
                          {sched.status !== 'paid' ? (
                            <button
                              onClick={() => handleOpenPay(sched)}
                              className="px-2.5 py-1 text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 rounded-md transition"
                            >
                              Record Pay
                            </button>
                          ) : (
                            <span className="text-emerald-500 flex items-center justify-end gap-1 font-medium text-[11px]">
                              <CheckCircle2 className="w-3.5 h-3.5" /> Complete
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-xs text-slate-400 italic py-3 text-center border border-dashed rounded-lg">
                No payment schedules generated for this lease.
              </p>
            )}
          </div>

          {/* Record Payment Sub-form Modal/Section */}
          {selectedSchedule && (
            <div className="p-4 bg-indigo-50/70 dark:bg-slate-900/80 rounded-xl border border-indigo-200 dark:border-slate-700 space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-bold text-indigo-900 dark:text-indigo-300 uppercase">
                  Record Installment Payment (Due: {selectedSchedule.due_date})
                </h4>
                <button
                  type="button"
                  onClick={() => setSelectedSchedule(null)}
                  className="text-xs text-slate-400 hover:text-slate-600"
                >
                  Cancel
                </button>
              </div>

              <form onSubmit={handleSubmitPayment} className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-600 dark:text-slate-400 mb-1">
                    Amount Paid (RWF)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={payAmount}
                    onChange={(e) => setPayAmount(e.target.value)}
                    className="w-full px-3 py-1.5 text-xs border rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white font-mono"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-600 dark:text-slate-400 mb-1">
                    Payment Reference / Receipt
                  </label>
                  <input
                    type="text"
                    placeholder="BK-TX-998822"
                    value={payRef}
                    onChange={(e) => setPayRef(e.target.value)}
                    className="w-full px-3 py-1.5 text-xs border rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white font-mono"
                  />
                </div>
                <div className="flex items-end">
                  <button
                    type="submit"
                    disabled={isSubmittingPay}
                    className="w-full py-1.5 px-3 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-sm disabled:opacity-50"
                  >
                    {isSubmittingPay ? 'Recording...' : 'Confirm Payment'}
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-slate-50 dark:bg-slate-800/80 border-t border-slate-200 dark:border-slate-700 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-lg"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
