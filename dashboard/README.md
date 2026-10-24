# Optimus dashboard

A live view of the robot's telemetry: the latest temperature, humidity and position, a map with its trail, and a line chart for each sensor. It polls the [telemetry API](../infra/README.md) every few seconds.

## Run it locally

```bash
cd dashboard
npm install
cp public/config.example.json public/config.json   # then paste the API URL into it
npm run dev
```

Open the printed URL and enter the API key when asked. The key is stored only in your browser.

## Settings

- **API URL:** `public/config.json` locally. On AWS, Terraform writes it for you.
- **Everything else:** poll interval, time ranges, staleness threshold and map tiles live in [`src/config.ts`](src/config.ts).
- **Colors:** the CSS variables at the top of [`src/styles.css`](src/styles.css), with light and dark values.

## Deploy

The dashboard is a static site in a public S3 bucket, deployed with the rest of the infra:

```bash
cd dashboard && npm run build && cd ../infra
terraform apply
terraform output -raw dashboard_url
```

## Layout

```
dashboard/
├── index.html            # page structure
├── public/               # config.json (API URL, gitignored)
├── src/
│   ├── main.ts           # polling loop that wires data to the widgets
│   ├── api.ts            # API client and response parsing
│   ├── config.ts         # tunables
│   ├── format.ts         # number and time formatting
│   ├── theme.ts          # reads colors from CSS variables
│   ├── styles.css
│   └── ui/               # one file per widget: tiles, line chart, map, status, time ranges, login
└── tests/
```

## Commands

```bash
npm run dev     # local server with hot reload
npm run build   # type-check and build into dist/
npm test        # unit tests
```
