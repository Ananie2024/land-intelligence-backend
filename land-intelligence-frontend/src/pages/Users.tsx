import React, { useState, useEffect } from 'react';
import { PageContainer } from '@/components/layout/PageContainer';
import { Table, Column } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { Users, UserPlus, Loader2 } from 'lucide-react';
import { userService } from '@/services/userService';
import { UserResponse } from '@/types/user';

export default function UsersPage() {
  const [users, setUsers] = useState<UserResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadUsers = async () => {
      try {
        const response = await userService.getUsers();
        if (response.success && response.data) {
          setUsers(response.data);
        }
      } catch (error) {
        console.error('Failed to load users', error);
      } finally {
        setIsLoading(false);
      }
    };
    loadUsers();
  }, []);

  const columns: Column<UserResponse>[] = [
    {
      key: 'username',
      header: 'Username',
      render: (row) => <span className="text-white font-bold">{row.username}</span>,
    },
    {
      key: 'email',
      header: 'Email Address',
    },
    {
      key: 'role',
      header: 'System Role',
      render: (row) => (
        <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider bg-slate-800 text-slate-300 border border-slate-700/80">
          {row.role}
        </span>
      ),
    },
    {
      key: 'is_active',
      header: 'Status',
      render: (row) => (
        <span className={`inline-flex items-center gap-1.5 text-xs font-semibold ${row.is_active ? 'text-success' : 'text-slate-500'}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${row.is_active ? 'bg-success animate-pulse' : 'bg-slate-600'}`} />
          {row.is_active ? 'Active' : 'Disabled'}
        </span>
      ),
    },
    {
      key: 'last_login',
      header: 'Last Session Login',
      render: (row) => (
        <span className="text-slate-400">
          {row.last_login ? new Date(row.last_login).toLocaleString() : '-'}
        </span>
      ),
    },
  ];

  return (
    <PageContainer
      title="User Registry Administration"
      subtitle="Manage access roles, active directories, and registrar profiles for Kigali Parishes."
      action={
        <Button variant="primary" leftIcon={<UserPlus className="w-4 h-4" />}>
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
          <div className="flex justify-center py-12">
            <Loader2 className="w-8 h-8 text-primary-400 animate-spin" />
          </div>
        ) : users.length === 0 ? (
          <div className="text-center py-12 text-slate-400">No users found</div>
        ) : (
          <Table columns={columns} data={users} />
        )}
      </div>
    </PageContainer>
  );
}
