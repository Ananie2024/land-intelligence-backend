// User Form Component
// Land Intelligence System

import { useForm } from 'react-hook-form';
import { FormField } from '@/components/ui/FormField';
import type { UserResponse, UserCreate, UserRole } from '@/types/user';

interface UserFormProps {
  user?: UserResponse | null;
  onSubmit: (data: UserCreate) => Promise<void>;
  isLoading?: boolean;
}

export const UserForm: React.FC<UserFormProps> = ({ user, onSubmit, isLoading = false }) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<UserCreate>({
    defaultValues: user ? {
      email: user.email,
      username: user.username,
      full_name: user.full_name || '',
      role: user.role,
      parish_id: user.parish_id || undefined,
    } : undefined,
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <FormField
        label="Email"
        name="email"
        type="email"
        register={register}
        validation={{ required: 'Email is required' }}
        error={errors.email}
        disabled={isLoading}
      />

      <FormField
        label="Username"
        name="username"
        type="text"
        register={register}
        validation={{ required: 'Username is required' }}
        error={errors.username}
        disabled={isLoading}
      />

      <FormField
        label="Full Name"
        name="full_name"
        type="text"
        register={register}
        disabled={isLoading}
        optional
      />

      <FormField
        label="Role"
        name="role"
        register={register}
        validation={{ required: 'Role is required' }}
        error={errors.role}
        disabled={isLoading}
      >
        <option value="viewer">Viewer</option>
        <option value="client">Client</option>
        <option value="admin">Admin</option>
      </FormField>

      <FormField
        label="Parish"
        name="parish_id"
        register={register}
        disabled={isLoading}
        optional
      />

      <FormField
        label={`Password ${user ? '(leave blank to keep current)' : ''}`}
        name="password"
        type="password"
        register={register}
        disabled={isLoading}
        placeholder={!user ? 'Enter password' : undefined}
      />

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isLoading}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-500 disabled:opacity-50 transition-colors"
        >
          {isLoading ? 'Saving...' : user ? 'Update User' : 'Create User'}
        </button>
      </div>
    </form>
  );
};

export default UserForm;