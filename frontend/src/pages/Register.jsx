import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api.js';

export default function Register() {
  const nav = useNavigate();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [msg, setMsg] = useState(null);
  const [err, setErr] = useState(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setErr(null);
    setMsg(null);
    setBusy(true);
    try {
      const data = await api.post('/auth/register', { username, email, password });
      setMsg(data.message || 'Zarejestrowano');
      setTimeout(() => nav(`/verify?email=${encodeURIComponent(email)}`), 800);
    } catch (e) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <h2>Rejestracja</h2>
      <form onSubmit={submit}>
        <div><label>Nazwa <input value={username} onChange={(e) => setUsername(e.target.value)} required /></label></div>
        <div><label>Email <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label></div>
        <div><label>Hasło <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required /></label></div>
        <button type="submit" disabled={busy}>{busy ? '...' : 'Zarejestruj'}</button>
      </form>
      {msg && <p style={{ color: 'green' }}>{msg}</p>}
      {err && <p style={{ color: 'red' }}>{err}</p>}
      <p><Link to="/login">Mam już konto</Link></p>
    </div>
  );
}
