// Logout Button Component
// Land Intelligence System

import { LogOut } from 'lucide-react';
import { useNavigate } from 'react-router';
import { useAuth } from '../store/authStore';

interface LogoutButtonProps {
  className?: string;
}

export const LogoutButton: React.FC<LogoutButtonProps> = ({ className = '' }) => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  return (
    <button
      onClick={handleLogout}
      className={`flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md ${className}`}
    >
      <LogOut className="h-4 w-4" />
      Sign out
    </button>
  );
};

export default LogoutButton;