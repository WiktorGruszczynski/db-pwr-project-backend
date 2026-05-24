import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../api.js';

export default function Verify() {
  const [params] = useSearchParams();
  const nav = useNavigate();
  const [email, setEmail] = useState(params.get('email') || '');
  const [code, setCode] = useState('');
  const [msg, setMsg] = useState(null);
  const [err, setErr] = useState(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setErr(null);
    setMsg(null);
    setBusy(true);
    try {
      const data = await api.post('/auth/verify', { email, code });
      setMsg(data.message);
      setTimeout(() => nav('/login'), 800);
    } catch (e) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <h2>Weryfikacja konta</h2>
      <form onSubmit={submit}>
        <div><label>Email <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label></div>
        <div><label>Kod <input value={code} onChange={(e) => setCode(e.target.value)} required /></label></div>
        <button type="submit" disabled={busy}>{busy ? '...' : 'Zweryfikuj'}</button>
      </form>
      {msg && <p style={{ color: 'green' }}>{msg}</p>}
      {err && <p style={{ color: 'red' }}>{err}</p>}
      <p><Link to="/login">Login</Link></p>
    </div>
  );
}
