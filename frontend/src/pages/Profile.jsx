import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../auth.jsx';
import { api } from '../api.js';
import Avatar from '../Avatar.jsx';

export default function Profile() {
  const { user } = useAuth();
  const [following, setFollowing] = useState([]);
  const [followErr, setFollowErr] = useState(null);

  // wyszukiwanie użytkowników
  const [searchQ, setSearchQ] = useState('');
  const [searchResults, setSearchResults] = useState(null); // null = nie szukano
  const [searchErr, setSearchErr] = useState(null);
  const [searchBusy, setSearchBusy] = useState(false);

  const loadFollowing = async () => {
    try {
      setFollowing(await api.get('/users/me/following'));
    } catch (e) {
      setFollowErr(e.message);
    }
  };

  useEffect(() => {
    loadFollowing();
  }, []);

  const isFollowing = (id) => following.some((u) => String(u.id) === String(id));

  const onSearch = async (e) => {
    e.preventDefault();
    setSearchErr(null);
    setSearchResults(null);
    setSearchBusy(true);
    try {
      setSearchResults(await api.get(`/users/search?q=${encodeURIComponent(searchQ)}`));
    } catch (e) {
      setSearchErr(e.message);
    } finally {
      setSearchBusy(false);
    }
  };

  const onFollow = async (id) => {
    setFollowErr(null);
    try {
      await api.post(`/users/${id}/follow`);
      await loadFollowing();
    } catch (e) {
      setFollowErr(e.message);
    }
  };

  const onUnfollow = async (id) => {
    setFollowErr(null);
    try {
      await api.del(`/users/${id}/follow`);
      await loadFollowing();
    } catch (e) {
      setFollowErr(e.message);
    }
  };

  return (
    <div>
      <h2>Profil</h2>
      <div style={{ display: 'flex', alignItems: 'center', gap: 14, margin: '14px 0 6px' }}>
        <Avatar name={user?.username || user?.email} size={56} />
        <div>
          <div style={{ fontSize: '1.25em', fontWeight: 700 }}>
            {user?.username}
            {user?.role === 'ADMIN' && (
              <span style={{ marginLeft: 8, fontSize: '0.6em', verticalAlign: 'middle', background: '#fef3c7', color: '#92400e', padding: '2px 6px', borderRadius: 4 }}>
                ADMIN
              </span>
            )}
          </div>
          <div style={{ color: 'var(--muted)' }}>{user?.email}</div>
        </div>
      </div>

      <h3>Obserwowani {following.length > 0 && <span style={{ color: 'var(--muted)', fontWeight: 400 }}>({following.length})</span>}</h3>
      {following.length === 0 ? (
        <p style={{ color: 'var(--muted)' }}>Nie obserwujesz nikogo — wyszukaj użytkownika poniżej.</p>
      ) : (
        <ul>
          {following.map((u) => (
            <li key={u.id} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <Avatar name={u.username} />
              <span style={{ flex: 1, minWidth: 0 }}>
                <Link to={`/users/${u.id}`}><strong>{u.username}</strong></Link>
                <br />
                <span style={{ color: 'var(--muted)', fontSize: '0.88em' }}>
                  {u.email} · obserwujesz od {new Date(u.followed_at).toLocaleDateString('pl-PL')}
                </span>
              </span>
              <button onClick={() => onUnfollow(u.id)} type="button">
                Przestań obserwować
              </button>
            </li>
          ))}
        </ul>
      )}
      {followErr && <p style={{ color: 'red' }}>{followErr}</p>}

      <h3>Znajdź użytkownika</h3>
      <form onSubmit={onSearch}>
        <input
          value={searchQ}
          onChange={(e) => setSearchQ(e.target.value)}
          placeholder="min. 2 znaki nazwy"
          required
          minLength={2}
        />
        <button type="submit" disabled={searchBusy}>
          {searchBusy ? '...' : 'Szukaj'}
        </button>
      </form>
      {searchErr && <p style={{ color: 'red' }}>{searchErr}</p>}

      {searchResults !== null && (
        searchResults.length === 0 ? (
          <p>Nie znaleziono użytkowników pasujących do „{searchQ}".</p>
        ) : (
          <ul>
            {searchResults.map((u) => {
              const alreadyFollowing = isFollowing(u.id);
              const isMe = String(u.id) === String(user?.id);
              return (
                <li key={u.id} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <Avatar name={u.username} />
                  <strong style={{ flex: 1 }}>
                    <Link to={`/users/${u.id}`}>{u.username}</Link>
                    {isMe && <em style={{ marginLeft: 8, color: 'var(--muted)', fontWeight: 400 }}>(to Ty)</em>}
                    {!isMe && alreadyFollowing && (
                      <span style={{ marginLeft: 8, fontSize: '0.75em', fontWeight: 600, background: 'var(--primary-soft)', color: 'var(--primary-hover)', padding: '2px 8px', borderRadius: 999 }}>
                        Obserwujesz
                      </span>
                    )}
                  </strong>
                  {!isMe && (
                    alreadyFollowing ? (
                      <button onClick={() => onUnfollow(u.id)} type="button">
                        Przestań obserwować
                      </button>
                    ) : (
                      <button onClick={() => onFollow(u.id)} type="button">
                        Obserwuj
                      </button>
                    )
                  )}
                </li>
              );
            })}
          </ul>
        )
      )}
    </div>
  );
}
