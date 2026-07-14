// Parish List Page with Full CRUD - Integrated into main Parishes page
// Land Intelligence System

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { PageContainer } from '@/components/layout/PageContainer';
import { Button } from '@/components/ui/Button';
import { Building2, Plus } from 'lucide-react';
import { landService } from '@/services/landService';
import type { Parish, ParishCreate } from '@/types/land';
import { ParishTable } from '@/features/land/components/ParishTable';
import { ParishForm } from '@/features/land/components/ParishForm';
import { Modal } from '@/components/ui/Modal';
import { Pagination } from '@/components/ui/Pagination';

export default function Parishes() {
  const navigate = useNavigate();
  const [parishes, setParishes] = useState<Parish[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingParish, setEditingParish] = useState<Parish | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [filters, setFilters] = useState({
    page: 1,
    size: 20,
    search: '',
  });
  const [totalItems, setTotalItems] = useState(0);
  const [totalPages, setTotalPages] = useState(0);

  const loadParishes = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await landService.getParishes(filters);
      if (response.success && response.data) {
        setParishes(response.data);
        setTotalItems(response.total ?? 0);
        setTotalPages(response.pages ?? 0);
      } else {
        setError(response.message || 'Failed to load parishes');
      }
    } catch (error) {
      console.error('Failed to load parishes', error);
      setError('Failed to load parishes');
      toast.error('Failed to load parishes');
    } finally {
      setIsLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadParishes();
  }, [loadParishes]);

  const handleCreate = async (data: ParishCreate) => {
    setIsSubmitting(true);
    try {
      const response = await landService.createParish(data);
      if (response.success) {
        setShowForm(false);
        toast.success('Parish created successfully');
        loadParishes();
      }
    } catch (error) {
      console.error('Failed to create parish', error);
      toast.error('Failed to create parish');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdate = async (data: ParishCreate) => {
    if (!editingParish) return;
    setIsSubmitting(true);
    try {
      const response = await landService.updateParish(editingParish.id, data);
      if (response.success) {
        setEditingParish(null);
        setShowForm(false);
        toast.success('Parish updated successfully');
        loadParishes();
      }
    } catch (error) {
      console.error('Failed to update parish', error);
      toast.error('Failed to update parish');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (parish: Parish) => {
    if (!confirm(`Delete parish "${parish.name}"? This action cannot be undone.`)) return;
    try {
      const response = await landService.deleteParish(parish.id);
      if (response.success) {
        toast.success('Parish deleted successfully');
        loadParishes();
      }
    } catch (error) {
      console.error('Failed to delete parish', error);
      toast.error('Failed to delete parish');
    }
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setEditingParish(null);
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
    loadParishes();
  };

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
