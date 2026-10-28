# Optimus dashboard

A live view of the robot's telemetry on a full-screen campus map: the latest readings, the robot's trail (in 2D or with 3D buildings), and a chart per sensor. Optimus shows up as a little robot face whose eyes follow the data: awake when it's live, sleepy when it goes stale, asleep when the API is unreachable. It polls the [telemetry API](../fiware/README.md) every few seconds.

## Run it locally

```bash
cd dashboard
npm install
cp public/config.example.json public/config.json   # points at the FIWARE api on localhost
npm run dev
```

Start the [FIWARE stack](../fiware/README.md) first, then open the printed URL and enter the API key when asked. The key is stored only in your browser.

## Settings

- **API URL:** `public/config.json` locally. When the FIWARE microservice serves the dashboard, it answers `config.json` itself.
- **Everything else:** poll interval, time ranges, staleness threshold, campus bounds, basemaps and the 3D view live in [`src/config.ts`](src/config.ts).
- **Colors and fonts:** the tokens in [`src/styles/tokens.css`](src/styles/tokens.css), with light and dark values.

## Deploy

The FIWARE microservice builds the dashboard into its image and serves it at `/`:

```bash
cd fiware
docker compose up -d --build api
```

## Layout

```
dashboard/
├── index.html            # page structure
├── public/               # config.json for npm run dev (API URL, gitignored)
├── src/
│   ├── main.ts           # polling loop that wires data to the widgets
│   ├── api.ts            # API client and response parsing
│   ├── config.ts         # tunables
│   ├── format.ts         # number, distance and time formatting
│   ├── geo.ts            # trail length and GeoJSON
│   ├── theme.ts          # reads colors from CSS variables, dark mode, reduced motion
│   ├── styles/           # tokens, layout, panels, robot face
│   └── ui/               # one file per widget: KPIs, line chart, map, robot, status, time ranges, login
└── tests/
```

## Commands

```bash
npm run dev     # local server with hot reload
npm run build   # type-check and build into dist/
npm test        # unit tests
```
