import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api.js';

const empty = {
  name: '',
  quantity: 100,
  quantity_unit: 'g',
  fat: 0,
  carbohydrates: 0,
  protein: 0,
  energy_kcal: 0,
};

export default function Products() {
  const [mine, setMine] = useState([]);
  const [q, setQ] = useState('');
  const [results, setResults] = useState(null); // null = nie szukano jeszcze
  const [form, setForm] = useState(empty);
  const [err, setErr] = useState(null);

  const loadMine = async () => {
    try {
      setMine(await api.get('/products/mine'));
    } catch (e) {
      setErr(e.message);
    }
  };

  useEffect(() => {
    loadMine();
  }, []);

  const onSearch = async (e) => {
    e.preventDefault();
    setErr(null);
    setResults(null);
    try {
      setResults(await api.get(`/products/search?q=${encodeURIComponent(q)}`));
    } catch (e) {
      setErr(e.message);
    }
  };

  const onCreate = async (e) => {
    e.preventDefault();
    setErr(null);
    try {
      const payload = {
        ...form,
        quantity: Number(form.quantity),
        fat: Number(form.fat),
        carbohydrates: Number(form.carbohydrates),
        protein: Number(form.protein),
        energy_kcal: Number(form.energy_kcal),
      };
      await api.post('/products/', payload);
      setForm(empty);
      loadMine();
    } catch (e) {
      setErr(e.message);
    }
  };

  const onDelete = async (id) => {
    if (!confirm('Usunąć produkt?')) return;
    try {
      await api.del(`/products/${id}`);
      loadMine();
    } catch (e) {
      setErr(e.message);
    }
  };

  const field = (k, label, type = 'text', step) => (
    <div>
      <label>
        {label}{' '}
        <input
          type={type}
          step={step}
          value={form[k]}
          onChange={(e) => setForm({ ...form, [k]: e.target.value })}
          required
        />
      </label>
    </div>
  );

  return (
    <div>
      <h2>Produkty</h2>

      <h3>Wyszukiwanie</h3>
      <form onSubmit={onSearch}>
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="min. 3 znaki" />
        <button type="submit">Szukaj</button>
      </form>
      {results !== null && (
        results.length === 0
          ? <p>Nie znaleziono produktów pasujących do „{q}".</p>
          : <ul>
              {results.map((p) => (
                <li key={p.id}>
                  <Link to={`/products/${p.id}`}>{p.name}</Link> — {p.energy_kcal} kcal / {p.quantity}{p.quantity_unit}
                </li>
              ))}
            </ul>
      )}

      <h3>Moje produkty</h3>
      <ul>
        {mine.map((p) => (
          <li key={p.id}>
            <Link to={`/products/${p.id}`}>{p.name}</Link> — {p.energy_kcal} kcal / {p.quantity}{p.quantity_unit}
            <button onClick={() => onDelete(p.id)} style={{ marginLeft: 8 }}>Usuń</button>
          </li>
        ))}
      </ul>

      <h3>Dodaj produkt</h3>
      <form onSubmit={onCreate}>
        {field('name', 'Nazwa')}
        {field('quantity', 'Ilość (g)', 'number', '0.01')}
        {field('fat', 'Tłuszcz', 'number', '0.01')}
        {field('carbohydrates', 'Węglowodany', 'number', '0.01')}
        {field('protein', 'Białko', 'number', '0.01')}
        {field('energy_kcal', 'Energia (kcal)', 'number', '0.01')}
        <button type="submit">Dodaj</button>
      </form>
      {err && <p style={{ color: 'red' }}>{err}</p>}
    </div>
  );
}
