import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export default function Unauthorized() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen w-screen bg-bg-base flex flex-col items-center justify-center p-6 relative font-sans">
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[500px] h-[500px] bg-danger/5 rounded-full blur-[150px] pointer-events-none" />
      <div className="absolute inset-0 bg-dot-pattern pointer-events-none opacity-[0.15] z-0" />

      <div className="text-center z-10 flex flex-col items-center gap-6 max-w-md">
        <div className="w-16 h-16 rounded-2xl bg-warning/10 border border-warning/20 flex items-center justify-center text-warning mb-2 animate-pulse">
          <ShieldAlert className="w-8 h-8" />
        </div>
        
        <h1 className="text-5xl font-black text-slate-800 m-0 tracking-tight leading-none bg-clip-text text-transparent bg-gradient-to-b from-slate-800 to-slate-400">
          Access Denied
        </h1>
        
        <h2 className="text-lg font-bold text-slate-600 tracking-tight leading-tight m-0">
          Insufficient Permissions
        </h2>
        
        <p className="text-slate-500 text-sm leading-relaxed">
          Your account credentials do not grant you read or write authorization for this administrative registry section.
        </p>

        <Button
          variant="secondary"
          className="mt-4"
          leftIcon={<ArrowLeft className="w-4 h-4" />}
          onClick={() => navigate('/dashboard')}
        >
          Return to Dashboard
        </Button>
      </div>
    </div>
  );
}
