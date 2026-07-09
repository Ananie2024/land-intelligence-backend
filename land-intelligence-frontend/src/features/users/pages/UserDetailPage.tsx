// User Detail Page
// Land Intelligence System

import { useParams } from 'react-router-dom';
import { RoleBadge } from '../components/RoleBadge';

export const UserDetailPage: React.FC = () => {
  // In a real implementation, this would fetch user data using the ID param
  const { id } = useParams<{ id: string }>();

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">User Details</h1>
      
      <div className="bg-white shadow rounded-lg p-6">
        <p className="text-gray-500">User ID: {id}</p>
        <p className="text-gray-500 mt-2">Loading user details...</p>
      </div>
    </div>
  );
};

export default UserDetailPage;