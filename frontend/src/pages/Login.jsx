import { useEffect, useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../auth.jsx';

export default function Login() {
  const { user, loading, login } = useAuth();
  const nav = useNavigate();
  const location = useLocation();
  const from = location.state?.from || '/profile';

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [err, setErr] = useState(null);
  const [busy, setBusy] = useState(false);

  // Już zalogowany — przekieruj
  useEffect(() => {
    if (!loading && user) {
      nav(from, { replace: true });
    }
  }, [user, loading]);

  const submit = async (e) => {
    e.preventDefault();
    setErr(null);
    setBusy(true);
    try {
      await login(email, password);
      nav(from, { replace: true });
    } catch (e) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  };

  if (loading) return <p>Ładowanie...</p>;

  return (
    <div>
      <h2>Logowanie</h2>
      <form onSubmit={submit}>
        <div>
          <label>
            Email{' '}
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              required
            />
          </label>
        </div>
        <div>
          <label>
            Hasło{' '}
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />
          </label>
        </div>
        <button type="submit" disabled={busy}>
          {busy ? 'Logowanie...' : 'Zaloguj'}
        </button>
      </form>

      {err && <p style={{ color: 'red' }}>{err}</p>}

      <p>
        <Link to="/register">Rejestracja</Link>
        {' · '}
        <Link to="/forgot-password">Zapomniałeś hasła?</Link>
      </p>
    </div>
  );
}
