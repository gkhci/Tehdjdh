    toast(e.message||'Failed to create volume',true);
  }}
  finally{{cbtn.disabled=false;cbtn.textContent=cbtn.getAttribute('data-'+lang)||'Create Volume'}}
}}

document.addEventListener('change',function(e){{
  if(e.target.id==='rw-project'&&e.target.value){{
    checkRailwayVolume();
  }}
}});

async function loadStats(){{
  try{{
    const r=await fetch('/stats');
    if(r.status===401){{showLogin();return}}
    if(!r.ok)throw new Error();
    sData=await r.json();
    $m('sv-traffic').innerHTML=(sData.total_traffic_mb||0)+'<span class="stat-unit"> MB</span>';
    $m('sv-links').textContent=sData.links_count||0;
    $m('sv-uptime').textContent=sData.uptime||'-';
    $m('sv-domain').textContent=sData.domain||'-';
    $m('nb').textContent=sData.links_count||0;
    $m('last-up').textContent='Updated '+new Date().toLocaleTimeString();
    if($m('t-tr'))$m('t-tr').textContent=(sData.total_traffic_mb||0)+' MB';
    if($m('t-rq'))$m('t-rq').textContent=(sData.total_requests||0).toLocaleString();
    if($m('t-up'))$m('t-up').textContent=sData.uptime||'-';
    if(sData.cpu_percent!==undefined){{
      const c=sData.cpu_percent;
      const cc=c>80?'var(--red)':c>50?'var(--yellow)':'var(--gold)';
      $m('cpu-v').textContent=c.toFixed(1)+'%';$m('cpu-v').style.color=cc;
      $m('cpu-b').style.width=c+'%';$m('cpu-b').style.background=cc;
    }}
    if(sData.memory_percent!==undefined){{
      const m=sData.memory_percent;
      const mc=m>80?'var(--red)':m>50?'var(--yellow)':'var(--green)';
      $m('mem-v').textContent=m.toFixed(1)+'%';$m('mem-v').style.color=mc;
      $m('mem-b').style.width=m+'%';$m('mem-b').style.background=mc;
    }}
    updChart();
  }}catch(e){{}}
}}

async function loadLinks(){{
  try{{
    const r=await fetch('/api/links');
    if(r.status===401){{showLogin();return}}
    if(!r.ok)throw new Error();
    const d=await r.json();
    allLinks=d.links||[];filterLinks();
  }}catch(e){{}}
}}

async function chgPw(){{
  const cur=$m('cpw').value;const nw=$m('npw').value;
  if(!cur||!nw){{toast('Fill all fields',true);return}}
  if(nw.length<4){{toast('Password must be at least 4 characters',true);return}}
  try{{
    const r=await fetch('/api/change-password',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{current_password:cur,new_password:nw}})}});
    if(!r.ok){{const d=await r.json().catch(()=>({{}}));throw new Error(d.detail||'Error')}}
    toast('Password updated');$m('cpw').value='';$m('npw').value='';
  }}catch(e){{toast(e.message,true)}}
}}

function initChart(){{
  const ctx=$m('tc');
  if(!ctx||tChart)return;
  tChart=new Chart(ctx,{{
    type:'bar',
    data:{{labels:[],datasets:[{{label:'MB',data:[],backgroundColor:'rgba(255,215,0,0.4)',borderColor:'#FFD700',borderWidth:1,borderRadius:4}}]}},
    options:{{responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{display:false}}}},
      scales:{{
        x:{{grid:{{display:false}},ticks:{{color:'rgba(255,215,0,0.35)',font:{{size:10}}}}}},
        y:{{grid:{{color:'rgba(255,215,0,0.06)'}},ticks:{{color:'rgba(255,215,0,0.35)',font:{{size:10}},callback:v=>v+' MB'}},beginAtZero:true}}
      }}
    }}
  }});

  const ctx2=$m('inbound-chart');
  if(ctx2&&!iChart){{
    iChart=new Chart(ctx2,{{
      type:'doughnut',
      data:{{labels:[],datasets:[{{data:[],
        backgroundColor:[],
        borderWidth:0}}]}},
      options:{{responsive:true,maintainAspectRatio:false,
        plugins:{{legend:{{display:true,position:'right',labels:{{color:'rgba(255,255,255,0.6)',font:{{size:10}}}}}}}}}}
    }});
  }}
  updChartColors();
}}

function updChartColors(){{
  if(!tChart)return;
  const col=theme==='light'?'rgba(0,0,0,0.4)':'rgba(255,215,0,0.35)';
  const gridCol=theme==='light'?'rgba(0,0,0,0.06)':'rgba(255,215,0,0.06)';
  tChart.options.scales.x.ticks.color=col;
  tChart.options.scales.y.ticks.color=col;
  tChart.options.scales.y.grid.color=gridCol;
  tChart.update();
}}

function updChart(){{
  if(!tChart||!sData.hourly_traffic)return;
  const entries=Object.entries(sData.hourly_traffic).sort((a,b)=>a[0].localeCompare(b[0])).slice(-12);
  tChart.data.labels=entries.map(x=>{{const p=x[0].split(' ');return p.length>1?p[1]:p[0]}});
  tChart.data.datasets[0].data=entries.map(x=>Math.round(x[1]/1048576));
  tChart.update();
}}

async function loadAddrs(){{
  try{{
    const r=await fetch('/api/addresses');
    if(!r.ok)throw new Error();
    const d=await r.json();allAddrs=d.addresses||[];renderAddrs();
  }}catch(e){{}}
}}

function renderAddrs(){{
  const el=$m('addr-list');
  if(!el)return;
  if(!allAddrs||!allAddrs.length){{el.innerHTML='<div style="color:var(--text3);font-size:12px">No addresses added</div>';return}}
  el.innerHTML=allAddrs.map((a,i)=>`<div style="display:flex;align-items:center;justify-content:space-between;padding:12px 14px;background:var(--surface3);border:1px solid var(--border);border-radius:10px;margin-bottom:8px">
    <div style="display:flex;align-items:center;gap:10px">
      <span style="color:var(--gold);font-size:16px">🌐</span>
      <div><div style="font-size:14px;font-weight:600">$(esc(a))</div><div style="font-size:11px;color:var(--text3);margin-top:2px">Address #${{i+1}}</div></div>
    </div>
    <button class="act-btn act-del" onclick="delAddr(${{i}})">${{tr('del')}}</button>
  </div>`).join('');
}}

function showAddAddrMo(){{$m('na').value='';$m('mo-addr').classList.add('show')}}

const NOTIF_ICONS = {{update:'🔔',quota:'⚠️',expiry:'⏰',info:'ℹ️'}};

async function loadNotifs(){{
  try{{
    const r=await fetch('/api/notifications');
    if(r.status===401)return;
    if(!r.ok)return;
    const d=await r.json();
    renderNotifs(d.notifications||[]);
  }}catch(e){{}}
}}

function renderNotifs(notifs){{
  const el=$m('notif-list');
  if(!el)return;
  if(!notifs||!notifs.length){{
    el.innerHTML='<div class="empty" style="padding:32px">'+(lang==='fa'?'هیچ اعلانی وجود ندارد':'No notifications')+'</div>';
    return;
  }}
  el.innerHTML=notifs.map(n=>{{
    const icon=NOTIF_ICONS[n.type]||'ℹ️';
    const cls=n.seen?'':'unseen';
    const time=new Date(n.created_at).toLocaleString();
    const linkHtml=n.link?`<a href="$(esc(n.link))" target="_blank" class="notif-link">${{tr('gh')}} ↗</a>`:'';
    return `<div class="notif-item ${{cls}}" onclick="markSeen(${{n.id}})">
      <div class="notif-icon ${{n.type}}">${{icon}}</div>
      <div class="notif-body">
        <div class="notif-title">$(esc(n.title))</div>
        <div class="notif-msg">$(esc(n.message))</div>
        <div class="notif-time">${{time}}</div>
        ${{linkHtml}}
      </div>
      ${{n.seen?'':'<div class="notif-dot"></div>'}}
    </div>`;
  }}).join('');
}}

async function markSeen(id){{
  await fetch('/api/notifications/'+id+'/seen',{{method:'POST'}});
  await loadNotifs();
  await updateNotifBadge();
}}

async function markAllSeen(){{
  await fetch('/api/notifications/seen-all',{{method:'POST'}});
  await loadNotifs();
  await updateNotifBadge();
}}

async function clearNotifs(){{
  if(!confirm(lang==='fa'?'حذف همه اعلانات؟':'Clear all notifications?'))return;
  await fetch('/api/notifications',{{method:'DELETE'}});
  await loadNotifs();
  await updateNotifBadge();
}}

async function updateNotifBadge(){{
  try{{
    const r=await fetch('/api/notifications/count');
    if(!r.ok)return;
    const d=await r.json();
    const badge=$m('notif-badge');
    if(badge){{
      if(d.count>0){{badge.style.display='';badge.textContent=d.count}}
      else{{badge.style.display='none'}}
    }}
  }}catch(e){{}}
}}

async function addAddrs(){{
  const lines=($m('na').value||'').trim().split('\n').map(l=>l.trim()).filter(l=>l);
  let ok=0,fail=0;
  for(const a of lines){{
    if(!/^[a-zA-Z0-9\\-_. ]+$/.test(a)){{fail++;continue}}
    try{{
      const r=await fetch('/api/addresses',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{address:a}})}});
      if(r.ok)ok++;else fail++;
    }}catch(e){{fail++}}
  }}
  if(ok)toast('Added '+ok);
  if(fail)toast(fail+' failed',true);
  if(ok){{$m('mo-addr').classList.remove('show');await loadAddrs()}}
}}

async function delAddr(i){{
  if(!confirm('Delete this address?'))return;
  try{{
    const r=await fetch('/api/addresses/'+i,{{method:'DELETE'}});
    if(!r.ok)throw new Error();
    toast('Deleted');await loadAddrs();
  }}catch(e){{toast('Error deleting',true)}}
}}

async function delAllAddrs(){{
  if(!allAddrs||!allAddrs.length){{toast('No addresses to delete',true);return}}
  if(!confirm('Delete ALL clean IP addresses?'))return;
  try{{
    const r=await fetch('/api/addresses',{{method:'DELETE'}});
    if(!r.ok)throw new Error();
    toast('All addresses deleted');await loadAddrs();
  }}catch(e){{toast('Error deleting',true)}}
}}

setTheme(theme);
setLang(lang);
checkAuth();
let statsInterval=null;
function startPolling(){{
  if(statsInterval)clearInterval(statsInterval);
  statsInterval=setInterval(()=>{{if(isAuthenticated){{loadStats();loadLinks();updateNotifBadge()}}}},12000);
}}
startPolling();

const PANEL_VERSION_KEY='luffy_panel_last_version';
const PANEL_GH_NOTIFIED_KEY='luffy_panel_last_notified_gh';
let loadedPanelVersion=null;

async function checkPanelVersion(isPeriodic){{
  try{{
    const r=await fetch('/api/version');
    if(!r.ok)return;
    const d=await r.json();
    const serverVersion=d.version;

    if(!loadedPanelVersion){{
      loadedPanelVersion=serverVersion;
      const lastSeen=localStorage.getItem(PANEL_VERSION_KEY);
      if(lastSeen&&lastSeen!==serverVersion){{
        toast('✅ Panel updated successfully to v'+serverVersion);
      }}
      localStorage.setItem(PANEL_VERSION_KEY,serverVersion);
    }}

    if(d.update_available&&d.latest_github_version){{
      const alreadyNotified=localStorage.getItem(PANEL_GH_NOTIFIED_KEY);
      if(alreadyNotified!==d.latest_github_version){{
        toast('🚀 New version available on GitHub: '+d.latest_github_version+' - pull the latest update');
        localStorage.setItem(PANEL_GH_NOTIFIED_KEY,d.latest_github_version);
      }}
    }}
  }}catch(e){{}}
}}
checkPanelVersion(false);
setInterval(()=>checkPanelVersion(true),5*60*1000);
</script>
</body>
</html>"""

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return HTMLResponse(content=PANEL_HTML)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return HTMLResponse(content=PANEL_HTML)

@app.get("/panel", response_class=HTMLResponse)
async def panel_page(request: Request):
    return HTMLResponse(content=PANEL_HTML)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=CONFIG["port"])
