// User Detail Page
// Land Intelligence System

import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { userService } from '@/services/userService';
import { UserDetail } from '../components/UserDetail';
import { Loader2, AlertCircle } from 'lucide-react';
import type { UserResponse } from '@/types/user';

export const UserDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    const loadUser = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await userService.getUserById(id);
        if (response.success && response.data) {
          setUser(response.data);
        } else {
          setError(response.message || 'Failed to load user');
        }
      } catch (err) {
        console.error('Failed to load user:', err);
        setError('Failed to load user details');
      } finally {
        setIsLoading(false);
      }
    };

    loadUser();
  }, [id]);

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[300px]">
        <div className="flex items-center gap-3 text-slate-400">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span>Loading user details...</span>
        </div>
      </div>
    );
  }

  if (error || !user) {
    return (
      <div className="p-6">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center gap-2 text-red-500 mb-2">
            <AlertCircle className="h-5 w-5" />
            <span className="font-medium">Error</span>
          </div>
          <p className="text-gray-500">{error || 'User not found'}</p>
          <p className="text-gray-400 text-sm mt-2">User ID: {id}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="bg-white shadow rounded-lg p-6">
        <UserDetail user={user} />
      </div>
    </div>
  );
};

export default UserDetailPage;