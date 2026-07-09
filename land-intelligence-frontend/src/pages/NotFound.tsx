import React from 'react';
import { useNavigate } from 'react-router-dom';
import { HelpCircle, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export default function NotFound() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen w-screen bg-slate-950 flex flex-col items-center justify-center p-6 relative font-sans">
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[500px] h-[500px] bg-primary-600/10 rounded-full blur-[150px] pointer-events-none" />
      <div className="absolute inset-0 bg-dot-pattern pointer-events-none opacity-[0.15] z-0" />

      <div className="text-center z-10 flex flex-col items-center gap-6 max-w-md">
        <div className="w-16 h-16 rounded-2xl bg-danger/10 border border-danger/20 flex items-center justify-center text-danger mb-2">
          <HelpCircle className="w-8 h-8" />
        </div>
        
        <h1 className="text-8xl font-black text-white m-0 tracking-tight leading-none bg-clip-text text-transparent bg-gradient-to-b from-white to-slate-500">
          404
        </h1>
        
        <h2 className="text-xl font-bold text-white tracking-tight leading-tight m-0">
          Record Not Found
        </h2>
        
        <p className="text-slate-400 text-sm leading-relaxed">
          The parcel, record, or system page you are looking for does not exist or has been relocated to another register.
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
