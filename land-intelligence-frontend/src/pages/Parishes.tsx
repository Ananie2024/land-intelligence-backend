// Parish List Page with Full CRUD - Integrated into main Parishes page
// Land Intelligence System

import { useState, useEffect } from 'react';
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

export default function Parishes() {
  const navigate = useNavigate();
  const [parishes, setParishes] = useState<Parish[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingParish, setEditingParish] = useState<Parish | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const loadParishes = async () => {
    setIsLoading(true);
    try {
      const response = await landService.getParishes();
      if (response.success && response.data) {
        setParishes(response.data);
      }
    } catch (error) {
      console.error('Failed to load parishes', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadParishes();
  }, []);

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
          <div className="text-sm">
            <p className="text-white font-bold">Parish Scopes</p>
            <p className="text-slate-400 mt-1">Manage diocese parish assets and assign registry permissions to parish clients.</p>
          </div>
        </div>

        {isLoading ? (
          <div className="text-center py-12 text-slate-400">Loading parishes...</div>
        ) : (
          <ParishTable 
            parishes={parishes}
            onView={(parish) => navigate(`/parishes/${parish.id}`)}
            onEdit={(parish) => {
              setEditingParish(parish);
              setShowForm(true);
            }}
            onDelete={handleDelete}
          />
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