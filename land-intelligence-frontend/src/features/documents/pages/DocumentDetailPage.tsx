// Document Detail Page
// Land Intelligence System

import { useParams } from 'react-router-dom';

export const DocumentDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Document Details</h1>
      
      <div className="bg-white shadow rounded-lg p-6">
        <p className="text-gray-500">Document ID: {id}</p>
        <p className="mt-2 text-gray-500">Loading document details...</p>
      </div>
    </div>
  );
};

export default DocumentDetailPage;