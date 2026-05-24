import { Routes, Route, Link, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from './auth.jsx';
import Login from './pages/Login.jsx';
import Register from './pages/Register.jsx';
import Verify from './pages/Verify.jsx';
import ForgotPassword from './pages/ForgotPassword.jsx';
import ResetPassword from './pages/ResetPassword.jsx';
import Profile from './pages/Profile.jsx';
import Products from './pages/Products.jsx';
import ProductDetail from './pages/ProductDetail.jsx';
import Recipes from './pages/Recipes.jsx';
import RecipeDetail from './pages/RecipeDetail.jsx';
import Meals from './pages/Meals.jsx';
import Leaderboard from './pages/Leaderboard.jsx';

function Nav() {
  const { user, logout } = useAuth();
  const nav = useNavigate();
  const onLogout = async () => {
    await logout();
    nav('/login');
  };
  return (
    <nav style={{ padding: 10, borderBottom: '1px solid #ccc', display: 'flex', gap: 12, flexWrap: 'wrap' }}>
      <Link to="/">Home</Link>
      {user ? (
        <>
          <Link to="/profile">Profil</Link>
          <Link to="/products">Produkty</Link>
          <Link to="/recipes">Przepisy</Link>
          <Link to="/meals">Posiłki</Link>
          <Link to="/leaderboard">Ranking</Link>
          <span style={{ marginLeft: 'auto' }}>
            {user.username || user.email}
            {user.role === 'ADMIN' && (
              <span style={{ marginLeft: 6, fontSize: '0.75em', background: '#fef3c7', color: '#92400e', padding: '1px 5px', borderRadius: 4 }}>
                ADMIN
              </span>
            )}
            <button onClick={onLogout} style={{ marginLeft: 8 }}>Wyloguj</button>
          </span>
        </>
      ) : (
        <>
          <Link to="/login">Login</Link>
          <Link to="/register">Rejestracja</Link>
        </>
      )}
    </nav>
  );
}

function Protected({ children }) {
  const { user, loading } = useAuth();
  const location = useLocation();
  if (loading) return <p>Ładowanie...</p>;
  if (!user) return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  return children;
}

function Home() {
  const { user } = useAuth();
  return (
    <div>
      <h1>Nutrition App</h1>
      {user ? (
        <p>Witaj, {user.username || user.email}!</p>
      ) : (
        <p>
          <Link to="/login">Zaloguj się</Link> lub <Link to="/register">zarejestruj</Link>.
        </p>
      )}
    </div>
  );
}

export default function App() {
  return (
    <>
      <Nav />
      <main style={{ padding: 16, maxWidth: 900, margin: '0 auto' }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/verify" element={<Verify />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/profile" element={<Protected><Profile /></Protected>} />
          <Route path="/products" element={<Protected><Products /></Protected>} />
          <Route path="/products/:id" element={<Protected><ProductDetail /></Protected>} />
          <Route path="/recipes" element={<Protected><Recipes /></Protected>} />
          <Route path="/recipes/:id" element={<Protected><RecipeDetail /></Protected>} />
          <Route path="/meals" element={<Protected><Meals /></Protected>} />
          <Route path="/leaderboard" element={<Protected><Leaderboard /></Protected>} />
          <Route path="*" element={<p>404 — nie znaleziono</p>} />
        </Routes>
      </main>
    </>
  );
}
