// User List Page with Full CRUD
// Land Intelligence System

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageContainer } from '@/components/layout/PageContainer';
import { Button } from '@/components/ui/Button';
import { Users, UserPlus } from 'lucide-react';
import { userService } from '@/services/userService';
import type { UserResponse, UserCreate } from '@/types/user';
import { UserTable } from '@/features/users/components/UserTable';
import { UserForm } from '@/features/users/components/UserForm';
import { Modal } from '@/components/ui/Modal';
import { toast } from 'react-hot-toast';

export default function UsersPage() {
  const navigate = useNavigate();
  const [users, setUsers] = useState<UserResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingUser, setEditingUser] = useState<UserResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const loadUsers = async () => {
    setIsLoading(true);
    try {
      const response = await userService.getUsers();
      if (response.success && response.data) {
        setUsers(response.data);
      }
    } catch (error) {
      console.error('Failed to load users', error);
      toast.error('Failed to load users');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleCreate = async (data: UserCreate) => {
    setIsSubmitting(true);
    try {
      const response = await userService.createUser(data);
      if (response.success) {
        setShowForm(false);
        toast.success('User created successfully');
        loadUsers();
      }
    } catch (error) {
      console.error('Failed to create user', error);
      toast.error('Failed to create user');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdate = async (data: UserCreate) => {
    if (!editingUser) return;
    setIsSubmitting(true);
    try {
      const response = await userService.updateUser(editingUser.id, data);
      if (response.success) {
        setEditingUser(null);
        setShowForm(false);
        toast.success('User updated successfully');
        loadUsers();
      }
    } catch (error) {
      console.error('Failed to update user', error);
      toast.error('Failed to update user');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (user: UserResponse) => {
    if (!confirm(`Delete user "${user.username}"? This action cannot be undone.`)) return;
    try {
      const response = await userService.deleteUser(user.id);
      if (response.success) {
        toast.success('User deleted successfully');
        loadUsers();
      }
    } catch (error) {
      console.error('Failed to delete user', error);
      toast.error('Failed to delete user');
    }
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setEditingUser(null);
  };

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
          <div className="text-xs">
            <p className="text-white font-bold">Role-Based Access Control Enforced</p>
            <p className="text-slate-500 mt-0.5">Only Administrators can manage permissions or assign parishes to client accounts.</p>
          </div>
        </div>

        {isLoading ? (
          <div className="text-center py-12 text-slate-400">Loading users...</div>
        ) : (
          <UserTable 
            users={users}
            onView={(user) => navigate(`/users/${user.id}`)}
            onEdit={(user) => {
              setEditingUser(user);
              setShowForm(true);
            }}
            onDelete={handleDelete}
          />
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