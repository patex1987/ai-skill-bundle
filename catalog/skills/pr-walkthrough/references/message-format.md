# Message Format

The engineer should be able to read each message in under a minute and always know
where they are. Detail is available on request; it is not front-loaded.

## Length budgets

| Message | Budget |
|---|---|
| Overview | about 20 lines including the topic list |
| Topic | about 30 lines; snippets count |
| Snippet | up to about 12 lines, at most two per topic |
| Answer to a follow-up | as short as the question allows; reuse the topic's references |
| Closing summary | about 15 lines; point to the record for the rest |

When a topic does not fit, split it into separate topics (see topic-map.md) or move
detail behind "ask for more". Never compress by dropping the evidence.

## Topic template

````text
Topic 2/5 — Total calculation
Files: src/checkout/total.ts, test/total.test.ts

In plain terms: the price is now worked out in two stages. First the items are added
up, then the coupon takes money off that sum.

How it works:
- `calculateTotal` adds item prices, then calls `applyCoupon` (src/checkout/total.ts:14).
- A fixed coupon subtracts its amount; a percentage coupon scales the subtotal (:22-31).

```ts
// src/checkout/total.ts:24-27
if (coupon.kind === 'fixed') {
  return subtotal - coupon.amountCents;
}
```

Why it's built this way: rounding happens once, at the end, so percentage and fixed
coupons round the same way (:33).

Findings:
1. [blocking] A fixed coupon larger than the subtotal gives a negative total.
   Evidence: :25 subtracts without a floor; nothing upstream caps the amount.
   Suggestion: clamp at zero, and add a test for it.

Route finding 1 (Open / Follow-up / drop), ask about this topic, or say "next" for
Topic 3/5 — Checkout wiring.
````

## Rules

- **Heading:** `Topic M/N — <name>` on the first line, then the files. Use the same
  topic name as in the overview.
- **In plain terms:** one or two sentences a product manager could follow. Describe
  what changes for the system or its users, not the syntax. An analogy is fine
  if it is exact. No code identifiers in this part.
- **How it works:** two to five bullets. Each names a symbol and a `path:line` or
  `path:start-end`. A bullet repeated from the same file can cite only `:line`.
- **Snippets:** show only the lines that carry the point, with a `// path:start-end`
  comment on the first line. Trim with `// …` comments, never silently. For a
  modification, a small diff (`-`/`+`) is better than the new version alone.
- **Why it's built this way:** include it only when the design choice is not obvious
  or has a tradeoff. Name the alternative it avoids.
- **Findings:** only in review mode, or for serious defects in explain mode. In
  review mode with nothing to raise, write "No findings." The full rules are in findings.md.
- **Gate:** the last line names the choices and the next topic with its number.
  When there are findings, the gate asks for their routing; the user may also ask
  questions first.
- **Follow-ups:** keep the `Topic M/N` heading when answering, so the position stays
  visible. Repeat the gate at the end.
- **Plain text over decoration:** no tables inside topics, no long headings, no emoji.
