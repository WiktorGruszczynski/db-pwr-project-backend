import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { api } from '../api.js';

export default function RecipeDetail() {
  const { id } = useParams();
  const nav = useNavigate();
  const [recipe, setRecipe] = useState(null);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [err, setErr] = useState(null);

  const load = async () => {
    try {
      const r = await api.get(`/recipes/${id}`);
      setRecipe(r);
      setName(r.name || '');
      setDescription(r.description || '');
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
      <h2>{recipe.name}</h2>
      <p>Ocena: {recipe.average_rating ?? 0}</p>
      {recipe.description && <p>{recipe.description}</p>}
      <h3>Składniki</h3>
      <ul>
        {recipe.ingredients.map((i) => (
          <li key={i.id}>
            <Link to={`/products/${i.product_id}`}>{i.product_id}</Link> — {i.quantity}{i.unit}
          </li>
        ))}
      </ul>
      {recipe.product_id && (
        <p>Auto-produkt: <Link to={`/products/${recipe.product_id}`}>{recipe.product_id}</Link></p>
      )}

      <h3>Edycja (nazwa/opis)</h3>
      <form onSubmit={onSave}>
        <div><label>Nazwa <input value={name} onChange={(e) => setName(e.target.value)} required /></label></div>
        <div><label>Opis <textarea value={description} onChange={(e) => setDescription(e.target.value)} /></label></div>
        <button type="submit">Zapisz</button>
        <button type="button" onClick={onDelete} style={{ marginLeft: 8 }}>Usuń</button>
      </form>
      {err && <p style={{ color: 'red' }}>{err}</p>}
    </div>
  );
}
