// User Detail Component
// Land Intelligence System

import { User, Mail, UserCheck, Shield } from 'lucide-react';
import type { UserResponse } from '@/types/user';

interface UserDetailProps {
  user: UserResponse;
}

export const UserDetail: React.FC<UserDetailProps> = ({ user }) => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-900">{user.full_name || user.username}</h2>
        <p className="text-sm text-gray-500">@{user.username}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h3 className="text-sm font-medium text-gray-700">Email Address</h3>
          <p className="mt-1 text-gray-900">{user.email}</p>
        </div>
        <div>
          <h3 className="text-sm font-medium text-gray-700">System Role</h3>
          <p className="mt-1 text-gray-900 capitalize">{user.role}</p>
        </div>
        <div>
          <h3 className="text-sm font-medium text-gray-700">Account Status</h3>
          <p className="mt-1">
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {user.is_active ? 'Active' : 'Inactive'}
            </span>
          </p>
        </div>
        {user.parish_id && (
          <div>
            <h3 className="text-sm font-medium text-gray-700">Assigned Parish</h3>
            <p className="mt-1 text-gray-900">{user.parish_id}</p>
          </div>
        )}
        {user.last_login && (
          <div>
            <h3 className="text-sm font-medium text-gray-700">Last Login</h3>
            <p className="mt-1 text-gray-900">{new Date(user.last_login).toLocaleString()}</p>
          </div>
        )}
        {user.created_at && (
          <div>
            <h3 className="text-sm font-medium text-gray-700">Created At</h3>
            <p className="mt-1 text-gray-900">{new Date(user.created_at).toLocaleString()}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserDetail;