// Parcel List Page with Full CRUD
// Land Intelligence System

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageContainer } from '@/components/layout/PageContainer';
import { Button } from '@/components/ui/Button';
import { MapPin, Plus } from 'lucide-react';
import { landService } from '@/services/landService';
import type { Parcel, ParcelCreate } from '@/types/land';
import { ParcelTable } from '@/features/land/components/ParcelTable';
import { ParcelForm } from '@/features/land/components/ParcelForm';
import { Modal } from '@/components/ui/Modal';
import { toast } from 'react-hot-toast';

export default function Parcels() {
  const navigate = useNavigate();
  const [parcels, setParcels] = useState<Parcel[]>([]);
  const [parishes, setParishes] = useState<Array<{ id: string; name: string }>>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingParcel, setEditingParcel] = useState<Parcel | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [parcelsResponse, parishesResponse] = await Promise.all([
        landService.getParcels(),
        landService.getParishes(),
      ]);
      
      if (parcelsResponse.success && parcelsResponse.data) {
        setParcels(parcelsResponse.data);
      }
      if (parishesResponse.success && parishesResponse.data) {
        setParishes(parishesResponse.data.map(p => ({ id: p.id, name: p.name })));
      }
    } catch (error) {
      console.error('Failed to load data', error);
      toast.error('Failed to load parcels');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

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
          <div className="text-xs">
            <p className="text-white font-bold">GIS Coordinates Active</p>
            <p className="text-slate-500 mt-0.5">Click any parcel record to open structural documents or display boundary pins.</p>
          </div>
        </div>

        {isLoading ? (
          <div className="text-center py-12 text-slate-400">Loading parcels...</div>
        ) : (
          <ParcelTable 
            parcels={parcels}
            onView={(parcel) => navigate(`/parcels/${parcel.id}`)}
            onEdit={(parcel) => {
              setEditingParcel(parcel);
              setShowForm(true);
            }}
            onDelete={handleDelete}
          />
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