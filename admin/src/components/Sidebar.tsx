import { LayoutDashboard, Key, Settings, BarChart3, LogOut, Disc, Users } from 'lucide-react';
import { cn } from '../lib/utils';
import { SystemHealth } from './SystemHealth';

interface SidebarProps {
    activeTab: string;
    setActiveTab: (tab: 'overview' | 'keys' | 'users' | 'analytics' | 'settings') => void;
}

export const Sidebar = ({ activeTab, setActiveTab }: SidebarProps) => {
    return (
        <aside className="w-72 bg-[#020617]/95 backdrop-blur-xl border-r border-white/5 flex flex-col h-screen sticky top-0 z-50">
            <div className="p-6">
                <div className="flex items-center gap-3 mb-10 group cursor-pointer">
                    <div className="relative">
                        <div className="w-10 h-10 bg-blue-600/20 rounded-xl flex items-center justify-center text-blue-500 font-bold text-lg shadow-[0_0_20px_rgba(37,99,235,0.2)] border border-blue-500/20 group-hover:bg-blue-600/30 transition-all duration-500">
                            <Disc size={22} className="animate-[spin_4s_linear_infinite]" />
                        </div>
                        <div className="absolute inset-0 bg-blue-500/20 rounded-xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <span className="text-lg font-bold text-white tracking-tight">AXON</span>
                            <span className="text-[10px] bg-blue-500/10 text-blue-400 px-1.5 py-0.5 rounded border border-blue-500/20 font-mono">PRO</span>
                        </div>
                        <div className="text-xs text-slate-500 font-medium">Command Center</div>
                    </div>
                </div>

                <nav className="space-y-1 mb-8">
                    <NavItem
                        icon={<LayoutDashboard size={18} />}
                        label="Overview"
                        isActive={activeTab === 'overview'}
                        onClick={() => setActiveTab('overview')}
                    />
                    <NavItem
                        icon={<Key size={18} />}
                        label="API Keys"
                        isActive={activeTab === 'keys'}
                        onClick={() => setActiveTab('keys')}
                    />
                    <NavItem
                        icon={<Users size={18} />}
                        label="Users"
                        isActive={activeTab === 'users'}
                        onClick={() => setActiveTab('users')}
                        badge="Admin"
                    />
                    <NavItem
                        icon={<BarChart3 size={18} />}
                        label="Analytics"
                        isActive={activeTab === 'analytics'}
                        onClick={() => setActiveTab('analytics')}
                    />
                    <NavItem
                        icon={<Settings size={18} />}
                        label="Settings"
                        isActive={activeTab === 'settings'}
                        onClick={() => setActiveTab('settings')}
                    />
                </nav>

                <SystemHealth />
            </div>

            <div className="mt-auto p-6 border-t border-white/5">
                <div className="flex items-center gap-3 mb-4 px-2">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 shadow-inner"></div>
                    <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-white truncate">Admin User</div>
                        <div className="text-xs text-slate-500 truncate">admin@axon.com</div>
                    </div>
                </div>
                <button className="flex items-center gap-3 text-sm font-medium text-slate-500 hover:text-white transition-colors w-full group px-2 py-2 rounded-lg hover:bg-white/5">
                    <LogOut size={16} className="group-hover:text-red-400 transition-colors" />
                    Sign Out
                </button>
            </div>
        </aside>
    );
};

const NavItem = ({ icon, label, isActive, onClick, badge }: any) => (
    <button
        onClick={onClick}
        className={cn(
            "flex items-center justify-between w-full px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-300 border border-transparent group relative overflow-hidden",
            isActive
                ? "bg-blue-600/10 text-blue-400 border-blue-500/20 shadow-[0_0_15px_rgba(37,99,235,0.1)]"
                : "text-slate-500 hover:text-slate-200 hover:bg-white/5"
        )}
    >
        <div className="flex items-center gap-3 z-10">
            <span className={cn("transition-colors duration-300", isActive ? "text-blue-400" : "text-slate-500 group-hover:text-slate-300")}>
                {icon}
            </span>
            {label}
        </div>
        {badge && (
            <span className="text-[10px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded border border-slate-700 ml-auto z-10">{badge}</span>
        )}
        {isActive && <div className="absolute inset-0 bg-blue-600/5 z-0"></div>}
    </button>
);
