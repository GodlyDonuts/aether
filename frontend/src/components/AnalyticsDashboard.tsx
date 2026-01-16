import { useState, useEffect } from 'react';

import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, CartesianGrid } from 'recharts';
import { TrendingUp, DollarSign, Target, Activity, LayoutDashboard, Settings, Users, ArrowLeft, MoreHorizontal } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface AnalyticsData {
    metrics: {
        total_revenue: number;
        total_sessions: number;
        active_nudges: number;
        cpif: number;
    };
    charts: {
        revenue_over_time: Array<{ time: string; revenue: number; amount: number }>;
        intent_distribution: Array<{ name: string; value: number }>;
    };
    recent_conversions: Array<{
        session_id: string;
        intent: string;
        status: string;
        revenue: number;
        timestamp: string;
    }>;
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'];

export const AnalyticsDashboard = () => {
    const navigate = useNavigate();
    const [data, setData] = useState<AnalyticsData | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await fetch('http://localhost:8000/analytics');
                const json = await res.json();
                setData(json);
            } catch (e) {
                console.error("Failed to fetch analytics", e);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 3000);
        return () => clearInterval(interval);
    }, []);

    if (!data) return (
        <div className="flex items-center justify-center min-h-screen bg-gray-50">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
    );

    return (
        <div className="h-screen bg-[#f2f2f7] flex font-sans text-slate-800 relative overflow-hidden">
            {/* Ambient Background Orbs */}
            <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] bg-blue-200/30 rounded-full blur-[100px] pointer-events-none mix-blend-multiply" />
            <div className="absolute bottom-[-20%] right-[-10%] w-[600px] h-[600px] bg-indigo-200/30 rounded-full blur-[100px] pointer-events-none mix-blend-multiply" />

            {/* Sidebar */}
            <aside className="w-64 bg-white/70 backdrop-blur-xl border-r border-white/50 flex flex-col shrink-0 z-20">
                <div className="p-6 border-b border-gray-100 flex items-center gap-2">
                    <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">A</div>
                    <span className="font-bold text-xl tracking-tight text-gray-900">AXON</span>
                </div>

                <nav className="flex-1 p-4 space-y-1">
                    <NavItem icon={<LayoutDashboard size={20} />} label="Overview" active />
                    <NavItem icon={<Users size={20} />} label="Audiences" />
                    <NavItem icon={<Target size={20} />} label="Campaigns" />
                    <NavItem icon={<Activity size={20} />} label="Real-time" />
                </nav>

                <div className="p-4 border-t border-gray-100">
                    <NavItem icon={<Settings size={20} />} label="Settings" />
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-y-auto">
                {/* Header */}
                <header className="h-16 bg-white/70 backdrop-blur-md border-b border-white/50 sticky top-0 z-30 px-8 flex items-center justify-between shadow-sm">
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => navigate('/')}
                            className="p-2 hover:bg-gray-100 rounded-full text-gray-500 transition-colors"
                        >
                            <ArrowLeft size={20} />
                        </button>
                        <div>
                            <h2 className="font-semibold text-gray-900">Dashboard</h2>
                            <p className="text-xs text-gray-500">Last updated: Just now</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2 px-3 py-1 bg-green-50 text-green-700 rounded-full text-xs font-medium border border-green-100">
                            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                            Live System
                        </div>
                        <button className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-semibold text-sm">
                            SR
                        </button>
                    </div>
                </header>

                <div className="p-8 max-w-7xl mx-auto space-y-8">
                    {/* Key Metrics */}
                    <div className="grid grid-cols-4 gap-6">
                        <NewStatCard
                            title="Total Revenue"
                            value={`$${data.metrics.total_revenue.toFixed(2)}`}
                            trend="+12.5%"
                            trendUp
                            icon={<DollarSign size={20} className="text-emerald-600" />}
                        />
                        <NewStatCard
                            title="CPIF (Net ROI)"
                            value={`$${data.metrics.cpif.toFixed(2)}`}
                            trend="+4.2%"
                            trendUp
                            icon={<TrendingUp size={20} className="text-blue-600" />}
                        />
                        <NewStatCard
                            title="Nudges Shown"
                            value={data.metrics.active_nudges.toString()}
                            trend="0%"
                            icon={<Target size={20} className="text-violet-600" />}
                        />
                        <NewStatCard
                            title="Active Sessions"
                            value={data.metrics.total_sessions.toString()}
                            icon={<Users size={20} className="text-orange-600" />}
                        />
                    </div>

                    {/* Charts Row */}
                    <div className="grid grid-cols-3 gap-6">
                        {/* Revenue Main Chart */}
                        <div className="col-span-2 bg-white/60 backdrop-blur-lg rounded-2xl border border-white/50 shadow-sm p-6 hover:shadow-md transition-shadow">
                            <div className="flex justify-between items-center mb-6">
                                <h3 className="font-semibold text-gray-900">Revenue Performance</h3>
                                <button className="text-gray-400 hover:text-gray-600"><MoreHorizontal size={20} /></button>
                            </div>
                            <div className="h-[350px] w-full" style={{ minHeight: '350px' }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={data.charts.revenue_over_time} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                                        <defs>
                                            <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1} />
                                                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                        <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} dy={10} />
                                        <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(v) => `$${v}`} dx={-10} />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                            itemStyle={{ color: '#1e293b', fontWeight: 600 }}
                                            formatter={(value: number | undefined) => [`$${(value || 0).toFixed(2)}`, 'Revenue']}
                                        />
                                        <Area
                                            type="monotone"
                                            dataKey="revenue"
                                            stroke="#3b82f6"
                                            strokeWidth={2}
                                            fillOpacity={1}
                                            fill="url(#colorRevenue)"
                                            animationDuration={1000}
                                        />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* Intent Distribution */}
                        <div className="bg-white/60 backdrop-blur-lg rounded-2xl border border-white/50 shadow-sm p-6 flex flex-col hover:shadow-md transition-shadow">
                            <h3 className="font-semibold text-gray-900 mb-6">Intent Segments</h3>
                            <div className="flex-1 min-h-[250px] relative" style={{ minHeight: '250px' }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart>
                                        <Pie
                                            data={data.charts.intent_distribution}
                                            cx="50%"
                                            cy="50%"
                                            innerRadius={60}
                                            outerRadius={90}
                                            paddingAngle={4}
                                            dataKey="value"
                                        >
                                            {data.charts.intent_distribution.map((_entry, index) => (
                                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} strokeWidth={0} />
                                            ))}
                                        </Pie>
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e2e8f0' }}
                                        />
                                    </PieChart>
                                </ResponsiveContainer>
                                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                                    <span className="text-3xl font-bold text-gray-900">
                                        {data.charts.intent_distribution.reduce((acc, curr) => acc + curr.value, 0)}
                                    </span>
                                    <span className="text-xs text-gray-500 font-medium uppercase tracking-wide">Intents</span>
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-3 mt-6">
                                {data.charts.intent_distribution.map((entry, index) => (
                                    <div key={entry.name} className="flex items-center gap-2 text-sm">
                                        <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }}></span>
                                        <span className="text-gray-600 truncate">{entry.name}</span>
                                        <span className="ml-auto font-medium text-gray-900">{entry.value}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Recent Conversions Table (Mock) */}
                    <div className="bg-white/60 backdrop-blur-lg rounded-2xl border border-white/50 shadow-sm overflow-hidden">
                        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
                            <h3 className="font-semibold text-gray-900">Recent Conversions</h3>
                            <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">View All</button>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm text-left">
                                <thead className="text-xs text-gray-500 uppercase bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3 font-medium">Session ID</th>
                                        <th className="px-6 py-3 font-medium">Intent</th>
                                        <th className="px-6 py-3 font-medium">Status</th>
                                        <th className="px-6 py-3 font-medium">Revenue</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-100">
                                    {(data.recent_conversions || []).length === 0 ? (
                                        <tr>
                                            <td colSpan={4} className="px-6 py-8 text-center text-gray-500">
                                                No conversions yet. Trigger a commercial intent in chat!
                                            </td>
                                        </tr>
                                    ) : (
                                        data.recent_conversions.map((conv, i) => (
                                            <tr key={i} className="hover:bg-gray-50/50 transition-colors">
                                                <td className="px-6 py-4 font-mono text-gray-600">{conv.session_id.substring(0, 8)}...</td>
                                                <td className="px-6 py-4 text-gray-900">{conv.intent}</td>
                                                <td className="px-6 py-4"><span className="px-2 py-1 rounded-full bg-green-50 text-green-700 text-xs font-medium border border-green-100">{conv.status}</span></td>
                                                <td className="px-6 py-4 font-medium text-gray-900">${conv.revenue.toFixed(2)}</td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

const NewStatCard = ({ title, value, icon, trend, trendUp }: any) => (
    <div className="bg-white/60 backdrop-blur-lg p-5 rounded-2xl border border-white/50 shadow-sm hover:shadow-md transition-all hover:bg-white/80">
        <div className="flex justify-between items-start mb-4">
            <div className={`p-2.5 rounded-lg bg-gray-50`}>
                {icon}
            </div>
            {trend && (
                <span className={`text-xs font-medium px-2 py-1 rounded-full ${trendUp ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                    {trend}
                </span>
            )}
        </div>
        <div>
            <h3 className="text-2xl font-bold text-gray-900 tracking-tight">{value}</h3>
            <p className="text-sm text-gray-500 font-medium mt-1">{title}</p>
        </div>
    </div>
);

const NavItem = ({ icon, label, active }: any) => (
    <button className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${active ? 'bg-blue-50 text-blue-700' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}`}>
        {icon}
        {label}
    </button>
);
