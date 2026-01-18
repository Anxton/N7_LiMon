const queueSnapshotsHistory = [];

module.exports = {
    queueSnapshotsHistory,

    add(snapshot) {
        queueSnapshotsHistory.push(snapshot)
    },

    getAll() {
        return queueSnapshotsHistory;
    },

    clear() {
        queueSnapshotsHistory.clear();
    }
};