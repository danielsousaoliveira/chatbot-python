import Navbar from '@/components/Navbar'
import ChatWidget from '@/components/ChatWidget'
import { useAuth } from '@/hooks/useAuth'
import { Bitcoin, TrendingUp, Wallet } from 'lucide-react'

export default function HomePage() {
  const { user } = useAuth()

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      <main className="flex-1 flex flex-col items-center justify-center px-4 gap-8">
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-white">
            Welcome, {user?.name?.split(' ')[0]}
          </h1>
          <p className="text-slate-400">Your Cryptocurrency Exchange dashboard</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full max-w-lg">
          <div className="bg-[#1a1a45] border border-white/10 rounded-xl p-4 flex flex-col items-center gap-2">
            <Wallet size={24} className="text-[#90aace]" />
            <p className="text-xs text-slate-400">Balance</p>
            <p className="text-xl font-bold text-white">{user?.balance ?? 0}</p>
            <p className="text-xs text-[#f97316] font-medium">BTC</p>
          </div>

          <div className="bg-[#1a1a45] border border-white/10 rounded-xl p-4 flex flex-col items-center gap-2">
            <TrendingUp size={24} className="text-green-400" />
            <p className="text-xs text-slate-400">Market</p>
            <p className="text-xl font-bold text-white">Active</p>
            <p className="text-xs text-green-400 font-medium">Live</p>
          </div>

          <div className="bg-[#1a1a45] border border-white/10 rounded-xl p-4 flex flex-col items-center gap-2">
            <Bitcoin size={24} className="text-[#f97316]" />
            <p className="text-xs text-slate-400">Account</p>
            <p className="text-xl font-bold text-white truncate max-w-full">{user?.username}</p>
            <p className="text-xs text-[#90aace] font-medium">Verified</p>
          </div>
        </div>

        <p className="text-slate-500 text-sm">
          Use the chat button below to buy, sell, or ask questions.
        </p>
      </main>

      <ChatWidget />
    </div>
  )
}
