import { Zap, Users as UsersIcon, DollarSign, Activity, TrendingUp, TrendingDown } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { getStats } from '../lib/api';
import { Sparkline } from './analytics/Sparkline';
import { ActiveConnections } from './analytics/ActiveConnections';
import { SyncCharts } from './analytics/SyncCharts';
import { cn } from '../lib/utils';
import { motion } from 'framer-motion';

export const Overview = () => {
    const { data: stats, isLoading } = useQuery({
        queryKey: ['stats'],
        queryFn: getStats
    });

    if (isLoading || !stats) {
        return <div className="text-slate-500 flex items-center gap-2"><Activity className="animate-spin" size={16} /> Connecting to neural network...</div>;
    }

    // Mock history data enhancement for charts if raw api keeps it simple
    // Currently expecting stats.history to have { timestamp, requests, revenue }

    return (
        <div className="space-y-6 animate-in fade-in zoom-in-95 duration-500">
            {/* Bento Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">

                {/* Metric Cards - Row 1 */}
                <StatCard
                    title="Total Requests"
                    value={stats.total_requests.toLocaleString()}
                    trend="+12.5%"
                    icon={<Zap size={18} className="text-blue-400" />}
                    chartData={stats.history.map(h => ({ value: h.requests }))}
                    color="#3b82f6"
                    className="col-span-1"
                />
                <StatCard
                    title="Active Users"
                    value={stats.active_users.toLocaleString()}
                    trend="+3.2%"
                    icon={<UsersIcon size={18} className="text-purple-400" />}
                    chartData={stats.history.map(h => ({ value: h.requests / 2 }))} // Mock different data
                    color="#a855f7"
                    className="col-span-1"
                />
                <StatCard
                    title="MRR"
                    value={`$${(stats.mrr || stats.revenue * 0.8).toLocaleString()}`}
                    trend="+8.4%"
                    icon={<DollarSign size={18} className="text-emerald-400" />}
                    chartData={stats.history.map(h => ({ value: h.revenue }))}
                    color="#10b981"
                    className="col-span-1"
                />
                <StatCard
                    title="Churn Rate"
                    value={`${stats.churn_rate || '0.8'}%`}
                    trend="-0.2%"
                    goodTrend={false} // actually for churn, down is good, handled in component logic if sophisticated
                    icon={<Activity size={18} className="text-rose-400" />}
                    chartData={stats.history.map(h => ({ value: h.requests * 0.1 }))}
                    color="#f43f5e"
                    className="col-span-1"
                />

                {/* Main Content - Row 2 & 3 */}
                <div className="col-span-1 lg:col-span-3 row-span-2">
                    <SyncCharts data={stats.history} />
                </div>

                <div className="col-span-1 lg:col-span-1 row-span-2 h-[400px]">
                    <ActiveConnections />
                </div>
            </div>
        </div>
    );
};

const StatCard = ({ title, value, trend, icon, chartData, color, className, goodTrend = true }: any) => (
    <motion.div
        whileHover={{ y: -2 }}
        className={cn("glass-card rounded-xl p-5 border border-white/5 flex flex-col justify-between overflow-hidden relative group", className)}
    >
        <div className="flex justify-between items-start z-10">
            <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</p>
                <div className="flex items-baseline gap-2 mt-1">
                    <h3 className="text-2xl font-bold text-white tracking-tight">{value}</h3>
                    <span className={cn("text-xs font-medium flex items-center", goodTrend && trend.startsWith('+') ? "text-emerald-400" : "text-emerald-400")}>
                        {trend.startsWith('+') ? <TrendingUp size={10} className="mr-0.5" /> : <TrendingDown size={10} className="mr-0.5" />}
                        {trend}
                    </span>
                </div>
            </div>
            <div className="p-2 bg-white/5 rounded-lg border border-white/5 group-hover:bg-white/10 transition-colors">
                {icon}
            </div>
        </div>

        <div className="mt-4 flex justify-between items-end z-10">
            <div className="text-xs text-slate-500">Last 7 days</div>
            <Sparkline data={chartData} color={color} />
        </div>

        {/* Glossy overlay effect */}
        <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>
    </motion.div>
);
