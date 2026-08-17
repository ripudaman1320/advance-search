HEADER_HTML = """
<div class="dr-brand">
    <div class="dr-mark">
        <span class="dr-bar dr-bar-1"></span>
        <span class="dr-bar dr-bar-2"></span>
        <span class="dr-bar dr-bar-3"></span>
    </div>
    <div class="dr-titles">
        <h1>Email<span class="dr-sep">/</span>RAG</h1>
        <p>AI-powered personal email retrieval</p>
    </div>
</div>
"""

CSS = """
.gradio-container {
    --dr-bg: #090d13;
    --dr-surface: #111a22;
    --dr-surface-2: #0d141b;
    --dr-line: #e8edf5;
    --dr-line-soft: #24303d;
    --dr-text: #edf3f9;
    --dr-muted: #9aa9ba;
    --dr-amber: #f2b84b;
    --dr-blue: #5ab6ff;
    --dr-purple: #9f7ae5;

    width: 100% !important;
    max-width: none !important;
    min-width: 0 !important;
    margin: 0 !important;
    padding: clamp(1.25rem, 2vw, 2.5rem) clamp(1rem, 2vw, 2rem) 4rem !important;
    background:
        radial-gradient(circle at top left, rgba(90, 182, 255, 0.12), transparent 28%),
        radial-gradient(circle at bottom right, rgba(159, 122, 229, 0.10), transparent 30%),
        var(--dr-bg) !important;
    color: var(--dr-text) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif !important;
}

body {
    margin: 0;
    min-width: 320px;
    background: var(--dr-bg, #090d13);
    overflow-x: hidden;
}

.dr-brand {
    display: grid;
    grid-template-columns: auto 1fr;
    align-items: center;
    gap: 1.4rem;
    padding-bottom: 1.25rem;
    border-bottom: 3px solid var(--dr-line);
    margin-bottom: 2rem;
}

.dr-mark {
    display: flex;
    flex-direction: column;
    gap: 5px;
    width: 38px;
}

.dr-bar {
    height: 7px;
    display: block;
}

.dr-bar-1 { background: var(--dr-amber); width: 100%; }
.dr-bar-2 { background: var(--dr-blue); width: 70%; }
.dr-bar-3 { background: var(--dr-purple); width: 45%; }

.dr-titles h1 {
    font-size: clamp(1.8rem, 4vw, 2.6rem);
    font-weight: 900;
    letter-spacing: -0.045em;
    margin: 0;
    line-height: 0.95;
    text-transform: uppercase;
    color: var(--dr-text);
}

.dr-sep {
    color: var(--dr-amber);
    font-weight: 300;
    margin: 0 0.04em;
}

.dr-titles p {
    font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, monospace;
    font-size: 0.7rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    margin: 0.55rem 0 0;
    color: var(--dr-muted);
}

#dr-query {
    width: 100% !important;
}

#dr-query textarea, #dr-query input {
    background: var(--dr-surface) !important;
    color: var(--dr-text) !important;
    border: 2px solid var(--dr-line-soft) !important;
    border-radius: 0 !important;
    padding: 1.05rem 1.2rem !important;
    font-size: 1.05rem !important;
    font-family: inherit !important;
    box-shadow: none !important;
    line-height: 1.45 !important;
    resize: none !important;
    min-height: 56px !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}

#dr-query textarea:focus, #dr-query input:focus {
    outline: none !important;
    border-color: var(--dr-blue) !important;
    box-shadow: 0 0 0 2px rgba(90, 182, 255, 0.2) !important;
}

#dr-query textarea::placeholder, #dr-query input::placeholder {
    color: var(--dr-muted) !important;
    opacity: 1 !important;
}

#dr-run {
    background: var(--dr-amber) !important;
    color: #0c0c0d !important;
    border: 2px solid var(--dr-line) !important;
    border-left: none !important;
    border-radius: 0 !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.14em !important;
    font-size: 0.85rem !important;
    box-shadow: none !important;
    transition: background 0.15s, color 0.15s, transform 0.08s !important;
    min-width: 150px !important;
    padding: 1rem 1.5rem !important;
}

#dr-run:hover {
    background: var(--dr-purple) !important;
    color: #ffffff !important;
}

#dr-run:active { transform: translate(2px, 2px) !important; }

#ingest-panel,
#emails-panel,
#about-panel,
#chat-output,
#sources-output {
    background: rgba(17, 26, 34, 0.9) !important;
    border: 1.5px solid var(--dr-line-soft) !important;
    border-radius: 0 !important;
    padding: 1.15rem 1.2rem !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
}

.tabs {
    border-bottom: 2px solid var(--dr-line-soft) !important;
    margin-top: 1.5rem !important;
}

.tabitem {
    background: transparent !important;
}

button {
    border-radius: 0 !important;
    font-weight: 700 !important;
}

button.primary {
    background: linear-gradient(135deg, var(--dr-amber) 0%, #d9961d 100%) !important;
    color: #101418 !important;
    border: 2px solid rgba(255,255,255,0.08) !important;
    box-shadow: 0 10px 25px rgba(242, 184, 75, 0.22) !important;
}

button.secondary {
    background: var(--dr-surface-2) !important;
    color: var(--dr-text) !important;
    border: 2px solid var(--dr-line-soft) !important;
    box-shadow: none !important;
}

button:hover {
    transform: translateY(-1px);
    transition: all 0.12s ease;
}

input, textarea, .gradio-textbox, .gradio-slider, .gradio-file {
    background: var(--dr-surface) !important;
    border: 2px solid var(--dr-line-soft) !important;
    color: var(--dr-text) !important;
    border-radius: 0 !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
}

label {
    color: var(--dr-text) !important;
    font-weight: 600 !important;
}

.markdown, .output-markdown {
    color: var(--dr-text) !important;
}

.output-markdown {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
}

footer { display: none !important; }

@media (max-width: 700px) {
    .gradio-container {
        padding: 1.25rem 0.75rem 2.5rem !important;
    }

    .dr-brand {
        grid-template-columns: 1fr;
        gap: 0.8rem;
    }

    #dr-run {
        border-left: 2px solid var(--dr-line) !important;
        border-top: none !important;
        width: 100% !important;
    }

    .gradio-row {
        flex-direction: column !important;
    }

    .gradio-column {
        width: 100% !important;
        min-width: 0 !important;
    }
}
"""

JS = """
() => {
    const focus = () => {
        const el = document.querySelector('#dr-query textarea, #dr-query input');
        if (el) { el.focus(); return true; }
        return false;
    };
    if (!focus()) {
        let tries = 0;
        const i = setInterval(() => {
            if (focus() || ++tries > 20) clearInterval(i);
        }, 100);
    }
}
"""
