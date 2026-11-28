# Development guide

Install the TypeScript compiler and run the checks from the project root:

```sh
npm install
npm test
npm run build
node dist/example.js
```

The source is split into validated domain models, in-memory repositories, business services,
query helpers, and small examples. `src/reports.ts` contains the paid-order daily sales summary;
`src/csv.ts` handles quoted CSV output. The self-test covers validation, relationships, queries,
and export formatting without a database or runtime dependency.
