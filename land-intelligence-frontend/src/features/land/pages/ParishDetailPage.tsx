// Parish Detail Page
// Land Intelligence System

import { useParams } from 'react-router-dom';
import type { Parish } from '@/types/land';
import { ParishDetail } from '../components/ParishDetail';

export const ParishDetailPage: React.FC = () => {
  // In a real implementation, this would fetch parish data using the ID param
  const { id } = useParams<{ id: string }>();

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Parish Details</h1>
      
      <div className="bg-white shadow rounded-lg p-6">
        <p className="text-gray-500">Parish ID: {id}</p>
        <p className="mt-2 text-gray-500">Loading parish details...</p>
      </div>
    </div>
  );
};

export default ParishDetailPage;