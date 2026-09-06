import { useEffect, useId, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { request } from "./api";
export const ASSETS = {
  land: "Участок",
  apartment: "Квартира",
  house: "Дом",
  commercial: "Коммерция",
};
export const STAGES = {
  new: "Новые",
  review: "Проверка",
  negotiation: "Переговоры",
  approval: "Решение",
  bought: "Выкуплен",
  selling: "В продаже",
  sold: "Продан",
  rejected: "Отклонён",
};
export const TRANSITIONS = {
  new: ["review", "rejected"],
  review: ["negotiation", "approval", "rejected"],
  negotiation: ["review", "approval", "rejected"],
  approval: ["review", "bought", "rejected"],
  bought: ["selling"],
  selling: ["sold"],
  sold: [],
  rejected: ["review"],
};
export const money = (value) =>
  value == null
    ? "—"
    : new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 0 }).format(
        value,
      ) + " ₽";
export const areaText = (obj) =>
  new Intl.NumberFormat("ru-RU").format(obj.area) +
  (obj.asset_type === "land" ? " сот." : " м²");
export const dateText = (value) =>
  value
    ? new Intl.DateTimeFormat("ru-RU", {
        dateStyle: "short",
        timeStyle: "short",
        timeZone: "Europe/Moscow",
      }).format(new Date(/Z|[+-]\d\d:\d\d$/.test(value) ? value : value + "Z"))
    : "—";
export function Icon({ name, size = 20 }) {
  const paths = {
    scan: (
      <>
        <circle cx="10" cy="10" r="6" />
        <path d="m15 15 5 5M10 7v6M7 10h6" />
      </>
    ),
    map: (
      <>
        <path d="m3 5 6-2 6 2 6-2v16l-6 2-6-2-6 2ZM9 3v16M15 5v16" />
      </>
    ),
    check: (
      <>
        <path d="M9 3H5v18h14V3h-4M9 2h6v4H9ZM8 13l3 3 5-6" />
      </>
    ),
    chat: <path d="M21 4H3v13h5l4 4v-4h9Z" />,
    deal: (
      <>
        <rect x="3" y="7" width="18" height="14" rx="2" />
        <path d="M8 7V3h8v4M3 12h18M10 12v3h4v-3" />
      </>
    ),
    buyers: (
      <>
        <circle cx="9" cy="7" r="4" />
        <path d="M2 21v-3a7 7 0 0 1 14 0v3M16 3a4 4 0 0 1 0 8M18 14c3 0 4 2 4 5" />
      </>
    ),
    chart: (
      <>
        <path d="M3 3v18h18M7 16v-5M12 16V7M17 16V4" />
      </>
    ),
    source: (
      <>
        <ellipse cx="12" cy="5" rx="9" ry="3" />
        <path d="M3 5v14c0 4 18 4 18 0V5M3 12c0 4 18 4 18 0" />
      </>
    ),
    back: <path d="m10 5-7 7 7 7M3 12h18" />,
    plus: <path d="M12 4v16M4 12h16" />,
    arrow: <path d="m9 5 7 7-7 7" />,
    close: <path d="m5 5 14 14M19 5 5 19" />,
    star: <path d="m12 3 3 6 7 1-5 5 1 7-6-3-6 3 1-7-5-5 7-1Z" />,
    bell: (
      <>
        <path d="M5 17V9a7 7 0 0 1 14 0v8l2 2H3ZM10 22h4" />
      </>
    ),
  };
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[name] || paths.scan}
    </svg>
  );
}
export function useResource(path) {
  const [state, setState] = useState({
    path,
    data: null,
    error: "",
    loading: true,
  });
  const [key, setKey] = useState(0);
  useEffect(() => {
    let live = true;
    setState({ path, data: null, error: "", loading: true });
    request(path)
      .then(
        (data) => live && setState({ path, data, error: "", loading: false }),
      )
      .catch(
        (e) =>
          live &&
          setState({ path, data: null, error: e.message, loading: false }),
      );
    return () => {
      live = false;
    };
  }, [path, key]);
  return {
    ...(state.path === path ? state : { data: null, error: "", loading: true }),
    refresh: () => setKey((k) => k + 1),
  };
}
export function Loading() {
  return (
    <div className="empty" role="status">
      <span className="spinner" />
      Загружаю данные…
    </div>
  );
}
export function ErrorBox({ children, retry }) {
  return (
    <div role="alert" className="error-box">
      {children}
      {retry && <button onClick={retry}>Повторить</button>}
    </div>
  );
}
export function Empty({ title, children, action }) {
  return (
    <div className="empty">
      <Icon name="scan" size={30} />
      <h3>{title}</h3>
      {children && <p>{children}</p>}
      {action}
    </div>
  );
}
export function Badge({ children, tone = "" }) {
  return <span className={"badge " + tone}>{children}</span>;
}
export function StageBadge({ stage }) {
  return (
    <Badge
      tone={
        ["bought", "sold"].includes(stage)
          ? "green"
          : stage === "approval"
            ? "amber"
            : ""
      }
    >
      {STAGES[stage]}
    </Badge>
  );
}
export function Field({ label, children, hint }) {
  return (
    <label className="field">
      <span>{label}</span>
      <span className="field-control">{children}</span>
      {hint && <small>{hint}</small>}
    </label>
  );
}
export function PageHeader({
  eyebrow = "ИНВЕСТСКАН",
  title,
  children,
  actions,
}) {
  return (
    <header className="page-header">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        {children && <p>{children}</p>}
      </div>
      {actions && <div className="header-actions">{actions}</div>}
    </header>
  );
}
export function Modal({ title, onClose, children, wide = false }) {
  const ref = useRef(null);
  const heading = useId();
  useEffect(() => {
    const el = ref.current;
    el.showModal();
    return () => el.close();
  }, []);
  return (
    <dialog
      ref={ref}
      className={"modal " + (wide ? "wide" : "")}
      aria-labelledby={heading}
      onCancel={(e) => {
        e.preventDefault();
        onClose();
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="modal-head">
        <h2 id={heading}>{title}</h2>
        <button className="icon-button" aria-label="Закрыть" onClick={onClose}>
          <Icon name="close" />
        </button>
      </div>
      {children}
    </dialog>
  );
}
export function ObjectTable({ items }) {
  return (
    <div className="table-scroll">
      <table>
        <thead>
          <tr>
            <th>Объект</th>
            <th>Цена предложения</th>
            <th>Площадь</th>
            <th>Этап</th>
            <th>Срочность</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {items.map((obj) => (
            <tr key={obj.id}>
              <td>
                <Link className="object-link" to={`/objects/${obj.id}`}>
                  {obj.title}
                </Link>
                <small>
                  {ASSETS[obj.asset_type]} · {obj.district || "Район не указан"}
                </small>
              </td>
              <td className="money">{money(obj.asking_price)}</td>
              <td>{areaText(obj)}</td>
              <td>
                <StageBadge stage={obj.stage} />
              </td>
              <td>
                {obj.urgency_evidence ? (
                  <Badge tone="amber">Есть основание</Badge>
                ) : (
                  <span className="muted">Не подтверждена</span>
                )}
              </td>
              <td>
                <Link
                  aria-label={`Открыть ${obj.title}`}
                  to={`/objects/${obj.id}`}
                >
                  <Icon name="arrow" />
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
