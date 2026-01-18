module.exports = {
    parseMQTTPayload(payload) {
        try {
            return JSON.parse(payload.toString());
        } catch (err) {
            console.error("[-] Failed to parse MQTT payload:", err);
            return null;
        }
    }
};