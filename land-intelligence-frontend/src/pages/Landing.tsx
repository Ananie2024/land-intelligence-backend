import React from 'react';
import { useNavigate } from 'react-router-dom';
import { LogIn } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center text-center space-y-6">
      <h1 className="text-3xl font-extrabold text-white tracking-tight leading-tight">
        Welcome to the
        <br />
        <span className="bg-gradient-to-r from-primary-400 via-gold-400 to-burgundy-400 bg-clip-text text-transparent">
          Land Intelligence System
        </span>
      </h1>
      <p className="text-slate-400 text-sm max-w-sm leading-relaxed">
        A comprehensive digital platform for managing, tracking, and verifying land records across the Archdiocese of Kigali.
      </p>

      <div className="flex flex-col items-center gap-2 pt-2">
        <Button
          size="lg"
          variant="primary"
          onClick={() => navigate('/login')}
          className="min-w-[200px]"
          rightIcon={<LogIn className="w-4 h-4" />}
        >
          Sign In to Continue
        </Button>
        <span className="text-[10px] text-slate-400 font-medium">
          Secure access for authorized personnel only
        </span>
      </div>
    </div>
  );
}