import { useState, useRef, useEffect } from 'react'
import type { KeyboardEvent } from 'react'
import { apiFetch } from '@/api/client'
import { useAuth } from '@/hooks/useAuth'
import { MessageCircle, X, Send } from 'lucide-react'

interface Message {
  role: 'user' | 'bot'
  text: string
}

export default function ChatWidget() {
  const { user } = useAuth()
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    { role: 'bot', text: `Hi ${user?.name?.split(' ')[0] ?? 'there'}! How can I help you today?` },
  ])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, open])

  async function send() {
    const text = input.trim()
    if (!text || sending) return
    setInput('')
    setMessages(prev => [...prev, { role: 'user', text }])
    setSending(true)
    try {
      const data = await apiFetch<{ answer: string }>('/crexusers/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      })
      setMessages(prev => [...prev, { role: 'bot', text: data.answer }])
    } catch {
      setMessages(prev => [...prev, { role: 'bot', text: "Sorry, I couldn't process that. Please try again." }])
    } finally {
      setSending(false)
    }
  }

  function handleKey(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter') send()
  }

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-3">
      {open && (
        <div className="w-80 h-[450px] rounded-2xl border border-white/10 bg-[#0a0a22] shadow-2xl flex flex-col overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 bg-[#f97316]">
            <div className="flex items-center gap-2">
              <MessageCircle size={18} className="text-white" />
              <div>
                <p className="text-sm font-semibold text-white leading-none">Chat Support</p>
                <p className="text-xs text-orange-100 mt-0.5">Kevin is here to help</p>
              </div>
            </div>
            <button
              onClick={() => setOpen(false)}
              className="text-white hover:text-orange-100 transition-colors"
            >
              <X size={18} />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-3 py-3 space-y-2">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-[75%] rounded-2xl px-3 py-2 text-sm leading-relaxed ${
                    msg.role === 'user'
                      ? 'bg-[#90aace] text-[#0f0f2e] font-medium rounded-br-sm'
                      : 'bg-white/10 text-slate-200 rounded-bl-sm'
                  }`}
                >
                  {msg.text}
                </div>
              </div>
            ))}
            {sending && (
              <div className="flex justify-start">
                <div className="bg-white/10 text-slate-400 text-sm rounded-2xl rounded-bl-sm px-3 py-2">
                  <span className="animate-pulse">...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="flex items-center gap-2 px-3 py-3 border-t border-white/10">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Type a message..."
              className="flex-1 bg-white/10 border border-white/20 rounded-full px-4 py-2 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-[#90aace]"
            />
            <button
              onClick={send}
              disabled={sending || !input.trim()}
              className="w-9 h-9 rounded-full bg-[#f97316] flex items-center justify-center text-white hover:bg-[#ea6c0e] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <Send size={15} />
            </button>
          </div>
        </div>
      )}

      {/* Toggle button */}
      <button
        onClick={() => setOpen(prev => !prev)}
        className="w-14 h-14 rounded-full bg-[#f97316] shadow-lg flex items-center justify-center text-white hover:bg-[#ea6c0e] transition-colors"
        aria-label="Toggle chat"
      >
        {open ? <X size={22} /> : <MessageCircle size={22} />}
      </button>
    </div>
  )
}
