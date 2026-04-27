import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Activity, Zap, TrendingUp, AlertTriangle, MessageSquare, Map as MapIcon, Calendar, UploadCloud, Download, Send, BarChart2 } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend, AreaChart, Area } from 'recharts';
import ReactMarkdown from 'react-markdown';
import './index.css';

const API_BASE = import.meta.env.DEV ? 'http://localhost:5000/api' : '/api';
const MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

const SUGGESTED_QUESTIONS = [
  "Which state has the worst power deficit right now?",
  "Where is Gujarat sending its surplus power?",
  "How does demand in May compare to January?",
  "Provide a 3-point plan to balance the national grid."
];

function App() {
  const [data, setData] = useState([]);
  const [analysis, setAnalysis] = useState([]);
  const [transfers, setTransfers] = useState([]);
  const [seasonalTrends, setSeasonalTrends] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const [query, setQuery] = useState('');
  const [chatHistory, setChatHistory] = useState([
    { role: 'ai', content: 'Hello! I am IndiaGrid AI. I have full context of the current national grid state. How can I assist you today?' }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const chatRef = useRef(null);

  const [uploadStatus, setUploadStatus] = useState('');
  const fileInputRef = useRef(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [liveRes, analysisRes, optimizeRes, seasonalRes] = await Promise.all([
        axios.get(`${API_BASE}/live-data`),
        axios.get(`${API_BASE}/surplus-deficit`),
        axios.get(`${API_BASE}/optimize`),
        axios.get(`${API_BASE}/seasonal-trends`)
      ]);
      setData(liveRes.data);
      setAnalysis(analysisRes.data);
      setTransfers(optimizeRes.data);
      setSeasonalTrends(seasonalRes.data);
    } catch (err) {
      console.error("Error fetching data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [chatHistory, isTyping]);

  const handleChatSubmit = async (overrideQuery = null) => {
    const userMsg = overrideQuery || query;
    if (!userMsg.trim()) return;
    
    setChatHistory(prev => [...prev, { role: 'user', content: userMsg }]);
    if (!overrideQuery) setQuery('');
    setIsTyping(true);

    try {
      const res = await axios.post(`${API_BASE}/ai-insights`, { 
        query: userMsg,
        analysis: analysis,
        transfers: transfers,
        seasonalTrends: seasonalTrends
      });
      setChatHistory(prev => [...prev, { role: 'ai', content: res.data.insight }]);
    } catch (err) {
      setChatHistory(prev => [...prev, { role: 'ai', content: err.response?.data?.error || 'Connection to intelligence network failed.' }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    setUploadStatus('Uploading and Processing...');

    try {
      await axios.post(`${API_BASE}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setUploadStatus('Success! Dataset Updated.');
      fetchData(); // Refresh all data
    } catch (err) {
      setUploadStatus(err.response?.data?.error || 'Upload failed.');
    }
    
    setTimeout(() => setUploadStatus(''), 5000);
  };

  if (loading && data.length === 0) {
    return (
      <div className="app-container" style={{display:'flex', justifyContent:'center', alignItems:'center', height:'100vh', flexDirection:'column'}}>
        <Zap size={64} color="var(--primary)" className="spin-pulse" />
        <h2 style={{marginTop:'24px', color:'var(--text-muted)'}}>Initializing Intelligence Engine...</h2>
      </div>
    );
  }

  const totalDemand = data.reduce((acc, curr) => acc + curr.demand_mw, 0);
  const totalSupply = data.reduce((acc, curr) => acc + curr.supply_mw, 0);
  const netSurplus = totalSupply - totalDemand;

  const seasonalChartData = seasonalTrends?.monthly_data?.map(d => ({
    name: MONTH_NAMES[d.month - 1],
    demand: d.demand_mw
  })) || [];

  return (
    <div className="app-container">
      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '40px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ background: 'rgba(88, 166, 255, 0.1)', padding: '12px', borderRadius: '12px' }}>
            <Zap size={40} color="var(--primary)" />
          </div>
          <div>
            <h1>IndiaGrid AI</h1>
            <p style={{ color: 'var(--text-muted)', margin: 0, marginTop: '-10px' }}>National Electricity Intelligence Platform</p>
          </div>
        </div>
        
        {/* Data Management Controls */}
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          <span style={{ color: uploadStatus.includes('Success') ? 'var(--success)' : 'var(--primary)', fontSize: '0.9rem', fontWeight: 'bold' }}>
            {uploadStatus}
          </span>
          <input type="file" ref={fileInputRef} style={{ display: 'none' }} accept=".csv, .xls, .xlsx" onChange={handleFileUpload} />
          <button className="btn btn-outline" onClick={() => fileInputRef.current.click()}>
            <UploadCloud size={18} /> Upload Data
          </button>
          <a href={`${API_BASE}/download-unified`} className="btn btn-primary" style={{ textDecoration: 'none' }}>
            <Download size={18} /> Export Unified CSV
          </a>
        </div>
      </header>

      <div className="dashboard-grid">
        {/* Overview Stats */}
        <div className="glass-panel">
          <div className="stat-label">National Demand</div>
          <div className="stat-value">{totalDemand.toLocaleString(undefined, {maximumFractionDigits:0})} MW</div>
          <Activity color="var(--primary)" size={24} style={{ marginTop: '8px' }} />
        </div>

        <div className="glass-panel">
          <div className="stat-label">National Supply</div>
          <div className="stat-value">{totalSupply.toLocaleString(undefined, {maximumFractionDigits:0})} MW</div>
          <TrendingUp color="var(--success)" size={24} style={{ marginTop: '8px' }} />
        </div>

        <div className="glass-panel">
          <div className="stat-label">Net Status</div>
          <div className={`stat-value ${netSurplus >= 0 ? 'surplus' : 'deficit'}`}>
            {netSurplus >= 0 ? '+' : ''}{netSurplus.toLocaleString(undefined, {maximumFractionDigits:0})} MW
          </div>
          <AlertTriangle color={netSurplus >= 0 ? "var(--success)" : "var(--danger)"} size={24} style={{ marginTop: '8px' }} />
        </div>

        {/* State Map Heatmap */}
        <div className="glass-panel wide-panel">
          <h2><MapIcon size={24} style={{ marginRight: '12px', color: 'var(--primary)' }}/> National Grid Map</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginTop: '24px' }}>
            {[...analysis].sort((a,b) => b.surplus_mw - a.surplus_mw).map((stateInfo, idx) => {
              const isBalanced = Math.abs(stateInfo.surplus_mw) <= 10;
              const isSurplus = stateInfo.surplus_mw > 10;
              let bg = isBalanced ? 'rgba(255, 255, 255, 0.05)' : (isSurplus ? 'rgba(46, 160, 67, 0.1)' : 'rgba(248, 81, 73, 0.1)');
              let border = isBalanced ? 'rgba(255, 255, 255, 0.1)' : (isSurplus ? 'rgba(46, 160, 67, 0.3)' : 'rgba(248, 81, 73, 0.3)');
              let color = isBalanced ? 'var(--text-main)' : (isSurplus ? 'var(--success)' : 'var(--danger)');
              return (
              <div key={idx} style={{ 
                padding: '16px', 
                borderRadius: '12px', 
                background: bg,
                border: `1px solid ${border}`,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                transition: 'transform 0.2s',
                cursor: 'default',
                minHeight: '110px'
              }} className="state-card" onMouseEnter={(e)=>e.currentTarget.style.transform='scale(1.05)'} onMouseLeave={(e)=>e.currentTarget.style.transform='scale(1)'}>
                <span style={{ fontWeight: '600', fontSize: '1.05rem', marginBottom: '4px', textAlign: 'center' }}>{stateInfo.state}</span>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{isBalanced ? 'Balanced' : (isSurplus ? 'Surplus' : 'Deficit')}</span>
                <span style={{ fontSize: '1.2rem', fontWeight: '700', color: color, marginTop: '4px' }}>
                  {stateInfo.surplus_mw > 0 && !isBalanced ? '+' : ''}{stateInfo.surplus_mw.toLocaleString(undefined, {maximumFractionDigits:0})} MW
                </span>
              </div>
            )})}
          </div>
        </div>
        
        {/* State-wise Bar Chart */}
        <div className="glass-panel wide-panel" id="chart-state-analysis">
          <h2><BarChart2 size={24} style={{ marginRight: '12px', color: 'var(--primary)' }}/> State-wise Supply vs Demand</h2>
          <div style={{ width: '100%', height: 400, marginTop: '24px' }}>
            <ResponsiveContainer>
              <BarChart data={analysis} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis dataKey="state" stroke="var(--text-muted)" tick={{fontSize: 11}} interval={0} angle={-45} textAnchor="end" height={80}/>
                <YAxis stroke="var(--text-muted)" />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-dark)', borderColor: 'var(--border)', borderRadius: '8px' }} />
                <Legend verticalAlign="top" height={36}/>
                <Bar dataKey="demand_mw" name="Demand (MW)" fill="rgba(248, 81, 73, 0.8)" radius={[4, 4, 0, 0]} />
                <Bar dataKey="supply_mw" name="Supply (MW)" fill="rgba(46, 160, 67, 0.8)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Seasonal Trends */}
        <div className="glass-panel wide-panel">
          <h2><Calendar size={24} style={{ marginRight: '12px', color: 'var(--primary)' }}/> Seasonal Demand Dynamics</h2>
          {seasonalTrends && (
            <p className="stat-label" style={{ marginBottom: '24px', textTransform: 'none', fontSize: '1rem' }}>
              Historical analysis shows grid usage peaks in <strong style={{color:'var(--text-main)'}}>{MONTH_NAMES[seasonalTrends.peak_month - 1]}</strong> and hits minimum capacity in <strong style={{color:'var(--text-main)'}}>{MONTH_NAMES[seasonalTrends.lowest_month - 1]}</strong>.
            </p>
          )}
          <div style={{ width: '100%', height: 350 }}>
            <ResponsiveContainer>
              <AreaChart data={seasonalChartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <defs>
                  <linearGradient id="colorDemand" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="var(--primary)" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis dataKey="name" stroke="var(--text-muted)" axisLine={false} tickLine={false} />
                <YAxis stroke="var(--text-muted)" domain={['auto', 'auto']} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-dark)', borderColor: 'var(--border)', borderRadius: '8px' }} />
                <Area type="monotone" dataKey="demand" name="Avg Demand (MW)" stroke="var(--primary)" strokeWidth={3} fillOpacity={1} fill="url(#colorDemand)" activeDot={{ r: 8, fill: 'var(--primary)', stroke: '#fff' }} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Distribution Flow */}
        <div className="glass-panel wide-panel">
          <h2><Activity size={24} style={{ marginRight: '12px', color: 'var(--primary)' }}/> Distribution Engine Transfers</h2>
          {transfers.length === 0 ? (
            <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)' }}>Grid is perfectly balanced.</div>
          ) : (
            <div style={{ marginTop: '16px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px', maxHeight: '400px', overflowY: 'auto', paddingRight: '8px' }}>
              {transfers.map((t, idx) => (
                <div key={idx} style={{ padding: '20px', background: 'var(--bg-card)', border: '1px solid rgba(88, 166, 255, 0.2)', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'relative', overflow: 'hidden' }}>
                  <div style={{ position: 'absolute', top: 0, left: 0, width: '4px', height: '100%', background: 'linear-gradient(to bottom, var(--success), var(--danger))' }} />
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', paddingLeft: '12px' }}>
                    <span style={{ color: 'var(--success)', fontWeight: '600', fontSize: '1.1rem' }}>{t.from_state}</span>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Zap size={14} color="var(--primary)"/> Transmitting
                    </span>
                    <span style={{ color: 'var(--danger)', fontWeight: '600', fontSize: '1.1rem' }}>{t.to_state}</span>
                  </div>
                  <div style={{ textAlign: 'right', background: 'rgba(88, 166, 255, 0.1)', padding: '12px 16px', borderRadius: '8px', border: '1px solid rgba(88, 166, 255, 0.2)' }}>
                    <div style={{ fontWeight: '800', fontSize: '1.4rem', color: 'var(--primary)' }}>{t.power_mw.toFixed(0)}</div>
                    <div style={{ color: 'var(--text-main)', fontSize: '0.85rem', fontWeight: '600', letterSpacing: '1px' }}>MW FLOW</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* AI Insights Chat Interface */}
        <div className="glass-panel wide-panel" style={{ display: 'flex', flexDirection: 'column' }}>
          <h2><MessageSquare size={24} style={{ marginRight: '12px', color: 'var(--primary)' }}/> AI Insights</h2>
          <p className="stat-label">Context-Aware Grid Assistant</p>
          
          <div className="chat-container">
            <div className="chat-history" ref={chatRef}>
              {chatHistory.map((msg, idx) => (
                <div key={idx} className={`chat-bubble bubble-${msg.role}`}>
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              ))}
              {isTyping && (
                <div className="typing-indicator">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
              )}
            </div>
            <div style={{ display: 'flex', gap: '8px', padding: '12px 16px', flexWrap: 'wrap', borderTop: '1px solid rgba(255, 255, 255, 0.05)', background: 'var(--bg-dark)' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', width: '100%', marginBottom: '4px' }}>Suggested Queries:</span>
              {SUGGESTED_QUESTIONS.map((q, idx) => (
                <button 
                  key={idx} 
                  onClick={() => handleChatSubmit(q)}
                  disabled={isTyping}
                  style={{ 
                    background: 'rgba(88, 166, 255, 0.1)', 
                    border: '1px solid rgba(88, 166, 255, 0.2)', 
                    color: 'var(--primary)', 
                    borderRadius: '16px', 
                    padding: '6px 12px', 
                    fontSize: '0.8rem',
                    cursor: isTyping ? 'not-allowed' : 'pointer',
                    transition: 'background 0.2s',
                    opacity: isTyping ? 0.5 : 1
                  }}
                  onMouseEnter={(e) => !isTyping && (e.target.style.background = 'rgba(88, 166, 255, 0.2)')}
                  onMouseLeave={(e) => !isTyping && (e.target.style.background = 'rgba(88, 166, 255, 0.1)')}
                >
                  {q}
                </button>
              ))}
            </div>

            <div className="chat-input-area">
              <input 
                type="text" 
                className="chat-input"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleChatSubmit()}
                placeholder="Ask about the live grid..."
              />
              <button className="btn btn-primary" onClick={() => handleChatSubmit()} disabled={isTyping}>
                <Send size={18} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
