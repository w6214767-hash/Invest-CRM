// Strict CSV parsing: quoted commas/newlines, BOM, doubled quotes and CRLF.
export function parseCsv(text) {
  text = text.replace(/^\uFEFF/, "");
  const header = text.split(/\r?\n/, 1)[0];
  const delimiter = header.includes(";") ? ";" : ",";
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  let closed = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c === '"' && text[i + 1] === '"') {
        field += '"';
        i++;
      } else if (c === '"') {
        quoted = false;
        closed = true;
      } else field += c;
    } else if (c === delimiter) {
      row.push(field);
      field = "";
      closed = false;
    } else if (c === "\n" || c === "\r") {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(field);
      if (row.some((x) => x.trim())) rows.push(row);
      row = [];
      field = "";
      closed = false;
    } else if (c === '"' && !field && !closed) quoted = true;
    else if (closed || c === '"') throw new Error("Некорректные кавычки в CSV");
    else field += c;
  }
  if (quoted) throw new Error("Незакрытые кавычки в CSV");
  row.push(field);
  if (row.some((x) => x.trim())) rows.push(row);
  if (rows.length < 2)
    throw new Error("В файле нужны заголовок и хотя бы одна строка");
  const keys = rows.shift().map((x) => x.trim());
  if (new Set(keys).size !== keys.length || keys.some((k) => !k))
    throw new Error("Заголовки должны быть уникальными и непустыми");
  const numeric = new Set(["area", "asking_price", "latitude", "longitude"]);
  return rows.map((values, idx) => {
    if (values.length !== keys.length)
      throw new Error(
        `Строка ${idx + 2}: число столбцов не совпадает с заголовком`,
      );
    return Object.fromEntries(
      keys.flatMap((key, i) => {
        const value = values[i].trim();
        if (!value) return [];
        if (!numeric.has(key)) return [[key, value]];
        const number = Number(value.replace(",", "."));
        if (!Number.isFinite(number))
          throw new Error(`Строка ${idx + 2}: неверное число в ${key}`);
        return [[key, number]];
      }),
    );
  });
}
export function readImport(text, filename) {
  if (text.length > 2_000_000)
    throw new Error("Файл больше 2 МБ; разделите его на части");
  let items;
  if (filename.toLowerCase().endsWith(".csv")) items = parseCsv(text);
  else {
    const parsed = JSON.parse(text);
    items = Array.isArray(parsed) ? parsed : parsed.items;
  }
  if (!Array.isArray(items) || !items.length || items.length > 500)
    throw new Error("Нужен массив от 1 до 500 объектов");
  for (const [index, item] of items.entries()) {
    if (
      !item ||
      typeof item !== "object" ||
      !item.external_id ||
      !item.title ||
      !item.asset_type ||
      !Number.isFinite(Number(item.area)) ||
      Number(item.area) <= 0 ||
      !Number.isInteger(Number(item.asking_price)) ||
      Number(item.asking_price) <= 0
    )
      throw new Error(
        `Строка ${index + 1}: нужны external_id, title, asset_type, положительные area и asking_price`,
      );
  }
  return items.map((item) => ({ ...item, source: item.source || "file" }));
}
export function download(name, content, type = "text/plain") {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
