// User Profile Page
// Land Intelligence System

import { useAuth } from '@/features/authentication';

export const UserProfilePage: React.FC = () => {
  const { state } = useAuth();
  const user = state.user;

  if (!user) {
    return <div>Loading profile...</div>;
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">My Profile</h1>
      
      <div className="bg-white shadow rounded-lg p-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-500">Email</label>
            <p className="mt-1 text-lg text-gray-900">{user.email}</p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-500">Username</label>
            <p className="mt-1 text-lg text-gray-900">{user.username}</p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-500">Full Name</label>
            <p className="mt-1 text-lg text-gray-900">{user.full_name || '-'}</p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-500">Role</label>
            <p className="mt-1 text-lg text-gray-900 capitalize">{user.role}</p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-500">Last Login</label>
            <p className="mt-1 text-lg text-gray-900">
              {user.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}
            </p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-500">Member Since</label>
            <p className="mt-1 text-lg text-gray-900">
              {new Date(user.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfilePage;