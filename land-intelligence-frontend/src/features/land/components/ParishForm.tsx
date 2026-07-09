// Parish Form Component
// Land Intelligence System

import { useForm } from 'react-hook-form';
import { MapPin } from 'lucide-react';
import type { Parish, ParishCreate } from '@/types/land';

interface ParishFormProps {
  parish?: Parish | null;
  onSubmit: (data: ParishCreate) => Promise<void>;
  isLoading?: boolean;
}

export const ParishForm: React.FC<ParishFormProps> = ({ parish, onSubmit, isLoading = false }) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ParishCreate>();

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700">
          Parish Name
        </label>
        <input
          {...register('name', { required: 'Name is required' })}
          type="text"
          id="name"
          defaultValue={parish?.name}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          disabled={isLoading}
        />
        {errors.name && (
          <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="code" className="block text-sm font-medium text-gray-700">
          Parish Code
        </label>
        <input
          {...register('code', { required: 'Code is required' })}
          type="text"
          id="code"
          defaultValue={parish?.code}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          disabled={isLoading}
        />
        {errors.code && (
          <p className="mt-1 text-sm text-red-600">{errors.code.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700">
          Description
        </label>
        <textarea
          {...register('description')}
          id="description"
          defaultValue={parish?.description || ''}
          rows={3}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          disabled={isLoading}
        />
      </div>

      <div>
        <label htmlFor="contact_email" className="block text-sm font-medium text-gray-700">
          Contact Email
        </label>
        <input
          {...register('contact_email')}
          type="email"
          id="contact_email"
          defaultValue={parish?.contact_email || ''}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          disabled={isLoading}
        />
      </div>

      <div>
        <label htmlFor="contact_phone" className="block text-sm font-medium text-gray-700">
          Contact Phone
        </label>
        <input
          {...register('contact_phone')}
          type="tel"
          id="contact_phone"
          defaultValue={parish?.contact_phone || ''}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          disabled={isLoading}
        />
      </div>

      <div>
        <label htmlFor="boundary_wkb" className="block text-sm font-medium text-gray-700">
          Boundary (WKB)
        </label>
        <textarea
          {...register('boundary_wkb')}
          id="boundary_wkb"
          defaultValue={parish?.boundary_wkb || ''}
          rows={3}
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
          {isLoading ? 'Saving...' : parish ? 'Update Parish' : 'Create Parish'}
        </button>
      </div>
    </form>
  );
};

export default ParishForm;