// Parish List Page with Full CRUD - Integrated into main Parishes page
// Land Intelligence System

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageContainer } from '@/components/layout/PageContainer';
import { Button } from '@/components/ui/Button';
import { Building2, Plus } from 'lucide-react';
import { landService } from '@/services/landService';
import type { Parish, ParishCreate } from '@/types/land';
import { ParishTable } from '@/features/land/components/ParishTable';
import { ParishForm } from '@/features/land/components/ParishForm';
import { Modal } from '@/components/ui/Modal';
import { Pagination } from '@/components/ui/Pagination';
import { useResourceList, useResourceMutation } from '@/hooks/useResourceList';
import toast from 'react-hot-toast';

export default function Parishes() {
  const navigate = useNavigate();
  const [showForm, setShowForm] = useState(false);
  const [editingParish, setEditingParish] = useState<Parish | null>(null);
  const [filters, setFilters] = useState({
    page: 1,
    size: 20,
    search: '',
  });

  const { data, isLoading, error, totalItems, totalPages, refetch } = useResourceList<Parish>(
    ['parishes'],
    (f) => landService.getParishes(f),
    filters,
    { defaultFilters: { page: 1, size: 20, search: '' } }
  );

  const createMutation = useResourceMutation(
    (data: ParishCreate) => landService.createParish(data),
    { invalidateKeys: ['parishes'] }
  );

  const updateMutation = useResourceMutation(
    (data: ParishCreate) => {
      if (!editingParish) throw new Error('No parish selected');
      return landService.updateParish(editingParish.id, data);
    },
    { invalidateKeys: ['parishes'] }
  );

  const deleteMutation = useResourceMutation(
    (id: string) => landService.deleteParish(id),
    { invalidateKeys: ['parishes'] }
  );

  const parishes = data || [];

  const handleCreate = async (data: ParishCreate) => {
    const success = await createMutation.mutate(data);
    if (success) {
      setShowForm(false);
      toast.success('Parish created successfully');
    }
  };

  const handleUpdate = async (data: ParishCreate) => {
    if (!editingParish) return;
    const success = await updateMutation.mutate(data);
    if (success) {
      setEditingParish(null);
      setShowForm(false);
      toast.success('Parish updated successfully');
    }
  };

  const handleDelete = async (parish: Parish) => {
    if (!confirm(`Delete parish "${parish.name}"? This action cannot be undone.`)) return;
    const success = await deleteMutation.mutate(parish.id);
    if (success) {
      toast.success('Parish deleted successfully');
    }
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setEditingParish(null);
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
      title="Parish Registries"
      subtitle="Parish administrative registry scopes within the Archdiocese of Kigali."
      action={
        <Button 
          variant="primary" 
          leftIcon={<Plus className="w-4 h-4" />}
          onClick={() => setShowForm(true)}
        >
          Add Parish
        </Button>
      }
    >
      <div className="space-y-6">
        <div className="flex items-center gap-3 p-6 rounded-xl border border-slate-800/80 bg-slate-900/30">
          <Building2 className="w-6 h-6 text-primary-400" />
          <div className="text-sm flex-1">
            <p className="text-white font-bold">Parish Scopes</p>
            <p className="text-slate-400 mt-1">Manage diocese parish assets and assign registry permissions to parish clients.</p>
          </div>
          <div className="relative">
            <input
              type="text"
              placeholder="Search parishes..."
              value={filters.search}
              onChange={handleSearchChange}
              className="pl-9 pr-3 py-2 w-64 bg-slate-900/60 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:border-primary-500"
            />
            <svg className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>

        {isLoading ? (
          <div className="text-center py-12 text-slate-400">Loading parishes...</div>
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
            <ParishTable 
              parishes={parishes}
              onView={(parish) => navigate(`/parishes/${parish.id}`)}
              onEdit={(parish) => {
                setEditingParish(parish);
                setShowForm(true);
              }}
              onDelete={handleDelete}
            />
            {totalPages > 1 && (
              <Pagination
                currentPage={filters.page}
                totalPages={totalPages}
                totalItems={totalItems}
                pageSize={filters.size}
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
          title={editingParish ? 'Edit Parish' : 'Add New Parish'}
          size="lg"
        >
          <ParishForm
            parish={editingParish}
            onSubmit={editingParish ? handleUpdate : handleCreate}
            isLoading={isSubmitting}
          />
        </Modal>
      </div>
    </PageContainer>
  );
}