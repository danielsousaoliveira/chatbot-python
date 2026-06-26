import { useState, useRef, useEffect } from 'react'
import type { KeyboardEvent } from 'react'
import { apiFetch } from '@/api/client'
import { useAuth } from '@/hooks/useAuth'
import { MessageCircle, X, Send } from 'lucide-react'
import flowData from '@/data/flow.json'

// ── Flow types ────────────────────────────────────────────────────────────────

interface FlowOption {
  label: string
  next: string
}

interface FlowInput {
  type: 'text' | 'number' | 'password' | 'email'
  placeholder: string
  action: 'buy' | 'sell' | 'update_password' | 'update_email'
  success_next: string
  back: string
}

interface FlowNode {
  message: string
  options?: FlowOption[]
  input?: FlowInput
  freetext?: boolean
  back?: string
}

interface Flow {
  start: string
  nodes: Record<string, FlowNode>
}

const flow = flowData as Flow

// ── Action API calls ──────────────────────────────────────────────────────────

async function executeAction(action: FlowInput['action'], value: string): Promise<void> {
  const routes: Record<FlowInput['action'], { path: string; body: object }> = {
    buy:             { path: '/crexusers/trade/buy',       body: { amount: Number(value) } },
    sell:            { path: '/crexusers/trade/sell',      body: { amount: Number(value) } },
    update_password: { path: '/crexusers/account/password', body: { password: value } },
    update_email:    { path: '/crexusers/account/email',   body: { email: value } },
  }
  const { path, body } = routes[action]
  await apiFetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}

// ── Component ─────────────────────────────────────────────────────────────────

interface Message {
  role: 'user' | 'bot'
  text: string
}

function resolveMessage(raw: string, name: string): string {
  return raw.replace('%%NAME%%', name.split(' ')[0])
}

export default function ChatWidget() {
  const { user } = useAuth()
  const firstName = user?.name?.split(' ')[0] ?? 'there'

  const startNode = flow.nodes[flow.start]
  const [nodeId, setNodeId] = useState<string>(flow.start)
  const [messages, setMessages] = useState<Message[]>([
    { role: 'bot', text: resolveMessage(startNode.message, firstName) },
  ])
  const [open, setOpen] = useState(false)
  const [inputValue, setInputValue] = useState('')
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const node = flow.nodes[nodeId]

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, open])

  function pushBotMessage(nodeKey: string) {
    const n = flow.nodes[nodeKey]
    if (!n) return
    setMessages(prev => [...prev, { role: 'bot', text: resolveMessage(n.message, firstName) }])
  }

  function navigate(nextId: string, userLabel?: string) {
    if (userLabel) {
      setMessages(prev => [...prev, { role: 'user', text: userLabel }])
    }
    setNodeId(nextId)
    pushBotMessage(nextId)
    setInputValue('')
  }

  async function submitInput() {
    if (!node.input || !inputValue.trim() || sending) return
    const { action, type, success_next } = node.input
    const displayValue = type === 'password' ? '••••••••' : inputValue.trim()
    setMessages(prev => [...prev, { role: 'user', text: displayValue }])
    setSending(true)
    setInputValue('')
    try {
      await executeAction(action, inputValue.trim())
      setNodeId(success_next)
      pushBotMessage(success_next)
    } catch (err: unknown) {
      const detail = (err as { detail?: string })?.detail ?? 'Something went wrong, please try again.'
      setMessages(prev => [...prev, { role: 'bot', text: detail }])
    } finally {
      setSending(false)
    }
  }

  async function submitFreetext() {
    if (!inputValue.trim() || sending) return
    const text = inputValue.trim()
    setMessages(prev => [...prev, { role: 'user', text }])
    setSending(true)
    setInputValue('')
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
    if (e.key !== 'Enter') return
    if (node.input) submitInput()
    else if (node.freetext) submitFreetext()
  }

  const showInput = !!(node.input || node.freetext)

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-3">
      {open && (
        <div className="w-80 h-[500px] rounded-2xl border border-white/10 bg-[#0a0a22] shadow-2xl flex flex-col overflow-hidden">
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

          {/* Option buttons */}
          {node.options && !sending && (
            <div className="px-3 pb-3 flex flex-col gap-1.5">
              {node.options.map(opt => (
                <button
                  key={opt.next}
                  onClick={() => navigate(opt.next, opt.label)}
                  className="w-full text-left px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-sm text-slate-200 transition-colors border border-white/10"
                >
                  {opt.label}
                </button>
              ))}
            </div>
          )}

          {/* Text / number / password / freetext input */}
          {showInput && (
            <div className="flex flex-col gap-2 px-3 pb-3 border-t border-white/10 pt-3">
              <div className="flex items-center gap-2">
                <input
                  type={node.input?.type ?? 'text'}
                  value={inputValue}
                  onChange={e => setInputValue(e.target.value)}
                  onKeyDown={handleKey}
                  placeholder={node.input?.placeholder ?? 'Type a message...'}
                  className="flex-1 bg-white/10 border border-white/20 rounded-full px-4 py-2 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-[#90aace]"
                />
                <button
                  onClick={node.freetext ? submitFreetext : submitInput}
                  disabled={sending || !inputValue.trim()}
                  className="w-9 h-9 rounded-full bg-[#f97316] flex items-center justify-center text-white hover:bg-[#ea6c0e] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  <Send size={15} />
                </button>
              </div>
              {/* Back link for input/freetext nodes */}
              {(node.input?.back ?? node.back) && (
                <button
                  onClick={() => navigate(node.input?.back ?? node.back!)}
                  className="text-xs text-slate-500 hover:text-slate-300 transition-colors text-center"
                >
                  ← Back
                </button>
              )}
            </div>
          )}
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
