import { useEffect, useState } from 'react';
import { useAuth } from '../auth.jsx';
import { api } from '../api.js';

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
      <pre>{JSON.stringify(user, null, 2)}</pre>

      <h3>Obserwowani</h3>
      {following.length === 0 ? (
        <p>Nie obserwujesz nikogo.</p>
      ) : (
        <ul>
          {following.map((u) => (
            <li key={u.id}>
              <strong>{u.username}</strong> ({u.email}) — od {new Date(u.followed_at).toLocaleString()}
              <button onClick={() => onUnfollow(u.id)} style={{ marginLeft: 8 }}>
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
                <li key={u.id}>
                  <strong>{u.username}</strong>
                  {isMe ? (
                    <em style={{ marginLeft: 8 }}>(to Ty)</em>
                  ) : alreadyFollowing ? (
                    <>
                      <span style={{ marginLeft: 8, color: 'green' }}>Obserwujesz</span>
                      <button onClick={() => onUnfollow(u.id)} style={{ marginLeft: 8 }}>
                        Przestań obserwować
                      </button>
                    </>
                  ) : (
                    <button onClick={() => onFollow(u.id)} style={{ marginLeft: 8 }}>
                      Obserwuj
                    </button>
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
