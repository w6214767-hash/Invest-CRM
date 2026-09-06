import { useState } from "react";
import { send } from "./api";
import { ASSETS, ErrorBox, Field, Modal } from "./shared";
export default function ObjectForm({ onClose, onSaved }) {
  const [data, set] = useState({
    title: "",
    asset_type: "land",
    district: "",
    address: "",
    area: "",
    asking_price: "",
    land_use: "",
    cadastral_number: "",
    latitude: "",
    longitude: "",
    description: "",
    urgency_evidence: "",
    url: "",
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const change = (key) => (e) => set((d) => ({ ...d, [key]: e.target.value }));
  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const payload = {
        ...data,
        area: Number(data.area),
        asking_price: Number(data.asking_price),
        cadastral_number: data.cadastral_number || null,
        latitude: data.latitude === "" ? null : Number(data.latitude),
        longitude: data.longitude === "" ? null : Number(data.longitude),
      };
      const result = await send("/objects", payload);
      onSaved(result.object);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <Modal title="Добавить объект" onClose={onClose} wide>
      <form onSubmit={submit}>
        <div className="form-grid">
          <Field label="Название">
            <input
              required
              minLength={3}
              maxLength={500}
              value={data.title}
              onChange={change("title")}
              placeholder="Участок, 10 соток, Домодедово"
            />
          </Field>
          <Field label="Тип объекта">
            <select value={data.asset_type} onChange={change("asset_type")}>
              {Object.entries(ASSETS).map(([v, n]) => (
                <option value={v} key={v}>
                  {n}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Цена предложения, ₽">
            <input
              type="number"
              required
              min="1"
              max="2000000000"
              value={data.asking_price}
              onChange={change("asking_price")}
            />
          </Field>
          <Field
            label={`Площадь, ${data.asset_type === "land" ? "сотки" : "м²"}`}
          >
            <input
              type="number"
              required
              min="0.01"
              step="0.01"
              value={data.area}
              onChange={change("area")}
            />
          </Field>
          {[
            ["district", "Район"],
            ["address", "Адрес"],
            ["land_use", "ВРИ / назначение"],
            ["cadastral_number", "Кадастровый номер"],
          ].map(([k, l]) => (
            <Field label={l} key={k}>
              <input value={data[k]} onChange={change(k)} />
            </Field>
          ))}
          <Field label="Широта">
            <input
              type="number"
              step="any"
              min="-90"
              max="90"
              value={data.latitude}
              onChange={change("latitude")}
            />
          </Field>
          <Field label="Долгота">
            <input
              type="number"
              step="any"
              min="-180"
              max="180"
              value={data.longitude}
              onChange={change("longitude")}
            />
          </Field>
        </div>
        <Field label="Ссылка на объявление">
          <input
            type="url"
            value={data.url}
            onChange={change("url")}
            placeholder="https://…"
          />
        </Field>
        <Field label="Описание">
          <textarea
            rows={3}
            value={data.description}
            onChange={change("description")}
          />
        </Field>
        <Field
          label="Подтверждение срочности"
          hint="Например: продавец сообщил срок продажи. Не заполняйте по предположению."
        >
          <textarea
            rows={2}
            value={data.urgency_evidence}
            onChange={change("urgency_evidence")}
          />
        </Field>
        {error && <ErrorBox>{error}</ErrorBox>}
        <div className="form-actions">
          <button type="button" className="secondary" onClick={onClose}>
            Отмена
          </button>
          <button disabled={busy} className="primary">
            {busy ? "Сохраняю…" : "Добавить объект"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
