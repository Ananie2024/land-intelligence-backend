// User List Page with Full CRUD
// Land Intelligence System

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageContainer } from '@/components/layout/PageContainer';
import { Button } from '@/components/ui/Button';
import { Users, UserPlus } from 'lucide-react';
import { userService } from '@/services/userService';
import type { UserResponse, UserCreate } from '@/types/user';
import { UserTable } from '@/features/users/components/UserTable';
import { UserForm } from '@/features/users/components/UserForm';
import { Modal } from '@/components/ui/Modal';
import { Pagination } from '@/components/ui/Pagination';
import { useResourceList, useResourceMutation } from '@/hooks/useResourceList';

export default function UsersPage() {
  const navigate = useNavigate();
  const [showForm, setShowForm] = useState(false);
  const [editingUser, setEditingUser] = useState<UserResponse | null>(null);
  const [filters, setFilters] = useState({
    page: 1,
    size: 20,
    search: '',
  });

  const { data, isLoading, error, totalItems, totalPages, refetch } = useResourceList<UserResponse>(
    ['users'],
    (f) => userService.getUsers(f),
    filters,
    { defaultFilters: { page: 1, size: 20, search: '' } }
  );

  const createMutation = useResourceMutation(
    (data: UserCreate) => userService.createUser(data),
    { invalidateKeys: ['users'] }
  );

  const updateMutation = useResourceMutation(
    (data: UserCreate) => {
      if (!editingUser) throw new Error('No user selected');
      return userService.updateUser(editingUser.id, data);
    },
    { invalidateKeys: ['users'] }
  );

  const deleteMutation = useResourceMutation(
    (userId: string) => userService.deleteUser(userId),
    { invalidateKeys: ['users'] }
  );

  const users = data || [];

  const handleCreate = async (formData: UserCreate) => {
    await createMutation.mutate(formData);
    if (!createMutation.error) {
      setShowForm(false);
    }
  };

  const handleUpdate = async (formData: UserCreate) => {
    if (!editingUser) return;
    await updateMutation.mutate(formData);
    if (!updateMutation.error) {
      setEditingUser(null);
      setShowForm(false);
    }
  };

  const handleDelete = async (user: UserResponse) => {
    if (!confirm(`Delete user "${user.username}"? This action cannot be undone.`)) return;
    await deleteMutation.mutate(user.id);
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setEditingUser(null);
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
      title="User Registry Administration"
      subtitle="Manage access roles, active directories, and registrar profiles for Kigali Parishes."
      action={
        <Button 
          variant="primary" 
          leftIcon={<UserPlus className="w-4 h-4" />}
          onClick={() => setShowForm(true)}
        >
          Invite User
        </Button>
      }
    >
      <div className="space-y-6">
        <div className="flex items-center gap-3 p-4 rounded-xl border border-slate-800/80 bg-slate-900/30">
          <div className="p-2 rounded-lg bg-accent-500/10 text-accent-400">
            <Users className="w-5 h-5" />
          </div>
          <div className="text-xs flex-1">
            <p className="text-white font-bold">Role-Based Access Control Enforced</p>
            <p className="text-slate-400 mt-0.5">Only Administrators can manage permissions or assign parishes to client accounts.</p>
          </div>
          <div className="relative">
            <input
              type="text"
              placeholder="Search users..."
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
          <div className="text-center py-12 text-slate-400">Loading users...</div>
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
            <UserTable 
              users={users}
              onView={(user) => navigate(`/users/${user.id}`)}
              onEdit={(user) => {
                setEditingUser(user);
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
          title={editingUser ? 'Edit User' : 'Invite New User'}
          size="lg"
        >
          <UserForm
            user={editingUser}
            onSubmit={editingUser ? handleUpdate : handleCreate}
            isLoading={isSubmitting}
          />
        </Modal>
      </div>
    </PageContainer>
  );
}
