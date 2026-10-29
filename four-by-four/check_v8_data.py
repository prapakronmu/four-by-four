from pathlib import Path
import pandas as pd
root=Path(__file__).resolve().parent
master=pd.read_csv(root/'data/thailand_77_provinces.csv')
loc=pd.read_csv(root/'data/province_approx_locations.csv')
data=pd.read_csv(root/'data/balanced_panel_BE2562-2567.csv')
assert len(master)==77 and master.province.nunique()==77
assert len(loc)==77 and loc.province.nunique()==77
assert set(master.province)==set(loc.province)
assert loc.lat.between(5,21).all() and loc.lon.between(97,106).all()
assert set(data.province)<=set(master.province)
assert data[['province','BE','M']].duplicated().sum()==0
assert data.M.between(1,12).all()
assert data.BE.between(2562,2567).all()
expected=len(data.province.unique())*len(data.BE.unique())*12
print('Master:',len(master),'Approximate province points:',len(loc))
print('Existing panel records:',len(data),'expected within existing province scope:',expected)
print('Provinces with records:',data.province.nunique(),'Without records:',77-data.province.nunique())
print('Duplicate keys:',data[['province','BE','M']].duplicated().sum())
print('Missing numeric:',data[['avg_rain_mm','tons']].isna().sum().to_dict())
print('Source value verification remains separate: see README_V8_TH.md')
