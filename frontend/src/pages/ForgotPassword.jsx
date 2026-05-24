import { useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api.js';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [msg, setMsg] = useState(null);
  const [err, setErr] = useState(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setErr(null);
    setMsg(null);
    setBusy(true);
    try {
      const data = await api.post('/auth/forgot-password', { email });
      setMsg(data.message);
    } catch (e) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <h2>Reset hasła</h2>
      <form onSubmit={submit}>
        <div><label>Email <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label></div>
        <button type="submit" disabled={busy}>{busy ? '...' : 'Wyślij kod'}</button>
      </form>
      {msg && <p style={{ color: 'green' }}>{msg}</p>}
      {err && <p style={{ color: 'red' }}>{err}</p>}
      <p><Link to={`/reset-password?email=${encodeURIComponent(email)}`}>Mam kod</Link> · <Link to="/login">Login</Link></p>
    </div>
  );
}
