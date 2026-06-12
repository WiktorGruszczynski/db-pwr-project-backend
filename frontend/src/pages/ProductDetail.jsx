import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { api } from '../api.js';
import { useAuth } from '../auth.jsx';

export default function ProductDetail() {
  const { id } = useParams();
  const nav = useNavigate();
  const { user } = useAuth();
  const isAdmin = user?.role === 'ADMIN';

  const [product, setProduct] = useState(null);
  const [form, setForm] = useState(null);
  const [err, setErr] = useState(null);
  const [globalBusy, setGlobalBusy] = useState(false);

  const load = async () => {
    try {
      const p = await api.get(`/products/${id}`);
      setProduct(p);
      setForm({
        name: p.name,
        quantity: p.quantity,
        fat: p.fat,
        carbohydrates: p.carbohydrates,
        protein: p.protein,
        energy_kcal: p.energy_kcal,
      });
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
      const payload = {
        name: form.name,
        quantity: Number(form.quantity),
        fat: Number(form.fat),
        carbohydrates: Number(form.carbohydrates),
        protein: Number(form.protein),
        energy_kcal: Number(form.energy_kcal),
      };
      const updated = await api.patch(`/products/${id}`, payload);
      setProduct(updated);
    } catch (e) {
      setErr(e.message);
    }
  };

  const onDelete = async () => {
    if (!confirm('Usunąć?')) return;
    try {
      await api.del(`/products/${id}`);
      nav('/products');
    } catch (e) {
      setErr(e.message);
    }
  };

  const onToggleGlobal = async () => {
    setErr(null);
    setGlobalBusy(true);
    try {
      const updated = await api.patch(`/products/${id}/global`, {
        is_global: !product.is_global,
      });
      setProduct(updated);
    } catch (e) {
      setErr(e.message);
    } finally {
      setGlobalBusy(false);
    }
  };

  if (!product || !form) return <p>{err || 'Ładowanie...'}</p>;

  const field = (k, label, type = 'text', step) => (
    <div>
      <label>
        {label}{' '}
        <input type={type} step={step} value={form[k]} onChange={(e) => setForm({ ...form, [k]: e.target.value })} />
      </label>
    </div>
  );

  return (
    <div>
      <p><Link to="/products">← Produkty</Link></p>
      <h2>
        {product.name}
        {product.is_global && (
          <span style={{ marginLeft: 8, fontSize: '0.75em', background: '#d1fae5', color: '#065f46', padding: '2px 6px', borderRadius: 4 }}>
            GLOBALNY
          </span>
        )}
      </h2>
      <pre>{JSON.stringify(product, null, 2)}</pre>

      {isAdmin && (
        <div style={{ margin: '8px 0' }}>
          <strong>[ADMIN]</strong>{' '}
          <button onClick={onToggleGlobal} disabled={globalBusy}>
            {globalBusy ? '...' : product.is_global ? 'Usuń z globalnych' : 'Ustaw jako globalny'}
          </button>
        </div>
      )}

      <h3>Edycja</h3>
      <form onSubmit={onSave}>
        {field('name', 'Nazwa')}
        {field('quantity', 'Ilość (g)', 'number', '0.01')}
        {field('fat', 'Tłuszcz', 'number', '0.01')}
        {field('carbohydrates', 'Węglowodany', 'number', '0.01')}
        {field('protein', 'Białko', 'number', '0.01')}
        {field('energy_kcal', 'Energia (kcal)', 'number', '0.01')}
        <button type="submit">Zapisz</button>
        {!product.is_global && (
          <button type="button" onClick={onDelete} style={{ marginLeft: 8 }}>Usuń</button>
        )}
      </form>
      {product.is_global && (
        <p style={{ color: 'var(--muted)' }}>Produkt globalny — nie można go usunąć.</p>
      )}
      {err && <p style={{ color: 'red' }}>{err}</p>}
    </div>
  );
}
