import { useNavigate } from 'react-router-dom';
import Lightfall from '../components/Lightfall';

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
          <div className="bg-[#1a1d27] border border-[#2a2d3a] text-[#6366f1] text-xs rounded-full px-3 py-1">
            Emotional AI Analysis
          </div>

          {/* Heading */}
          <h1 className="text-5xl font-bold text-white max-w-2xl text-center">
            Understand Every Emotional State
          </h1>

          {/* Description */}
          <p className="text-lg text-slate-400 max-w-xl text-center">
            Real-time Short, Mid and Long-Term emotional state tracking powered by EMA and PRISM scoring
          </p>

          {/* Buttons */}
          <div className="flex gap-4 mt-4">
            <button
              onClick={handleAnalyzeNow}
              className="bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg px-6 py-3 transition-colors"
            >
              Analyze Now
            </button>
            <button className="border border-slate-700 text-white rounded-lg px-6 py-3 bg-transparent hover:bg-slate-800 transition-colors">
              View Docs
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
