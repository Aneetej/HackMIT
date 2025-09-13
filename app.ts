import express from "express";
import cors from "cors";

const app = express();

app.use(cors());
app.use (express.json());

export default app;
// Additional sanity check 
app.get("/health", (_req, res) => res.status(200).send("ok"));

