import { useAuth } from '@/hooks/useAuth'
import { Button } from '@/components/ui/button'
import { Bitcoin } from 'lucide-react'

export default function Navbar() {
  const { user, logout } = useAuth()

  return (
    <nav className="w-full bg-[#0a0a22] border-b border-white/10 px-6 h-14 flex items-center justify-between">
      <span className="text-lg font-bold text-white tracking-tight">
        Cryptocurrency Exchange
      </span>

      <div className="flex items-center gap-4">
        {user && (
          <>
            <div className="flex items-center gap-1.5 text-sm text-[#90aace]">
              <Bitcoin size={15} className="text-[#f97316]" />
              <span className="font-medium">{user.balance} BTC</span>
            </div>

            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-[#90aace] flex items-center justify-center text-[#0f0f2e] text-sm font-bold">
                {user.name.charAt(0).toUpperCase()}
              </div>
              <span className="text-sm text-slate-300 hidden sm:block">{user.name}</span>
            </div>

            <Button variant="ghost" size="sm" onClick={logout}>
              Logout
            </Button>
          </>
        )}
      </div>
    </nav>
  )
}
