import { useEffect, useState } from 'react';
import { api } from '../api.js';

export default function Leaderboard() {
  const [scope, setScope] = useState('global');
  const [from, setFrom] = useState('');
  const [to, setTo] = useState('');
  const [rows, setRows] = useState([]);
  const [err, setErr] = useState(null);

  const load = async () => {
    setErr(null);
    try {
      const params = new URLSearchParams({ scope });
      if (from) params.set('from', from);
      if (to) params.set('to', to);
      setRows(await api.get(`/leaderboard/?${params.toString()}`));
    } catch (e) {
      setErr(e.message);
    }
  };

  useEffect(() => {
    load();
  }, [scope]);

  return (
    <div>
      <h2>Ranking</h2>
      <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
        <label>Zakres
          <select value={scope} onChange={(e) => setScope(e.target.value)}>
            <option value="global">global</option>
            <option value="friends">friends</option>
          </select>
        </label>
        <label>Od <input type="date" value={from} onChange={(e) => setFrom(e.target.value)} /></label>
        <label>Do <input type="date" value={to} onChange={(e) => setTo(e.target.value)} /></label>
        <button onClick={load}>Filtruj</button>
      </div>

      <table style={{ marginTop: 12, borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{ textAlign: 'left', paddingRight: 16 }}>#</th>
            <th style={{ textAlign: 'left', paddingRight: 16 }}>Użytkownik</th>
            <th style={{ textAlign: 'right', paddingRight: 16 }}>Punkty</th>
            <th style={{ textAlign: 'right' }}>Wpisy</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.user_id}>
              <td>{r.rank}</td>
              <td>{r.username}</td>
              <td style={{ textAlign: 'right' }}>{r.total_score}</td>
              <td style={{ textAlign: 'right' }}>{r.entries_count}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {err && <p style={{ color: 'red' }}>{err}</p>}
    </div>
  );
}
