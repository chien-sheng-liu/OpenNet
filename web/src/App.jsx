import React, { useMemo, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

function TextArea({ label, value, onChange, rows = 4 }) {
  return (
    <label style={{ display: 'block', marginBottom: 12 }}>
      <div style={{ fontWeight: 600, marginBottom: 4 }}>{label}</div>
      <textarea
        rows={rows}
        style={{ width: '100%', fontFamily: 'monospace' }}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </label>
  )
}

function NumberInput({ label, value, onChange, min = 0 }) {
  return (
    <label style={{ display: 'block', marginBottom: 12 }}>
      <div style={{ fontWeight: 600, marginBottom: 4 }}>{label}</div>
      <input type="number" min={min} value={value} onChange={(e) => onChange(Number(e.target.value))} />
    </label>
  )
}

function App() {
  const [steps, setSteps] = useState(200)
  const [evalSpins, setEvalSpins] = useState(50000)
  const [spins, setSpins] = useState(100000)
  const [seed, setSeed] = useState(1337)
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)

  const [bet, setBet] = useState(1)
  const [reelsJson, setReelsJson] = useState('')
  const [spinStops, setSpinStops] = useState([0, 0, 0])
  const [spinResult, setSpinResult] = useState(null)
  const [spinning, setSpinning] = useState(false)
  const [animGrid, setAnimGrid] = useState(null)
  const [animTimer, setAnimTimer] = useState(null)
  const [simRes, setSimRes] = useState(null)

  const reelsValid = useMemo(() => {
    try {
      const r = JSON.parse(reelsJson)
      return Boolean(r.reel_1 && r.reel_2 && r.reel_3)
    } catch {
      return false
    }
  }, [reelsJson])

  const reelsObj = useMemo(() => {
    try { return JSON.parse(reelsJson) } catch { return null }
  }, [reelsJson])

  async function callSearch() {
    setBusy(true)
    setResult(null)
    try {
      const res = await fetch(`${API_BASE}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ steps, eval_spins: evalSpins, spins, seed }),
      })
      if (!res.ok) throw new Error('Search failed')
      const data = await res.json()
      setResult(data)
      setReelsJson(JSON.stringify(data.reels, null, 2))
    } catch (e) {
      alert(e.message)
    } finally {
      setBusy(false)
    }
  }

  async function callSpin() {
    try {
      // start reel animation based on actual reels if available
      setSpinning(true)
      setSpinResult(null)
      if (animTimer) clearInterval(animTimer)
      let stops = [
        Math.floor(Math.random()*1000)%((reelsObj?.reel_1?.length)||20),
        Math.floor(Math.random()*1000)%((reelsObj?.reel_2?.length)||25),
        Math.floor(Math.random()*1000)%((reelsObj?.reel_3?.length)||30),
      ]
      setSpinStops(stops)
      const t = setInterval(() => {
        if (reelsObj?.reel_1 && reelsObj?.reel_2 && reelsObj?.reel_3) {
          stops = [
            (stops[0] + 3) % reelsObj.reel_1.length,
            (stops[1] + 2) % reelsObj.reel_2.length,
            (stops[2] + 1) % reelsObj.reel_3.length,
          ]
          setSpinStops(stops)
          setAnimGrid(computeGrid(reelsObj, stops))
        } else {
          setAnimGrid(randomGrid())
        }
      }, 80)
      setAnimTimer(t)
      const res = await fetch(`${API_BASE}/spin`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reels: JSON.parse(reelsJson), bet_amount: bet }),
      })
      if (!res.ok) throw new Error('Spin failed')
      const data = await res.json()
      if (t) clearInterval(t)
      setAnimTimer(null)
      setSpinStops(data.stops)
      setAnimGrid(reelsObj ? computeGrid(reelsObj, data.stops) : data.grid)
      setSpinning(false)
      setSpinResult(data)
    } catch (e) {
      alert(e.message)
      if (animTimer) clearInterval(animTimer)
      setAnimTimer(null)
      setSpinning(false)
    }
  }

  async function callSimulate() {
    try {
      const res = await fetch(`${API_BASE}/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reels: JSON.parse(reelsJson), spins: Math.min(spins, 20000), seed }),
      })
      if (!res.ok) throw new Error('Simulate failed')
      const data = await res.json()
      setSimRes(data)
    } catch (e) {
      alert(e.message)
    }
  }

  return (
    <div style={{ maxWidth: 960, margin: '24px auto', padding: 16, fontFamily: 'system-ui, sans-serif' }}>
      <h1>3×3 Slot Game</h1>
      <section style={{ marginTop: 24, padding: 12, border: '1px solid #ddd', borderRadius: 8 }}>
        <h2>Search Reels</h2>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
          <NumberInput label="Steps" value={steps} onChange={setSteps} min={1} />
          <NumberInput label="Eval Spins" value={evalSpins} onChange={setEvalSpins} min={100} />
          <NumberInput label="Validation Spins" value={spins} onChange={setSpins} min={100} />
          <NumberInput label="Seed" value={seed} onChange={setSeed} />
        </div>
        <button onClick={callSearch} disabled={busy}>
          {busy ? 'Searching…' : 'Run Search'}
        </button>
        {result && (
          <div style={{ marginTop: 12 }}>
            <div>RTP: {result.validation?.rtp}</div>
            <div>Win Rate: {result.validation?.win_rate}</div>
            <div style={{ marginTop: 8 }}>
              <MetricBars rtp={result.validation?.rtp} winRate={result.validation?.win_rate} />
            </div>
          </div>
        )}
      </section>

      <section style={{ marginTop: 24, padding: 12, border: '1px solid #ddd', borderRadius: 8 }}>
        <h2>Reels</h2>
        <TextArea label="Reel Config (JSON)" value={reelsJson} onChange={setReelsJson} rows={10} />
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 8 }}>
          <button onClick={() => { try { setReelsJson(JSON.stringify(JSON.parse(reelsJson), null, 2)) } catch {} }}>Pretty</button>
          <button onClick={() => { try { setReelsJson(JSON.stringify(JSON.parse(reelsJson))) } catch {} }}>Minify</button>
          {reelsObj && <ReelStats reels={reelsObj} />}
        </div>
        <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
          <NumberInput label="Bet Amount" value={bet} onChange={setBet} min={0} />
          <button onClick={callSpin} disabled={!reelsValid}>{spinning ? 'Spinning…' : 'Spin'}</button>
          <button onClick={callSimulate} disabled={!reelsValid}>Quick Simulate</button>
        </div>
        {(spinning || spinResult) && (
          <div style={{ marginTop: 12 }}>
            {spinResult && <div style={{ marginBottom: 8 }}><strong>Spin Payout:</strong> {spinResult.payout.toFixed(2)}</div>}
            <GridBoard grid={spinResult ? spinResult.grid : (animGrid || randomGrid())} matches={spinResult?.matches || []} animating={spinning} />
            {spinResult ? (spinResult.matches?.length > 0 ? (
              <div style={{ marginTop: 8 }}>
                <div><strong>Winning Patterns:</strong></div>
                <ul>
                  {spinResult.matches.map((m, i) => (
                    <li key={i}>
                      {m.pattern} — symbol {m.symbol}, weight {m.weight}, multiplier {m.multiplier}, payout {m.payout}
                    </li>
                  ))}
                </ul>
              </div>
            ) : (
              <div style={{ marginTop: 8, color: '#666' }}>No winning patterns</div>
            )) : null}
          </div>
        )}
        {simRes && (
          <div style={{ marginTop: 12 }}>
            <div><strong>Sim Spins:</strong> {simRes.spins}</div>
            <div><strong>RTP:</strong> {simRes.rtp}</div>
            <div><strong>Win Rate:</strong> {simRes.win_rate}</div>
            <div style={{ marginTop: 8 }}>
              <MetricBars rtp={simRes.rtp} winRate={simRes.win_rate} />
            </div>
          </div>
        )}
      </section>

      <section style={{ marginTop: 24, padding: 12, border: '1px solid #ddd', borderRadius: 8 }}>
        <h2>Notes</h2>
        <ul>
          <li>Targets: RTP = 0.95, Win Rate ≥ 0.55.</li>
          <li>Reels are circular; each column shows 3 consecutive symbols.</li>
          <li>Full 3×3 match pays 5× symbol multiplier; 2×2 matches pay 1×.</li>
        </ul>
        <div style={{ marginTop: 12 }}>
          <h3>Pattern Legend</h3>
          <PatternLegend />
        </div>
      </section>
    </div>
  )
}

export default App

function GridBoard({ grid, matches, animating = false }) {
  // Build a set of coords to highlight
  const highlight = new Set(matches?.flatMap((m) => m.coords.map((c) => `${c[0]}-${c[1]}`)) || [])
  const symbolColor = (s) => {
    switch (s) {
      case 4: return '#e76f51'
      case 3: return '#f4a261'
      case 2: return '#2a9d8f'
      case 1: return '#457b9d'
      default: return '#6c757d'
    }
  }
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 64px)', gap: 6 }}>
      {grid.map((row, r) => row.map((val, c) => {
        const key = `${r}-${c}`
        const active = highlight.has(key)
        return (
          <div key={key} style={{
            width: 64,
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: 8,
            border: active ? '3px solid #e9c46a' : '1px solid #ddd',
            background: symbolColor(val),
            color: 'white',
            fontWeight: 700,
            fontSize: 20,
            transition: 'transform 100ms ease',
            transform: animating ? `rotate(${(Math.random()*4-2).toFixed(2)}deg)` : 'none'
          }}>
            {val}
          </div>
        )
      }))}
    </div>
  )
}

function MetricBars({ rtp, winRate }) {
  const clamp = (v) => Math.max(0, Math.min(1.5, v || 0))
  const rtpTarget = 0.95
  const winTarget = 0.55
  const bar = (value, target, label) => {
    const v = clamp(value)
    const pct = Math.min(1, v)
    const targetPct = Math.min(1, target)
    const ok = value >= target && label === 'Win Rate' || (label === 'RTP' && Math.abs(value - target) < 0.02)
    return (
      <div style={{ marginBottom: 8 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
          <strong>{label}</strong>
          <span>{(value ?? 0).toFixed(3)} / target {target.toFixed(3)}</span>
        </div>
        <div style={{ position: 'relative', height: 14, background: '#eee', borderRadius: 7 }}>
          <div style={{ position: 'absolute', left: `${targetPct * 100}%`, top: 0, bottom: 0, width: 2, background: '#333' }} />
          <div style={{ height: 14, width: `${pct * 100}%`, background: ok ? '#2a9d8f' : '#e76f51', borderRadius: 7 }} />
        </div>
      </div>
    )
  }
  return (
    <div>
      {bar(rtp, rtpTarget, 'RTP')}
      {bar(winRate, winTarget, 'Win Rate')}
    </div>
  )
}

function PatternLegend() {
  const patterns = [
    { name: 'top_left_2x2', coords: [[0,0],[0,1],[1,0],[1,1]] },
    { name: 'top_right_2x2', coords: [[0,1],[0,2],[1,1],[1,2]] },
    { name: 'bottom_left_2x2', coords: [[1,0],[1,1],[2,0],[2,1]] },
    { name: 'bottom_right_2x2', coords: [[1,1],[1,2],[2,1],[2,2]] },
    { name: 'full_3x3', coords: Array.from({length: 9}, (_, i) => [Math.floor(i/3), i%3]) },
  ]
  const Cell = ({ active }) => (
    <div style={{ width: 16, height: 16, border: '1px solid #888', background: active ? '#e9c46a' : 'transparent' }} />
  )
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 12 }}>
      {patterns.map((p) => (
        <div key={p.name} style={{ textAlign: 'center' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 16px)', gap: 2, margin: '0 auto 4px' }}>
            {Array.from({ length: 9 }, (_, i) => {
              const r = Math.floor(i/3), c = i%3
              const active = p.coords.some(([rr, cc]) => rr === r && cc === c)
              return <Cell key={i} active={active} />
            })}
          </div>
          <div style={{ fontSize: 12 }}>{p.name}</div>
        </div>
      ))}
    </div>
  )
}

function randomGrid() {
  return Array.from({ length: 3 }, () => Array.from({ length: 3 }, () => Math.floor(Math.random()*5)))
}

function computeGrid(reels, stops) {
  // reels: {reel_1, reel_2, reel_3}; stops: [s1,s2,s3]
  const cols = [reels.reel_1, reels.reel_2, reels.reel_3].map((reel, i) => [0,1,2].map(o => reel[(stops[i] + o) % reel.length]))
  // cols to 3x3 grid rows
  return [0,1,2].map(r => [0,1,2].map(c => cols[c][r]))
}

function ReelStats({ reels }) {
  const counts = (arr) => arr.reduce((m, v) => { m[v] = (m[v]||0)+1; return m }, {})
  const c1 = counts(reels.reel_1||[]), c2 = counts(reels.reel_2||[]), c3 = counts(reels.reel_3||[])
  const chip = (label, value) => (
    <span style={{ background:'#f1f1f1', border:'1px solid #ddd', borderRadius:12, padding:'2px 8px', marginRight:6, fontSize:12 }}>
      {label}: {value}
    </span>
  )
  const row = (name, c) => (
    <div style={{ marginTop: 4 }}>
      <strong>{name}</strong> (len {Object.values(c).reduce((a,b)=>a+b,0)}) — {chip('0', c[0]||0)}{chip('1', c[1]||0)}{chip('2', c[2]||0)}{chip('3', c[3]||0)}{chip('4', c[4]||0)}
    </div>
  )
  return (
    <div>
      {row('Reel 1', c1)}
      {row('Reel 2', c2)}
      {row('Reel 3', c3)}
    </div>
  )
}
