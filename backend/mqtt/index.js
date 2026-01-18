const mqtt = require("mqtt");
const snapshotStore = require("../store/snapshot.store");
const { parseMQTTPayload } = require("../utils/mqtt.utils");

const client = mqtt.connect(process.env.MQTT_BROKER_URL);
const mqttTopic = process.env.MQTT_TOPIC || "limon";


client.on("connect", () => {
    console.log(`[+] MQTT connected to ${process.env.MQTT_BROKER_URL}`);
    client.subscribe(mqttTopic);
    console.log(`[+] Subscribed to topic: ${mqttTopic}`);
});

client.on("message", (topic, message) => {
    if (topic !== mqttTopic) return;
    console.log(`[+] MQTT message received on topic: ${topic} - ${message.toString()}`);

    const parsedPayload = parseMQTTPayload(message);
    if (!parsedPayload) return;

    snapshotStore.add({
        people: parsedPayload.people ?? null,
        receivedAt: new Date().toUTCString()
    });
});

client.on("error", (err) => {
    console.error("[-] MQTT error:", err);
});

client.on("reconnect", () => {
    console.log("[!] MQTT reconnecting...");
});

module.exports = client;
