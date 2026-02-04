STYLE = """<style>
* {
    font-family: 'Trebuchet MS', 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', Arial, sans-serif;
}

/* Dark Mode (Default) */
html, body, [class*="css"] {
    background-color: #0b1220 !important;
}

[data-testid="stSidebar"] {
    background-color: #1a1a1a !important;
}
[data-testid="stSidebar"] > div:first-child {
    background-color: #1a1a1a !important;
}

#sidebar-title {
    color: white;
    text-align: center;
    font-size: 45px;
    font-weight: bold;
    margin-bottom: 20px;
    margin-top: 10px;
}

[data-testid="stSidebar"] .stButton button {
    width: 100%;
    height: 48px;
    padding: 0 12px;
    transition-duration: 0.2s;
    background-color: white !important;
    color: #333 !important;
    border: 5px solid #12284c !important;
    border-radius: 7px !important;
    font-weight: 600 !important;
}

[data-testid="stSidebar"] .stButton button:hover {
    transition-duration: 0.2s;
    background-color: white !important;
    border-bottom: 5px solid #d4af37 !important;
    color: #d4af37 !important;
}

[data-testid="stSidebar"] .stButton button:active {
    transition-duration: 0.05s;
    background-color: #12284c !important;
    color: white !important;
}

/* Light Mode */
@media (prefers-color-scheme: light) {
    html, body, [class*="css"] {
        background-color: #f5f5f5 !important;
        color: #333 !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #1a1a1a !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        background-color: #1a1a1a !important;
    }
    
    [data-testid="stSidebar"] .stButton button {
        width: 100%;
        transition-duration: 0.2s;
        background-color: white !important;
        color: #333 !important;
        border: 5px solid #12284c !important;
        border-radius: 7px !important;
        font-weight: 600 !important;
    }
}

.card {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 20px;
    padding: 18px;
}

.card h3 {
    margin: 0;
    font-size: 18px;
}

.muted {
    color: rgba(255, 255, 255, 0.68);
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
}

@media (max-width: 980px) {
    .metric-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

.metric {
    background: rgba(255, 255, 255, 0.09);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 18px;
    padding: 14px;
}

.metric .k {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.68);
}

.metric .v {
    font-size: 22px;
    font-weight: 700;
    margin-top: 6px;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}
</style>"""
