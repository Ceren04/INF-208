"""
firmware/comm/web_ui.py — Flask Web Kontrol Arayüzü
Erişim: http://<pi_ip>:5000
ÇALIŞTIĞI YER: Raspberry Pi 3B
"""

import threading
import logging
import time
from flask import Flask, jsonify, request, render_template_string
from firmware.config import WebConfig

logger = logging.getLogger(__name__)

_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>VeloGuard</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { background:#111; color:#eee; }
    .card { background:#222; border:none; }
    #state-badge { font-size:1.4rem; padding:.4rem 1rem; }
  </style>
</head>
<body class="p-3">
  <h3 class="mb-3">🛡️ VeloGuard</h3>

  <div class="card p-3 mb-3">
    <div class="mb-2">
      Mod: <span id="state-badge" class="badge bg-secondary">—</span>
      <span id="tamper-badge"></span>
    </div>
    <div id="tamper-clear" class="d-none mt-2">
      <div class="input-group">
        <input type="password" id="tamper-pwd" placeholder="Şifre" class="form-control">
        <button class="btn btn-warning" onclick="clearTamper()">🔑 Tamper Temizle</button>
      </div>
    </div>
    <small>
      Pil: <span id="bat">?</span>% &nbsp;|&nbsp;
      CPU: <span id="cpu">?</span>°C &nbsp;|&nbsp;
      IMU: <span id="mag">?</span>g &nbsp;|&nbsp;
      Süre: <span id="dur">?</span>s
    </small>
  </div>

  <div class="d-flex gap-2 flex-wrap mb-3">
    <button class="btn btn-success btn-lg flex-fill" onclick="cmd('protect')">🛡️ KORU</button>
    <button class="btn btn-primary btn-lg flex-fill" onclick="cmd('owner')">🏠 YANINDAYIM</button>
    <button class="btn btn-danger  btn-lg flex-fill" onclick="cmd('off')">🔓 KAPAT</button>
  </div>
  <div class="d-flex gap-2 flex-wrap mb-3">
    <button class="btn btn-info btn-lg flex-fill" onclick="cmd('ride')">🚴 SÜRÜŞ</button>
    <button class="btn btn-warning btn-lg flex-fill" onclick="cmd('ride_end')">🏁 SÜRÜŞ BİTİR</button>
    <button class="btn btn-outline-danger btn-lg flex-fill" onclick="stopAlarm()">🔕 ALARM DURDUR</button>
  </div>

  <div id="log" class="small text-secondary" style="max-height:200px;overflow-y:auto"></div>

  <script>
    const COLOR = {DISARMED:'secondary',ARMED:'success',PRE_ALARM:'warning',ALARM:'danger',RIDE:'primary'};
    async function cmd(c) {
      const r = await fetch('/api/command',{method:'POST',
        headers:{'Content-Type':'application/json'},body:JSON.stringify({command:c})});
      const d = await r.json();
      addLog('CMD: '+c+' → '+(d.state||d.error));
      refresh();
    }
    async function stopAlarm() {
      const r = await fetch('/api/command',{method:'POST',
        headers:{'Content-Type':'application/json'},body:JSON.stringify({command:'stop_alarm'})});
      const d = await r.json();
      addLog('🔕 Alarm durdur → '+(d.state||d.error));
      refresh();
    }
    async function refresh() {
      try {
        const r = await fetch('/api/status'); const d = await r.json();
        const col = COLOR[d.state] || 'secondary';
        document.getElementById('state-badge').className = 'badge bg-'+col;
        document.getElementById('state-badge').textContent = d.state;
        document.getElementById('tamper-badge').innerHTML =
          d.is_tamper ? '<span class="badge bg-danger ms-2">⚠ TAMPER</span>' : '';
        // Show tamper clear form when tamper is active
        if (d.is_tamper) {
          document.getElementById('tamper-clear').classList.remove('d-none');
        } else {
          document.getElementById('tamper-clear').classList.add('d-none');
        }
        document.getElementById('bat').textContent = d.battery_pct != null ? d.battery_pct.toFixed(0) : 'Adaptör';
        document.getElementById('cpu').textContent = d.cpu_temp_c != null ? d.cpu_temp_c.toFixed(1) : '?';
        document.getElementById('mag').textContent = d.imu_magnitude != null ? d.imu_magnitude.toFixed(4) : '?';
        document.getElementById('dur').textContent = d.state_duration_s ?? '?';
      } catch(e) { addLog('Bağlantı hatası'); }
    }
    async function clearTamper() {
      const pwd = document.getElementById('tamper-pwd').value;
      const r = await fetch('/api/clear_tamper', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({password: pwd})
      });
      const d = await r.json();
      if (d.ok) addLog('✅ Tamper temizlendi');
      else addLog('❌ Tamper temizleme başarısız');
      refresh();
    }
    function addLog(msg) {
      const el = document.getElementById('log');
      el.innerHTML = new Date().toLocaleTimeString()+' '+msg+'<br>'+el.innerHTML;
    }
    setInterval(refresh, 1500); refresh();
  </script>
</body>
</html>"""


class WebUI:
    def __init__(self, fsm, shared_state):
        self._app = Flask(__name__)
        self._app.logger.setLevel(logging.WARNING)  # Flask log gürültüsünü azalt
        import logging as _l
        _l.getLogger("werkzeug").setLevel(_l.WARNING)
        self._fsm = fsm
        self._shared_state = shared_state
        self._server_thread = None
        self._register_routes()

    def _register_routes(self):
        app = self._app

        @app.route("/")
        def _index():
            return render_template_string(_HTML_TEMPLATE)

        @app.route("/api/status")
        def _get_status():
            snap   = self._shared_state.get_snapshot()
            status = self._fsm.get_status_dict()
            return jsonify({
                **status,
                "imu_magnitude": round(snap.imu_magnitude, 5),
                "imu_filtered":  round(snap.imu_filtered, 5),
                "cpu_temp_c":    snap.cpu_temp_c,
                "battery_pct":   snap.battery_pct,
                "humidity_pct":  snap.humidity_pct,
                "reed_is_open":  snap.reed_is_open,
            })

        @app.route("/api/command", methods=["POST"])
        def _handle_command():
            from firmware.fsm import Event
            data = request.get_json(silent=True) or {}
            cmd  = data.get("command", "")
            mapping = {
                "protect":    Event.ARM,         # Bisikleti koruma altına al
                "owner":      Event.RIDE_START,  # Yanındayım — yeşil sabit, alarm yok
                "off":        Event.DISARM,      # Tüm korumayı kapat
                "ride":       Event.RIDE_START,  # Sürüş modu
                "ride_end":   Event.RIDE_END,    # Sürüş bitti → KORU moduna dön
                "stop_alarm": Event.STOP_ALARM,  # Siren sustur, KORU modunda kal
                # Geriye dönük uyumluluk
                "arm":        Event.ARM,
                "disarm":     Event.DISARM,
            }
            event = mapping.get(cmd)
            if event is None:
                return jsonify({"error": f"Bilinmeyen komut: {cmd}"}), 400
            # FSMTask aktüatörleri tetiklesin diye kuyruğa gönder
            old_state = self._fsm.get_state().name
            self._shared_state.push_event(event)
            for _ in range(20):
              time.sleep(0.05)
            new_state = self._fsm.get_state().name
            changed = old_state != new_state
            message = f"{old_state} → {new_state}" if changed else f"Geçiş yapılamadı: {old_state}"
            return jsonify({"ok": True, "state": new_state, "changed": changed, "message": message})

        @app.route("/api/clear_tamper", methods=["POST"])
        def _clear_tamper():
            data = request.get_json(silent=True) or {}
            pwd  = data.get("password", "")
            if self._fsm.clear_tamper(pwd):
                return jsonify({"ok": True})
            return jsonify({"error": "Yanlış parola"}), 403

    def start(self):
        self._server_thread = threading.Thread(
            target=self._app.run,
            kwargs={
                "host":        WebConfig.HOST,
                "port":        WebConfig.PORT,
                "debug":       False,
                "use_reloader": False,
            },
            daemon=True,
            name="WebUI",
        )
        self._server_thread.start()
        logger.info(f"Web UI başlatıldı: http://0.0.0.0:{WebConfig.PORT}")

    def stop(self):
        # Daemon thread — process kapanınca otomatik ölür
        logger.info("WebUI durduruldu.")
