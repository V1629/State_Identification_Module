import { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
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
    <div className="flex h-screen bg-[#0f1117]">
      {/* Sidebar */}
      <div className="fixed left-0 top-0 h-screen w-60 bg-[#0d0f14] border-r border-slate-800 flex flex-col">
        {/* Header */}
        <div className="px-6 pt-6 pb-8">
          <h1 className="text-white font-bold text-xl">SIM</h1>
          <p className="text-slate-500 text-xs">State Identification</p>
        </div>

        {/* Nav Items */}
        <nav className="flex-1 space-y-2">
          <div className="mx-3 px-3 py-2 bg-indigo-500/10 text-indigo-400 rounded-lg text-sm">
            Dashboard
          </div>
          <div className="mx-3 px-3 py-2 text-slate-400 text-sm cursor-pointer hover:text-slate-300">
            History
          </div>
          <div className="mx-3 px-3 py-2 text-slate-400 text-sm cursor-pointer hover:text-slate-300">
            Configuration
          </div>
        </nav>

        {/* Footer Version */}
        <div className="px-6 pb-6 text-slate-600 text-xs">v1.0.0</div>
      </div>

      {/* Main Content */}
      <div className="ml-60 w-[calc(100%-240px)] overflow-y-auto">
        {/* Topbar */}
        <div className="border-b border-slate-800 px-6 py-4 flex justify-between items-center sticky top-0 bg-[#0f1117]/95 backdrop-blur">
          <h2 className="text-white font-semibold text-lg">Emotional State Dashboard</h2>
          <div className="flex items-center gap-2 bg-green-500/10 text-green-400 text-xs rounded-full px-3 py-1 border border-green-500/20">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            System Active
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Section 1: Stat Cards */}
          <div className="grid grid-cols-3 gap-4">
            {/* Short-Term State */}
            <Card className="bg-[#1a1d27] border-slate-800 p-4">
              <p className="text-slate-400 text-sm mb-3">Short-Term State</p>
              <p className="text-white text-2xl font-bold mb-3">Neutral</p>
              <div className="inline-block bg-indigo-500/10 text-indigo-400 text-xs rounded-full px-3 py-1 border border-indigo-500/20">
                Current
              </div>
            </Card>

            {/* Mid-Term State */}
            <Card className="bg-[#1a1d27] border-slate-800 p-4">
              <p className="text-slate-400 text-sm mb-3">Mid-Term State</p>
              <p className="text-white text-2xl font-bold mb-3">Stable</p>
              <div className="inline-block bg-emerald-500/10 text-emerald-400 text-xs rounded-full px-3 py-1 border border-emerald-500/20">
                Trending
              </div>
            </Card>

            {/* Long-Term State */}
            <Card className="bg-[#1a1d27] border-slate-800 p-4">
              <p className="text-slate-400 text-sm mb-3">Long-Term State</p>
              <p className="text-white text-2xl font-bold mb-3">Positive</p>
              <div className="inline-block bg-rose-500/10 text-rose-400 text-xs rounded-full px-3 py-1 border border-rose-500/20">
                Overall
              </div>
            </Card>
          </div>

          {/* Section 2: EMA Score Chart */}
          <Card className="bg-[#1a1d27] border-slate-800 p-4">
            <h3 className="text-white font-semibold text-sm mb-4">EMA Score Timeline</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a2d3a" />
                <XAxis dataKey="time" stroke="#64748b" style={{ fontSize: '12px' }} />
                <YAxis stroke="#64748b" style={{ fontSize: '12px' }} domain={[0, 10]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0d0f14',
                    border: '1px solid #2a2d3a',
                    borderRadius: '6px',
                  }}
                  labelStyle={{ color: '#e2e8f0' }}
                />
                <Line
                  type="monotone"
                  dataKey="shortTerm"
                  stroke="#6366f1"
                  dot={false}
                  strokeWidth={2}
                  name="Short-Term"
                />
                <Line
                  type="monotone"
                  dataKey="midTerm"
                  stroke="#10b981"
                  dot={false}
                  strokeWidth={2}
                  name="Mid-Term"
                />
                <Line
                  type="monotone"
                  dataKey="longTerm"
                  stroke="#f43f5e"
                  dot={false}
                  strokeWidth={2}
                  name="Long-Term"
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>

          {/* Section 3: Two Columns */}
          <div className="grid grid-cols-2 gap-4">
            {/* Message Input Card */}
            <Card className="bg-[#1a1d27] border-slate-800 p-4">
              <label className="text-slate-400 text-sm block mb-3">Input Message</label>
              <Textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Enter message to analyze..."
                className="bg-[#0d0f14] border-slate-700 text-white placeholder-slate-500 mb-3"
              />
              <Button className="w-full bg-indigo-500 hover:bg-indigo-600 text-white">
                Analyze
              </Button>
            </Card>

            {/* Significance Score Card */}
            <Card className="bg-[#1a1d27] border-slate-800 p-4 flex flex-col justify-center">
              <label className="text-slate-400 text-sm block mb-4">Significance Score</label>
              <p className="text-5xl font-bold text-white mb-4">7.4</p>
              <div className="inline-block w-fit bg-rose-500/10 text-rose-400 text-xs rounded-full px-3 py-1 border border-rose-500/20 mb-4">
                High Significance
              </div>
              <p className="text-slate-500 text-sm">Score above 7.0 indicates a critical emotional shift</p>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}