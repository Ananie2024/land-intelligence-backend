// User List Page
// Land Intelligence System

import { useState } from 'react';
import { UserTable } from '../components/UserTable';
import type { UserResponse } from '@/types/user';

export const UserListPage: React.FC = () => {
  const [users] = useState<UserResponse[]>([]);
  const [isLoading] = useState(false);

  const handleView = (user: UserResponse) => {
    console.log('View user:', user);
  };

  const handleEdit = (user: UserResponse) => {
    console.log('Edit user:', user);
  };

  const handleDelete = (user: UserResponse) => {
    console.log('Delete user:', user);
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Users</h1>
        <button className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
          Add User
        </button>
      </div>
      
      {isLoading ? (
        <div className="text-center py-12">Loading users...</div>
      ) : (
        <UserTable 
          users={users}
          onView={handleView}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
      )}
    </div>
  );
};

export default UserListPage;