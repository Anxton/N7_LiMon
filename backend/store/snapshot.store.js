const queueSnapshotsHistory = [];

module.exports = {
    queueSnapshotsHistory,

    add(snapshot) {
        queueSnapshotsHistory.push(snapshot)
        // Limit history to last 100000 snapshots
        if (queueSnapshotsHistory.length > 100000) {
            queueSnapshotsHistory.shift();
        }
    },

    getAll() {
        return queueSnapshotsHistory;
    },

    clear() {
        queueSnapshotsHistory.clear();
    }
};