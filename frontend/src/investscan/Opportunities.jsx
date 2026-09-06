import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { queryString, send } from "./api";
import ObjectForm from "./ObjectForm";
import {
  ASSETS,
  Badge,
  Empty,
  ErrorBox,
  Field,
  Icon,
  Loading,
  Modal,
  ObjectTable,
  PageHeader,
  STAGES,
  useResource,
} from "./shared";
const defaults = {
  q: "",
  asset_type: "",
  district: "",
  stage: "",
  min_price: "",
  max_price: "",
  min_area: "",
  max_area: "",
  urgent: false,
  starred: false,
  exclude: "",
};
export default function Opportunities() {
  const [params, setParams] = useSearchParams();
  const initial = { ...defaults, ...Object.fromEntries(params) };
  initial.urgent = params.get("urgent") === "true";
  initial.starred = params.get("starred") === "true";
  const [draft, setDraft] = useState(initial);
  const [add, setAdd] = useState(false);
  const [save, setSave] = useState(false);
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();
  const resource = useResource("/objects?" + params.toString());
  const profiles = useResource("/searches");
  const change = (k) => (e) => setDraft((d) => ({ ...d, [k]: e.target.value }));
  const apply = (values) => {
    setDraft(values);
    setParams(queryString(values));
  };
  async function saveProfile(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    const values = {
      ...defaults,
      ...Object.fromEntries([...params].filter(([key]) => key in defaults)),
      urgent: params.get("urgent") === "true",
      starred: params.get("starred") === "true",
    };
    for (const k of ["min_price", "min_area"])
      values[k] = Number(values[k] || 0);
    for (const k of ["max_price", "max_area"])
      values[k] = values[k] === "" ? null : Number(values[k]);
    for (const k of ["stage", "asset_type"]) values[k] ||= null;
    try {
      await send("/searches", { name, filters: values });
      setSave(false);
      profiles.refresh();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <PageHeader
        title="Возможности"
        actions={
          <>
            <Link className="button secondary" to="/sources">
              Импортировать
            </Link>
            <button className="primary" onClick={() => setAdd(true)}>
              <Icon name="plus" />
              Добавить объект
            </button>
          </>
        }
      >
        Объекты для срочного выкупа
      </PageHeader>
      <div className="quick-filters">
        <button
          className={
            !params.get("urgent") && !params.get("starred") ? "active" : ""
          }
          onClick={() => apply(defaults)}
        >
          Все объекты
        </button>
        <button
          className={params.get("urgent") ? "active" : ""}
          onClick={() => apply({ ...draft, urgent: !draft.urgent })}
        >
          С подтверждённой срочностью
        </button>
        <button
          className={params.get("starred") ? "active" : ""}
          onClick={() => apply({ ...draft, starred: !draft.starred })}
        >
          <Icon name="star" size={16} />
          Избранное
        </button>
      </div>
      <section className="panel filters">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            apply(draft);
          }}
        >
          <div className="filter-top">
            <input
              aria-label="Поиск по названию, адресу или кадастровому номеру"
              placeholder="Название, адрес или кадастровый номер"
              value={draft.q}
              onChange={change("q")}
            />
            <select
              aria-label="Тип объекта"
              value={draft.asset_type || ""}
              onChange={change("asset_type")}
            >
              <option value="">Все типы</option>
              {Object.entries(ASSETS).map(([v, n]) => (
                <option value={v} key={v}>
                  {n}
                </option>
              ))}
            </select>
            <input
              aria-label="Район"
              placeholder="Район"
              value={draft.district}
              onChange={change("district")}
            />
            <button className="primary">Найти</button>
          </div>
          <details>
            <summary>Цена, площадь и дополнительные условия</summary>
            <div className="form-grid four">
              {[
                ["min_price", "Цена от, ₽"],
                ["max_price", "Цена до, ₽"],
                ["min_area", "Площадь от"],
                ["max_area", "Площадь до"],
              ].map(([k, l]) => (
                <Field label={l} key={k}>
                  <input
                    type="number"
                    min="0"
                    step={k.includes("area") ? "0.01" : "1"}
                    value={draft[k] ?? ""}
                    onChange={change(k)}
                  />
                </Field>
              ))}
              <Field label="Этап">
                <select value={draft.stage || ""} onChange={change("stage")}>
                  <option value="">Все этапы</option>
                  {Object.entries(STAGES).map(([v, n]) => (
                    <option value={v} key={v}>
                      {n}
                    </option>
                  ))}
                </select>
              </Field>
              <Field label="Исключить слова" hint="Через запятую">
                <input value={draft.exclude} onChange={change("exclude")} />
              </Field>
            </div>
          </details>
        </form>
      </section>
      <div className="section-toolbar">
        <div className="row">
          <h2>Подборка</h2>
          {resource.data && <Badge>{resource.data.total}</Badge>}
        </div>
        <div className="row">
          <select
            aria-label="Сохранённый поиск"
            defaultValue=""
            onChange={(e) => {
              const p = profiles.data?.find(
                (p) => String(p.id) === e.target.value,
              );
              if (p) apply({ ...defaults, ...p.filters });
              e.target.value = "";
            }}
          >
            <option value="">Сохранённые поиски</option>
            {profiles.data?.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
          <button
            className="secondary"
            onClick={() => {
              setError("");
              setSave(true);
            }}
          >
            Сохранить поиск
          </button>
        </div>
      </div>
      <section className="panel">
        {resource.loading ? (
          <Loading />
        ) : resource.error ? (
          <ErrorBox retry={resource.refresh}>{resource.error}</ErrorBox>
        ) : resource.data.items.length ? (
          <ObjectTable items={resource.data.items} />
        ) : (
          <Empty
            title="Объектов в этой подборке пока нет"
            action={
              <button className="primary" onClick={() => setAdd(true)}>
                Добавить первый объект
              </button>
            }
          >
            Добавьте объект вручную или импортируйте подборку из файла.
            Автоматические источники подключаются отдельно.
          </Empty>
        )}
      </section>
      {resource.data?.total > 50 && (
        <div className="pagination">
          <button
            disabled={!Number(params.get("offset"))}
            onClick={() =>
              setParams((p) => {
                p.set("offset", Math.max(0, Number(p.get("offset") || 0) - 50));
                return p;
              })
            }
          >
            Назад
          </button>
          <span>
            {Number(params.get("offset") || 0) + 1}–
            {Math.min(
              Number(params.get("offset") || 0) + 50,
              resource.data.total,
            )}{" "}
            из {resource.data.total}
          </span>
          <button
            disabled={
              Number(params.get("offset") || 0) + 50 >= resource.data.total
            }
            onClick={() =>
              setParams((p) => {
                p.set("offset", Number(p.get("offset") || 0) + 50);
                return p;
              })
            }
          >
            Далее
          </button>
        </div>
      )}
      {add && (
        <ObjectForm
          onClose={() => setAdd(false)}
          onSaved={(obj) => navigate(`/objects/${obj.id}`)}
        />
      )}{" "}
      {save && (
        <Modal title="Сохранить текущий поиск" onClose={() => setSave(false)}>
          <form onSubmit={saveProfile}>
            <Field label="Название">
              <input
                required
                minLength={2}
                value={name}
                onChange={(e) => setName(e.target.value)}
                autoFocus
              />
            </Field>
            {error && <ErrorBox>{error}</ErrorBox>}
            <div className="form-actions">
              <button className="primary" disabled={busy}>
                {busy ? "Сохраняю…" : "Сохранить"}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </>
  );
}
