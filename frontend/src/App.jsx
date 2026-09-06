import { createContext, useContext, useEffect, useState } from "react";
import {
  Link,
  Navigate,
  NavLink,
  Outlet,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";
import { loginUrl, request, send, setCsrf } from "./investscan/api";
import { ErrorBox, Icon, Loading } from "./investscan/shared";
import Opportunities from "./investscan/Opportunities";
import ObjectDetail from "./investscan/ObjectDetail";
import {
  AnalyticsPage,
  BuyersPage,
  ChecksPage,
  DealsPage,
  Market,
  SourcesPage,
} from "./investscan/WorkspacePages";
const Auth = createContext(null);
const menu = [
  ["/", "scan", "Возможности"],
  ["/market", "map", "Карта и рынок"],
  ["/checks", "check", "Проверки"],
  ["/negotiations", "chat", "Переговоры"],
  ["/deals", "deal", "Сделки и капитал"],
  ["/buyers", "buyers", "Покупатели и партнёры"],
  ["/analytics", "chart", "Аналитика"],
  ["/sources", "source", "Источники и автоматизация"],
];
function Shell() {
  const auth = useContext(Auth);
  const location = useLocation();
  const [open, setOpen] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => setOpen(false), [location.pathname]);
  if (auth.loading) return <Loading />;
  if (auth.error)
    return (
      <ErrorBox retry={() => window.location.reload()}>{auth.error}</ErrorBox>
    );
  if (!auth.user)
    return (
      <Navigate
        to={
          "/login?next=" +
          encodeURIComponent(location.pathname + location.search)
        }
        replace
      />
    );
  return (
    <div className="app-shell">
      <button
        className="mobile-menu"
        onClick={() => setOpen(!open)}
        aria-expanded={open}
      >
        ☰ Меню ИнвестСкана
      </button>
      <aside className={open ? "sidebar open" : "sidebar"}>
        <Link className="brand" to="/">
          <div className="brand-logo">Ю</div>
          <div>
            <strong>ЮРЖИЛСЕРВИС</strong>
            <span>ИнвестСкан</span>
          </div>
        </Link>
        <div className="sidebar-caption">ИНВЕСТИЦИОННЫЙ МОДУЛЬ</div>
        <nav aria-label="Меню ИнвестСкана">
          {menu.map(([to, icon, label]) => (
            <NavLink to={to} end={to === "/"} key={to}>
              <Icon name={icon} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <a
            className="return-link"
            href={auth.config?.shtab_url || "https://shtab.ugsdom.ru/#platform"}
          >
            <Icon name="back" />В штаб
          </a>
          <div className="user-card">
            <div className="avatar">{auth.user.name[0]}</div>
            <div>
              <strong>{auth.user.name}</strong>
              <span>
                {
                  {
                    owner: "Собственник",
                    analyst: "Аналитик",
                    viewer: "Просмотр",
                  }[auth.user.role]
                }
              </span>
            </div>
          </div>
          <button
            className="logout"
            onClick={async () => {
              try {
                await send("/auth/logout", {});
                setCsrf("");
                auth.setUser(null);
              } catch (e) {
                setError(e.message);
              }
            }}
          >
            Выйти из ИнвестСкана
          </button>
        </div>
      </aside>
      <main className="workspace">
        {error && <ErrorBox>{error}</ErrorBox>}
        <Outlet />
      </main>
    </div>
  );
}
function Login() {
  const auth = useContext(Auth);
  const location = useLocation();
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  let next = new URLSearchParams(location.search).get("next") || "/";
  if (
    !next.startsWith("/") ||
    next.startsWith("//") ||
    next.includes("\\") ||
    next.startsWith("/login")
  )
    next = "/";
  if (auth.loading) return <Loading />;
  if (auth.user) return <Navigate to={next} replace />;
  const ssoError = new URLSearchParams(location.search).has("error");
  return (
    <div className="login-surface">
      <section className="login-card">
        <div className="brand-logo">Ю</div>
        <div className="eyebrow">ЮРЖИЛСЕРВИС</div>
        <h1>ИнвестСкан</h1>
        <p>Поиск объектов для срочного выкупа</p>
        {auth.error && <ErrorBox>{auth.error}</ErrorBox>}
        {ssoError && (
          <ErrorBox>
            Не удалось подтвердить вход. Повторите попытку через Штаб.
          </ErrorBox>
        )}
        {auth.config?.sso_configured ? (
          <a className="button primary" href={loginUrl(next)}>
            Продолжить с учётной записью Штаба
          </a>
        ) : (
          <div className="setup-note">
            <strong>Единый вход ещё не подключён</strong>
            <p>
              Для запуска нужно связать ИнвестСкан с авторизацией Штаба.
              Отдельные логин и пароль здесь не создаются.
            </p>
          </div>
        )}
        {auth.config?.dev_auth && (
          <button
            className="secondary"
            disabled={busy}
            onClick={async () => {
              setBusy(true);
              try {
                await send("/auth/development", {});
                const me = await request("/auth/me");
                setCsrf(me.csrf_token);
                auth.setUser(me);
                navigate(next);
              } catch (e) {
                setError(e.message);
              } finally {
                setBusy(false);
              }
            }}
          >
            Открыть локальную разработку
          </button>
        )}
        {error && <ErrorBox>{error}</ErrorBox>}
        <a
          className="back-link"
          href={auth.config?.shtab_url || "https://shtab.ugsdom.ru/#platform"}
        >
          <Icon name="back" size={16} />
          Вернуться в штаб
        </a>
      </section>
    </div>
  );
}
export default function App() {
  const [state, setState] = useState({
    user: null,
    config: null,
    loading: true,
    error: "",
  });
  useEffect(() => {
    let active = true;
    async function load() {
      try {
        const config = await request("/auth/config");
        let user = null;
        try {
          user = await request("/auth/me");
          setCsrf(user.csrf_token);
        } catch (e) {
          if (e.status !== 401 && e.status !== 403) throw e;
        }
        if (active) setState({ config, user, loading: false, error: "" });
      } catch (e) {
        if (active)
          setState((s) => ({ ...s, loading: false, error: e.message }));
      }
    }
    load();
    const expired = () => {
      setCsrf("");
      setState((s) => ({ ...s, user: null }));
    };
    window.addEventListener("investscan-session-expired", expired);
    return () => {
      active = false;
      window.removeEventListener("investscan-session-expired", expired);
    };
  }, []);
  return (
    <Auth.Provider
      value={{ ...state, setUser: (user) => setState((s) => ({ ...s, user })) }}
    >
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route element={<Shell />}>
          <Route path="/" element={<Opportunities />} />
          <Route path="/objects/:id" element={<ObjectDetail />} />
          <Route path="/market" element={<Market />} />
          <Route path="/checks" element={<ChecksPage />} />
          <Route path="/negotiations" element={<DealsPage negotiations />} />
          <Route path="/deals" element={<DealsPage />} />
          <Route path="/buyers" element={<BuyersPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/sources" element={<SourcesPage />} />
          <Route path="/listings" element={<Navigate to="/" replace />} />
          <Route
            path="/integrations"
            element={<Navigate to="/sources" replace />}
          />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Auth.Provider>
  );
}
