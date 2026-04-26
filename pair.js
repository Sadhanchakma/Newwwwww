const { makeid } = require('./id');
const express = require('express');
const fs = require('fs');
const router = express.Router();
const pino = require('pino');
const {
    default: Arslan_Tech,
    useMultiFileAuthState,
    delay,
    makeCacheableSignalKeyStore,
    Browsers
} = require('@whiskeysockets/baileys');

router.get('/pair', async (req, res) => {
    const id = makeid();
    let num = req.query.number;

    if (!num) return res.send({ error: "Number is required" });

    // পুরনো ডাটা ক্লিনআপ
    if (fs.existsSync('./temp/' + id)) {
        fs.rmSync('./temp/' + id, { recursive: true, force: true });
    }

    const { state, saveCreds } = await useMultiFileAuthState('./temp/' + id);

    try {
        let sock = Arslan_Tech({
            auth: {
                creds: state.creds,
                keys: makeCacheableSignalKeyStore(state.keys, pino({ level: 'fatal' })),
            },
            printQRInTerminal: false,
            logger: pino({ level: 'fatal' }),
            browser: ["Ubuntu", "Chrome", "20.0.04"],
            connectTimeoutMs: 60000,
            defaultQueryTimeoutMs: 0,
            keepAliveIntervalMs: 10000,
            generateHighQualityLink: true
        });

        sock.ev.on('creds.update', saveCreds);

        sock.ev.on('connection.update', async (s) => {
            const { connection } = s;
            if (connection === 'open') {
                await delay(5000);
                let data = fs.readFileSync(`./temp/${id}/creds.json`);
                let b64data = Buffer.from(data).toString('base64');
                
                // সেশন আইডি আপনার নিজের হোয়াটসঅ্যাপে যাবে
                await sock.sendMessage(sock.user.id, { text: 'ARSLAN-MD~' + b64data });

                await delay(2000);
                await sock.ws.close();
                if (fs.existsSync('./temp/' + id)) fs.rmSync('./temp/' + id, { recursive: true, force: true });
            }
        });

        // ৪২৮ এরর এবং সকেট ক্লোজ ফিক্স করার জন্য ৫ সেকেন্ড ওয়েট
        await delay(5000); 

        if (!sock.authState.creds.registered) {
            num = num.replace(/[^0-9]/g, '');
            try {
                const code = await sock.requestPairingCode(num);
                if (!res.headersSent) {
                    res.send({ code: code });
                }
            } catch (err) {
                console.log("❌ Pairing Error:", err.message);
                if (!res.headersSent) res.send({ error: "WhatsApp Server রিজেক্ট করেছে। আবার চেষ্টা করুন।" });
            }
        }

    } catch (err) {
        if (!res.headersSent) res.send({ error: "Service Currently Unavailable" });
    }
});

module.exports = router;
