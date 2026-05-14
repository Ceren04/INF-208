"""
firmware/comm/web_ui.py — Flask Web Kontrol Arayüzü
Erişim: http://<pi_ip>:5000
ÇALIŞTIĞI YER: Raspberry Pi 3B
"""

import threading
import logging
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
    <small>
      Pil: <span id="bat">?</span>% &nbsp;|&nbsp;
      CPU: <span id="cpu">?</span>°C &nbsp;|&nbsp;
      IMU: <span id="mag">?</span>g &nbsp;|&nbsp;
      Süre: <span id="dur">?</span>s
    </small>
  </div>

  <div class="d-flex gap-2 flex-wrap mb-3">
    <button class="btn btn-success btn-lg flex-fill" onclick="cmd('arm')">🔒 ARM</button>
    <button class="btn btn-danger  btn-lg flex-fill" onclick="cmd('disarm')">🔓 DISARM</button>
    <button class="btn btn-primary btn-lg flex-fill" onclick="cmd('ride')">🚴 SÜRÜŞ</button>
  </div>

  <div id="log" class="small text-secondary" style="max-height:200px;overflow-y:auto"></div>

  <script>
    const COLOR = {DISARMED:'secondary',ARMED:'success',PRE_ALARM:'warning',ALARM:'danger',RIDE:'primary'};
    async function cmd(c) {
      const r = await fetch('/api/command',{method:'POST',
        headers:{'Content-Type':'application/json'},body:JSON.stringify({command:c})});
      const d = await r.json();
      addLog('CMD: '+c+' → '+d.state);
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
        document.getElementById('bat').textContent = d.battery_pct != null ? d.battery_pct.toFixed(0) : '?';
        document.getElementById('cpu').textContent = d.cpu_temp_c != null ? d.cpu_temp_c.toFixed(1) : '?';
        document.getElementById('mag').textContent = d.imu_magnitude != null ? d.imu_magnitude.toFixed(4) : '?';
        document.getElementById('dur').textContent = d.state_duration_s ?? '?';
      } catch(e) { addLog('Bağlantı hatası'); }
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
                "arm":    Event.ARM,
                "disarm": Event.DISARM,
                "ride":   Event.RIDE_START,
                "ride_end": Event.RIDE_END,
            }
            event = mapping.get(cmd)
            if event is None:
                return jsonify({"error": f"Bilinmeyen komut: {cmd}"}), 400
            self._fsm.handle_event(event)
            return jsonify({"ok": True, "state": self._fsm.get_state().name})

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
