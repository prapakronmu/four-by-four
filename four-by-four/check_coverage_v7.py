"""Audit actual province/year/month coverage without generating fake values."""
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parent
panel=pd.read_csv(ROOT/'data/balanced_panel_BE2562-2567.csv')
provinces=pd.read_csv(ROOT/'data/thailand_77_provinces.csv')['province'].tolist()
years=sorted(panel.BE.unique())
months=list(range(1,13))
assert len(provinces)==77 and len(set(provinces))==77
assert set(panel.province).issubset(provinces), 'ชื่อจังหวัดในข้อมูลหลักไม่ตรงกับรายการ 77 จังหวัด'
assert not panel.duplicated(['province','BE','M']).any(),'พบคีย์ข้อมูลซ้ำ'
expected=len(provinces)*len(years)*len(months)
allkeys=pd.MultiIndex.from_product([provinces,years,months],names=['province','BE','M'])
observed=pd.MultiIndex.from_frame(panel[['province','BE','M']])
missing=allkeys.difference(observed)
coverage=pd.DataFrame({'province':provinces}).merge(panel.groupby('province',as_index=False).size().rename(columns={'size':'observed_rows'}),on='province',how='left')
coverage['observed_rows']=coverage.observed_rows.fillna(0).astype(int)
coverage['expected_rows']=len(years)*len(months)
coverage['missing_rows']=coverage.expected_rows-coverage.observed_rows
coverage['status']=coverage.missing_rows.map(lambda m:'ครบ' if m==0 else ('ไม่มีข้อมูล' if m==len(years)*len(months) else 'บางส่วน'))
coverage.to_csv(ROOT/'data/coverage_77_provinces_audit.csv',index=False,encoding='utf-8-sig')
print('รายการที่คาดหวัง',expected,'รายการที่มี',len(observed),'รายการที่ขาด',len(missing))
print('จังหวัดครบ',sum(coverage.status=='ครบ'),'จังหวัดไม่มีข้อมูล',sum(coverage.status=='ไม่มีข้อมูล'))
print('จังหวัดที่ยังไม่มีข้อมูล:',', '.join(coverage.loc[coverage.status=='ไม่มีข้อมูล','province']))
