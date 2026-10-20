import { useEffect, useState } from 'react'

type Email = { id: number; subject: string; sender: string; snippet: string; ai_summary: string | null; ai_category: string | null; ai_priority: string | null }
type Task = { id: number; title: string; description: string; due_date: string; priority: string; status: string }
type Account = { id: number; email_address: string; provider: string }

function App() {
  const [accounts, setAccounts] = useState<Account[]>([])
  const [activeAccountId, setActiveAccountId] = useState<number | null>(null)
  
  const [activeTab, setActiveTab] = useState<'inbox' | 'tasks' | 'reports'>('inbox')
  const [emails, setEmails] = useState<Email[]>([])
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(false)
  const [reportLoading, setReportLoading] = useState(false)

  const fetchData = async (accountId: number) => {
    try {
      const [emailsRes, tasksRes] = await Promise.all([
        fetch(`http://localhost:8000/api/emails/?account_id=${accountId}`),
        fetch(`http://localhost:8000/api/tasks/?account_id=${accountId}`)
      ])
      setEmails(await emailsRes.json())
      setTasks(await tasksRes.json())
    } catch (err) { console.error(err) }
  }

  const fetchAccounts = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/accounts/')
      const data = await res.json()
      setAccounts(data)
      if (data.length > 0) {
        setActiveAccountId(data[0].id)
        fetchData(data[0].id)
      }
    } catch (err) { console.error(err) }
  }

  useEffect(() => { fetchAccounts() }, [])

  const handleAccountChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const id = Number(e.target.value)
    setActiveAccountId(id)
    fetchData(id)
  }

  const connectGmail = async () => {
    const res = await fetch('http://localhost:8000/api/accounts/gmail/connect')
    const data = await res.json()
    if (data.auth_url) window.location.href = data.auth_url
  }

  const syncData = async () => {
    if (!activeAccountId) return alert("No account selected.")
    setLoading(true)
    try {
      const res = await fetch(`http://localhost:8000/api/emails/sync/${activeAccountId}`, { method: 'POST' })
      if (!res.ok) throw new Error((await res.json()).detail)
      await fetchData(activeAccountId)
    } catch (err: any) { alert(`Sync Failed: ${err.message}`) } finally { setLoading(false) }
  }

  // ... (Keep the linkTelegram, sendReport, enableWebPush, testWebPush, and getPriorityStyle functions exactly as they are) ...
  const linkTelegram = async () => { /* ... */ }
  const sendReport = async (type: string) => { /* ... */ }
  const enableWebPush = async () => { /* ... */ }
  const testWebPush = async () => { /* ... */ }
  const getPriorityStyle = (priority: string | null) => { /* ... */ }

  return (
    <div style={{ padding: '40px 24px', maxWidth: 1000, margin: '0 auto', minHeight: '100vh' }}>
      
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 30 }}>
        <h1 style={{ fontSize: 42, margin: 0, letterSpacing: '-1.5px' }}>MailMind <span className="neon-text">AI</span></h1>
        
        <div style={{ display: 'flex', gap: 15, alignItems: 'center' }}>
          {accounts.length > 0 && (
            <select 
              value={activeAccountId || ''} 
              onChange={handleAccountChange}
              className="glass-panel"
              style={{ padding: '10px', color: '#fff', background: 'rgba(0,0,0,0.5)', outline: 'none', cursor: 'pointer' }}
            >
              {accounts.map(acc => (
                <option key={acc.id} value={acc.id} style={{ color: '#000' }}>
                  {acc.email_address} ({acc.provider})
                </option>
              ))}
            </select>
          )}
          
          <button onClick={connectGmail} className="btn-cyber" style={{ padding: '10px 15px', fontSize: 12 }}>
            + Add Account
          </button>

          {activeAccountId && (
            <button onClick={syncData} disabled={loading} className="btn-cyber">
              {loading ? '⚡ Scanning...' : '⚡ Sync'}
            </button>
          )}
        </div>
      </header>
      
      {/* ... (Keep the rest of the JSX exactly the same as your last working version) ... */}
      {/* Just make sure to replace the old `{connected ? ...}` logic with `{accounts.length > 0 ? ...}` */}
      
    </div>
  )
}
export default App