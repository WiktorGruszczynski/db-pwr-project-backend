import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../api.js';
import Avatar from '../Avatar.jsx';

export default function UserProfile() {
  const { id } = useParams();
  const [profile, setProfile] = useState(null);
  const [recipes, setRecipes] = useState(null);
  const [err, setErr] = useState(null);

  useEffect(() => {
    (async () => {
      setErr(null);
      setProfile(null);
      setRecipes(null);
      try {
        setProfile(await api.get(`/users/${id}`));
        setRecipes(await api.get(`/users/${id}/recipes`));
      } catch (e) {
        setErr(e.message);
      }
    })();
  }, [id]);

  if (err) return <p style={{ color: 'red' }}>{err}</p>;
  if (!profile) return <p>Ładowanie...</p>;

  return (
    <div>
      <p><Link to="/profile">← Profil</Link></p>
      <div style={{ display: 'flex', alignItems: 'center', gap: 14, margin: '14px 0 6px' }}>
        <Avatar name={profile.username} size={56} />
        <div style={{ fontSize: '1.25em', fontWeight: 700 }}>{profile.username}</div>
      </div>

      <h3>
        Przepisy{' '}
        {recipes && recipes.length > 0 && (
          <span style={{ color: 'var(--muted)', fontWeight: 400 }}>({recipes.length})</span>
        )}
      </h3>
      {!recipes ? (
        <p>Ładowanie...</p>
      ) : recipes.length === 0 ? (
        <p style={{ color: 'var(--muted)' }}>Ten użytkownik nie ma jeszcze przepisów.</p>
      ) : (
        <ul>
          {recipes.map((r) => (
            <li key={r.id}>
              <Link to={`/recipes/${r.id}`}><strong>{r.name}</strong></Link>
              {r.description && (
                <>
                  <br />
                  <span style={{ color: 'var(--muted)', fontSize: '0.9em' }}>{r.description}</span>
                </>
              )}
              <span style={{ float: 'right', color: 'var(--muted)' }}>★ {r.average_rating ?? 0}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
