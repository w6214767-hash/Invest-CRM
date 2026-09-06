import { useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { send } from "./api";
import { download, readImport } from "./import";
import {
  ASSETS,
  Badge,
  dateText,
  Empty,
  ErrorBox,
  Field,
  Icon,
  Loading,
  Modal,
  money,
  ObjectTable,
  PageHeader,
  STAGES,
  useResource,
} from "./shared";

export function Market() {
  const data = useResource("/objects?limit=200");
  const [params] = useSearchParams();
  const selected = params.get("object");
  const mapRef = useRef(null);
  const [tileError, setTileError] = useState(false);
  useEffect(() => {
    if (!data.data || !mapRef.current) return;
    const map = L.map(mapRef.current).setView([55.45, 37.75], 9);
    const layer = L.tileLayer(
      "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
      {
        attribution:
          '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        maxZoom: 19,
      },
    ).addTo(map);
    layer.on("tileerror", () => setTileError(true));
    const points = [];
    data.data.items
      .filter((x) => x.latitude != null && x.longitude != null)
      .forEach((obj) => {
        const point = [obj.latitude, obj.longitude];
        points.push(point);
        const body = document.createElement("div");
        const link = document.createElement("a");
        link.href = `/objects/${obj.id}`;
        link.textContent = obj.title;
        body.append(
          link,
          document.createElement("br"),
          document.createTextNode(money(obj.asking_price)),
        );
        const marker = L.circleMarker(point, {
          radius: 9,
          color: "#244f78",
          fillColor: obj.urgency_evidence ? "#dda33e" : "#447cad",
          fillOpacity: 0.9,
          weight: 2,
        })
          .addTo(map)
          .bindPopup(body);
        if (String(obj.id) === selected) {
          marker.openPopup();
          map.setView(point, 14);
        }
      });
    if (points.length && !selected)
      map.fitBounds(points, { padding: [35, 35], maxZoom: 13 });
    return () => map.remove();
  }, [data.data, selected]);
  if (data.loading) return <Loading />;
  if (data.error) return <ErrorBox retry={data.refresh}>{data.error}</ErrorBox>;
  const mapped = data.data.items.filter((x) => x.latitude != null);
  return (
    <>
      <PageHeader title="Карта и рынок">
        {mapped.length} объектов с координатами · до 200 последних объектов
      </PageHeader>
      {tileError && (
        <ErrorBox>
          Картографический слой недоступен. Карточки объектов доступны в списке.
        </ErrorBox>
      )}
      <section className="panel">
        <div
          ref={mapRef}
          className="market-map"
          aria-label="Карта инвестиционных объектов"
        />
        {!mapped.length && (
          <div className="map-note">
            Добавьте координаты в новые объекты, чтобы увидеть их на карте.
          </div>
        )}
      </section>
      <div className="section-toolbar">
        <h2>Объекты на карте</h2>
        <Link to="/">Все фильтры →</Link>
      </div>
      <section className="panel">
        {mapped.length ? (
          <ObjectTable items={mapped} />
        ) : (
          <Empty title="Нет объектов с координатами" />
        )}
      </section>
      <p className="muted small">
        Рыночные аналоги доступны во вкладке «Экономика» каждого объекта. Карта
        использует OpenStreetMap.
      </p>
    </>
  );
}
export function ChecksPage() {
  const resource = useResource("/tasks");
  const objects = useResource("/objects?stage=review&limit=200");
  const [error, setError] = useState("");
  return (
    <>
      <PageHeader title="Проверки и поручения">
        Документы, осмотры и следующие действия
      </PageHeader>
      {error && <ErrorBox>{error}</ErrorBox>}
      <section className="panel padded">
        <h2>Задачи</h2>
        {resource.loading ? (
          <Loading />
        ) : resource.error ? (
          <ErrorBox retry={resource.refresh}>{resource.error}</ErrorBox>
        ) : !resource.data.length ? (
          <Empty title="Задач пока нет">
            Создайте задачу в карточке объекта, во вкладке «Переговоры и
            задачи».
          </Empty>
        ) : (
          resource.data.map((t) => (
            <div className="list-row" key={t.id}>
              <div>
                <Link className="object-link" to={`/objects/${t.object_id}`}>
                  {t.title}
                </Link>
                <small>
                  {t.assignee || "Ответственный не назначен"} ·{" "}
                  {dateText(t.due_at)}
                </small>
              </div>
              <div className="row">
                <Badge tone={t.completed_at ? "green" : ""}>
                  {t.completed_at ? "Выполнено" : "В работе"}
                </Badge>
                <button
                  className="secondary"
                  onClick={async () => {
                    try {
                      await send(
                        `/tasks/${t.id}`,
                        { done: !t.completed_at },
                        "PATCH",
                      );
                      resource.refresh();
                    } catch (e) {
                      setError(e.message);
                    }
                  }}
                >
                  {t.completed_at ? "Вернуть" : "Завершить"}
                </button>
              </div>
            </div>
          ))
        )}
      </section>
      <div className="section-toolbar">
        <h2>Объекты на проверке</h2>
      </div>
      <section className="panel">
        {objects.loading ? (
          <Loading />
        ) : objects.error ? (
          <ErrorBox retry={objects.refresh}>{objects.error}</ErrorBox>
        ) : objects.data.items.length ? (
          <ObjectTable items={objects.data.items} />
        ) : (
          <Empty title="Нет объектов на этапе проверки" />
        )}
      </section>
    </>
  );
}
export function DealsPage({ negotiations = false }) {
  const resource = useResource("/objects?limit=200");
  const keys = negotiations
    ? ["negotiation", "approval"]
    : ["approval", "bought", "selling", "sold"];
  return (
    <>
      <PageHeader title={negotiations ? "Переговоры" : "Сделки и капитал"}>
        {negotiations
          ? "Контакты с продавцами и объекты на решении"
          : "От решения о выкупе до продажи"}
      </PageHeader>
      {resource.loading ? (
        <Loading />
      ) : resource.error ? (
        <ErrorBox retry={resource.refresh}>{resource.error}</ErrorBox>
      ) : (
        <>
          <div className={"kanban cols-" + keys.length}>
            {keys.map((stage) => {
              const items = resource.data.items.filter(
                (x) => x.stage === stage,
              );
              return (
                <section className="kanban-column" key={stage}>
                  <div className="row">
                    <h2>{STAGES[stage]}</h2>
                    <Badge>{items.length}</Badge>
                  </div>
                  {items.map((obj) => (
                    <Link
                      className="deal-card"
                      to={`/objects/${obj.id}`}
                      key={obj.id}
                    >
                      <small>
                        {ASSETS[obj.asset_type]} · {obj.district}
                      </small>
                      <h3>{obj.title}</h3>
                      <strong>{money(obj.asking_price)}</strong>
                      <small>Цена предложения</small>
                      {obj.urgency_evidence && (
                        <Badge tone="amber">Срочная продажа</Badge>
                      )}
                    </Link>
                  ))}
                  {!items.length && (
                    <p className="column-empty">Объектов пока нет</p>
                  )}
                </section>
              );
            })}
          </div>
          <p className="muted small">
            До 200 последних объектов. Фактические платежи и движение капитала в
            этой версии ещё не ведутся. Расчётная экономика — в карточках.
          </p>
        </>
      )}
    </>
  );
}
function BuyerForm({ buyer, onClose, saved }) {
  const [form, setForm] = useState(
    buyer
      ? {
          ...buyer,
          districts: buyer.districts.join(", "),
          max_area: buyer.max_area ?? "",
        }
      : {
          name: "",
          contact: "",
          asset_type: "land",
          districts: "",
          max_budget: "",
          min_area: 0,
          max_area: "",
          notes: "",
          active: true,
        },
  );
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const change = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));
  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const payload = {
        name: form.name,
        contact: form.contact,
        asset_type: form.asset_type,
        districts: form.districts
          .split(",")
          .map((x) => x.trim())
          .filter(Boolean),
        max_budget: Number(form.max_budget),
        min_area: Number(form.min_area),
        max_area: form.max_area === "" ? null : Number(form.max_area),
        notes: form.notes,
        active: form.active,
      };
      await send(
        buyer ? `/buyers/${buyer.id}` : "/buyers",
        payload,
        buyer ? "PUT" : "POST",
      );
      saved();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <Modal
      title={buyer ? "Заявка покупателя" : "Добавить покупателя"}
      onClose={onClose}
    >
      <form onSubmit={submit}>
        {[
          ["name", "Имя / компания"],
          ["contact", "Контакт"],
        ].map(([k, l]) => (
          <Field label={l} key={k}>
            <input
              required={k === "name"}
              minLength={k === "name" ? 2 : 0}
              value={form[k]}
              onChange={change(k)}
            />
          </Field>
        ))}
        <Field label="Тип объекта">
          <select value={form.asset_type} onChange={change("asset_type")}>
            {Object.entries(ASSETS).map(([v, n]) => (
              <option key={v} value={v}>
                {n}
              </option>
            ))}
          </select>
        </Field>
        <div className="form-grid">
          {[
            ["max_budget", "Бюджет до, ₽"],
            ["min_area", "Площадь от"],
            ["max_area", "Площадь до"],
          ].map(([k, l]) => (
            <Field label={l} key={k}>
              <input
                type="number"
                required={k !== "max_area"}
                min={k === "max_budget" ? 1 : 0}
                step={k === "max_budget" ? 1 : 0.01}
                value={form[k]}
                onChange={change(k)}
              />
            </Field>
          ))}
        </div>
        <Field label="Районы через запятую">
          <input value={form.districts} onChange={change("districts")} />
        </Field>
        <Field label="Дополнительные условия">
          <textarea value={form.notes} onChange={change("notes")} />
        </Field>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={form.active}
            onChange={(e) =>
              setForm((f) => ({ ...f, active: e.target.checked }))
            }
          />
          Заявка актуальна
        </label>
        {error && <ErrorBox>{error}</ErrorBox>}
        <div className="form-actions">
          <button className="primary" disabled={busy}>
            Сохранить заявку
          </button>
        </div>
      </form>
    </Modal>
  );
}
export function BuyersPage() {
  const resource = useResource("/buyers");
  const [editing, setEditing] = useState(undefined);
  return (
    <>
      <PageHeader
        title="Покупатели и партнёры"
        actions={
          <button className="primary" onClick={() => setEditing(null)}>
            <Icon name="plus" />
            Добавить покупателя
          </button>
        }
      >
        Заявки для подбора возможного выхода из инвестиции
      </PageHeader>
      <section className="panel">
        {resource.loading ? (
          <Loading />
        ) : resource.error ? (
          <ErrorBox retry={resource.refresh}>{resource.error}</ErrorBox>
        ) : !resource.data.length ? (
          <Empty title="Нет заявок покупателей">
            Добавьте требования покупателя. Совпадения появятся в карточках
            подходящих объектов.
          </Empty>
        ) : (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Покупатель</th>
                  <th>Тип и районы</th>
                  <th>Бюджет</th>
                  <th>Актуальность</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {resource.data.map((b) => (
                  <tr key={b.id}>
                    <td>
                      <strong>{b.name}</strong>
                      <small>{b.contact || "Без контакта"}</small>
                    </td>
                    <td>
                      {ASSETS[b.asset_type]}
                      <small>{b.districts.join(", ") || "Все районы"}</small>
                    </td>
                    <td>{money(b.max_budget)}</td>
                    <td>
                      <Badge tone={b.active ? "green" : ""}>
                        {b.active ? "Активна" : "Неактивна"}
                      </Badge>
                      <small>{dateText(b.updated_at)}</small>
                    </td>
                    <td>
                      <button
                        className="secondary"
                        onClick={() => setEditing(b)}
                      >
                        Изменить
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
      <section className="panel padded spaced">
        <h2>Партнёрский поток</h2>
        <p className="muted">
          Объекты партнёров можно импортировать с полем source: partners.
          Кабинет партнёра и вознаграждения — следующий этап.
        </p>
        <Link className="text-link" to="/sources">
          Открыть импорт →
        </Link>
      </section>
      {editing !== undefined && (
        <BuyerForm
          buyer={editing}
          onClose={() => setEditing(undefined)}
          saved={() => {
            setEditing(undefined);
            resource.refresh();
          }}
        />
      )}
    </>
  );
}
export function AnalyticsPage() {
  const resource = useResource("/overview");
  if (resource.loading) return <Loading />;
  if (resource.error)
    return <ErrorBox retry={resource.refresh}>{resource.error}</ErrorBox>;
  const d = resource.data;
  return (
    <>
      <PageHeader title="Аналитика">
        Данные на {dateText(d.as_of)} · московское время
      </PageHeader>
      <div className="stats-grid">
        {[
          ["Объектов в базе", d.total],
          ["Со срочностью", d.urgent],
          ["Проверок не завершено", d.pending_checks],
          ["Просроченных задач", d.overdue_tasks],
        ].map(([label, value]) => (
          <div className="stat" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>
      <div className="detail-columns">
        <section className="panel padded">
          <h2>Воронка</h2>
          {Object.entries(STAGES).map(([key, name]) => (
            <Link className="funnel-row" key={key} to={`/?stage=${key}`}>
              <span>{name}</span>
              <div className="funnel-track">
                <div
                  style={{
                    width: `${d.total ? ((d.stages[key] || 0) / d.total) * 100 : 0}%`,
                  }}
                />
              </div>
              <strong>{d.stages[key] || 0}</strong>
            </Link>
          ))}
        </section>
        <section className="panel padded">
          <h2>Последние действия</h2>
          {d.recent_activity.length ? (
            d.recent_activity.map((a) => (
              <div className="timeline-item" key={a.id}>
                {a.object_id ? (
                  <Link to={`/objects/${a.object_id}`} className="text-link">
                    Объект №{a.object_id}
                  </Link>
                ) : (
                  <Badge>Система</Badge>
                )}
                <p>{a.body}</p>
                <small>
                  {a.author} · {dateText(a.created_at)}
                </small>
              </div>
            ))
          ) : (
            <Empty title="Действий пока нет" />
          )}
        </section>
      </div>
    </>
  );
}
export function SourcesPage() {
  const resource = useResource("/sources");
  const [items, setItems] = useState(null);
  const [filename, setFilename] = useState("");
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  async function select(e) {
    setError("");
    setItems(null);
    setResult(null);
    const file = e.target.files?.[0];
    if (!file) return;
    setFilename(file.name);
    try {
      if (file.size > 2000000) throw new Error("Файл больше 2 МБ");
      setItems(readImport(await file.text(), file.name));
    } catch (e) {
      setError(e.message);
    }
  }
  async function upload() {
    setBusy(true);
    setError("");
    try {
      setResult(await send("/imports", { items }));
      setItems(null);
      resource.refresh();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  function template() {
    download(
      "investscan-import-example.csv",
      "external_id,source,title,asset_type,district,area,asking_price,land_use,urgency_evidence\nexample-training-001,file,Учебный пример — заменить перед импортом,land,Домодедово,10,2000000,ИЖС,\n",
      "text/csv;charset=utf-8",
    );
  }
  return (
    <>
      <PageHeader
        title="Источники и автоматизация"
        actions={
          <button className="secondary" onClick={template}>
            Скачать шаблон CSV
          </button>
        }
      >
        Подключения и журнал поступления объектов
      </PageHeader>
      {resource.loading ? (
        <Loading />
      ) : resource.error ? (
        <ErrorBox retry={resource.refresh}>{resource.error}</ErrorBox>
      ) : (
        <div className="source-grid">
          {resource.data.sources.map((s) => (
            <section className="panel padded" key={s.id}>
              <div className="row between">
                <Icon name="source" />
                <Badge tone={s.status === "available" ? "green" : ""}>
                  {s.status === "available" ? "Доступно" : "Не подключено"}
                </Badge>
              </div>
              <h3>{s.name}</h3>
              <p className="muted small">{s.count} объявлений в базе</p>
            </section>
          ))}
        </div>
      )}
      <section className="panel padded spaced">
        <h2>Импорт подборки</h2>
        <p className="muted">
          JSON или CSV, до 500 строк и 2 МБ. Повторная пара source + external_id
          обновляет цену объявления. Пакет проверяется до записи.
        </p>
        <div className="import-zone">
          <Icon name="source" size={28} />
          <label className="button secondary file-button">
            Выбрать файл
            <input
              type="file"
              accept=".json,.csv,application/json,text/csv"
              onChange={select}
            />
          </label>
          <span>{filename || "Выберите подготовленную подборку"}</span>
        </div>
        {error && <ErrorBox>{error}</ErrorBox>}
        {items && (
          <>
            <div className="section-toolbar">
              <h3>К импорту: {items.length} строк</h3>
              <button className="primary" disabled={busy} onClick={upload}>
                {busy ? "Импортирую…" : "Импортировать в базу"}
              </button>
            </div>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Название</th>
                    <th>Источник</th>
                    <th>Цена</th>
                  </tr>
                </thead>
                <tbody>
                  {items.slice(0, 10).map((x, i) => (
                    <tr key={i}>
                      <td>{x.title}</td>
                      <td>{x.source}</td>
                      <td>{money(x.asking_price)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {items.length > 10 && (
              <p className="muted small">Показаны первые 10 строк</p>
            )}
          </>
        )}
        {result && (
          <div className="success-box">
            Импорт завершён: новых {result.created}, изменений цены{" "}
            {result.updated}, без изменений {result.unchanged}.{" "}
            <Link to="/">Открыть объекты →</Link>
          </div>
        )}
        <details className="spaced">
          <summary>Поля файла</summary>
          <p className="small">
            Обязательные: external_id, title, asset_type, area, asking_price.
            Типы: land, apartment, house, commercial. Площадь участка — сотки,
            остальных — м². Дополнительно: source, district, address, url,
            cadastral_number, latitude, longitude, land_use, description,
            urgency_evidence. Один external_id всегда обозначает одно
            объявление.
          </p>
        </details>
      </section>
      <section className="panel padded spaced">
        <h2>Журнал импорта</h2>
        {resource.data?.runs.length ? (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Время</th>
                  <th>Автор</th>
                  <th>Новые</th>
                  <th>Цена изменена</th>
                  <th>Без изменений</th>
                </tr>
              </thead>
              <tbody>
                {resource.data.runs.map((r) => (
                  <tr key={r.id}>
                    <td>{dateText(r.created_at)}</td>
                    <td>{r.author}</td>
                    <td>{r.created}</td>
                    <td>{r.updated}</td>
                    <td>{r.unchanged}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="muted">Импортов пока не было.</p>
        )}
      </section>
    </>
  );
}
