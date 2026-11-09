from __future__ import annotations

import json
import os
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .models import MarketSnapshot, RiskLimits
from .orchestrator import SimulationOrchestrator

HTML = """<!doctype html><html lang='it'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>paperperclipAI Dashboard</title><style>
:root{--bg:#07111f;--panel:#102238;--line:#23405f;--txt:#edf5ff;--muted:#91a8c0;--green:#38d996;--red:#ff7282;--yellow:#f5c451;--blue:#65aaff}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 100% 0,#173b63,#07111f 48%);color:var(--txt);font:14px Segoe UI,Arial,sans-serif}.wrap{max-width:1400px;margin:auto;padding:28px}.top{display:flex;justify-content:space-between;align-items:center;margin-bottom:22px}.brand{display:flex;gap:12px;align-items:center}.logo{width:42px;height:42px;border-radius:13px;background:linear-gradient(135deg,#5aa7ff,#8b5cff);display:grid;place-items:center;font-weight:800;font-size:21px}.title{font-size:23px;font-weight:700}.sub,.muted{color:var(--muted)}.buttons{display:flex;gap:9px}.btn{border:1px solid var(--line);background:var(--panel);color:var(--txt);border-radius:9px;padding:10px 14px;cursor:pointer}.primary{background:#2679df;border-color:#438ee8}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:16px}.card{background:linear-gradient(145deg,#122945e8,#0b1a2ce8);border:1px solid var(--line);border-radius:14px;padding:17px;box-shadow:0 12px 28px #0003}.label{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.09em}.value{font-size:24px;font-weight:700;margin-top:7px}.good{color:var(--green)}.warn{color:var(--yellow)}.bad{color:var(--red)}.layout{display:grid;grid-template-columns:1.25fr .75fr;gap:16px}.section{font-size:16px;font-weight:700;margin-bottom:13px}.chart{height:245px;width:100%;display:block}.row{display:flex;justify-content:space-between;gap:12px;padding:11px 0;border-bottom:1px solid #1b3551}.row:last-child{border:0}.agent{font-weight:600}.detail{font-size:12px;color:var(--muted);margin-top:3px}.pill{font-size:10px;padding:4px 7px;border-radius:15px;border:1px solid currentColor;white-space:nowrap}.inactive{color:#9ab0c8;background:#1b3046;border-color:#38526d}.table{overflow:auto}table{width:100%;border-collapse:collapse}th,td{padding:10px 7px;border-bottom:1px solid #1b3551;text-align:left;white-space:nowrap}th{font-size:10px;color:var(--muted);text-transform:uppercase}td{font-size:12px}.event{border-bottom:1px solid #1b3551;padding:9px 0;line-height:1.35}.event:last-child{border:0}.event small{display:block;color:var(--muted);margin-bottom:3px}.foot{text-align:center;color:var(--muted);font-size:12px;margin-top:16px}@media(max-width:900px){.grid{grid-template-columns:repeat(2,1fr)}.layout{grid-template-columns:1fr}}@media(max-width:550px){.wrap{padding:15px}.top{align-items:flex-start;gap:15px;flex-direction:column}.grid{gap:8px}.value{font-size:19px}}
</style></head><body><main class='wrap'><header class='top'><div class='brand'><div class='logo'>P</div><div><div class='title'>paperperclipAI</div><div class='sub'>Scalping Control Room · <b class='good'>SIMULAZIONE</b></div></div></div><div class='buttons'><button class='btn' onclick='ctl("stop")'>Pausa</button><button class='btn primary' onclick='ctl("start")'>Avvia</button></div></header><section class='grid'><div class='card'><div class='label'>Sessione</div><div id='session' class='value good'>ATTIVA</div></div><div class='card'><div class='label'>Equity</div><div id='equity' class='value'>€ 10.000,00</div></div><div class='card'><div class='label'>P&amp;L</div><div id='pnl' class='value good'>€ 0,00</div></div><div class='card'><div class='label'>Paper orders</div><div id='orders' class='value'>0</div></div></section><section class='layout'><div class='card'><div class='section'>Equity e operazioni <span id='updated' class='muted'></span></div><svg id='chart' class='chart' viewBox='0 0 900 245' preserveAspectRatio='none'></svg><div class='section'>Operazioni recenti</div><div class='table'><table><thead><tr><th>Ora</th><th>Strumento</th><th>Dir.</th><th>Qtà</th><th>Prezzo</th><th>Motivo</th><th>Stato</th></tr></thead><tbody id='ops'></tbody></table></div></div><aside><div class='card'><div class='section'>Agenti <span id='count' class='muted'></span></div><div id='agents'></div></div><div class='card' style='margin-top:16px'><div class='section'>Diario decisioni</div><div id='events'></div></div></aside></section><div class='foot'>Risk Gate obbligatorio · nessun ordine reale · MT5 non collegato</div></main><script>
const euro=n=>new Intl.NumberFormat('it-IT',{style:'currency',currency:'EUR'}).format(n);const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function chart(p){let s=document.getElementById('chart');if(!p.length){s.innerHTML='';return}let v=p.map(x=>x.equity),lo=Math.min(...v)-1,hi=Math.max(...v)+1,w=900,h=245,pts=p.map((x,i)=>`${18+i/(Math.max(1,p.length-1))*864},${h-18-(x.equity-lo)/(hi-lo)*209}`).join(' ');s.innerHTML=`<polyline points='${pts}' fill='none' stroke='#65aaff' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'/>`}
function draw(s){let q=document.getElementById('session');q.textContent=s.running?'ATTIVA':'IN PAUSA';q.className='value '+(s.running?'good':'warn');document.getElementById('equity').textContent=euro(s.equity);let p=document.getElementById('pnl');p.textContent=euro(s.pnl);p.className='value '+(s.pnl>=0?'good':'bad');document.getElementById('orders').textContent=s.operations.length;document.getElementById('updated').textContent=' · '+s.updated_at;document.getElementById('count').textContent=Object.keys(s.agents).length+' componenti';document.getElementById('agents').innerHTML=Object.entries(s.agents).map(([n,a])=>`<div class='row'><div><div class='agent'>${esc(n)}</div><div class='detail'>${esc(a.detail)}</div></div><span class='pill ${a.status==='ATTIVO'?'good':'inactive'}'>${esc(a.status)}</span></div>`).join('');document.getElementById('ops').innerHTML=s.operations.slice().reverse().map(o=>`<tr><td>${esc(o.time)}</td><td><b>${esc(o.symbol)}</b></td><td class='${o.direction==='LONG'?'good':'bad'}'>${esc(o.direction)}</td><td>${o.quantity}</td><td>${o.price.toFixed(2)}</td><td>${esc(o.reason)}</td><td><span class='pill good'>${esc(o.status)}</span></td></tr>`).join('')||`<tr><td colspan='7' class='muted'>Nessuna operazione simulata</td></tr>`;document.getElementById('events').innerHTML=s.events.slice().reverse().map(e=>`<div class='event'><small>${esc(e.time)} · ${esc(e.level)}</small>${esc(e.message)}</div>`).join('');chart(s.points)}async function refresh(){try{draw(await (await fetch('/api/state')).json())}catch(_){}}async function ctl(a){await fetch('/api/'+a,{method:'POST'});refresh()}refresh();setInterval(refresh,2000);
</script></body></html>"""


class State:
    def __init__(self) -> None:
        self.lock = threading.Lock(); self.running = False; self.equity = 10_000.0; self.pnl = 0.0; self.tick = 0
        self.operations: list[dict[str, Any]] = []; self.events: list[dict[str, str]] = []; self.points = [{"equity": self.equity}]
        self.agents = {"Orchestrator": ("ATTIVO", "Coordina il ciclo"), "Technical Analysis": ("ATTIVO", "VWAP e ATR"), "Risk Manager": ("ATTIVO", "Controlli fail-closed"), "Paper Execution": ("ATTIVO", "Fill simulati"), "Market Scanner": ("IN PREPARAZIONE", "Multi-strumento"), "News & Sentiment": ("IN PREPARAZIONE", "Fonti non collegate"), "Strategy Engine": ("IN PREPARAZIONE", "Prima strategia nel demo"), "Performance Analyst": ("IN PREPARAZIONE", "Report avanzati")}

    def event(self, level: str, msg: str) -> None:
        self.events.append({"time": datetime.now().strftime("%H:%M:%S"), "level": level, "message": msg}); self.events = self.events[-30:]

    def step(self, o: SimulationOrchestrator) -> None:
        with self.lock:
            if not self.running: return
            self.tick += 1; last = 190.01 + ((self.tick % 9) - 4) * .035
            m = MarketSnapshot("AAPL", last-.01, last+.01, last, 189.98, .20, datetime.now(timezone.utc)); r = o.run_once(m, RiskLimits(equity=self.equity, max_position_notional=5_000)); sig=r["signal"]; risk=r["risk"]
            self.event("INFO", f"Technical Analysis: {sig['direction']} su AAPL — {sig['reason']}")
            if risk["approved"] and "order" in r:
                z=r["order"]; self.operations.append({"time":datetime.now().strftime("%H:%M:%S"),"symbol":z["symbol"],"direction":z["direction"],"quantity":z["quantity"],"price":z["price"],"reason":sig["reason"],"status":z["status"]}); self.event("PASS", f"Risk Manager: approvato {z['quantity']} azioni, paper fill {z['order_id']}")
            else: self.event("BLOCK", f"Risk Manager: bloccata — {risk['reason']}")
            self.operations=self.operations[-20:]; self.points=(self.points+[ {"equity":self.equity+self.pnl} ])[-60:]

    def snapshot(self) -> dict[str, Any]:
        with self.lock: return {"running":self.running,"equity":self.equity,"pnl":self.pnl,"operations":self.operations,"events":self.events,"points":self.points,"agents":{k:{"status":v[0],"detail":v[1]} for k,v in self.agents.items()},"updated_at":datetime.now().strftime("%H:%M:%S")}

STATE=State()

class Handler(BaseHTTPRequestHandler):
    def send_json(self, data: Any, content: str="application/json") -> None:
        self.send_response(200); self.send_header("Content-Type", content); self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(data if isinstance(data,bytes) else json.dumps(data).encode())
    def do_GET(self) -> None:  # noqa: N802
        if self.path=='/': self.send_json(HTML.encode(), 'text/html; charset=utf-8')
        elif self.path=='/api/state': self.send_json(STATE.snapshot())
        else: self.send_error(404)
    def do_POST(self) -> None:  # noqa: N802
        if self.path in ('/api/start','/api/stop'):
            with STATE.lock: STATE.running=self.path.endswith('start'); STATE.event('INFO' if STATE.running else 'WARN', 'Sessione avviata' if STATE.running else 'Sessione messa in pausa')
            self.send_json({"ok":True})
        else: self.send_error(404)
    def log_message(self, *_args: Any) -> None: return

def main() -> None:
    orch=SimulationOrchestrator()
    def loop() -> None:
        while True: STATE.step(orch); time.sleep(2)
    port = int(os.environ.get('PAPERPERCLIP_PORT', '8899'))
    threading.Thread(target=loop,daemon=True).start(); print(f'Dashboard disponibile su http://127.0.0.1:{port}'); ThreadingHTTPServer(('127.0.0.1',port),Handler).serve_forever()

if __name__=='__main__': main()
