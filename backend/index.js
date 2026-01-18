require("dotenv").config();

require("./mqtt");

const express = require("express");
const app = express();

app.use(express.json());

app.use("/queue_snapshots", require("./routers/queue_snapshots"));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`[+] LIMON backend server listening on port ${PORT}`);
});
