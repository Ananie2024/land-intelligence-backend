// Parcel Form Component
// Land Intelligence System

import { useForm } from 'react-hook-form';
import type { Parcel, ParcelCreate } from '@/types/land';

interface ParcelFormProps {
  parcel?: Parcel | null;
  onSubmit: (data: ParcelCreate) => Promise<void>;
  isLoading?: boolean;
  parishes?: Array<{ id: string; name: string }>;
}

export const ParcelForm: React.FC<ParcelFormProps> = ({ parcel, onSubmit, isLoading = false, parishes = [] }) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ParcelCreate>({
    defaultValues: parcel ? {
      parcel_number: parcel.parcel_number,
      parish_id: parcel.parish_id,
      area_sqm: parcel.area_sqm,
      owner_name: parcel.owner_name,
      title_deed_number: parcel.title_deed_number || '',
      location_description: parcel.location_description || '',
      geometry_wkb: parcel.geometry_wkb || '',
    } : undefined,
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <label htmlFor="parcel_number" className="block text-sm font-medium text-gray-700">
          Parcel Number
        </label>
        <input
          {...register('parcel_number', { required: 'Parcel number is required' })}
          type="text"
          id="parcel_number"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          disabled={isLoading}
        />
        {errors.parcel_number && (
          <p className="mt-1 text-sm text-red-600">{errors.parcel_number.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="parish_id" className="block text-sm font-medium text-gray-700">
          Parish
        </label>
        <select
          {...register('parish_id', { required: 'Parish is required' })}
          id="parish_id"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          disabled={isLoading}
        >
          <option value="">Select a parish</option>
          {parishes.map((p) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="area_sqm" className="block text-sm font-medium text-gray-700">
          Area (m²)
        </label>
        <input
          {...register('area_sqm', { required: 'Area is required', valueAsNumber: true })}
          type="number"
          id="area_sqm"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          disabled={isLoading}
        />
        {errors.area_sqm && (
          <p className="mt-1 text-sm text-red-600">{errors.area_sqm.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="owner_name" className="block text-sm font-medium text-gray-700">
          Owner Name
        </label>
        <input
          {...register('owner_name', { required: 'Owner name is required' })}
          type="text"
          id="owner_name"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          disabled={isLoading}
        />
        {errors.owner_name && (
          <p className="mt-1 text-sm text-red-600">{errors.owner_name.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="title_deed_number" className="block text-sm font-medium text-gray-700">
          Title Deed Number
        </label>
        <input
          {...register('title_deed_number')}
          type="text"
          id="title_deed_number"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          disabled={isLoading}
        />
      </div>

      <div>
        <label htmlFor="location_description" className="block text-sm font-medium text-gray-700">
          Location Description
        </label>
        <textarea
          {...register('location_description')}
          id="location_description"
          rows={2}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          disabled={isLoading}
        />
      </div>

      <div>
        <label htmlFor="geometry_wkb" className="block text-sm font-medium text-gray-700">
          Geometry (WKB)
        </label>
        <textarea
          {...register('geometry_wkb')}
          id="geometry_wkb"
          rows={2}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 font-mono text-xs"
          disabled={isLoading}
          placeholder="Hex-encoded Well-Known Binary geometry (optional)"
        />
      </div>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isLoading}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
        >
          {isLoading ? 'Saving...' : parcel ? 'Update Parcel' : 'Create Parcel'}
        </button>
      </div>
    </form>
  );
};

export default ParcelForm;