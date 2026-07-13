// Parish List Page
// Land Intelligence System

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { landService } from '@/services/landService';
import type { Parish } from '@/types/land';
import { ParishTable } from '../components/ParishTable';
import { ParishForm } from '../components/ParishForm';
import type { ParishCreate } from '@/types/land';

export const ParishListPage: React.FC = () => {
  const navigate = useNavigate();
  const [parishes, setParishes] = useState<Parish[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingParish, setEditingParish] = useState<Parish | null>(null);

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
    try {
      const response = await landService.createParish(data);
      if (response.success) {
        setShowForm(false);
        loadParishes();
      }
    } catch (error) {
      console.error('Failed to create parish', error);
    }
  };

  const handleUpdate = async (data: ParishCreate) => {
    if (!editingParish) return;
    try {
      const response = await landService.updateParish(editingParish.id, data);
      if (response.success) {
        setEditingParish(null);
        setShowForm(false);
        loadParishes();
      }
    } catch (error) {
      console.error('Failed to update parish', error);
    }
  };

  const handleDelete = async (parish: Parish) => {
    if (!confirm(`Delete parish "${parish.name}"?`)) return;
    try {
      const response = await landService.deleteParish(parish.id);
      if (response.success) {
        loadParishes();
      }
    } catch (error) {
      console.error('Failed to delete parish', error);
    }
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Parishes</h1>
        <button 
          onClick={() => setShowForm(true)}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        >
          Add Parish
        </button>
      </div>
      
{isLoading ? (
        <div className="text-center py-12">Loading parishes...</div>
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
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full">
            <h2 className="text-lg font-bold mb-4">
              {editingParish ? 'Edit Parish' : 'Create Parish'}
            </h2>
            <ParishForm
              parish={editingParish}
              onSubmit={editingParish ? handleUpdate : handleCreate}
              isLoading={isLoading}
            />
            <button
              onClick={() => {
                setShowForm(false);
                setEditingParish(null);
              }}
              className="mt-4 px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ParishListPage;