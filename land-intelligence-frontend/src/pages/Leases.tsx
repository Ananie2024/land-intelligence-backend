import React, { useState, useEffect } from 'react';
import { PageContainer } from '@/components/layout/PageContainer';
import { FileText, Plus, Search, Filter, DollarSign, Calendar, AlertCircle, CheckCircle2, Eye, Trash2 } from 'lucide-react';
import { leaseService } from '@/services/leaseService';
import { LeaseAgreement, LeaseSummaryStats, LeaseStatus } from '@/types/lease';
import { CreateLeaseModal } from '@/features/leases/components/CreateLeaseModal';
import { LeaseDetailModal } from '@/features/leases/components/LeaseDetailModal';
import { Pagination } from '@/components/ui/Pagination';
import { toast } from 'react-hot-toast';

export default function Leases() {
  const [leases, setLeases] = useState<LeaseAgreement[]>([]);
  const [stats, setStats] = useState<LeaseSummaryStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Search & Filter
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<LeaseStatus | ''>('');

  // Pagination
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [total, setTotal] = useState(0);

  // Modals
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [selectedLease, setSelectedLease] = useState<LeaseAgreement | null>(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);

  const fetchLeases = async () => {
    setIsLoading(true);
    try {
      const [leasesRes, statsRes] = await Promise.all([
        leaseService.getLeases({
          tenant: searchQuery.trim() || undefined,
          status: (statusFilter as LeaseStatus) || undefined,
          page,
          page_size: pageSize,
        }),
        leaseService.getStats(),
      ]);

      if (leasesRes.success && leasesRes.data) {
        setLeases(leasesRes.data.items);
        setTotal(leasesRes.data.total);
      }
      if (statsRes.success && statsRes.data) {
        setStats(statsRes.data);
      }
    } catch (err: any) {
      toast.error('Failed to load lease agreements.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchLeases();
  }, [page, pageSize, statusFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchLeases();
  };

  const handleOpenDetail = async (leaseId: string) => {
    try {
      const res = await leaseService.getLeaseById(leaseId);
      if (res.success && res.data) {
        setSelectedLease(res.data);
        setIsDetailOpen(true);
      }
    } catch (err) {
      toast.error('Failed to fetch lease details.');
    }
  };

  const handleDeleteLease = async (leaseId: string) => {
    if (!window.confirm('Are you sure you want to delete this lease agreement?')) return;
    try {
      const res = await leaseService.deleteLease(leaseId);
      if (res.success) {
        toast.success('Lease agreement deleted.');
        fetchLeases();
      }
    } catch (err) {
      toast.error('Failed to delete lease agreement.');
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

  return (
    <PageContainer
      title="Lease Agreements & Revenue"
      description="Track tenant agreements, rental fees, payment terms, and installment schedules for church land."
    >
      <div className="space-y-6">
        {/* Top Summary Metrics */}
        {stats && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white dark:bg-slate-800 p-5 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Active Leases</span>
                <div className="p-2 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded-lg">
                  <FileText className="w-5 h-5" />
                </div>
              </div>
              <p className="text-2xl font-black text-slate-900 dark:text-white mt-2">{stats.active_leases}</p>
              <p className="text-xs text-slate-500 mt-1">{stats.total_leases} total registered contracts</p>
            </div>

            <div className="bg-white dark:bg-slate-800 p-5 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Annual Revenue</span>
                <div className="p-2 bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 rounded-lg">
                  <DollarSign className="w-5 h-5" />
                </div>
              </div>
              <p className="text-2xl font-black text-slate-900 dark:text-white mt-2 font-mono">
                {Number(stats.total_annual_revenue).toLocaleString()} RWF
              </p>
              <p className="text-xs text-slate-500 mt-1">Expected annual rental fees</p>
            </div>

            <div className="bg-white dark:bg-slate-800 p-5 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Collected Income</span>
                <div className="p-2 bg-sky-500/10 text-sky-600 dark:text-sky-400 rounded-lg">
                  <CheckCircle2 className="w-5 h-5" />
                </div>
              </div>
              <p className="text-2xl font-black text-emerald-600 dark:text-emerald-400 mt-2 font-mono">
                {Number(stats.total_collected_revenue).toLocaleString()} RWF
              </p>
              <p className="text-xs text-slate-500 mt-1">Fulfilled installment payments</p>
            </div>

            <div className="bg-white dark:bg-slate-800 p-5 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Overdue Installments</span>
                <div className="p-2 bg-rose-500/10 text-rose-600 dark:text-rose-400 rounded-lg">
                  <AlertCircle className="w-5 h-5" />
                </div>
              </div>
              <p className="text-2xl font-black text-rose-600 dark:text-rose-400 mt-2 font-mono">{stats.overdue_payments_count}</p>
              <p className="text-xs text-slate-500 mt-1">Pending payments past due date</p>
            </div>
          </div>
        )}

        {/* Action Header & Search Controls */}
        <div className="bg-white dark:bg-slate-800 p-4 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
          <form onSubmit={handleSearchSubmit} className="flex-1 flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="text"
                placeholder="Search tenant name, ID or lease code..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-xl bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value as LeaseStatus | '');
                setPage(1);
              }}
              className="px-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-xl bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">All Statuses</option>
              <option value="active">Active</option>
              <option value="draft">Draft</option>
              <option value="expired">Expired</option>
              <option value="terminated">Terminated</option>
            </select>
            <button
              type="submit"
              className="px-4 py-2 text-sm font-medium text-white bg-slate-800 dark:bg-slate-700 hover:bg-slate-900 rounded-xl transition"
            >
              Filter
            </button>
          </form>

          <button
            onClick={() => setIsCreateOpen(true)}
            className="px-4 py-2 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-sm flex items-center justify-center gap-2 transition"
          >
            <Plus className="w-4 h-4" /> New Lease Agreement
          </button>
        </div>

        {/* Leases Table */}
        <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
          {isLoading ? (
            <div className="p-12 text-center text-slate-400">Loading lease agreements...</div>
          ) : leases.length === 0 ? (
            <div className="p-12 text-center space-y-2">
              <FileText className="w-10 h-10 text-slate-300 mx-auto" />
              <p className="text-sm font-medium text-slate-600 dark:text-slate-400">No lease agreements found</p>
              <p className="text-xs text-slate-400">Click "New Lease Agreement" to record a tenant agreement.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 dark:bg-slate-900/60 text-slate-400 uppercase font-bold border-b border-slate-200 dark:border-slate-700">
                  <tr>
                    <th className="px-6 py-3.5">Lease Code</th>
                    <th className="px-6 py-3.5">Tenant Name</th>
                    <th className="px-6 py-3.5">Parcel UPI</th>
                    <th className="px-6 py-3.5">Term Dates</th>
                    <th className="px-6 py-3.5">Annual Rent</th>
                    <th className="px-6 py-3.5">Frequency</th>
                    <th className="px-6 py-3.5">Status</th>
                    <th className="px-6 py-3.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-700 text-slate-700 dark:text-slate-300">
                  {leases.map((lease) => (
                    <tr key={lease.id} className="hover:bg-slate-50/60 dark:hover:bg-slate-700/30 transition">
                      <td className="px-6 py-4 font-mono font-bold text-indigo-600 dark:text-indigo-400">{lease.lease_number}</td>
                      <td className="px-6 py-4">
                        <div className="font-semibold text-slate-900 dark:text-white">{lease.tenant_name}</div>
                        <div className="text-[11px] text-slate-400">{lease.tenant_contact || 'No contact'}</div>
                      </td>
                      <td className="px-6 py-4 font-mono">{lease.parcel?.upi || lease.parcel_id}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {lease.start_date} to {lease.end_date}
                      </td>
                      <td className="px-6 py-4 font-mono font-bold text-emerald-600 dark:text-emerald-400">
                        {Number(lease.annual_rent_amount).toLocaleString()} RWF
                      </td>
                      <td className="px-6 py-4 capitalize">{lease.payment_frequency.replace('_', ' ')}</td>
                      <td className="px-6 py-4">{getStatusBadge(lease.status)}</td>
                      <td className="px-6 py-4 text-right space-x-2">
                        <button
                          onClick={() => handleOpenPayDetail(lease.id)}
                          className="p-1.5 text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition"
                          title="View Details"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteLease(lease.id)}
                          className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-lg transition"
                          title="Delete Lease"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination */}
          {total > pageSize && (
            <div className="px-6 py-4 border-t border-slate-200 dark:border-slate-700">
              <Pagination currentPage={page} totalPages={Math.ceil(total / pageSize)} onPageChange={(p) => setPage(p)} />
            </div>
          )}
        </div>
      </div>

      {/* Modals */}
      <CreateLeaseModal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} onSuccess={fetchLeases} />
      <LeaseDetailModal
        lease={selectedLease}
        isOpen={isDetailOpen}
        onClose={() => setIsDetailOpen(false)}
        onRefresh={() => {
          if (selectedLease) handleOpenPayDetail(selectedLease.id);
          fetchLeases();
        }}
      />
    </PageContainer>
  );

  function handleOpenPayDetail(id: string) {
    handleOpenDetail(id);
  }
}
