import { useEffect, useState } from 'react'
import { api } from './api/client'

function App() {
  const [status, setStatus] = useState('loading...')
  useEffect(() => {
    api.get<{ status: string; database: string }>('/health')
      .then(d => setStatus(`${d.status} / db: ${d.database}`))
      .catch(() => setStatus('error reaching backend'))
  }, [])
  return <div className="p-8">Backend health: {status}</div>
}
export default App