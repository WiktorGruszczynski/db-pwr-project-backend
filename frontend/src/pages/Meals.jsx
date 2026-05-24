import { useEffect, useState } from 'react';
import { api } from '../api.js';

const MEAL_TYPES = ['BREAKFAST', 'LUNCH', 'DINNER', 'SNACK'];

function today() {
  return new Date().toISOString().slice(0, 10);
}

export default function Meals() {
  const [date, setDate] = useState(today());
  const [meals, setMeals] = useState([]);
  const [err, setErr] = useState(null);

  const [mealType, setMealType] = useState('BREAKFAST');
  const [productId, setProductId] = useState('');
  const [portion, setPortion] = useState(100);

  const load = async () => {
    setErr(null);
    try {
      setMeals(await api.get(`/meals/?date=${date}`));
    } catch (e) {
      setErr(e.message);
    }
  };

  useEffect(() => {
    load();
  }, [date]);

  const onAdd = async (e) => {
    e.preventDefault();
    setErr(null);
    try {
      await api.post('/meals/items', {
        date,
        meal_type: mealType,
        product_id: productId,
        portion: Number(portion),
      });
      setProductId('');
      load();
    } catch (e) {
      setErr(e.message);
    }
  };

  const onDelete = async (itemId) => {
    try {
      await api.del(`/meals/items/${itemId}`);
      load();
    } catch (e) {
      setErr(e.message);
    }
  };

  return (
    <div>
      <h2>Posiłki</h2>
      <label>Dzień <input type="date" value={date} onChange={(e) => setDate(e.target.value)} /></label>

      {meals.length === 0 ? <p>Brak pozycji na ten dzień.</p> : meals.map((m) => (
        <div key={m.id} style={{ border: '1px solid #ddd', padding: 8, margin: '8px 0' }}>
          <h3>{m.meal_type}</h3>
          {m.items.length === 0 ? <p>—</p> : (
            <ul>
              {m.items.map((it) => (
                <li key={it.id}>
                  {it.product_name} — {it.portion}g · {it.energy_kcal} kcal (B: {it.protein}, W: {it.carbohydrates}, T: {it.fat})
                  <button onClick={() => onDelete(it.id)} style={{ marginLeft: 8 }}>Usuń</button>
                </li>
              ))}
            </ul>
          )}
        </div>
      ))}

      <h3>Dodaj pozycję</h3>
      <form onSubmit={onAdd}>
        <div><label>Posiłek
          <select value={mealType} onChange={(e) => setMealType(e.target.value)}>
            {MEAL_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </label></div>
        <div><label>Produkt UUID <input value={productId} onChange={(e) => setProductId(e.target.value)} required style={{ width: 320 }} /></label></div>
        <div><label>Porcja (g) <input type="number" step="0.01" value={portion} onChange={(e) => setPortion(e.target.value)} required /></label></div>
        <button type="submit">Dodaj</button>
      </form>
      {err && <p style={{ color: 'red' }}>{err}</p>}
    </div>
  );
}
