// User Table Component
// Land Intelligence System

import { Pencil, Trash2, Eye } from 'lucide-react';
import { RoleBadge } from './RoleBadge';
import type { UserResponse } from '@/types/user';

interface UserTableProps {
  users: UserResponse[];
  onEdit: (user: UserResponse) => void;
  onDelete: (user: UserResponse) => void;
  onView: (user: UserResponse) => void;
}

export const UserTable: React.FC<UserTableProps> = ({ users, onEdit, onDelete, onView }) => {
  if (!users || users.length === 0) {
    return (
      <div className="text-center py-12 text-slate-400">
        <p>No users found</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-slate-800">
        <thead className="bg-slate-900/60">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Name
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Email
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Username
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Role
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-slate-900/40 divide-y divide-slate-800">
          {users.map((user) => (
            <tr key={user.id} className="hover:bg-slate-900/60 transition-colors">
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-200">
                {user.full_name || user.username}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                {user.email}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                {user.username}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <RoleBadge role={user.role} />
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  user.is_active ? 'bg-success/20 text-success' : 'bg-red-500/20 text-red-400'
                }`}>
                  {user.is_active ? 'Active' : 'Inactive'}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div className="flex items-center justify-end gap-2">
                  <button
                    onClick={() => onView(user)}
                    className="text-slate-400 hover:text-slate-200"
                    title="View"
                  >
                    <Eye className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => onEdit(user)}
                    className="text-primary-400 hover:text-primary-300"
                    title="Edit"
                  >
                    <Pencil className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => onDelete(user)}
                    className="text-red-400 hover:text-red-300"
                    title="Delete"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default UserTable;
