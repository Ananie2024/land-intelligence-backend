// Parcel Detail Page
// Land Intelligence System

import { useParams } from 'react-router-dom';
import type { Parcel } from '@/types/land';
import { ParcelDetail } from '../components/ParcelDetail';

export const ParcelDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Parcel Details</h1>
      
      <div className="bg-white shadow rounded-lg p-6">
        <p className="text-gray-500">Parcel ID: {id}</p>
        <p className="mt-2 text-gray-500">Loading parcel details...</p>
      </div>
    </div>
  );
};

export default ParcelDetailPage;