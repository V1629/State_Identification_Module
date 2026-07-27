import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import { Mail, Lock, UserPlus, User } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { GlassCard } from '../components/ui/GlassCard';
import { GlassButton } from '../components/ui/GlassButton';
import Lightfall from '../components/Lightfall';

export default function SignupPage() {
  const navigate = useNavigate();
  const { user, loginWithGoogle, register } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // If already logged in, redirect to dashboard
  useEffect(() => {
    if (user) {
      navigate('/dashboard');
    }
  }, [user, navigate]);

  const handleEmailSignup = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register(name, email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      await loginWithGoogle(credentialResponse.credential, true); // true = isSignup
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Google Signup failed. Please try again.');
    }
  };

  return (
    <div className="relative w-full h-screen bg-[#0f1117] overflow-hidden flex items-center justify-center font-sans">
      {/* Lightfall Background */}
      <div className="absolute inset-0 w-full h-full z-0 pointer-events-none">
        <Lightfall
          colors={['#6366f1', '#818cf8', '#4f46e5']}
          backgroundColor="#0f1117"
          speed={0.4}
          streakCount={4}
          streakWidth={1}
          streakLength={1}
          glow={0.8}
          density={0.5}
          opacity={0.6}
          mouseInteraction={true}
          mouseStrength={0.5}
          mouseRadius={1}
        />
      </div>

      <div className="z-10 w-full max-w-md px-6">
        <GlassCard className="animate-in fade-in slide-in-from-bottom-8 duration-1000 flex flex-col items-center py-10 px-8 border border-white/10 shadow-2xl backdrop-blur-2xl bg-[#1a1d27]/70">
          
          <div className="w-16 h-16 rounded-2xl bg-indigo-500/20 flex items-center justify-center border border-indigo-500/30 shadow-[0_0_30px_rgba(99,102,241,0.2)] mb-6">
            <UserPlus className="w-8 h-8 text-indigo-400" />
          </div>
          
          <h1 className="text-3xl font-bold text-white tracking-tight mb-2">Create Account</h1>
          <p className="text-slate-400 text-sm mb-8 text-center leading-relaxed">
            Join us to start tracking and analyzing your emotional states.
          </p>

          {error && (
            <div className="w-full bg-red-500/10 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg mb-6 text-sm text-center">
              {error}
            </div>
          )}

          <form onSubmit={handleEmailSignup} className="w-full flex flex-col gap-4 mb-6">
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Full Name"
                required
                className="w-full bg-[#0f1117]/50 border border-[#2a2d3a] rounded-xl py-3 pl-10 pr-4 text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
              />
            </div>

            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email address"
                required
                className="w-full bg-[#0f1117]/50 border border-[#2a2d3a] rounded-xl py-3 pl-10 pr-4 text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
              />
            </div>
            
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                required
                className="w-full bg-[#0f1117]/50 border border-[#2a2d3a] rounded-xl py-3 pl-10 pr-4 text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
              />
            </div>

            <GlassButton type="submit" variant="primary" className="w-full justify-center mt-2" disabled={loading}>
              {loading ? 'Creating account...' : 'Sign Up'}
            </GlassButton>
          </form>

          <div className="w-full flex items-center gap-4 mb-6">
            <div className="h-px bg-[#2a2d3a] flex-1"></div>
            <span className="text-slate-500 text-sm">or</span>
            <div className="h-px bg-[#2a2d3a] flex-1"></div>
          </div>

          <div className="w-full flex justify-center mb-6">
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={() => setError('Google Signup Failed')}
              theme="filled_black"
              shape="pill"
            />
          </div>

          <p className="text-slate-400 text-sm">
            Already have an account?{' '}
            <Link to="/login" className="text-indigo-400 hover:text-indigo-300 transition-colors font-medium">
              Sign in
            </Link>
          </p>

        </GlassCard>
      </div>
    </div>
  );
}
