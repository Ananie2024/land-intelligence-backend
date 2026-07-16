// Parcel List Page with Full CRUD
// Land Intelligence System

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageContainer } from '@/components/layout/PageContainer';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { MapPin, Plus } from 'lucide-react';
import { landService } from '@/services/landService';
import type { Parcel, ParcelCreate, Parish } from '@/types/land';
import { ParcelTable } from '@/features/land/components/ParcelTable';
import { ParcelForm } from '@/features/land/components/ParcelForm';
import { Modal } from '@/components/ui/Modal';
import { Pagination } from '@/components/ui/Pagination';
import { useResourceList, useResourceMutation, useResourceQuery } from '@/hooks/useResourceList';
import toast from 'react-hot-toast';

export default function Parcels() {
  const navigate = useNavigate();
  const [showForm, setShowForm] = useState(false);
  const [editingParcel, setEditingParcel] = useState<Parcel | null>(null);
  const [filters, setFilters] = useState({
    page: 1,
    size: 20,
    search: '',
  });

  const { data, isLoading, error, totalItems, totalPages, refetch } = useResourceList<Parcel>(
    ['parcels'],
    (f) => landService.getParcels(f),
    filters,
    { defaultFilters: { page: 1, size: 20, search: '' } }
  );

  // Load parishes for the form dropdown (all, no pagination)
  const { data: parishes } = useResourceQuery<Parish[]>(
    ['parishes-all'],
    () => landService.getParishesAll()
  );

  const createMutation = useResourceMutation(
    (data: ParcelCreate) => landService.createParcel(data),
    { invalidateKeys: ['parcels'] }
  );

  const updateMutation = useResourceMutation(
    (data: ParcelCreate) => {
      if (!editingParcel) throw new Error('No parcel selected');
      return landService.updateParcel(editingParcel.id, data);
    },
    { invalidateKeys: ['parcels'] }
  );

  const deleteMutation = useResourceMutation(
    (id: string) => landService.deleteParcel(id),
    { invalidateKeys: ['parcels'] }
  );

  const parcels = data || [];
  const parishOptions = (parishes || []).map(p => ({ id: p.id, name: p.name }));

  const handleCreate = async (data: ParcelCreate) => {
    const success = await createMutation.mutate(data);
    if (success) {
      setShowForm(false);
      toast.success('Parcel created successfully');
    }
  };

  const handleUpdate = async (data: ParcelCreate) => {
    if (!editingParcel) return;
    const success = await updateMutation.mutate(data);
    if (success) {
      setEditingParcel(null);
      setShowForm(false);
      toast.success('Parcel updated successfully');
    }
  };

  const handleDelete = async (parcel: Parcel) => {
    if (!confirm(`Delete parcel "${parcel.upi}"? This action cannot be undone.`)) return;
    const success = await deleteMutation.mutate(parcel.id);
    if (success) {
      toast.success('Parcel deleted successfully');
    }
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setEditingParcel(null);
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFilters(prev => ({ ...prev, search: e.target.value, page: 1 }));
  };

  const handlePageChange = (page: number) => {
    setFilters(prev => ({ ...prev, page }));
  };

  const handlePageSizeChange = (size: number) => {
    setFilters(prev => ({ ...prev, size, page: 1 }));
  };

  const handleRetry = () => {
    refetch();
  };

  const isSubmitting = createMutation.isLoading || updateMutation.isLoading;

  return (
    <PageContainer
      title="Land Parcels Registry"
      subtitle="Comprehensive list of church land properties registered within the Diocese."
      action={
        <Button 
          variant="primary" 
          leftIcon={<Plus className="w-4 h-4" />}
          onClick={() => setShowForm(true)}
        >
          Register Parcel
        </Button>
      }
    >
      <div className="space-y-6">
        <div className="flex items-center gap-3 p-4 rounded-xl border border-slate-800/80 bg-slate-900/30">
          <div className="p-2 rounded-lg bg-primary-500/10 text-primary-400">
            <MapPin className="w-5 h-5" />
          </div>
          <div className="text-xs flex-1">
            <p className="text-white font-bold">GIS Coordinates Active</p>
            <p className="text-slate-500 mt-0.5">Click any parcel record to open structural documents or display boundary pins.</p>
          </div>
          <div className="relative">
            <input
              type="text"
              placeholder="Search parcels..."
              value={filters.search || ''}
              onChange={handleSearchChange}
              className="pl-9 pr-3 py-2 w-64 bg-slate-900/60 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:border-primary-500"
            />
            <svg className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>

        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-12 gap-3">
            <LoadingSpinner size="md" className="border-t-primary-500" />
            <span className="text-slate-400 text-xs">Loading parcels...</span>
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-red-400 mb-4">{error}</p>
            <button 
              onClick={handleRetry}
              className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
            >
              Try Again
            </button>
          </div>
        ) : (
          <>
            <ParcelTable 
              parcels={parcels}
              onView={(parcel) => navigate(`/parcels/${parcel.id}`)}
              onEdit={(parcel) => {
                setEditingParcel(parcel);
                setShowForm(true);
              }}
              onDelete={handleDelete}
            />
            {totalPages > 1 && (
              <Pagination
                currentPage={filters.page || 1}
                totalPages={totalPages}
                totalItems={totalItems}
                pageSize={filters.size || 20}
                onPageChange={handlePageChange}
                onPageSizeChange={handlePageSizeChange}
              />
            )}
          </>
        )}

        {/* Modal Form */}
        <Modal
          isOpen={showForm}
          onClose={handleCloseForm}
          title={editingParcel ? 'Edit Parcel' : 'Register New Parcel'}
          size="lg"
        >
          <ParcelForm
            parcel={editingParcel}
            onSubmit={editingParcel ? handleUpdate : handleCreate}
            isLoading={isSubmitting}
            parishes={parishOptions}
          />
        </Modal>
      </div>
    </PageContainer>
  );
}