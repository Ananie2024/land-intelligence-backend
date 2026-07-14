// Parcel List Page with Full CRUD
// Land Intelligence System

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageContainer } from '@/components/layout/PageContainer';
import { Button } from '@/components/ui/Button';
import { MapPin, Plus } from 'lucide-react';
import { landService } from '@/services/landService';
import type { Parcel, ParcelCreate, ParcelFilters } from '@/types/land';
import { ParcelTable } from '@/features/land/components/ParcelTable';
import { ParcelForm } from '@/features/land/components/ParcelForm';
import { Modal } from '@/components/ui/Modal';
import { Pagination } from '@/components/ui/Pagination';
import { toast } from 'react-hot-toast';

export default function Parcels() {
  const navigate = useNavigate();
  const [parcels, setParcels] = useState<Parcel[]>([]);
  const [parishes, setParishes] = useState<Array<{ id: string; name: string }>>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingParcel, setEditingParcel] = useState<Parcel | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [filters, setFilters] = useState<ParcelFilters & { search?: string }>({
    page: 1,
    size: 20,
    search: '',
  });
  const [totalItems, setTotalItems] = useState(0);
  const [totalPages, setTotalPages] = useState(0);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [parcelsResponse, parishesResponse] = await Promise.all([
        landService.getParcels(filters),
        landService.getParishes(),
      ]);
      
      if (parcelsResponse.success && parcelsResponse.data) {
        setParcels(parcelsResponse.data);
        setTotalItems(parcelsResponse.total ?? 0);
        setTotalPages(parcelsResponse.pages ?? 0);
      } else {
        setError(parcelsResponse.message || 'Failed to load parcels');
      }
      if (parishesResponse.success && parishesResponse.data) {
        setParishes(parishesResponse.data.map(p => ({ id: p.id, name: p.name })));
      }
    } catch (error) {
      console.error('Failed to load data', error);
      setError('Failed to load parcels');
      toast.error('Failed to load parcels');
    } finally {
      setIsLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleCreate = async (data: ParcelCreate) => {
    setIsSubmitting(true);
    try {
      const response = await landService.createParcel(data);
      if (response.success) {
        setShowForm(false);
        toast.success('Parcel created successfully');
        loadData();
      }
    } catch (error) {
      console.error('Failed to create parcel', error);
      toast.error('Failed to create parcel');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdate = async (data: ParcelCreate) => {
    if (!editingParcel) return;
    setIsSubmitting(true);
    try {
      const response = await landService.updateParcel(editingParcel.id, data);
      if (response.success) {
        setEditingParcel(null);
        setShowForm(false);
        toast.success('Parcel updated successfully');
        loadData();
      }
    } catch (error) {
      console.error('Failed to update parcel', error);
      toast.error('Failed to update parcel');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (parcel: Parcel) => {
    if (!confirm(`Delete parcel "${parcel.upi}"? This action cannot be undone.`)) return;
    try {
      const response = await landService.deleteParcel(parcel.id);
      if (response.success) {
        toast.success('Parcel deleted successfully');
        loadData();
      }
    } catch (error) {
      console.error('Failed to delete parcel', error);
      toast.error('Failed to delete parcel');
    }
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setEditingParcel(null);
  };

  // Handle search input change
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFilters(prev => ({ ...prev, search: e.target.value, page: 1 }));
  };

  // Handle page change
  const handlePageChange = (page: number) => {
    setFilters(prev => ({ ...prev, page }));
  };

  // Handle page size change
  const handlePageSizeChange = (size: number) => {
    setFilters(prev => ({ ...prev, size, page: 1 }));
  };

  // Retry function
  const handleRetry = () => {
    loadData();
  };

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
          <div className="text-center py-12 text-slate-400">Loading parcels...</div>
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
            parishes={parishes}
          />
        </Modal>
      </div>
    </PageContainer>
  );
}
