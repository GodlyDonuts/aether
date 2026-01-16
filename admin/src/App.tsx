import { useState } from 'react';
import { KeyManager } from './components/KeyManager';
import { Overview } from './components/Overview';
import { Sidebar } from './components/Sidebar';
import { Users } from './components/Users';
import { AnimatePresence, motion } from 'framer-motion';

function App() {
  const [activeTab, setActiveTab] = useState<'overview' | 'keys' | 'users' | 'analytics' | 'settings'>('overview');

  return (
    <div className="min-h-screen flex font-sans text-slate-200 bg-[#020617] selection:bg-blue-500/30">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto relative h-screen">
        {/* Ambient Glows */}
        <div className="fixed top-0 left-64 w-[500px] h-[500px] bg-blue-900/10 rounded-full blur-[128px] pointer-events-none mix-blend-screen" />
        <div className="fixed bottom-0 right-0 w-[500px] h-[500px] bg-purple-900/5 rounded-full blur-[128px] pointer-events-none mix-blend-screen" />

        <div className="max-w-7xl mx-auto p-8 relative z-10">
          <header className="flex justify-between items-center mb-10">
            <div>
              <h1 className="text-3xl font-bold text-white tracking-tight">
                {activeTab === 'overview' && 'Dashboard'}
                {activeTab === 'keys' && 'API Access'}
                {activeTab === 'users' && 'User Management'}
                {activeTab === 'analytics' && 'Analytics'}
                {activeTab === 'settings' && 'Settings'}
              </h1>
              <p className="text-slate-500 mt-1">
                {activeTab === 'overview' && 'Real-time overview of your system performance.'}
                {activeTab === 'keys' && 'Manage programmatic access to your Aether instance.'}
                {activeTab === 'users' && 'Manage high-value customer accounts and billing.'}
              </p>
            </div>
          </header>

          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              {activeTab === 'overview' && <Overview />}
              {activeTab === 'keys' && <KeyManager />}
              {activeTab === 'users' && <Users />}
              {(activeTab === 'analytics' || activeTab === 'settings') && (
                <div className="glass-card rounded-xl p-12 text-center border-dashed border-2 border-slate-800">
                  <div className="text-slate-500">Feature Coming Soon</div>
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        </div>
      </main>
    </div>
  )
}

export default App
