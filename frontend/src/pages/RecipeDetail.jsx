import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { api } from '../api.js';
import { useAuth } from '../auth.jsx';

export default function RecipeDetail() {
  const { id } = useParams();
  const nav = useNavigate();
  const { user } = useAuth();
  const [recipe, setRecipe] = useState(null);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [myRating, setMyRating] = useState(null);
  const [err, setErr] = useState(null);

  const load = async () => {
    try {
      const r = await api.get(`/recipes/${id}`);
      setRecipe(r);
      setName(r.name || '');
      setDescription(r.description || '');
      setMyRating(r.my_rating ?? null);
    } catch (e) {
      setErr(e.message);
    }
  };

  const onRate = async (value) => {
    setErr(null);
    try {
      const res = await api.post(`/recipes/${id}/rating`, { rating: value });
      setMyRating(res.my_rating);
      setRecipe((prev) => ({ ...prev, average_rating: res.average_rating }));
    } catch (e) {
      setErr(e.message);
    }
  };

  useEffect(() => {
    load();
  }, [id]);

  const onSave = async (e) => {
    e.preventDefault();
    setErr(null);
    try {
      const r = await api.patch(`/recipes/${id}`, { name, description: description || null });
      setRecipe(r);
    } catch (e) {
      setErr(e.message);
    }
  };

  const onDelete = async () => {
    if (!confirm('Usunąć przepis?')) return;
    try {
      await api.del(`/recipes/${id}`);
      nav('/recipes');
    } catch (e) {
      setErr(e.message);
    }
  };

  if (!recipe) return <p>{err || 'Ładowanie...'}</p>;

  return (
    <div>
      <p><Link to="/recipes">← Przepisy</Link></p>
      <h2>
        {recipe.name}
        {recipe.is_private && (
          <span
            title="Przepis prywatny — jego produkt może zjeść tylko autor"
            style={{
              marginLeft: 10,
              fontSize: '0.55em',
              verticalAlign: 'middle',
              background: '#f1f5f9',
              color: '#475569',
              padding: '3px 10px',
              borderRadius: 999,
              fontWeight: 600,
            }}
          >
            🔒 Prywatny
          </span>
        )}
      </h2>
      {recipe.description && <p>{recipe.description}</p>}
      <p>Ocena: {recipe.average_rating ?? 0} / 5</p>
      <p>
        Twoja ocena:{' '}
        {[1, 2, 3, 4, 5].map((v) => (
          <button
            key={v}
            type="button"
            onClick={() => onRate(v)}
            title={`Oceń na ${v}`}
            style={{
              padding: '2px 6px',
              marginRight: 4,
              fontSize: '1.1em',
              color: myRating !== null && v <= myRating ? '#f59e0b' : '#94a3b8',
            }}
          >
            {myRating !== null && v <= myRating ? '★' : '☆'}
          </button>
        ))}
        {myRating !== null && <em style={{ color: 'var(--muted)' }}>({myRating}/5)</em>}
      </p>
      <h3>Składniki</h3>
      <ul>
        {recipe.ingredients.map((i) => (
          <li key={i.id}>
            <Link to={`/products/${i.product_id}`}>{i.product_name || i.product_id}</Link> — {i.quantity}{i.unit}
          </li>
        ))}
      </ul>
      {recipe.product_id && (
        <p>Auto-produkt: <Link to={`/products/${recipe.product_id}`}>{recipe.product_id}</Link></p>
      )}

      {String(recipe.user_id) === String(user?.id) && (
        <>
          <h3>Edycja (nazwa/opis)</h3>
          <form onSubmit={onSave}>
            <div><label>Nazwa <input value={name} onChange={(e) => setName(e.target.value)} required /></label></div>
            <div><label>Opis <textarea value={description} onChange={(e) => setDescription(e.target.value)} /></label></div>
            <button type="submit">Zapisz</button>
            <button type="button" onClick={onDelete} style={{ marginLeft: 8 }}>Usuń</button>
          </form>
        </>
      )}
      {err && <p style={{ color: 'red' }}>{err}</p>}
    </div>
  );
}
