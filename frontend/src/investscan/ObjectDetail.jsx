import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { send } from "./api";
import {
  areaText,
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
  PageHeader,
  STAGES,
  StageBadge,
  TRANSITIONS,
  useResource,
} from "./shared";

function Finance({ data, refresh }) {
  const obj = data.object;
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const initial = {
    resale_price: "",
    purchase_price: obj.asking_price,
    repairs: 0,
    legal_costs: 0,
    other_costs: 0,
    reserve: 0,
    target_profit: 0,
    holding_months: 3,
    monthly_holding: 0,
    annual_finance_pct: 0,
    financed_share_pct: 0,
    sale_cost_pct: 0,
    acquisition_cost_pct: 0,
    resale_basis: "",
  };
  const [form, setForm] = useState({ ...initial, ...data.evaluation?.inputs });
  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const payload = Object.fromEntries(
        Object.entries(form).map(([k, v]) => [
          k,
          k === "resale_basis" ? v : Number(v),
        ]),
      );
      await send(`/objects/${obj.id}/evaluations`, {
        ...payload,
        object_version: obj.version,
      });
      refresh();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  const labels = {
    resale_price: "Консервативная цена продажи, ₽",
    purchase_price: "Планируемая цена покупки, ₽",
    repairs: "Подготовка и ремонт, ₽",
    legal_costs: "Оформление и проверки, ₽",
    other_costs: "Прочие расходы и налоги, ₽",
    reserve: "Резерв, ₽",
    target_profit: "Целевая прибыль, ₽",
    holding_months: "Срок владения, месяцев",
    monthly_holding: "Содержание в месяц, ₽",
    annual_finance_pct: "Ставка финансирования, % годовых",
    financed_share_pct: "Доля заёмных средств в покупке, %",
    sale_cost_pct: "Расходы от цены продажи, %",
    acquisition_cost_pct: "Расходы от цены покупки, %",
  };
  const results = data.evaluation?.results;
  return (
    <div className="detail-columns">
      <section className="panel padded">
        <h2>Экономика выкупа</h2>
        <form onSubmit={submit}>
          <div className="form-grid">
            {Object.entries(labels).map(([k, l]) => (
              <Field key={k} label={l}>
                <input
                  type="number"
                  required
                  min={
                    [
                      "purchase_price",
                      "resale_price",
                      "holding_months",
                    ].includes(k)
                      ? 1
                      : 0
                  }
                  max={
                    k.includes("pct")
                      ? 100
                      : k === "holding_months"
                        ? 120
                        : 2000000000
                  }
                  step={k.includes("pct") ? "0.01" : 1}
                  value={form[k]}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, [k]: e.target.value }))
                  }
                />
              </Field>
            ))}
          </div>
          <Field label="Основание цены продажи">
            <textarea
              required
              minLength={3}
              maxLength={2000}
              value={form.resale_basis}
              onChange={(e) =>
                setForm((f) => ({ ...f, resale_basis: e.target.value }))
              }
              placeholder="Какие аналоги и фактические сделки использованы, дата проверки"
            />
          </Field>
          <p className="muted small">
            Налоги не определяются автоматически. Укажите их сумму в расходах.
            Сценарии показывают расчёт, а не обещание доходности.
          </p>
          {error && <ErrorBox>{error}</ErrorBox>}
          <button className="primary" disabled={busy}>
            {busy ? "Считаю…" : "Рассчитать и сохранить"}
          </button>
        </form>
      </section>
      <div className="stack">
        {results ? (
          <section className="panel padded">
            <div className="eyebrow">ПРЕДЕЛЬНАЯ ЦЕНА ВЫКУПА</div>
            <div className="big-number">{money(results.max_buyout_price)}</div>
            <Badge
              tone={
                data.evaluation_stale
                  ? "amber"
                  : results.headroom >= 0
                    ? "green"
                    : "red"
              }
            >
              {data.evaluation_stale
                ? "Нужен пересчёт"
                : results.headroom >= 0
                  ? "Покупка укладывается в лимит"
                  : "Цена выше лимита"}
            </Badge>
            <dl className="key-values">
              <div>
                <dt>Расчётная прибыль</dt>
                <dd>{money(results.profit)}</dd>
              </div>
              <div>
                <dt>Все затраты</dt>
                <dd>{money(results.total_cost)}</dd>
              </div>
              <div>
                <dt>Финансирование</dt>
                <dd>{money(results.financing_cost)}</dd>
              </div>
              <div>
                <dt>Рентабельность проекта</dt>
                <dd>{results.project_roi_pct}%</dd>
              </div>
              <div>
                <dt>Запас к лимиту</dt>
                <dd>{money(results.headroom)}</dd>
              </div>
            </dl>
            <h3>Цена продажи ±10%</h3>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Сценарий</th>
                    <th>Прибыль</th>
                    <th>Лимит</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    ["stress", "Снижение"],
                    ["base", "Базовый"],
                    ["upside", "Рост"],
                  ].map(([k, n]) => (
                    <tr key={k}>
                      <td>{n}</td>
                      <td>{money(results.scenarios[k].profit)}</td>
                      <td>{money(results.scenarios[k].max_buyout_price)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="muted small">
              Сохранено: {dateText(data.evaluation.created_at)} ·{" "}
              {data.evaluation.author}
            </p>
          </section>
        ) : (
          <section className="panel">
            <Empty title="Расчёт ещё не выполнен">
              Укажите консервативную цену продажи, затраты и целевую прибыль.
            </Empty>
          </section>
        )}
        <section className="panel padded">
          <h2>Аналоги в базе</h2>
          <div className="big-number smaller">
            {money(data.market.estimated_price)}
          </div>
          <Badge>{data.market.count} аналогов</Badge>
          <p className="muted small">{data.market.basis}</p>
          {data.market.items.slice(0, 10).map((x) => (
            <Link className="list-row" to={`/objects/${x.id}`} key={x.id}>
              <span>{x.title}</span>
              <strong>{money(x.price)}</strong>
            </Link>
          ))}
        </section>
      </div>
    </div>
  );
}
function CheckRow({ check, objectId, refresh }) {
  const [status, setStatus] = useState(check.status);
  const [evidence, setEvidence] = useState(check.evidence);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await send(
        `/objects/${objectId}/checks/${check.code}`,
        { status, evidence },
        "PUT",
      );
      refresh();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <form className="check-row" onSubmit={submit}>
      <div>
        <h3>{check.label}</h3>
        <span className="muted small">
          {check.author
            ? `${check.author} · ${dateText(check.checked_at)}`
            : "Пока не проверено"}
        </span>
      </div>
      <select
        aria-label={`Результат: ${check.label}`}
        value={status}
        onChange={(e) => setStatus(e.target.value)}
      >
        <option value="unknown">Не проверено</option>
        <option value="passed">Подтверждено</option>
        <option value="failed">Есть проблема</option>
      </select>
      <textarea
        aria-label={`Основание: ${check.label}`}
        placeholder="Документ, ссылка или основание результата"
        value={evidence}
        onChange={(e) => setEvidence(e.target.value)}
        required={status !== "unknown"}
        minLength={status !== "unknown" ? 3 : 0}
      />
      <button className="secondary" disabled={busy}>
        Сохранить
      </button>
      {error && <ErrorBox>{error}</ErrorBox>}
    </form>
  );
}
function ActivityForm({ obj, refresh }) {
  const [body, setBody] = useState("");
  const [kind, setKind] = useState("note");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await send(`/objects/${obj.id}/activities`, { body, kind });
      refresh();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <form onSubmit={submit}>
      <div className="row">
        <h2>Контакт с продавцом</h2>
        <select
          aria-label="Тип записи"
          value={kind}
          onChange={(e) => setKind(e.target.value)}
        >
          {[
            ["note", "Заметка"],
            ["call", "Звонок"],
            ["viewing", "Осмотр"],
            ["draft", "Черновик сообщения"],
          ].map(([v, n]) => (
            <option key={v} value={v}>
              {n}
            </option>
          ))}
        </select>
      </div>
      <Field label="Результат или текст">
        <textarea
          required
          rows={4}
          value={body}
          onChange={(e) => setBody(e.target.value)}
          placeholder="Что выяснили, о чём договорились, следующий шаг"
        />
      </Field>
      {kind === "draft" && (
        <p className="muted small">
          Черновик сохранится в карточке. Отправка продавцу пока не подключена.
        </p>
      )}
      {error && <ErrorBox>{error}</ErrorBox>}
      <button disabled={busy} className="primary">
        Сохранить запись
      </button>
    </form>
  );
}
function TaskForm({ objectId, refresh }) {
  const [title, setTitle] = useState("");
  const [assignee, setAssignee] = useState("");
  const [due, setDue] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await send("/tasks", {
        object_id: objectId,
        title,
        assignee,
        due_at: due ? new Date(due).toISOString() : null,
      });
      refresh();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <form onSubmit={submit}>
      <h3>Следующее действие</h3>
      <Field label="Задача">
        <input
          required
          minLength={3}
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Запросить документы у продавца"
        />
      </Field>
      <div className="form-grid">
        <Field label="Ответственный">
          <input
            value={assignee}
            onChange={(e) => setAssignee(e.target.value)}
          />
        </Field>
        <Field label="Срок (часовой пояс устройства)">
          <input
            type="datetime-local"
            value={due}
            onChange={(e) => setDue(e.target.value)}
          />
        </Field>
      </div>
      {error && <ErrorBox>{error}</ErrorBox>}
      <button className="secondary" disabled={busy}>
        Создать задачу
      </button>
    </form>
  );
}
export default function ObjectDetail() {
  const { id } = useParams();
  useEffect(() => {
    setStage("");
    setEdit(false);
    setError("");
    setTab("overview");
  }, [id]);
  const resource = useResource(`/objects/${id}`);
  const [tab, setTab] = useState("overview");
  const [stage, setStage] = useState("");
  const [reason, setReason] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [edit, setEdit] = useState(false);
  async function update(values) {
    setBusy(true);
    setError("");
    try {
      await send(
        `/objects/${id}`,
        { version: resource.data.object.version, ...values },
        "PATCH",
      );
      setStage("");
      setEdit(false);
      resource.refresh();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  if (resource.loading) return <Loading />;
  if (resource.error)
    return <ErrorBox retry={resource.refresh}>{resource.error}</ErrorBox>;
  const data = resource.data,
    obj = data.object,
    passed = data.checks.filter((x) => x.status === "passed").length;
  return (
    <>
      <Link className="back-link" to="/">
        <Icon name="back" size={16} />К возможностям
      </Link>
      <PageHeader
        eyebrow={`${ASSETS[obj.asset_type]} · ОБЪЕКТ №${obj.id}`}
        title={obj.title}
        actions={
          <>
            <button
              className={"icon-button " + (obj.starred ? "is-starred" : "")}
              aria-label={obj.starred ? "Убрать из избранного" : "В избранное"}
              aria-pressed={obj.starred}
              onClick={() => update({ starred: !obj.starred })}
              disabled={busy}
            >
              <Icon name="star" />
            </button>
            <button className="secondary" onClick={() => setEdit(true)}>
              Изменить
            </button>
            <select
              aria-label="Перевести на этап"
              value=""
              onChange={(e) => {
                setError("");
                setReason("");
                setStage(e.target.value);
              }}
            >
              <option value="">Перевести на этап</option>
              {TRANSITIONS[obj.stage].map((s) => (
                <option value={s} key={s}>
                  {STAGES[s]}
                </option>
              ))}
            </select>
          </>
        }
      >
        {obj.address || obj.district || "Адрес не указан"}
      </PageHeader>
      <div className="row wrap">
        <StageBadge stage={obj.stage} />
        {obj.urgency_evidence && (
          <Badge tone="amber">Срочность подтверждена записью</Badge>
        )}
        {data.evaluation_stale && <Badge tone="amber">Расчёт устарел</Badge>}
      </div>
      {error && !stage && !edit && <ErrorBox>{error}</ErrorBox>}
      <div className="stats-grid">
        <div className="stat">
          <span>Цена предложения</span>
          <strong>{money(obj.asking_price)}</strong>
          <small>{areaText(obj)}</small>
        </div>
        <div className="stat">
          <span>Лимит выкупа</span>
          <strong>{money(data.evaluation?.results.max_buyout_price)}</strong>
          <small>
            {data.evaluation_stale
              ? "Нужен пересчёт"
              : data.evaluation
                ? "По сохранённому расчёту"
                : "Расчёт не выполнен"}
          </small>
        </div>
        <div className="stat">
          <span>Проверки</span>
          <strong>
            {passed}
            <em> / {data.checks.length}</em>
          </strong>
          <small>
            {passed === data.checks.length
              ? "Все подтверждены"
              : "Есть незавершённые"}
          </small>
        </div>
        <div className="stat">
          <span>Покупатели по параметрам</span>
          <strong>{data.buyers.length}</strong>
          <small>Интерес нужно подтвердить</small>
        </div>
      </div>
      <div className="tabs" role="tablist">
        {[
          ["overview", "Объект"],
          ["finance", "Экономика"],
          ["checks", "Проверки"],
          ["activity", "Переговоры и задачи"],
          ["history", "История"],
        ].map(([v, n]) => (
          <button
            key={v}
            role="tab"
            aria-selected={tab === v}
            className={tab === v ? "active" : ""}
            onClick={() => setTab(v)}
          >
            {n}
          </button>
        ))}
      </div>
      {tab === "overview" && (
        <div className="detail-columns">
          <section className="panel padded">
            <h2>Характеристики</h2>
            <dl className="key-values">
              <div>
                <dt>Тип</dt>
                <dd>{ASSETS[obj.asset_type]}</dd>
              </div>
              <div>
                <dt>Район</dt>
                <dd>{obj.district || "Не указан"}</dd>
              </div>
              <div>
                <dt>Площадь</dt>
                <dd>{areaText(obj)}</dd>
              </div>
              <div>
                <dt>ВРИ / назначение</dt>
                <dd>{obj.land_use || "Не указано"}</dd>
              </div>
              <div>
                <dt>Кадастровый номер</dt>
                <dd>{obj.cadastral_number || "Не указан"}</dd>
              </div>
            </dl>
            <h3>Описание</h3>
            <p className="prewrap">
              {obj.description || "Описание пока не добавлено"}
            </p>
            <h3>Почему продажа срочная</h3>
            <p className="prewrap">
              {obj.urgency_evidence || "Подтверждения от продавца пока нет"}
            </p>
            <h3>Источники</h3>
            {data.sources.map((s) => (
              <div className="list-row" key={s.id}>
                <span>
                  {s.source}
                  <small>Проверено: {dateText(s.last_seen)}</small>
                </span>
                {s.url ? (
                  <a
                    href={s.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-link"
                  >
                    Открыть объявление ↗
                  </a>
                ) : (
                  <Badge>Добавлено вручную</Badge>
                )}
              </div>
            ))}
          </section>
          <div className="stack">
            <section className="panel padded">
              <h2>Подходящие заявки покупателей</h2>
              {data.buyers.length ? (
                data.buyers.map((b) => (
                  <div className="list-row" key={b.id}>
                    <div>
                      <strong>{b.name}</strong>
                      <small>{b.contact || "Контакт не указан"}</small>
                      <small>Обновлена: {dateText(b.updated_at)}</small>
                    </div>
                    <span>{money(b.max_budget)}</span>
                  </div>
                ))
              ) : (
                <p className="muted">
                  Совпадений по типу, району, площади и бюджету нет.
                </p>
              )}
            </section>
            {data.possible_duplicates.length > 0 && (
              <section className="panel padded">
                <h2>Возможные дубли</h2>
                <p className="muted">
                  Совпадает кадастровый номер. Записи не объединены
                  автоматически.
                </p>
                {data.possible_duplicates.map((d) => (
                  <Link className="list-row" key={d.id} to={`/objects/${d.id}`}>
                    {d.title}
                    <Icon name="arrow" />
                  </Link>
                ))}
              </section>
            )}
            <section className="panel padded">
              <h3>Координаты</h3>
              {obj.latitude != null ? (
                <>
                  <p>
                    {obj.latitude}, {obj.longitude}
                  </p>
                  <Link className="text-link" to={`/market?object=${obj.id}`}>
                    Показать на карте →
                  </Link>
                </>
              ) : (
                <p className="muted">Координаты не указаны при добавлении.</p>
              )}
            </section>
          </div>
        </div>
      )}
      {tab === "finance" && (
        <Finance
          key={data.evaluation?.id || "new"}
          data={data}
          refresh={resource.refresh}
        />
      )}{" "}
      {tab === "checks" && (
        <section className="panel padded">
          <h2>Проверки перед выкупом</h2>
          <p className="muted">
            Каждый результат сохраняется с основанием, автором и временем.
          </p>
          {data.checks.map((c) => (
            <CheckRow
              key={`${c.id}-${c.checked_at}`}
              check={c}
              objectId={obj.id}
              refresh={resource.refresh}
            />
          ))}
        </section>
      )}
      {tab === "activity" && (
        <div className="detail-columns">
          <div className="stack">
            <section className="panel padded">
              <ActivityForm obj={obj} refresh={resource.refresh} />
            </section>
            <section className="panel padded">
              <h2>Записи контактов</h2>
              {data.activities
                .filter((a) =>
                  ["note", "call", "viewing", "draft"].includes(a.kind),
                )
                .map((a) => (
                  <div className="timeline-item" key={a.id}>
                    <Badge>
                      {
                        {
                          note: "Заметка",
                          call: "Звонок",
                          viewing: "Осмотр",
                          draft: "Черновик",
                        }[a.kind]
                      }
                    </Badge>
                    <p className="prewrap">{a.body}</p>
                    <small>
                      {a.author} · {dateText(a.created_at)}
                    </small>
                  </div>
                ))}
            </section>
          </div>
          <section className="panel padded">
            <TaskForm objectId={obj.id} refresh={resource.refresh} />
            <h3>Задачи по объекту</h3>
            {data.tasks.map((t) => (
              <div className="list-row" key={t.id}>
                <div>
                  <strong>{t.title}</strong>
                  <small>
                    {t.assignee || "Без ответственного"} · {dateText(t.due_at)}
                  </small>
                </div>
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
                  {t.completed_at ? "Вернуть" : "Выполнено"}
                </button>
              </div>
            ))}
          </section>
        </div>
      )}
      {tab === "history" && (
        <div className="detail-columns">
          <section className="panel padded">
            <h2>История изменений</h2>
            {data.activities.map((a) => (
              <div className="timeline-item" key={a.id}>
                <p className="prewrap">{a.body}</p>
                <small>
                  {a.author} · {dateText(a.created_at)}
                </small>
              </div>
            ))}
          </section>
          <section className="panel padded">
            <h2>История цены</h2>
            {data.prices.map((p) => (
              <div className="list-row" key={p.id}>
                <span>{dateText(p.observed_at)}</span>
                <strong>{money(p.price)}</strong>
              </div>
            ))}
          </section>
        </div>
      )}
      {stage && (
        <Modal
          title={`Перевести: ${STAGES[stage]}`}
          onClose={() => setStage("")}
        >
          <form
            onSubmit={(e) => {
              e.preventDefault();
              update({ stage, reason });
            }}
          >
            <Field label="Основание решения">
              <textarea
                required
                minLength={3}
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                autoFocus
              />
            </Field>
            {error && <ErrorBox>{error}</ErrorBox>}
            <div className="form-actions">
              <button className="primary" disabled={busy}>
                Сохранить решение
              </button>
            </div>
          </form>
        </Modal>
      )}
      {edit && (
        <Modal title="Изменить объект" onClose={() => setEdit(false)}>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const f = new FormData(e.currentTarget);
              update({
                title: f.get("title"),
                asking_price: Number(f.get("asking_price")),
                urgency_evidence: f.get("urgency_evidence"),
              });
            }}
          >
            <Field label="Название">
              <input
                name="title"
                required
                minLength={3}
                defaultValue={obj.title}
              />
            </Field>
            <Field label="Цена предложения, ₽">
              <input
                name="asking_price"
                type="number"
                required
                min="1"
                defaultValue={obj.asking_price}
              />
            </Field>
            <Field label="Подтверждение срочности">
              <textarea
                name="urgency_evidence"
                defaultValue={obj.urgency_evidence}
              />
            </Field>
            <p className="muted small">
              После изменения данных потребуется обновить расчёт.
            </p>
            {error && <ErrorBox>{error}</ErrorBox>}
            <div className="form-actions">
              <button disabled={busy} className="primary">
                Сохранить
              </button>
            </div>
          </form>
        </Modal>
      )}
    </>
  );
}
