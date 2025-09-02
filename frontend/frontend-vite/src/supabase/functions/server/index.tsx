import { Hono } from "npm:hono";
import { cors } from "npm:hono/cors";
import { logger } from "npm:hono/logger";
import * as kv from "./kv_store.tsx";
import { portfolioRoutes, watchlistRoutes, marketInsightsRoutes, positionRoutes } from "./routes.tsx";

const app = new Hono();

// Enable logger
app.use('*', logger(console.log));

// Enable CORS for all routes and methods
app.use(
  "/*",
  cors({
    origin: "*",
    allowHeaders: ["Content-Type", "Authorization"],
    allowMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    exposeHeaders: ["Content-Length"],
    maxAge: 600,
  }),
);

// Health check endpoint
app.get("/make-server-9c463a03/health", (c) => {
  return c.json({ status: "ok" });
});

// Mount routes
app.route("/make-server-9c463a03/portfolio", portfolioRoutes);
app.route("/make-server-9c463a03/watchlist", watchlistRoutes);
app.route("/make-server-9c463a03/market-insights", marketInsightsRoutes);
app.route("/make-server-9c463a03/positions", positionRoutes);

Deno.serve(app.fetch);
