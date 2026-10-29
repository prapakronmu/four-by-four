from pathlib import Path
import pandas as pd
root=Path(__file__).resolve().parent
main=pd.read_csv(root/'data/balanced_panel_BE2562-2567.csv')
hrdi=pd.read_csv(root/'data/hrdi_monthly_clean.csv')
assert {'BE','M','province','avg_rain_mm','tons'} <= set(main.columns)
assert not main.duplicated(['BE','M','province']).any(), 'Duplicate province/year/month!'
assert main['M'].between(1,12).all()
assert main['BE'].between(2562,2567).all()
assert len(main)==main[['BE','M','province']].drop_duplicates().shape[0]
assert main[['avg_rain_mm','tons']].notna().all().all()
print(f'PASS: main={len(main)} rows; provinces={main.province.nunique()}; HRDI={len(hrdi)} rows')
for p,y,m in [('ขอนแก่น',2567,7),('เชียงใหม่',2566,1)]:
 d=main[(main.province==p)&(main.BE==y)&(main.M==m)]
 print(p,y,m,'rows:',len(d),'rain:',d.avg_rain_mm.tolist(),'tons:',d.tons.tolist())
print('Warning: official provenance of tons remains unverified')
