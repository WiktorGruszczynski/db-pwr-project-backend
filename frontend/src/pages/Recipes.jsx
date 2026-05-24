import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api.js';

export default function Recipes() {
  const nav = useNavigate();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [ingredients, setIngredients] = useState([{ product_id: '', quantity: 100, unit: 'g' }]);
  const [recipeId, setRecipeId] = useState('');
  const [err, setErr] = useState(null);

  const setIngredient = (i, k, v) => {
    const next = [...ingredients];
    next[i] = { ...next[i], [k]: v };
    setIngredients(next);
  };
  const addIngredient = () => setIngredients([...ingredients, { product_id: '', quantity: 100, unit: 'g' }]);
  const removeIngredient = (i) => setIngredients(ingredients.filter((_, idx) => idx !== i));

  const onCreate = async (e) => {
    e.preventDefault();
    setErr(null);
    try {
      const payload = {
        name,
        description: description || null,
        ingredients: ingredients.map((i) => ({
          product_id: i.product_id,
          quantity: Number(i.quantity),
          unit: i.unit,
        })),
      };
      const r = await api.post('/recipes/', payload);
      nav(`/recipes/${r.id}`);
    } catch (e) {
      setErr(e.message);
    }
  };

  const goToRecipe = (e) => {
    e.preventDefault();
    if (recipeId) nav(`/recipes/${recipeId}`);
  };

  return (
    <div>
      <h2>Przepisy</h2>

      <h3>Otwórz przepis</h3>
      <form onSubmit={goToRecipe}>
        <label>UUID przepisu <input value={recipeId} onChange={(e) => setRecipeId(e.target.value)} style={{ width: 320 }} required /></label>
        <button type="submit">Otwórz</button>
      </form>

      <h3>Nowy przepis</h3>
      <form onSubmit={onCreate}>
        <div><label>Nazwa <input value={name} onChange={(e) => setName(e.target.value)} required /></label></div>
        <div><label>Opis <textarea value={description} onChange={(e) => setDescription(e.target.value)} /></label></div>
        <h4>Składniki</h4>
        {ingredients.map((ing, i) => (
          <div key={i} style={{ marginBottom: 6 }}>
            <label>Produkt UUID <input value={ing.product_id} onChange={(e) => setIngredient(i, 'product_id', e.target.value)} required style={{ width: 320 }} /></label>{' '}
            <label>Ilość (g) <input type="number" step="0.01" value={ing.quantity} onChange={(e) => setIngredient(i, 'quantity', e.target.value)} required /></label>{' '}
            {ingredients.length > 1 && <button type="button" onClick={() => removeIngredient(i)}>Usuń</button>}
          </div>
        ))}
        <button type="button" onClick={addIngredient}>+ Składnik</button>
        <br /><br />
        <button type="submit">Utwórz przepis</button>
      </form>
      {err && <p style={{ color: 'red' }}>{err}</p>}
    </div>
  );
}
