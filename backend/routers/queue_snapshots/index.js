const express = require('express')
const router = express.Router()

const snapshotStore = require("../../store/snapshot.store")

router.get('/', (req, res) => {
    res.send(snapshotStore.getAll());
})

module.exports = router;