import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '../context/AuthContext';
import { GlassCard } from '../components/ui/GlassCard';

export default function LoginPage() {
  const navigate = useNavigate();
  const { user, loginWithGoogle } = useAuth();

  // If already logged in, redirect to dashboard
  useEffect(() => {
    if (user) {
      navigate('/dashboard');
    }
  }, [user, navigate]);

  const handleSuccess = async (credentialResponse) => {
    try {
      await loginWithGoogle(credentialResponse.credential);
      navigate('/dashboard');
    } catch (error) {
      alert('Login failed. Please try again.');
    }
  };

  const handleError = () => {
    console.error('Google Login Failed');
    alert('Google Login Failed');
  };

  return (
    <div className="flex h-screen mesh-bg items-center justify-center font-sans overflow-hidden">
      
      {/* Animated background elements */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-[100px] animate-pulse"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-[100px] animate-pulse" style={{ animationDelay: '2s' }}></div>

      <div className="z-10 w-full max-w-md px-6">
        <GlassCard className="animate-in fade-in slide-in-from-bottom-8 duration-1000 flex flex-col items-center py-10 px-8 text-center border border-white/10 shadow-2xl backdrop-blur-2xl bg-white/5">
          
          <div className="w-16 h-16 rounded-2xl bg-indigo-500/20 flex items-center justify-center border border-indigo-500/30 shadow-[0_0_30px_rgba(99,102,241,0.2)] mb-6">
            <div className="w-6 h-6 bg-indigo-400 rounded-full animate-pulse shadow-[0_0_15px_rgba(99,102,241,0.8)]"></div>
          </div>
          
          <h1 className="text-3xl font-bold text-white tracking-tight mb-2">Welcome Back</h1>
          <p className="text-slate-400 text-sm mb-8 leading-relaxed max-w-[250px]">
            Sign in to access your emotional state tracking dashboard.
          </p>

          <div className="w-full flex justify-center py-2 relative">
            <GoogleLogin
              onSuccess={handleSuccess}
              onError={handleError}
              useOneTap
              theme="filled_black"
              shape="pill"
            />
          </div>

        </GlassCard>
      </div>
    </div>
  );
}
