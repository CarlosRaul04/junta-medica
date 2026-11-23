"""Estilos visuales de la interfaz (colores de la presentación: azul noche, verde azulado y óxido)."""
import streamlit as st

CSS = """
<style>
:root {
  --jm-navy: #13293D; --jm-teal: #0B6E70; --jm-teal-soft: #E6F2F2; --jm-rust: #B4501A;
  --jm-red: #B42318; --jm-red-soft: #FEF3F2; --jm-amber: #B54708; --jm-amber-soft: #FFFAEB;
  --jm-green: #067647; --jm-green-soft: #ECFDF3; --jm-gray: #57606A; --jm-line: #E3E8EE;
}
.block-container { padding-top: 2.2rem; max-width: 1180px; }
h1, h2, h3 { color: var(--jm-navy); letter-spacing: -0.01em; }
[data-testid="stSidebar"] { background: var(--jm-navy); }
[data-testid="stSidebar"] * { color: #E8EEF3; }
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"] { background: rgba(255,255,255,.12); }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.15); }
[data-testid="stSidebar"] button { background: transparent; border-color: rgba(255,255,255,.35); }

.jm-brand { display:flex; align-items:center; gap:.6rem; margin: .2rem 0 1rem 0; }
.jm-brand-mark { width:2.3rem; height:2.3rem; border-radius:.6rem; background: var(--jm-teal);
  display:flex; align-items:center; justify-content:center; font-weight:700; color:#fff; font-size:1.05rem; }
.jm-brand-name { font-weight:700; font-size:1.05rem; line-height:1.1; }
.jm-brand-sub { font-size:.75rem; opacity:.75; }

.jm-header { margin-bottom: 1.2rem; }
.jm-eyebrow { color: var(--jm-teal); font-size:.78rem; font-weight:700; text-transform: uppercase; letter-spacing:.06em; }
.jm-title { font-size: 1.85rem; font-weight: 750; color: var(--jm-navy); margin: .1rem 0 .25rem 0; line-height:1.2; }
.jm-subtitle { color: var(--jm-gray); font-size: .98rem; max-width: 52rem; }

.jm-card { background:#fff; border:1px solid var(--jm-line); border-radius: .9rem; padding: 1.1rem 1.25rem;
  margin-bottom: .8rem; }
.jm-card h4 { margin: 0 0 .35rem 0; font-size: 1rem; color: var(--jm-navy); }
.jm-card p { margin: 0; color: var(--jm-gray); font-size: .92rem; }

.jm-hero { border-radius: 1rem; padding: 1.3rem 1.5rem; margin-bottom: 1rem; border:1px solid var(--jm-line);
  border-left: 6px solid var(--jm-teal); background: #fff; }
.jm-hero.warning { border-left-color: var(--jm-amber); background: var(--jm-amber-soft); }
.jm-hero-label { font-size:.78rem; font-weight:700; text-transform:uppercase; letter-spacing:.06em; color: var(--jm-teal); }
.jm-hero.warning .jm-hero-label { color: var(--jm-amber); }
.jm-hero-title { font-size: 1.45rem; font-weight: 750; color: var(--jm-navy); margin:.2rem 0 .5rem 0; }
.jm-hero-code { display:inline-block; font-family: ui-monospace, monospace; background: var(--jm-teal);
  color:#fff; border-radius:.45rem; padding:.05rem .5rem; margin-right:.5rem; font-size:1.1rem; }
.jm-hero-text { color: #2B3A47; font-size: .98rem; line-height: 1.55; }

.jm-chip { display:inline-block; border-radius: 999px; padding: .12rem .6rem; font-size: .8rem; font-weight:600;
  margin: .15rem .3rem .15rem 0; border:1px solid var(--jm-line); background:#fff; color: var(--jm-navy); }
.jm-chip.teal { background: var(--jm-teal-soft); border-color: transparent; color: var(--jm-teal); }
.jm-chip.red { background: var(--jm-red-soft); border-color: transparent; color: var(--jm-red); }
.jm-chip.amber { background: var(--jm-amber-soft); border-color: transparent; color: var(--jm-amber); }
.jm-chip.green { background: var(--jm-green-soft); border-color: transparent; color: var(--jm-green); }
.jm-chip.gray { background: #F2F4F7; border-color: transparent; color: var(--jm-gray); }
.jm-source { font-size:.8rem; color: var(--jm-gray); margin-top:.25rem; }

.jm-alert { border-radius:.75rem; padding:.8rem 1rem; margin-bottom:.6rem; border:1px solid var(--jm-line); background:#fff; }
.jm-alert.severe { border-color:#FDA29B; background: var(--jm-red-soft); }
.jm-alert.moderate { border-color:#FEDF89; background: var(--jm-amber-soft); }
.jm-alert-text { color: var(--jm-navy); font-size: .95rem; margin-top:.25rem; }

.jm-metric { background:#fff; border:1px solid var(--jm-line); border-radius:.8rem; padding:.8rem 1rem; height:100%; }
.jm-metric-label { color: var(--jm-gray); font-size:.78rem; font-weight:600; }
.jm-metric-value { color: var(--jm-navy); font-size:1.5rem; font-weight:750; line-height:1.3; }
.jm-metric-help { color: var(--jm-gray); font-size:.75rem; }

.jm-steps { display:flex; gap:.4rem; margin: .2rem 0 1.2rem 0; flex-wrap: wrap; }
.jm-step { flex:1; min-width: 8rem; border-top: 4px solid var(--jm-line); padding-top:.45rem; font-size:.82rem; color: var(--jm-gray); }
.jm-step b { display:block; font-size:.72rem; letter-spacing:.05em; text-transform:uppercase; }
.jm-step.done { border-top-color: var(--jm-teal); color: var(--jm-teal); }
.jm-step.current { border-top-color: var(--jm-navy); color: var(--jm-navy); font-weight:600; }

.jm-agent { background:#fff; border:1px solid var(--jm-line); border-radius:.8rem; padding:.85rem 1rem; height:100%; }
.jm-agent-head { display:flex; justify-content:space-between; align-items:center; gap:.5rem; margin-bottom:.4rem; }
.jm-agent-name { font-weight:700; color: var(--jm-navy); }
.jm-agent ul { margin: .3rem 0 0 1rem; padding:0; font-size:.88rem; color:#2B3A47; }

.jm-card table, .jm-card td, .jm-card tr { border: none !important; background: transparent !important; }
.jm-card tr + tr td { border-top: 1px solid var(--jm-line) !important; }
.jm-muted { color: var(--jm-gray); font-size:.85rem; }
.jm-disclaimer { color: var(--jm-gray); font-size: .78rem; border-top:1px solid var(--jm-line); padding-top:.7rem; margin-top: 1.5rem; }
div[data-testid="stTabs"] button p { font-weight: 600; }
</style>
"""


def apply() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
