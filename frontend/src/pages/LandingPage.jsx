import { useNavigate } from 'react-router-dom';
import Lightfall from '../components/Lightfall';
import { GlassButton } from '../components/ui/GlassButton';

export default function LandingPage() {
  const navigate = useNavigate();

  const handleAnalyzeNow = () => {
    navigate('/dashboard');
  };

  return (
    <div className="relative w-full h-screen bg-[#0f1117] overflow-hidden">
      {/* Lightfall Background */}
      <div className="absolute inset-0 w-full h-full z-0">
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

      {/* Content */}
      <div className="relative z-10 w-full h-full flex items-center justify-center">
        <div className="flex flex-col items-center justify-center gap-6 px-4">
          {/* Badge */}
          <div className="bg-[#1a1d27]/80 backdrop-blur-md border border-[#2a2d3a] text-[#6366f1] text-xs font-medium uppercase tracking-wider rounded-full px-4 py-1.5 shadow-[0_0_15px_rgba(99,102,241,0.1)]">
            Emotional AI Analysis
          </div>

          {/* Heading */}
          <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold text-white max-w-4xl text-center tracking-tight leading-tight">
            Understand Every <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">Emotional State</span>
          </h1>

          {/* Description */}
          <p className="text-lg md:text-xl text-slate-400 max-w-2xl text-center font-medium">
            Real-time Short, Mid and Long-Term emotional state tracking powered by EMA and PRISM scoring
          </p>

          {/* Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 mt-8">
            <GlassButton
              onClick={handleAnalyzeNow}
              size="xl"
              variant="primary"
            >
              Analyze Now
            </GlassButton>
            <GlassButton 
              size="xl"
              variant="secondary"
            >
              View Docs
            </GlassButton>
          </div>
        </div>
      </div>
    </div>
  );
}
