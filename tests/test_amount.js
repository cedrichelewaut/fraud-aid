// Run with: node tests/test_amount.js
const parse = require("../static/amount.js");
const assert = require("assert");

const ok = [
  ["444", 444], ["444,00", 444], ["444,5", 444.5], ["444.50", 444.5], ["444,50", 444.5],
  ["1.234,56", 1234.56], ["1,234.56", 1234.56], ["1 234,56", 1234.56], ["1 234,56", 1234.56],
  ["1.234", 1234], ["12.345.678", 12345678], ["1,234,567", 1234567], ["€ 444,00", 444], ["444 EUR", 444],
  ["10000", 10000], [",50", 0.5], ["0,99", 0.99], ["7,4", 7.4],
];
for (const [input, want] of ok) assert.strictEqual(parse(input), want, `${input} -> ${parse(input)} (want ${want})`);

for (const bad of ["", "abc", ",", ".", "12,345,67.8", "1,2,3,45", "4,4444", "--5", "12e3", "1,23,456"]) {
  assert.ok(Number.isNaN(parse(bad)), `${JSON.stringify(bad)} should be rejected, got ${parse(bad)}`);
}
console.log("amount ok");
