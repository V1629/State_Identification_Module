import { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { GlassCard } from '../components/ui/GlassCard';
import { GlassButton } from '../components/ui/GlassButton';
import { Textarea } from '../components/ui/textarea';
import { useAnalyze } from '../hooks/useAnalyze';
import { useEmaScores } from '../hooks/useEmaScores';
import { useStates } from '../hooks/useStates';

const chartData = [
  { time: '00:00', shortTerm: 5.2, midTerm: 5.0, longTerm: 5.1 },
  { time: '04:00', shortTerm: 6.1, midTerm: 5.3, longTerm: 5.2 },
  { time: '08:00', shortTerm: 7.4, midTerm: 6.2, longTerm: 5.5 },
  { time: '12:00', shortTerm: 6.8, midTerm: 6.5, longTerm: 5.8 },
  { time: '16:00', shortTerm: 7.2, midTerm: 6.8, longTerm: 6.1 },
  { time: '20:00', shortTerm: 6.5, midTerm: 6.7, longTerm: 6.2 },
  { time: '23:00', shortTerm: 7.4, midTerm: 7.0, longTerm: 6.5 },
  { time: '24:00', shortTerm: 7.4, midTerm: 7.1, longTerm: 6.6 },
];

export default function DashboardPage() {
  const [message, setMessage] = useState('');
  const { analyze, loading: analyzing, error: analyzeError, result } = useAnalyze();
  const { states, loading: statesLoading } = useStates();
  const { data, chartData: emaChartData, loading: chartLoading } = useEmaScores();

  const handleAnalyze = async () => {
    if (!message.trim()) {
      alert('Please enter a message to analyze');
      return;
    }

    try {
      await analyze(message);
      setMessage(''); // Clear input after successful analysis
    } catch (err) {
      console.error('Analysis failed:', err);
    }
  };

  return (
    <div className="flex h-screen mesh-bg text-slate-100 overflow-hidden font-sans">
      {/* Sidebar - Glassmorphism */}
      <div className="fixed left-0 top-0 h-screen w-64 glass-panel border-l-0 rounded-l-none border-y-0 bg-white/5 dark:bg-[#0f1117]/30 flex flex-col z-20">
        {/* Header */}
        <div className="px-6 pt-8 pb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/20 flex items-center justify-center border border-indigo-500/30 shadow-[0_0_15px_rgba(99,102,241,0.2)]">
              <div className="w-3 h-3 bg-indigo-400 rounded-full animate-pulse"></div>
            </div>
            <h1 className="text-white font-bold text-2xl tracking-tight">SIM</h1>
          </div>
          <p className="text-slate-400/80 text-xs font-medium uppercase tracking-widest pl-1">State Identification</p>
        </div>

        {/* Nav Items */}
        <nav className="flex-1 space-y-2 px-3">
          <div className="px-4 py-3 bg-indigo-500/15 text-indigo-200 rounded-xl text-sm font-medium border border-indigo-500/20 shadow-inner backdrop-blur-sm transition-all">
            Dashboard
          </div>
          <div className="px-4 py-3 text-slate-400 text-sm cursor-pointer hover:bg-white/5 hover:text-slate-200 rounded-xl transition-all">
            History
          </div>
          <div className="px-4 py-3 text-slate-400 text-sm cursor-pointer hover:bg-white/5 hover:text-slate-200 rounded-xl transition-all">
            Configuration
          </div>
        </nav>

        {/* Footer Version */}
        <div className="px-6 pb-8 text-slate-500/70 text-xs font-medium">v1.0.0</div>
      </div>

      {/* Main Content */}
      <div className="ml-64 w-[calc(100%-256px)] h-full overflow-y-auto relative z-10 custom-scrollbar">
        {/* Topbar */}
        <div className="sticky top-0 z-30 px-8 py-5 flex justify-between items-center glass-panel border-x-0 border-t-0 rounded-none bg-white/5 dark:bg-[#0f1117]/30 backdrop-blur-xl">
          <h2 className="text-white font-semibold text-xl tracking-tight">Emotional State Dashboard</h2>
          <div className="flex items-center gap-2 bg-emerald-500/10 text-emerald-300 text-xs font-medium rounded-full px-4 py-1.5 border border-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.1)]">
            <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse shadow-[0_0_5px_rgba(16,185,129,0.8)]"></div>
            System Active
          </div>
        </div>

        {/* Content */}
        <div className="p-8 space-y-6 max-w-7xl mx-auto">
          {/* Section 1: Stat Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Short-Term State */}
            <GlassCard className="animate-in fade-in slide-in-from-bottom-4 duration-500 flex flex-col justify-between">
              <div>
                <p className="text-slate-400/80 text-sm font-medium uppercase tracking-wider mb-2">Short-Term State</p>
                <p className="text-white text-3xl font-bold mb-4 tracking-tight">
                  {result?.short_term_state || states?.short_term || 'Neutral'}
                </p>
              </div>
              <div className="inline-flex w-fit items-center bg-indigo-500/15 text-indigo-300 text-xs font-medium rounded-full px-3 py-1 border border-indigo-500/20">
                Current
              </div>
            </GlassCard>

            {/* Mid-Term State */}
            <GlassCard className="animate-in fade-in slide-in-from-bottom-4 duration-700 flex flex-col justify-between">
              <div>
                <p className="text-slate-400/80 text-sm font-medium uppercase tracking-wider mb-2">Mid-Term State</p>
                <p className="text-white text-3xl font-bold mb-4 tracking-tight">
                  {result?.mid_term_state || states?.mid_term || 'Stable'}
                </p>
              </div>
              <div className="inline-flex w-fit items-center bg-emerald-500/15 text-emerald-300 text-xs font-medium rounded-full px-3 py-1 border border-emerald-500/20">
                Trending
              </div>
            </GlassCard>

            {/* Long-Term State */}
            <GlassCard className="animate-in fade-in slide-in-from-bottom-4 duration-1000 flex flex-col justify-between">
              <div>
                <p className="text-slate-400/80 text-sm font-medium uppercase tracking-wider mb-2">Long-Term State</p>
                <p className="text-white text-3xl font-bold mb-4 tracking-tight">
                  {result?.long_term_state || states?.long_term || 'Positive'}
                </p>
              </div>
              <div className="inline-flex w-fit items-center bg-rose-500/15 text-rose-300 text-xs font-medium rounded-full px-3 py-1 border border-rose-500/20">
                Overall
              </div>
            </GlassCard>
          </div>

          {/* Section 2: EMA Score Chart */}
          <GlassCard className="animate-in fade-in slide-in-from-bottom-6 duration-1000 delay-100">
            <h3 className="text-white font-semibold text-lg tracking-tight mb-6">EMA Score Timeline</h3>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                  <XAxis 
                    dataKey="time" 
                    stroke="rgba(255,255,255,0.4)" 
                    style={{ fontSize: '12px', fontWeight: 500 }} 
                    tickLine={false}
                    axisLine={false}
                    dy={10}
                  />
                  <YAxis 
                    stroke="rgba(255,255,255,0.4)" 
                    style={{ fontSize: '12px', fontWeight: 500 }} 
                    domain={[0, 10]} 
                    tickLine={false}
                    axisLine={false}
                    dx={-10}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(15, 17, 23, 0.8)',
                      backdropFilter: 'blur(12px)',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '12px',
                      boxShadow: '0 8px 32px rgba(0,0,0,0.4)'
                    }}
                    itemStyle={{ fontWeight: 500 }}
                    labelStyle={{ color: '#94a3b8', marginBottom: '4px', fontWeight: 600 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="shortTerm"
                    stroke="#818cf8"
                    strokeWidth={3}
                    dot={{ r: 4, fill: '#818cf8', strokeWidth: 0 }}
                    activeDot={{ r: 6, fill: '#fff', stroke: '#818cf8', strokeWidth: 2 }}
                    name="Short-Term"
                  />
                  <Line
                    type="monotone"
                    dataKey="midTerm"
                    stroke="#34d399"
                    strokeWidth={3}
                    dot={{ r: 4, fill: '#34d399', strokeWidth: 0 }}
                    activeDot={{ r: 6, fill: '#fff', stroke: '#34d399', strokeWidth: 2 }}
                    name="Mid-Term"
                  />
                  <Line
                    type="monotone"
                    dataKey="longTerm"
                    stroke="#fb7185"
                    strokeWidth={3}
                    dot={{ r: 4, fill: '#fb7185', strokeWidth: 0 }}
                    activeDot={{ r: 6, fill: '#fff', stroke: '#fb7185', strokeWidth: 2 }}
                    name="Long-Term"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </GlassCard>

          {/* Section 3: Two Columns */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pb-8">
            {/* Message Input Card */}
            <GlassCard className="animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-200">
              <label className="text-slate-300 font-medium text-sm block mb-4">Analyze New Interaction</label>
              <Textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Enter conversation text or context to analyze emotional state..."
                className="bg-black/20 border-white/10 text-white placeholder-slate-500 mb-5 min-h-[120px] rounded-xl focus:border-indigo-500/50 focus:ring-indigo-500/20 resize-none glass-panel"
              />
              <GlassButton 
                onClick={handleAnalyze}
                disabled={analyzing}
                className="w-full"
              >
                {analyzing ? 'Processing Analysis...' : 'Run Analysis'}
              </GlassButton>
              {analyzeError && (
                <p className="text-rose-400 text-sm mt-3 font-medium bg-rose-500/10 px-3 py-2 rounded-lg border border-rose-500/20">{analyzeError}</p>
              )}
              {result && (
                <div className="mt-5 p-4 bg-black/30 rounded-xl border border-white/5 text-sm text-slate-300 overflow-x-auto max-h-[200px] custom-scrollbar glass-panel">
                  <pre className="font-mono text-xs text-indigo-200">{JSON.stringify(result, null, 2)}</pre>
                </div>
              )}
            </GlassCard>

            {/* Significance Score Card */}
            <GlassCard className="animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-300 flex flex-col justify-center items-center text-center relative overflow-hidden group">
              {/* Subtle background glow effect */}
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 bg-rose-500/20 rounded-full blur-[60px] group-hover:bg-rose-500/30 transition-all duration-700"></div>
              
              <div className="relative z-10">
                <label className="text-slate-400/80 text-sm font-medium uppercase tracking-wider block mb-6">Significance Score</label>
                <div className="flex items-baseline justify-center gap-1 mb-6">
                  <p className="text-7xl font-bold text-white tracking-tighter drop-shadow-[0_0_15px_rgba(255,255,255,0.2)]">
                    {result?.significance_score?.toFixed(1) || '—'}
                  </p>
                  <span className="text-2xl text-slate-500 font-medium">/10</span>
                </div>
                <div className="inline-flex items-center bg-rose-500/15 text-rose-300 text-sm font-medium rounded-full px-4 py-1.5 border border-rose-500/30 mb-6 shadow-[0_0_15px_rgba(244,63,94,0.15)]">
                  <div className="w-2 h-2 bg-rose-400 rounded-full mr-2"></div>
                  High Significance
                </div>
                <p className="text-slate-400 text-sm max-w-[250px] mx-auto leading-relaxed">
                  Score above 7.0 indicates a critical emotional shift in the user's state.
                </p>
              </div>
            </GlassCard>
          </div>
        </div>
      </div>
    </div>
  );
}