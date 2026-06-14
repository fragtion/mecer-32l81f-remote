#!/usr/bin/env python3
# Mecer 32L81F web remote.  Codes reverse-engineered from the ROM (MStar Aeon disasm).
# Most buttons use vendor id 0x40 (user remote); SERVICE buttons use vendor id 0x41
# (engineer remote). NEC, REV (bit-reversed) Tasmota encoding, per-button vendor.
#   pip install flask requests ; python3 mecer_remote.py ; open http://localhost:5000
from flask import Flask, jsonify, Response
import requests
BLASTER = "http://192.168.10.175/cm"

# name -> (command, vendor_id)
KEYS = {
 "power":(0x0A,0x40),"menu":(0x40,0x40),"exit":(0x20,0x40),
 "up":(0x0B,0x40),"down":(0x0E,0x40),"left":(0x10,0x40),"right":(0x11,0x40),"ok":(0x0D,0x40),
 "vol+":(0x15,0x40),"vol-":(0x1C,0x40),"mute":(0x0F,0x40),
 "ch+":(0x1F,0x40),"ch-":(0x1E,0x40),
 "0":(0x45,0x40),"1":(0x01,0x40),"2":(0x02,0x40),"3":(0x03,0x40),"4":(0x04,0x40),
 "5":(0x05,0x40),"6":(0x06,0x40),"7":(0x07,0x40),"8":(0x08,0x40),"9":(0x09,0x40),
 "pmode":(0x42,0x40),"colortemp":(0x43,0x40),"aspect":(0x19,0x40),"sound":(0x1A,0x40),
 "info":(0x16,0x40),"prev":(0x18,0x40),"chlist":(0x1D,0x40),
 "source":(0x41,0x40),"tv":(0x4B,0x40),"hdmi":(0xF7,0x40),"av":(0x4E,0x40),"pc":(0xF5,0x40),
 "ttx":(0x12,0x40),"pal_ntsc":(0x46,0x40),"freeze":(0x00,0x40),"sleep":(0x17,0x40),
 # service (engineer / vendor 0x41)
 "factory1":(0x4F,0x40),"factory2":(0xB6,0x41),"factory3":(0xEF,0x41),
 "internal_info":(0xBA,0x41),"hdcp":(0xBD,0x41),
}
def rev8(b):
    b&=0xFF;r=0
    for _ in range(8): r=(r<<1)|(b&1);b>>=1
    return r
def frame(cmd,addr): return (rev8(addr)<<24)|(rev8(addr)<<16)|(rev8(cmd)<<8)|rev8(cmd^0xFF)
app=Flask(__name__)
@app.route("/send/<key>",methods=["POST"])
def send(key):
    k=key.lower()
    if k not in KEYS: return jsonify(ok=False,error="?"),400
    cmd,addr=KEYS[k];d=frame(cmd,addr)
    pl='{"Protocol":"NEC","Bits":32,"Data":"0x%08X","Repeat":1}'%d
    try:
        r=requests.get(BLASTER,params={"cmnd":"IRSend %s"%pl},timeout=4)
        return jsonify(ok=True,cmd="0x%02X@%02X"%(cmd,addr))
    except Exception as e: return jsonify(ok=False,error=str(e)),502

PAGE=r"""<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Mecer 32L81F</title><style>
:root{--bg:#0e1116;--b1:#1c2230;--b2:#141a26;--btn:#2a3142;--btn2:#343d52;--tx:#e7edf6;--mut:#8b95a8;--svc:#7a4ddb}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
body{margin:0;background:var(--bg);font-family:-apple-system,Segoe UI,Roboto,sans-serif;display:flex;justify-content:center;color:var(--tx)}
.r{width:330px;margin:12px;padding:16px 14px 22px;border-radius:34px;background:linear-gradient(180deg,var(--b1),var(--b2));box-shadow:0 16px 40px rgba(0,0,0,.5)}
.brand{text-align:center;color:var(--mut);letter-spacing:3px;font-size:11px;margin:2px 0 12px}
.row{display:flex;justify-content:center;gap:11px;margin:9px 0}
button{border:0;color:var(--tx);background:linear-gradient(180deg,var(--btn2),var(--btn));border-radius:50%;width:56px;height:56px;font-size:11px;font-weight:600;cursor:pointer;box-shadow:0 3px 6px rgba(0,0,0,.4)}
button:active{transform:translateY(2px);filter:brightness(1.5)}
button.s{width:50px;height:50px;font-size:10px}.pwr{background:linear-gradient(180deg,#c33,#911)}
.dpad{position:relative;width:200px;height:200px;margin:4px auto}
.dpad button{position:absolute;width:62px;height:62px;border-radius:16px}
.dpad .u{top:0;left:69px}.dpad .d{bottom:0;left:69px}.dpad .l{left:0;top:69px}.dpad .ri{right:0;top:69px}
.dpad .ok{top:69px;left:69px;border-radius:50%;background:linear-gradient(180deg,#3b82f6,#2560c8);font-size:14px}
.rk{display:flex;flex-direction:column;background:var(--btn);border-radius:28px;overflow:hidden}
.rk button{border-radius:0;width:52px;height:44px;background:transparent;box-shadow:none}
.mid{display:flex;flex-direction:column;justify-content:center}
.nums{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:10px 4px 2px}
.nums button{width:100%;height:42px;border-radius:13px}
h4{color:var(--mut);font-size:9px;letter-spacing:1px;margin:14px 0 5px;text-align:center;text-transform:uppercase}
.grid{display:flex;flex-wrap:wrap;justify-content:center;gap:7px}
.grid button{width:auto;height:32px;border-radius:16px;padding:0 12px;font-size:10px}
.grid button.svc{background:linear-gradient(180deg,#8a5be0,#6b3fc0)}
#t{position:fixed;bottom:12px;left:50%;transform:translateX(-50%);background:#0b0f16;border:1px solid #2a3142;padding:7px 13px;border-radius:9px;font-size:12px;color:var(--mut);opacity:0;transition:.2s;font-family:monospace}#t.on{opacity:1}
</style>
<div class=r>
 <div class=brand>MECER 32L81F</div>
 <div class=row style="justify-content:space-between">
  <button class=pwr data-k=power>POWER</button>
  <div style="display:flex;gap:11px"><button class=s data-k=menu>MENU&nbsp;↩</button><button class=s data-k=exit>EXIT</button></div>
 </div>
 <h4>Sources</h4>
 <div class=grid>
  <button data-k=source>SOURCE</button><button data-k=tv>TV</button><button data-k=hdmi>HDMI</button>
  <button data-k=av>AV</button><button data-k=pc>PC</button>
 </div>
 <div class=dpad>
  <button class=u data-k=up>▲</button><button class=l data-k=left>◀</button>
  <button class=ok data-k=ok>OK</button><button class=ri data-k=right>▶</button><button class=d data-k=down>▼</button>
 </div>
 <div class=row style="align-items:stretch">
  <div class=rk><button data-k=vol+>VOL+</button><button data-k=vol->VOL−</button></div>
  <div class=mid style="gap:6px"><button class=s data-k=mute>MUTE</button><button class=s data-k=prev>PREV</button></div>
  <div class=rk><button data-k=ch+>CH+</button><button data-k=ch->CH−</button></div>
 </div>
 <div class=row><button class=s data-k=pmode>PIC</button><button class=s data-k=colortemp>COLOR</button><button class=s data-k=aspect>ZOOM</button><button class=s data-k=sound>SOUND</button></div>
 <div class=nums>
  <button data-k=1>1</button><button data-k=2>2</button><button data-k=3>3</button>
  <button data-k=4>4</button><button data-k=5>5</button><button data-k=6>6</button>
  <button data-k=7>7</button><button data-k=8>8</button><button data-k=9>9</button>
  <button data-k=chlist>LIST</button><button data-k=0>0</button><button data-k=info>INFO</button>
 </div>
 <h4>TV control</h4>
 <div class=grid>
  <button data-k=ttx>TTX</button><button data-k=pal_ntsc>PAL/NTSC</button>
  <button data-k=freeze>FREEZE</button><button data-k=sleep>SLEEP</button>
 </div>
 <h4>Service (engineer / vendor 0x41)</h4>
 <div class=grid>
  <button class=svc data-k=factory1>FACTORY1</button><button class=svc data-k=factory2>FACTORY2</button>
  <button class=svc data-k=factory3>FACTORY3</button><button class=svc data-k=internal_info>INTERNAL INFO</button>
  <button class=svc data-k=hdcp>HDCP</button>
 </div>
</div><div id=t></div>
<script>
const t=document.getElementById('t');let tm;
function flash(m){t.textContent=m;t.classList.add('on');clearTimeout(tm);tm=setTimeout(()=>t.classList.remove('on'),1100)}
document.querySelectorAll('button[data-k]').forEach(b=>b.onclick=async()=>{
 try{const r=await fetch('/send/'+b.dataset.k,{method:'POST'});const j=await r.json();
  flash(j.ok?(b.dataset.k.toUpperCase()+'  '+j.cmd):('ERR '+(j.error||'')));}catch(e){flash('net err')}});
</script>"""
@app.route("/")
def index(): return Response(PAGE,mimetype="text/html")
if __name__=="__main__":
    print("Mecer 32L81F remote at http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000)
