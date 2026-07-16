import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { KeyRound, Mail, AlertCircle, Eye, EyeOff } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useAuth } from '@/features/authentication';

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, state } = useAuth();
  
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // Redirect to the page the user was trying to access, or home
  useEffect(() => {
    if (state.isAuthenticated) {
      const from = (location.state as any)?.from?.pathname || '/dashboard';
      navigate(from, { replace: true });
    }
  }, [state.isAuthenticated, navigate, location]);

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await login({ username, password });
  };

  return (
    <form onSubmit={handleLoginSubmit} className="space-y-5">
      {state.error && (
        <div className="flex items-start gap-2.5 p-3 rounded-lg bg-danger/10 border border-danger/25 text-danger text-xs leading-normal">
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <span>{state.error}</span>
        </div>
      )}

      {/* Username / Email field */}
      <div className="space-y-1.5">
        <label className="text-xs font-bold text-slate-300 block">Username or Email</label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
            <Mail className="w-4 h-4" />
          </div>
          <input
            type="text"
            required
            placeholder="Enter your username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full bg-slate-950/60 border border-slate-800 rounded-lg py-2.5 pl-10 pr-4 text-sm text-white placeholder-slate-600 outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 transition-all"
          />
        </div>
      </div>

      {/* Password field */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between">
          <label className="text-xs font-bold text-slate-300 block">Password</label>
          <a href="#" className="text-[10px] font-bold text-primary-400 hover:text-primary-300 transition-colors">
            Forgot?
          </a>
        </div>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
            <KeyRound className="w-4 h-4" />
          </div>
          <input
            type={showPassword ? 'text' : 'password'}
            required
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full bg-slate-950/60 border border-slate-800 rounded-lg py-2.5 pl-10 pr-10 text-sm text-white placeholder-slate-600 outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 transition-all"
          />
           <button
             type="button"
             onClick={() => setShowPassword(!showPassword)}
             className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-500 hover:text-slate-300 transition-colors"
             aria-label={showPassword ? 'Hide password' : 'Show password'}
           >
             {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
           </button>
        </div>
      </div>

      {/* Submit Button */}
      <Button
        type="submit"
        isLoading={state.isLoading}
        className="w-full mt-2"
        size="lg"
      >
        Sign In
      </Button>
    </form>
  );
}