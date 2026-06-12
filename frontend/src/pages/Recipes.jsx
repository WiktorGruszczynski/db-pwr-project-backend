import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../api.js';
import { useAuth } from '../auth.jsx';

export default function Recipes() {
  const nav = useNavigate();
  const { user } = useAuth();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [ingredients, setIngredients] = useState([]); // {product_id, name, quantity}
  const [mine, setMine] = useState([]);
  const [err, setErr] = useState(null);

  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [searchErr, setSearchErr] = useState(null);

  // wyszukiwarka produktow do skladnikow przepisu
  const [ingQuery, setIngQuery] = useState('');
  const [ingResults, setIngResults] = useState(null);

  const loadMine = async () => {
    try {
      setMine(await api.get('/recipes/mine'));
    } catch (e) {
      setErr(e.message);
    }
  };

  useEffect(() => {
    loadMine();
  }, []);

  const onSearch = async (e) => {
    e.preventDefault();
    setSearchErr(null);
    setResults(null);
    try {
      const r = await api.get(`/recipes/search?q=${encodeURIComponent(query)}`);
      setResults(r);
    } catch (e) {
      setSearchErr(e.message);
    }
  };

  const onIngSearch = async (e) => {
    e.preventDefault();
    if (ingQuery.trim().length < 3) return;
    setErr(null);
    try {
      setIngResults(await api.get(`/products/search?q=${encodeURIComponent(ingQuery)}`));
    } catch (e) {
      setErr(e.message);
    }
  };

  const addIngredient = (p) => {
    if (ingredients.some((i) => i.product_id === p.id)) return;
    setIngredients([...ingredients, { product_id: p.id, name: p.name, quantity: 100 }]);
  };
  const setQuantity = (i, v) => {
    const next = [...ingredients];
    next[i] = { ...next[i], quantity: v };
    setIngredients(next);
  };
  const removeIngredient = (i) => setIngredients(ingredients.filter((_, idx) => idx !== i));

  const onCreate = async (e) => {
    e.preventDefault();
    setErr(null);
    if (ingredients.length === 0) {
      setErr('Dodaj co najmniej jeden składnik (wyszukaj produkt po nazwie).');
      return;
    }
    try {
      const payload = {
        name,
        description: description || null,
        ingredients: ingredients.map((i) => ({
          product_id: i.product_id,
          quantity: Number(i.quantity),
          unit: 'g',
        })),
      };
      const r = await api.post('/recipes/', payload);
      nav(`/recipes/${r.id}`);
    } catch (e) {
      setErr(e.message);
    }
  };

  const onDelete = async (id) => {
    if (!window.confirm('Usunąć ten przepis?')) return;
    setSearchErr(null);
    try {
      await api.del(`/recipes/${id}`);
      setResults((prev) => (prev ? prev.filter((r) => r.id !== id) : prev));
      setMine((prev) => prev.filter((r) => r.id !== id));
    } catch (e) {
      setSearchErr(e.message);
    }
  };

  return (
    <div>
      <h2>Przepisy</h2>

      <h3>Szukaj przepisu po nazwie</h3>
      <form onSubmit={onSearch}>
        <label>Nazwa <input value={query} onChange={(e) => setQuery(e.target.value)} minLength={2} required /></label>{' '}
        <button type="submit">Szukaj</button>
      </form>
      {searchErr && <p style={{ color: 'red' }}>{searchErr}</p>}
      {results && results.length === 0 && (
        <p>Nie znaleziono przepisów pasujących do „{query}”.</p>
      )}
      {results && results.length > 0 && (
        <ul>
          {results.map((r) => (
            <li key={r.id}>
              <Link to={`/recipes/${r.id}`}>{r.name}</Link>
              {r.description ? ` — ${r.description}` : ''}{' '}
              {String(r.user_id) === String(user?.id) && (
                <button type="button" onClick={() => onDelete(r.id)}>Usuń</button>
              )}
            </li>
          ))}
        </ul>
      )}

      <h3>Moje przepisy {mine.length > 0 && <span style={{ color: 'var(--muted)', fontWeight: 400 }}>({mine.length})</span>}</h3>
      {mine.length === 0 ? (
        <p style={{ color: 'var(--muted)' }}>Nie masz jeszcze żadnych przepisów — utwórz pierwszy poniżej.</p>
      ) : (
        <ul>
          {mine.map((r) => (
            <li key={r.id}>
              <Link to={`/recipes/${r.id}`}>{r.name}</Link>
              {r.description ? ` — ${r.description}` : ''}{' '}
              <span style={{ color: 'var(--muted)' }}>★ {r.average_rating ?? 0}</span>{' '}
              <button type="button" onClick={() => onDelete(r.id)}>Usuń</button>
            </li>
          ))}
        </ul>
      )}

      <h3>Nowy przepis</h3>
      <form onSubmit={onCreate}>
        <div><label>Nazwa <input value={name} onChange={(e) => setName(e.target.value)} required /></label></div>
        <div><label>Opis <textarea value={description} onChange={(e) => setDescription(e.target.value)} /></label></div>
        <h4>Składniki</h4>
        {ingredients.length === 0 ? (
          <p style={{ color: 'var(--muted)' }}>Brak składników — wyszukaj produkt poniżej i dodaj go do przepisu.</p>
        ) : (
          <ul>
            {ingredients.map((ing, i) => (
              <li key={ing.product_id}>
                {ing.name}{' '}
                <label>Ilość (g) <input type="number" step="0.01" min="0.01" value={ing.quantity} onChange={(e) => setQuantity(i, e.target.value)} required style={{ width: 90 }} /></label>{' '}
                <button type="button" onClick={() => removeIngredient(i)}>Usuń</button>
              </li>
            ))}
          </ul>
        )}
        <div>
          <label>Szukaj produktu
            <input
              value={ingQuery}
              onChange={(e) => setIngQuery(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') onIngSearch(e); }}
              placeholder="min. 3 znaki"
            />
          </label>{' '}
          <button type="button" onClick={onIngSearch}>Szukaj</button>
        </div>
        {ingResults && ingResults.length === 0 && (
          <p>Nie znaleziono produktów pasujących do „{ingQuery}”.</p>
        )}
        {ingResults && ingResults.length > 0 && (
          <ul>
            {ingResults.map((p) => (
              <li key={p.id}>
                {p.name} ({p.energy_kcal} kcal / {p.quantity}{p.quantity_unit}){' '}
                {ingredients.some((i) => i.product_id === p.id)
                  ? <em style={{ color: 'var(--muted)' }}>dodano</em>
                  : <button type="button" onClick={() => addIngredient(p)}>+ Dodaj</button>}
              </li>
            ))}
          </ul>
        )}
        <br />
        <button type="submit">Utwórz przepis</button>
      </form>
      {err && <p style={{ color: 'red' }}>{err}</p>}
    </div>
  );
}
