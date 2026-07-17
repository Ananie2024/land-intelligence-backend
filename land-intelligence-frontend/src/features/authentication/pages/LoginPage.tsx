// Login Page
// Land Intelligence System

import { useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAuth } from '../store/authStore';
import type { LoginCredentials } from '../types/auth';

export const LoginPage: React.FC = () => {
  const { login, state } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginCredentials>();

  const onSubmit = async (data: LoginCredentials) => {
    await login(data);
    if (state.isAuthenticated) {
      // Redirect to the page the user was trying to access, or home
      const from = (location.state as any)?.from?.pathname || '/';
      navigate(from, { replace: true });
    }
  };

  const inputClasses = 'appearance-none rounded-none relative block w-full px-3 py-2 border border-slate-700 placeholder-slate-500 text-white rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm bg-slate-800/50';

  return (
    <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
      <div className="rounded-md shadow-sm -space-y-px">
        <div>
          <label htmlFor="username" className="sr-only">
            Username
          </label>
          <input
            {...register('username', { required: 'Username is required' })}
            type="text"
            id="username"
            className={inputClasses}
            placeholder="Username"
          />
          {errors.username && (
            <p className="mt-1 text-sm text-red-400">{errors.username.message}</p>
          )}
        </div>
        <div>
          <label htmlFor="password" className="sr-only">
            Password
          </label>
          <input
            {...register('password', { required: 'Password is required' })}
            type="password"
            id="password"
            className={inputClasses}
            placeholder="Password"
          />
          {errors.password && (
            <p className="mt-1 text-sm text-red-400">{errors.password.message}</p>
          )}
        </div>
      </div>

      {state.error && (
        <div className="rounded-md bg-danger/10 p-4">
          <p className="text-sm text-danger">{state.error}</p>
        </div>
      )}

      <div>
        <button
          type="submit"
          disabled={state.isLoading}
          className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 focus:ring-offset-slate-900 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {state.isLoading ? 'Signing in...' : 'Sign in'}
        </button>
      </div>
    </form>
  );
};

export default LoginPage;