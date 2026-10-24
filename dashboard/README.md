# Optimus dashboard

A live view of the robot's telemetry on a full-screen campus map: the latest readings, the robot's trail (in 2D or with 3D buildings), and a chart per sensor. Optimus shows up as a little robot face whose eyes follow the data: awake when it's live, sleepy when it goes stale, asleep when the API is unreachable. It polls the [telemetry API](../infra/README.md) every few seconds, and shows the robot's camera when the [video signaling](../infra/README.md#video-streaming) server is set up.

## Run it locally

```bash
cd dashboard
npm install
cp public/config.example.json public/config.json   # then paste the API URL into it
npm run dev
```

Open the printed URL and enter the API key when asked. The key is stored only in your browser.

## Settings

- **API URL, signaling URL and room:** `public/config.json` locally. On AWS, Terraform writes it for you. Without `signalingUrl` the camera panel stays hidden.
- **Everything else:** poll interval, time ranges, staleness threshold, campus bounds, basemaps and the 3D view live in [`src/config.ts`](src/config.ts).
- **Colors and fonts:** the tokens in [`src/styles/tokens.css`](src/styles/tokens.css), with light and dark values.

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
│   ├── format.ts         # number, distance and time formatting
│   ├── geo.ts            # trail length and GeoJSON
│   ├── signaling.ts      # OpenBot WebRTC signaling messages
│   ├── video.ts          # WebRTC connection to the robot's camera
│   ├── theme.ts          # reads colors from CSS variables, dark mode, reduced motion
│   ├── styles/           # tokens, layout, panels, robot face
│   └── ui/               # one file per widget: camera, KPIs, line chart, map, robot, status, time ranges, login
└── tests/
```

## Commands

```bash
npm run dev     # local server with hot reload
npm run build   # type-check and build into dist/
npm test        # unit tests
```
