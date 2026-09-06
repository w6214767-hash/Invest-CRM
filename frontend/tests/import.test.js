import test from "node:test";
import assert from "node:assert/strict";
import { parseCsv, readImport } from "../src/investscan/import.js";
test("CSV handles BOM, quoted multiline fields, comma prices and CRLF", () => {
  const parsed = parseCsv(
    '\uFEFFexternal_id;title;area;asking_price\r\na;"Дом, \"\"Юг\"\"\nМосква";"10,5";3000000\r\n',
  );
  assert.equal(parsed[0].title, 'Дом, "Юг"\nМосква');
  assert.equal(parsed[0].area, 10.5);
});
test("Malformed CSV and duplicate headers cannot silently shift columns", () => {
  assert.throws(() => parseCsv("title,title\na,b"));
  assert.throws(() => parseCsv('title,area\n"unfinished,10'));
  assert.throws(() => parseCsv("title,area\na,1,2"));
});
test("Imports require stable IDs and positive integer prices", () => {
  assert.throws(() => readImport('[{"title":"Дом"}]', "a.json"));
  const item = {
    external_id: "one",
    title: "Дом",
    asset_type: "house",
    area: 100,
    asking_price: 2000000,
  };
  assert.equal(readImport(JSON.stringify([item]), "a.json")[0].source, "file");
  assert.throws(() =>
    readImport(JSON.stringify([{ ...item, asking_price: 1.1 }]), "a.json"),
  );
});
