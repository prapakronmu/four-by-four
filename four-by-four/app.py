"""Dashboard V6: luxury-minimal formal Halloween theme; central shared filters."""
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from dash import Dash, dcc, html, dash_table, Input, Output, State, ctx, no_update

ROOT = Path(__file__).resolve().parent
DATA = pd.read_csv(ROOT / 'data' / 'balanced_panel_BE2562-2567.csv')
HRDI = pd.read_csv(ROOT / 'data' / 'hrdi_monthly_clean.csv')
ALL_PROVINCES = pd.read_csv(ROOT / 'data' / 'thailand_77_provinces.csv')['province'].tolist()

DATA['BE'] = pd.to_numeric(DATA['BE'], errors='raise').astype(int)
DATA['M'] = pd.to_numeric(DATA['M'], errors='raise').astype(int)
DATA['avg_rain_mm'] = pd.to_numeric(DATA['avg_rain_mm'], errors='coerce')
DATA['tons'] = pd.to_numeric(DATA['tons'], errors='coerce')
HRDI['YEAR'] = pd.to_numeric(HRDI['YEAR'], errors='coerce')
HRDI['RAINFALL'] = pd.to_numeric(HRDI['RAINFALL'], errors='coerce')

POINTS = pd.read_csv(ROOT / 'data' / 'province_approx_locations.csv')
BOUNDARY_PATH = ROOT / 'data' / 'thailand_provinces.geojson'
GEOJSON = None
GEOJSON_FIELD = None
if BOUNDARY_PATH.exists():
    try:
        candidate = json.loads(BOUNDARY_PATH.read_text(encoding='utf-8-sig'))
        features = candidate.get('features', [])
        if candidate.get('type') == 'FeatureCollection' and len(features) == 77:
            for field in ('province', 'name_th', 'NAME_1', 'NAME_TH'):
                names = [str(f.get('properties', {}).get(field, '')) for f in features]
                if len(set(names)) == 77 and set(names) == set(ALL_PROVINCES):
                    GEOJSON, GEOJSON_FIELD = candidate, 'properties.' + field
                    break
    except (ValueError, OSError):
        pass

MONTHS = ['ม.ค.','ก.พ.','มี.ค.','เม.ย.','พ.ค.','มิ.ย.','ก.ค.','ส.ค.','ก.ย.','ต.ค.','พ.ย.','ธ.ค.']
PALETTE = {
    'bg': '#120f16',
    'card': '#1c1723',
    'fg': '#f6efe6',
    'sub': '#d2c4b2',
    'rain': '#c58bff',
    'yield': '#ff9e57',
    'gold': '#d9b36c',
    'line': '#3b2d47',
    'accent': '#7a4b2a',
}

app = Dash(__name__, title='Rainfall × Rubber | Executive Intelligence', suppress_callback_exceptions=False)
server = app.server


def opts(values, prefix=''):
    return [{'label': f'{prefix}{v}', 'value': v} for v in values]


def graph(gid):
    return dcc.Graph(id=gid, config={'displaylogo': False, 'responsive': True, 'toImageButtonOptions': {'format': 'png', 'filename': 'agriculture-chart', 'scale': 2}}, style={'minHeight': '330px'})


def panel(*children):
    return html.Div(children, className='panel')


def graph_pair(*ids):
    return html.Div([panel(graph(i)) for i in ids], className='graph-grid')


app.index_string = '''<!DOCTYPE html><html><head>{%metas%}<title>{%title%}</title>{%favicon%}{%css%}
<style>
:root{--bg:#120f16;--card:#1c1723;--fg:#f6efe6;--sub:#d2c4b2;--yield:#ff9e57;--rain:#c58bff;--gold:#d9b36c;--line:#3b2d47;--accent:#7a4b2a}
*{box-sizing:border-box}
body{background:radial-gradient(circle at top right,#241826 0%,#17131c 40%,#120f16 100%);color:var(--fg);font-family:Inter,'Noto Sans Thai','Segoe UI',Arial,sans-serif;margin:0}
.wrap{max-width:1480px;margin:auto;padding:28px 22px 34px}
.hero{background:linear-gradient(90deg,rgba(18,15,22,.80),rgba(18,15,22,.35)),url('/assets/halloween-banner.png') center 48%/cover;border:1px solid rgba(217,179,108,.30);border-radius:24px;padding:22px 24px 18px;box-shadow:0 14px 40px rgba(0,0,0,.28);margin-bottom:18px}
.hero{min-height:180px;display:flex;flex-direction:column;justify-content:center}.hero-badge{display:inline-block;padding:6px 12px;border-radius:999px;background:rgba(255,158,87,.12);border:1px solid rgba(255,158,87,.28);color:#ffd6b2;font-size:12px;letter-spacing:.05em;text-transform:uppercase}
.map-shell{display:grid;grid-template-columns:minmax(0,1.75fr) minmax(300px,1fr);gap:14px;margin-top:14px}.map-side{display:flex;flex-direction:column;gap:14px}.sidebar-card{padding:18px}.sidebar-card h3{margin:0 0 12px;font-size:17px}.sidebar-card p{line-height:1.7;color:#e9d5bf;font-size:14px}.info-tag{display:inline-block;border-radius:10px;border:1px solid #80604b;padding:5px 10px;margin:4px;color:#f6d2a2}.map-hint{font-size:12px;color:#cdbbba;margin:10px 0}@media(max-width:950px){.map-shell{grid-template-columns:1fr}}h1{font-size:31px;line-height:1.2;margin:12px 0 8px;font-weight:800;letter-spacing:.01em}
.muted{color:var(--sub);font-size:13px;line-height:1.55}
.filters{display:grid;grid-template-columns:2fr 1.3fr 1.3fr 1fr;gap:14px;margin:20px 0}
.filter{background:rgba(28,23,35,.92);backdrop-filter:blur(4px);border:1px solid rgba(217,179,108,.18);padding:13px 14px 14px;border-radius:18px;box-shadow:0 10px 26px rgba(0,0,0,.18)}
.filter label{display:block;color:#f3dbc0;font-size:12px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;margin-bottom:8px}
.panel{background:rgba(28,23,35,.96);border:1px solid rgba(217,179,108,.14);border-radius:20px;padding:12px;min-width:0;box-shadow:0 14px 34px rgba(0,0,0,.22)}
.graph-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:12px 0}
.kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
.kpi{background:linear-gradient(180deg,rgba(255,255,255,.02),rgba(255,158,87,.04));border:1px solid rgba(217,179,108,.16);padding:18px 18px 16px;border-radius:18px;box-shadow:0 12px 30px rgba(0,0,0,.18)}
.kpi strong{display:block;font-size:28px;margin-top:8px;color:#fff7ef;font-weight:800}
.note{background:linear-gradient(135deg,rgba(255,158,87,.08),rgba(197,139,255,.07));color:#f0e0ce;padding:14px 16px;border-radius:16px;margin:14px 0;font-size:13px;border:1px solid rgba(217,179,108,.18);line-height:1.6}
.tab-shell{margin-top:16px}
.dash-tabs{background:transparent!important}
.dash-tabs .tab{background:rgba(28,23,35,.72)!important;color:#eadfcf!important;border:1px solid rgba(217,179,108,.12)!important;border-radius:12px 12px 0 0!important;margin-right:8px!important;padding:10px 14px!important}
.dash-tabs .tab--selected{background:linear-gradient(180deg,rgba(255,158,87,.18),rgba(28,23,35,1))!important;color:white!important;border-bottom:3px solid var(--yield)!important}
button{background:linear-gradient(135deg,#ff9e57,#d97b39);color:white;border:0;border-radius:14px;font-weight:700;box-shadow:0 12px 24px rgba(255,126,60,.18)}
button:hover{filter:brightness(1.03)}
.Select-control,.Select-menu-outer,.Select-menu{background:#211a29!important;color:var(--fg)!important;border-color:rgba(217,179,108,.18)!important}
.Select--multi .Select-value{background:rgba(197,139,255,.18)!important;border-color:rgba(197,139,255,.38)!important;color:#f7ecff!important}
.Select-placeholder,.Select-value-label,.Select-input>input{color:var(--fg)!important}
.Select-arrow{border-top-color:var(--sub)!important}
@media(max-width:950px){.filters,.graph-grid,.kpis{grid-template-columns:1fr 1fr}}
@media(max-width:560px){.wrap{padding:16px}.hero{padding:18px}.filters,.graph-grid,.kpis{grid-template-columns:1fr}.map-shell{display:grid;grid-template-columns:minmax(0,1.75fr) minmax(300px,1fr);gap:14px;margin-top:14px}.map-side{display:flex;flex-direction:column;gap:14px}.sidebar-card{padding:18px}.sidebar-card h3{margin:0 0 12px;font-size:17px}.sidebar-card p{line-height:1.7;color:#e9d5bf;font-size:14px}.info-tag{display:inline-block;border-radius:10px;border:1px solid #80604b;padding:5px 10px;margin:4px;color:#f6d2a2}.map-hint{font-size:12px;color:#cdbbba;margin:10px 0}@media(max-width:950px){.map-shell{grid-template-columns:1fr}}h1{font-size:24px}}

/* V9 - editorial dashboard / inspired by provided visual reference */
body{font-family:'Segoe UI',Tahoma,Arial,sans-serif}
.hero{min-height:240px;border-radius:22px;background-position:center 49%;background-size:cover;padding:32px}
.hero h1{font-size:clamp(24px,3vw,39px);text-shadow:0 3px 12px rgba(0,0,0,.85)}
.hero .muted{color:#f7e0c5;font-size:15px;text-shadow:0 2px 8px #080608}
.hero-badge{width:max-content;padding:8px 14px;backdrop-filter:blur(8px)}
.dash-tabs{position:relative;border:0!important;margin-top:14px}
.dash-tabs .tab{font-weight:700;transition:background .2s,color .2s,transform .2s;line-height:1.4}
.dash-tabs .tab:hover{background:#382333!important;color:#ffe2a7!important;transform:translateY(-1px)}
.panel{transition:box-shadow .2s ease,border-color .2s ease}
.panel:hover{border-color:rgba(255,158,87,.35);box-shadow:0 14px 38px rgba(0,0,0,.32)}
.action-bar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:12px 0}
.action-button{padding:10px 17px;cursor:pointer;min-height:40px}
.action-secondary{background:#2e2635;color:#ffdeb4;border:1px solid #796047}
.explore-grid{display:grid;grid-template-columns:1fr;gap:14px}
.data-table .dash-spreadsheet-container{border-radius:12px;overflow-x:auto}
.data-table .dash-cell{font-family:'Segoe UI',Tahoma,sans-serif!important}
.help-text{color:#e6d0bc;font-size:13px;line-height:1.7}
.small-pill{display:inline-block;color:#f9d8ae;background:#3a2a2a;border:1px solid #8f6553;padding:6px 11px;border-radius:40px;font-size:12px}
@media(max-width:600px){.hero{min-height:195px;padding:20px}.action-bar{flex-direction:column;align-items:stretch}.action-bar button{width:100%}.dash-tabs .tab{font-size:11px;padding:8px!important}}
</style></head><body>{%app_entry%}<footer>{%config%}{%scripts%}{%renderer%}</footer></body></html>'''

app.layout = html.Div(className='wrap', children=[
    html.Div(className='hero', children=[
        html.Div('THAILAND • EXECUTIVE AGRICULTURAL INTELLIGENCE', className='hero-badge'),
        html.H1('วิเคราะห์ปริมาณน้ำฝนและผลผลิตยางพารา'),
        html.Div('ระบบวิเคราะห์ฝนและผลผลิตยางพาราเชิงพื้นที่ • คลิกสำรวจจังหวัด เปรียบเทียบรายเดือน และดาวน์โหลดข้อมูลตามตัวกรอง', className='muted'),
    ]),
    html.Div(className='filters', children=[
        html.Div(className='filter', children=[html.Label('จังหวัด (เลือกหลายจังหวัดได้)'), dcc.Dropdown(id='province', multi=True, options=opts(ALL_PROVINCES), placeholder='ทุกจังหวัด', value=[])]),
        html.Div(className='filter', children=[html.Label('ปี พ.ศ. (เลือกหลายปีได้)'), dcc.Dropdown(id='year', multi=True, options=opts(sorted(DATA.BE.unique())), placeholder='ทุกปี', value=[])]),
        html.Div(className='filter', children=[html.Label('เดือน (เลือกหลายเดือนได้)'), dcc.Dropdown(id='month', multi=True, options=[{'label': MONTHS[i-1], 'value': i} for i in range(1, 13)], placeholder='ทุกเดือน', value=[])]),
        html.Div(className='filter', children=[html.Label('ล้างตัวกรอง'), html.Button('ล้างทั้งหมด', id='clear', n_clicks=0, style={'width': '100%', 'padding': '10px', 'cursor': 'pointer'})])
    ]),
    html.Div(className='action-bar', children=[
        html.Span('INTERACTIVE • สำรวจข้อมูลได้จากแผนที่และกราฟ', className='small-pill'),
        html.Button('⬇ ดาวน์โหลด CSV ที่กรองแล้ว', id='download-btn', n_clicks=0, className='action-button'),
        html.Button('↻ รีเซ็ตการเลือก', id='reset-btn', n_clicks=0, className='action-button action-secondary'),
        dcc.Download(id='download-csv'),
    ]),
    html.Div(id='filter-caption', className='note'),
    html.Div(id='kpis', className='kpis'),
    html.Div(id='coverage-status', className='note'),
    html.Div(className='filter', children=[html.Label('ตัวชี้วัดแผนที่'), dcc.RadioItems(id='map-metric', options=[{'label':' ฝนเฉลี่ย (มม.)','value':'avg_rain_mm'},{'label':' ผลผลิตรวม (ตัน)','value':'tons'}],value='avg_rain_mm',inline=True,style={'display':'flex','gap':'30px','flexWrap':'wrap'})]),
    html.Div(className='map-shell',children=[panel(html.H3('แผนที่ประเทศไทย • เลือกจังหวัดได้'),graph('province-map'),html.Div(id='map-method',className='map-hint')),html.Div(className='map-side',children=[panel(html.Div([html.H3('ข้อมูลจังหวัดที่เลือก'),html.Div(id='selected-profile')],className='sidebar-card')),panel(html.Div([html.H3('อันดับจังหวัด'),html.Div(id='top-provinces')],className='sidebar-card'))])]),
    dcc.Tabs(id='tabs', value='overview', className='dash-tabs', children=[
        dcc.Tab(label='ภาพรวม', value='overview', children=[html.Div(className='tab-shell', children=[graph_pair('overview-rain', 'overview-yield'), panel(graph('overview-province'))])]),
        dcc.Tab(label='ปริมาณน้ำฝน', value='rain', children=[html.Div(className='tab-shell', children=[graph_pair('rain-month', 'rain-province')])]),
        dcc.Tab(label='ผลผลิตยางพารา', value='yield', children=[html.Div(className='tab-shell', children=[graph_pair('yield-month', 'yield-province')])]),
        dcc.Tab(label='เปรียบเทียบฝนกับผลผลิต', value='compare', children=[html.Div(className='tab-shell', children=[graph_pair('compare-trend', 'compare-scatter'), panel(graph('compare-heat'))])]),
        dcc.Tab(label='ความครอบคลุม 77 จังหวัด', value='coverage', children=[html.Div(className='tab-shell', children=[
            html.Div('ตารางความครบถ้วนแสดงข้อมูลเดิมเท่านั้น: เครื่องหมาย ไม่มีข้อมูล ไม่ได้หมายถึงค่าศูนย์ และไม่ได้หมายความว่าจังหวัดนั้นไม่มีสวนยาง', className='note'),
            panel(graph('coverage-chart')),
            panel(html.Div(id='coverage-table'))
        ])]),
        dcc.Tab(label='สำรวจข้อมูล / ตาราง', value='explorer', children=[html.Div(className='tab-shell explore-grid',children=[
            html.Div('ค้นหาหรือเรียงตารางได้ • ค่าที่ไม่มีข้อมูลยังคงเป็นช่องว่าง • ตารางนี้แสดงเฉพาะรายการตามตัวกรองปัจจุบัน',className='note'),
            panel(dash_table.DataTable(id='data-table',columns=[
                {'name':'จังหวัด','id':'province'}, {'name':'ปี พ.ศ.','id':'BE'}, {'name':'เดือน','id':'month_label'},
                {'name':'ฝนเฉลี่ย (มม.)','id':'avg_rain_mm','type':'numeric'},
                {'name':'ผลผลิต (ตัน)','id':'tons','type':'numeric'}],
                data=[],page_size=15,sort_action='native',filter_action='native',page_action='native',
                style_table={'overflowX':'auto'},
                style_header={'backgroundColor':'#3c2837','color':'#ffe2ae','fontWeight':'bold','padding':'12px','borderColor':'#665061'},
                style_cell={'backgroundColor':'#211b29','color':'#f4ebdf','padding':'10px','textAlign':'left','minWidth':'110px','borderColor':'#3c3140'},
                style_filter={'backgroundColor':'#35273c','color':'#f8efe4'},
                style_data_conditional=[{'if':{'row_index':'odd'},'backgroundColor':'#292031'}]))
        ])]),
        dcc.Tab(label='สถานี HRDI', value='hrdi', children=[html.Div(className='tab-shell', children=[html.Div('หมายเหตุ: ข้อมูล HRDI เป็นอีกชุดข้อมูล ใช้ปี ค.ศ. และไม่ควรนำไปรวมกับข้อมูลฝนหลักโดยตรง', className='note'), graph_pair('hrdi-stations', 'hrdi-rain')])]),
    ]),
    html.Div('ข้อจำกัด: ตัวเลขผลผลิตในไฟล์ต้นทางยังไม่ได้ยืนยันกับแหล่งข้อมูลทางการ • ค่าเฉลี่ยฝนใช้ค่าเฉลี่ยของแถวที่เลือก ไม่ใช่ยอดรวมปริมาณฝน • ธีมนี้ออกแบบให้หรู เรียบ และมีอารมณ์ฮาโลวีนแบบสุภาพเพื่อยังเหมาะกับงานวิชาการ', className='note')
])


def empty(title, msg='ไม่มีข้อมูลในเงื่อนไขนี้'):
    f = go.Figure()
    f.add_annotation(text=msg, showarrow=False, font={'size': 17, 'color': PALETTE['sub']})
    return style(f, title)


def style(fig, title):
    fig.update_layout(
        title={'text': title, 'font': {'size': 18, 'color': PALETTE['fg']}},
        paper_bgcolor=PALETTE['card'],
        plot_bgcolor=PALETTE['card'],
        font={'color': PALETTE['fg']},
        margin={'l': 50, 'r': 25, 't': 68, 'b': 54},
        hovermode='closest',
        legend={'orientation': 'h', 'y': -0.2},
        uirevision='static',
        title_x=0.02,
    )
    fig.update_xaxes(gridcolor=PALETTE['line'], zerolinecolor=PALETTE['line'], showline=False)
    fig.update_yaxes(gridcolor=PALETTE['line'], zerolinecolor=PALETTE['line'], showline=False)
    return fig


def line_by_time(df, field, title, mode):
    if df.empty:
        return empty(title)
    agg = df.groupby(['BE', 'M'], as_index=False).agg(value=(field, mode))
    agg['period'] = agg['BE'].astype(str) + '-' + agg['M'].astype(str).str.zfill(2)
    color = PALETTE['rain'] if field == 'avg_rain_mm' else PALETTE['yield']
    fig = px.line(agg, x='period', y='value', markers=True, color_discrete_sequence=[color])
    fig.update_traces(line={'width': 3})
    fig.update_yaxes(title='มม.' if field == 'avg_rain_mm' else 'ตัน')
    return style(fig, title)


def by_province(df, field, title, mode):
    if df.empty:
        return empty(title)
    d = df.groupby('province', as_index=False)[field].agg(mode).sort_values(field, ascending=False).head(20)
    color = PALETTE['rain'] if field == 'avg_rain_mm' else PALETTE['yield']
    fig = px.bar(d, x='province', y=field, color_discrete_sequence=[color])
    fig.update_yaxes(title='มม.' if field == 'avg_rain_mm' else 'ตัน')
    return style(fig, title + ' (สูงสุด 20 จังหวัด)')


def monthly(df, field, title, mode):
    if df.empty:
        return empty(title)
    d = df.groupby('M', as_index=False)[field].agg(mode)
    d['เดือน'] = d.M.map(lambda x: MONTHS[x-1])
    color = PALETTE['rain'] if field == 'avg_rain_mm' else PALETTE['yield']
    fig = px.bar(d, x='เดือน', y=field, color_discrete_sequence=[color])
    fig.update_yaxes(title='มม.' if field == 'avg_rain_mm' else 'ตัน')
    return style(fig, title)


def combined(df):
    if df.empty:
        return empty('แนวโน้มรายเดือน: ฝนเทียบกับผลผลิต')
    d = df.groupby(['BE', 'M'], as_index=False).agg(rain=('avg_rain_mm', 'mean'), yield_ton=('tons', 'sum'))
    d['period'] = d.BE.astype(str) + '-' + d.M.astype(str).str.zfill(2)
    fig = go.Figure()
    fig.add_bar(x=d.period, y=d.yield_ton, name='ผลผลิตรวม (ตัน)', marker_color=PALETTE['yield'])
    fig.add_trace(go.Scatter(x=d.period, y=d.rain, name='ฝนเฉลี่ย (มม.)', mode='lines+markers', yaxis='y2', line={'color': PALETTE['rain'], 'width': 3}))
    fig.update_layout(
        yaxis={'title': 'ผลผลิตรวม (ตัน)'},
        yaxis2={'title': 'ฝนเฉลี่ย (มม.)', 'overlaying': 'y', 'side': 'right'},
        barmode='group'
    )
    return style(fig, 'เปรียบเทียบตามปี–เดือน (สองแกน)')


def scatter(df):
    if df.empty:
        return empty('ความสัมพันธ์ฝนกับผลผลิต')
    fig = px.scatter(
        df,
        x='avg_rain_mm',
        y='tons',
        color='BE',
        hover_data=['province', 'M'],
        labels={'avg_rain_mm': 'ฝนเฉลี่ย (มม.)', 'tons': 'ผลผลิต (ตัน)', 'BE': 'ปี พ.ศ.'},
        color_continuous_scale=[[0, '#5c2e91'], [0.5, '#a86ef5'], [1, '#ffd08b']],
        opacity=.72,
    )
    return style(fig, 'Scatter: 1 จุด = 1 จังหวัด–ปี–เดือน')


def heat(df):
    if df.empty:
        return empty('Heatmap ฝนเฉลี่ย ปี × เดือน')
    d = df.groupby(['BE', 'M'], as_index=False).avg_rain_mm.mean()
    p = d.pivot(index='BE', columns='M', values='avg_rain_mm')
    fig = px.imshow(
        p,
        labels={'x': 'เดือน', 'y': 'ปี พ.ศ.', 'color': 'ฝนเฉลี่ย (มม.)'},
        aspect='auto',
        color_continuous_scale=[[0, '#2b2135'], [0.35, '#7a4ea3'], [0.7, '#c58bff'], [1, '#ffd08b']]
    )
    return style(fig, 'Heatmap ปริมาณฝนเฉลี่ยแยกปี–เดือน')


def hrdi_figures(provinces):
    h = HRDI.copy()
    if provinces:
        h = h[h['PROVINCE'].isin(provinces)]
    if h.empty:
        return empty('สถานี HRDI'), empty('ฝนสถานี HRDI')
    stations = h.groupby('PROVINCE', as_index=False).agg(stations=('STA_TH', 'nunique')).sort_values('stations', ascending=False)
    f = px.bar(stations, x='PROVINCE', y='stations', color_discrete_sequence=[PALETTE['rain']])
    f = style(f, 'จำนวนสถานี HRDI แยกจังหวัด')
    rr = h.groupby('YEAR', as_index=False).RAINFALL.mean().dropna().sort_values('YEAR')
    g = px.line(rr, x='YEAR', y='RAINFALL', markers=True, color_discrete_sequence=[PALETTE['rain']])
    g.update_traces(line={'width': 3})
    g = style(g, 'ฝนเฉลี่ย HRDI ตามปี ค.ศ. (เฉพาะค่าที่มี)')
    return f, g



def coverage_report(provinces, years, months):
    """Inspect original panel only; never fill missing observations with zeros."""
    province_scope = provinces if provinces else ALL_PROVINCES
    year_scope = years if years else sorted(DATA.BE.unique())
    month_scope = months if months else list(range(1, 13))
    expected = len(year_scope) * len(month_scope)
    source = DATA[DATA.BE.isin(year_scope) & DATA.M.isin(month_scope)]
    counts = source.groupby('province').size().to_dict()
    rows = []
    for name in province_scope:
        count = int(counts.get(name, 0))
        rows.append({'จังหวัด': name, 'พบข้อมูล': count, 'คาดหวัง': expected, 'ขาด': expected - count,
                     'สถานะ': 'ครบ' if count == expected else ('บางส่วน' if count else 'ไม่มีข้อมูล')})
    table = pd.DataFrame(rows).sort_values(['ขาด','จังหวัด'], ascending=[False,True])
    complete = int((table['สถานะ'] == 'ครบ').sum())
    missing = int((table['สถานะ'] == 'ไม่มีข้อมูล').sum())
    partial = int((table['สถานะ'] == 'บางส่วน').sum())
    status = (f'ความครอบคลุมในตัวกรองที่เลือก: ครบ {complete} จังหวัด • บางส่วน {partial} จังหวัด • '
              f'ไม่มีข้อมูล {missing} จังหวัด • คาดหวังจังหวัดละ {expected} เดือน-ปี | '
              'ข้อมูลหลัก 52 จังหวัด ไม่ใช่ทุกจังหวัดในประเทศไทย')
    figure = go.Figure()
    colors = [PALETTE['yield'] if v == expected else ('#e0ad57' if v else '#655d66') for v in table['พบข้อมูล']]
    figure.add_bar(y=table['จังหวัด'], x=table['พบข้อมูล'], orientation='h', marker_color=colors,
                   hovertemplate='%{y}: %{x} รายการ<extra></extra>')
    figure.update_layout(height=max(450, min(len(table)*23+120, 1900)), yaxis={'autorange':'reversed'},
                         xaxis_title='จำนวนรายการจังหวัด–ปี–เดือน')
    figure = style(figure, 'ความครอบคลุมข้อมูลรายจังหวัด (ไม่มีข้อมูล ≠ 0)')
    th = html.Tr([html.Th(col, style={'textAlign':'left','padding':'10px','borderBottom':'1px solid #564258'}) for col in table.columns])
    tr = [html.Tr([html.Td(str(rec[col]), style={'padding':'8px','borderBottom':'1px solid #332938'}) for col in table.columns]) for rec in table.to_dict('records')]
    grid = html.Div(html.Table([html.Thead(th),html.Tbody(tr)],style={'width':'100%','fontSize':'13px'}),
                    style={'overflowX':'auto','maxHeight':'520px','overflowY':'auto'})
    return status, figure, grid


def map_figure(d, metric):
    # Never interpret absent rows as 0; point locations are approximate province positions.
    mode = 'mean' if metric == 'avg_rain_mm' else 'sum'
    agg = d.groupby('province', as_index=False)[metric].agg(mode).dropna()
    locations = POINTS.merge(agg, on='province', how='left')
    available = locations[locations[metric].notna()].copy()
    not_available = locations[locations[metric].isna()].copy()
    fig = go.Figure()
    if GEOJSON is not None:
        # Empty polygons are shown as grey using a separate trace.
        fig.add_trace(go.Choropleth(geojson=GEOJSON, locations=POINTS.province.tolist(),
             featureidkey=GEOJSON_FIELD,z=[0]*len(POINTS),colorscale=[[0,'#3e3748'],[1,'#3e3748']],
             showscale=False,marker_line_width=.6,marker_line_color='#706178',name='ขอบเขตจังหวัด',hoverinfo='skip'))
        if len(available):
            fig.add_trace(go.Choropleth(geojson=GEOJSON,locations=available.province,
              featureidkey=GEOJSON_FIELD,z=available[metric],
              colorscale=[[0,'#3b284b'],[.45,'#b25342'],[1,'#ffc56e']],
              colorbar_title='มม.' if metric=='avg_rain_mm' else 'ตัน',
              marker_line_color='#cfad84',marker_line_width=.5,
              customdata=available[['province']].to_numpy(),
              hovertemplate='%{location}<br>ค่า: %{z:,.2f}<extra></extra>',name='ข้อมูลที่มี'))
        fig.update_geos(fitbounds='locations', visible=False, bgcolor=PALETTE['card'])
    else:
        # Position view until trusted administrative polygon data is provided.
        fig.add_trace(go.Scattergeo(lon=not_available.lon,lat=not_available.lat,
            text=not_available.province,customdata=not_available[['province']].to_numpy(),
            mode='markers',marker={'size':7,'color':'#786c81','line':{'color':'#e1d3cf','width':.4}},
            hovertemplate='%{text}<br>ไม่มีข้อมูลในช่วงที่เลือก<extra></extra>',name='ไม่มีข้อมูล'))
        if len(available):
            fig.add_trace(go.Scattergeo(lon=available.lon,lat=available.lat,text=available.province,
              customdata=available[['province']].to_numpy(),mode='markers',
              marker={'size':12,'color':available[metric],
                      'colorscale':[[0,'#59335e'],[.5,'#ce623a'],[1,'#ffcc78']],
                      'showscale':True,'colorbar':{'title':'มม.' if metric=='avg_rain_mm' else 'ตัน'},
                      'line':{'width':1,'color':'#ffdab5'}},
              hovertemplate='%{text}<br>ค่า: %{marker.color:,.2f}<extra></extra>',name='มีข้อมูล'))
        fig.update_geos(projection_type='mercator',lonaxis_range=[97,106.5],
                        lataxis_range=[5.2,20.9],showland=True,landcolor='#292431',
                        showcountries=True,countrycolor='#66536b',showcoastlines=True,
                        coastlinecolor='#83718a',showocean=True,oceancolor='#171521',bgcolor=PALETTE['card'])
    fig.update_layout(height=660,margin={'t':20,'b':10,'l':10,'r':10},
        paper_bgcolor=PALETTE['card'],font_color=PALETTE['fg'],legend={'orientation':'h','y':0})
    return fig

def map_details(d, provinces, metric):
    available = d.dropna(subset=[metric]).groupby('province',as_index=False)[metric].agg('mean' if metric=='avg_rain_mm' else 'sum')
    top = available.nlargest(8,metric)
    if top.empty:
        ranking = html.P('ไม่มีข้อมูลที่ตรงกับตัวกรอง')
    else:
        ranking = html.Ol([html.Li(f'{r.province}: {getattr(r,metric):,.2f} '+('มม.' if metric=='avg_rain_mm' else 'ตัน')) for r in top.itertuples(index=False)])
    scope = provinces or []
    if len(scope)!=1:
        profile=html.P('คลิกจังหวัดบนแผนที่หรือเลือกจังหวัดจากตัวกรอง เพื่อดูรายละเอียดเฉพาะจังหวัดนั้น')
    else:
        subset=d[d.province==scope[0]]
        if subset.empty:
            profile=html.P(f'{scope[0]} — ไม่มีข้อมูลในชุดเดิมสำหรับช่วงที่เลือก (ไม่ใช่ค่าศูนย์)')
        else:
            rain=subset.avg_rain_mm.mean()
            rubber=subset.tons.sum(min_count=1)
            profile=html.Div([html.H2(scope[0]),
                html.P(f'ปริมาณฝนเฉลี่ยของรายการที่เลือก: {rain:,.2f} มม.' if pd.notna(rain) else 'ฝน: ไม่มีข้อมูล'),
                html.P(f'ผลผลิตรวมของรายการที่เลือก: {rubber:,.0f} ตัน' if pd.notna(rubber) else 'ผลผลิต: ไม่มีข้อมูล'),
                html.P(f'จำนวนรายการ: {len(subset):,} จังหวัด–ปี–เดือน'),
                html.P('หมายเหตุ: ผลผลิตในข้อมูลเดิมยังไม่ผ่านการตรวจสอบกับ OAE')])
    return profile, ranking


def table_records(d):
    if d.empty:return []
    t=d[['province','BE','M','avg_rain_mm','tons']].copy()
    t['month_label']=t['M'].map(lambda m: MONTHS[int(m)-1])
    t=t[['province','BE','month_label','avg_rain_mm','tons']].round(2)
    return t.astype(object).where(pd.notnull(t),None).to_dict('records')


@app.callback(Output('province', 'value'), Output('year', 'value'), Output('month', 'value'),
              Input('clear','n_clicks'),Input('reset-btn','n_clicks'),Input('province-map','clickData'),
              Input('overview-rain','clickData'),Input('overview-yield','clickData'),
              Input('rain-month','clickData'),Input('yield-month','clickData'),
              Input('overview-province','clickData'),Input('rain-province','clickData'),Input('yield-province','clickData'),
              prevent_initial_call=True)
def map_or_clear(_, __, map_click, rain_click, yield_click, rain_month_click, yield_month_click,
                 overview_province_click, rain_province_click, yield_province_click):
    trig=ctx.triggered_id
    if trig in ('clear','reset-btn'):
        return [],[],[]
    if trig == 'province-map':
        if not map_click or not map_click.get('points'):
            return no_update,no_update,no_update
        point=map_click['points'][0]
        name=point.get('location') or (point.get('customdata') or [None])[0]
        if name in ALL_PROVINCES:
            return [name],no_update,no_update
    if trig in ('overview-rain','overview-yield'):
        click=rain_click if trig=='overview-rain' else yield_click
        try:
            period=str(click['points'][0]['x'])
            year,month=map(int,period.split('-'))
            if year in DATA.BE.unique() and month in range(1,13):
                return no_update,[year],[month]
        except (KeyError,IndexError,ValueError,TypeError):pass
    if trig in ('rain-month','yield-month'):
        click=rain_month_click if trig=='rain-month' else yield_month_click
        try:
            month=MONTHS.index(str(click['points'][0]['x']))+1
            return no_update,no_update,[month]
        except (KeyError,IndexError,ValueError,TypeError):pass
    if trig in ('overview-province','rain-province','yield-province'):
        click={'overview-province':overview_province_click,'rain-province':rain_province_click,'yield-province':yield_province_click}.get(trig)
        try:
            name=str(click['points'][0]['x'])
            if name in ALL_PROVINCES:return [name],no_update,no_update
        except (KeyError,IndexError,ValueError,TypeError):pass
    return no_update,no_update,no_update


@app.callback(Output('download-csv','data'),Input('download-btn','n_clicks'),
              State('province','value'),State('year','value'),State('month','value'),prevent_initial_call=True)
def download_filtered(n,provinces,years,months):
    d=filter_panel(provinces,years,months).copy()
    d=d[['province','BE','M','avg_rain_mm','tons']]
    return dcc.send_data_frame(d.to_csv,'rainfall_rubber_filtered.csv',index=False,encoding='utf-8-sig')


def filter_panel(provinces,years,months):
    d=DATA
    if provinces:d=d[d.province.isin(provinces)]
    if years:d=d[d.BE.isin(years)]
    if months:d=d[d.M.isin(months)]
    return d


@app.callback(
    Output('province-map','figure'),Output('map-method','children'),Output('selected-profile','children'),Output('top-provinces','children'),
    Output('filter-caption', 'children'), Output('kpis', 'children'), Output('coverage-status', 'children'), Output('coverage-chart', 'figure'), Output('coverage-table', 'children'),
    Output('overview-rain', 'figure'), Output('overview-yield', 'figure'), Output('overview-province', 'figure'),
    Output('rain-month', 'figure'), Output('rain-province', 'figure'),
    Output('yield-month', 'figure'), Output('yield-province', 'figure'),
    Output('compare-trend', 'figure'), Output('compare-scatter', 'figure'), Output('compare-heat', 'figure'),
    Output('hrdi-stations', 'figure'), Output('hrdi-rain', 'figure'), Output('data-table','data'),
    Input('province', 'value'), Input('year', 'value'), Input('month', 'value'),Input('map-metric','value')
)
def update(provinces, years, months, map_metric):
    provinces = provinces or []
    years = years or []
    months = months or []
    d = filter_panel(provinces, years, months)

    caption = (
        f"ขอบเขต: {', '.join(provinces) if provinces else 'ทุกจังหวัด'} | "
        f"ปี {', '.join(map(str, years)) if years else 'ทุกปี'} | "
        f"เดือน {', '.join(MONTHS[m-1] for m in months) if months else 'ทุกเดือน'} | {len(d):,} แถว"
    )

    def kpi(label, value):
        return html.Div([html.Div(label, className='muted'), html.Strong(value)], className='kpi')

    kpis = [
        kpi('จังหวัดที่มีข้อมูล', f'{d.province.nunique():,}'),
        kpi('รายการจังหวัด–ปี–เดือน', f'{len(d):,}'),
        kpi('ฝนเฉลี่ย (มม.)', f'{d.avg_rain_mm.mean():,.2f}' if len(d) else '—'),
        kpi('ผลผลิตรวม (ตัน)', f'{d.tons.sum(min_count=1):,.0f}' if d.tons.notna().any() else '—'),
    ]

    coverage_status, coverage_figure, coverage_table = coverage_report(provinces, years, months)
    hr1, hr2 = hrdi_figures(provinces)
    details, ranking = map_details(d, provinces, map_metric)
    map_label = ('แผนที่เขตจังหวัดจาก GeoJSON ที่ผ่านการตรวจสอบ 77 จังหวัด' if GEOJSON else
                 'แผนที่ตำแหน่งโดยประมาณของ 77 จังหวัด (จุดไม่ใช่ขอบเขตจังหวัด) • เพิ่ม data/thailand_provinces.geojson ที่ผ่านการตรวจสอบเพื่อแสดงขอบเขตจริง')
    return (
        map_figure(d, map_metric),map_label,details,ranking,
        caption, kpis, coverage_status, coverage_figure, coverage_table,
        line_by_time(d, 'avg_rain_mm', 'ฝนเฉลี่ยตามปี–เดือน', 'mean'),
        line_by_time(d, 'tons', 'ผลผลิตรวมตามปี–เดือน', 'sum'),
        by_province(d, 'tons', 'ผลผลิตรวมรายจังหวัด', 'sum'),
        monthly(d, 'avg_rain_mm', 'ฝนเฉลี่ยรายเดือน', 'mean'),
        by_province(d, 'avg_rain_mm', 'ฝนเฉลี่ยรายจังหวัด', 'mean'),
        monthly(d, 'tons', 'ผลผลิตรวมรายเดือน', 'sum'),
        by_province(d, 'tons', 'ผลผลิตรวมรายจังหวัด', 'sum'),
        combined(d), scatter(d), heat(d), hr1, hr2,
        table_records(d)
    )


if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=8050)
