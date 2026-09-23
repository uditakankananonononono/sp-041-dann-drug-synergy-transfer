import pandas as pd, numpy as np, json, os, warnings, hashlib, traceback
from synergy.combination import ZIP
from synergy.single import Hill
from collections import Counter
P='raw/drugcomb_data_v1.4.csv'; OUT='outputs'
os.makedirs(OUT,exist_ok=True)
MAP={'almanac':'ALMANAC','oneil':"O\'Neil",'mathews':'Mathews','forcina':'FORCINA'}
cols=['block_id','conc_r','conc_c','inhibition','drug_row','drug_col','cell_line_name','drug_row_cid','drug_col_cid','cellosaurus_accession','study_name','conc_r_unit','conc_c_unit']
parts=[]
for c in pd.read_csv(P,usecols=cols,chunksize=500000,low_memory=False):
 key=c.study_name.astype('string').str.strip().str.casefold(); m=key.isin(MAP)
 c=c[m].copy(); c['study']=key[m].map(MAP); parts.append(c)
df=pd.concat(parts,ignore_index=True); del parts
# canonical entity fields; identifier maps are already carried in raw table. Require finite unique IDs.
audit=Counter(rows_selected=len(df),blocks_selected=df.block_id.nunique())
results=[]; blocklogs=[]
for bid,g in df.groupby('block_id',sort=False):
 rec={'block_id':str(bid),'study':str(g.study.iloc[0]),'n_rows':len(g),'status':'eligible'}
 try:
  if g.study.nunique()!=1: raise ValueError('multi_study')
  if not ((g.conc_r_unit=='uM').all() and (g.conc_c_unit=='uM').all()): raise ValueError('unit_missing_unparseable')
  num=g[['conc_r','conc_c','inhibition']].apply(pd.to_numeric,errors='coerce')
  combo=(num.conc_r>0)&(num.conc_c>0)
  if num.loc[combo,'inhibition'].isna().any(): raise ValueError('missing_combo_inhibition')
  E=(100-num.inhibition)/100
  if (~np.isfinite(E)).any(): raise ValueError('nonfinite_effect')
  if ((E<0)|(E>1)).any(): raise ValueError('effect_outside_0_1')
  # own mono rows: d2=0 for row drug, d1=0 for col drug; require >=4 usable positive dose points each
  m1=(num.conc_r>0)&(num.conc_c==0); m2=(num.conc_c>0)&(num.conc_r==0)
  if m1.sum()<4 or m2.sum()<4: raise ValueError('insufficient_monotherapy_points')
  d1m=num.loc[m1,'conc_r'].to_numpy(float); e1=E[m1].to_numpy(float)
  d2m=num.loc[m2,'conc_c'].to_numpy(float); e2=E[m2].to_numpy(float)
  h1=Hill(E0=1.0); h1.fit(d1m,e1,use_jacobian=True)
  h2=Hill(E0=1.0); h2.fit(d2m,e2,use_jacobian=True)
  if not (h1.is_specified and h2.is_specified): raise ValueError('hill_fit_failed')
  # compute ZIP across assayed combo points only with prefitted monotherapy models
  d1=num.loc[combo,'conc_r'].to_numpy(float); d2=num.loc[combo,'conc_c'].to_numpy(float); ec=E[combo].to_numpy(float)
  if len(ec)==0: raise ValueError('no_combo_points')
  z=ZIP(use_jacobian=True,drug1_model=h1,drug2_model=h2)
  delta=z.fit(d1,d2,ec,use_jacobian=True)
  finite=np.isfinite(delta)
  if not finite.any(): raise ValueError('no_finite_zip')
  zip_native=float(np.mean(100*delta[finite]))
  dr=g.drug_row_cid.dropna().astype(str).unique(); dc=g.drug_col_cid.dropna().astype(str).unique(); cl=g.cellosaurus_accession.dropna().astype(str).unique()
  if len(dr)!=1 or len(dc)!=1 or len(cl)!=1: raise ValueError('ambiguous_identifiers')
  if dr[0]==dc[0]: raise ValueError('same_drug')
  a,b=sorted([dr[0],dc[0]])
  results.append({'block_id':str(bid),'study':rec['study'],'drug_a_cid':a,'drug_b_cid':b,'cell_id':cl[0],'zip_native':zip_native,'n_combo':int(combo.sum())})
  rec.update(n_combo=int(combo.sum()),zip_native=zip_native,status='included')
  audit['included_blocks']+=1
 except Exception as e:
  reason=str(e); rec['status']='excluded'; rec['reason']=reason; audit['excluded_'+reason]+=1
 blocklogs.append(rec)
 if len(blocklogs)%10000==0: print(len(blocklogs),dict(audit),flush=True)
pd.DataFrame(results).to_csv(f'{OUT}/block_zip.csv',index=False)
pd.DataFrame(blocklogs).to_csv(f'{OUT}/block_audit.csv',index=False)
# locked within-study mean per triplet
r=pd.DataFrame(results)
if len(r):
 t=r.groupby(['study','drug_a_cid','drug_b_cid','cell_id'],as_index=False).agg(zip=('zip_native','mean'),n_blocks=('block_id','nunique'))
 t.to_csv(f'{OUT}/triplets.csv',index=False)
json.dump(dict(audit),open(f'{OUT}/preprocess-audit.json','w'),indent=2)
print('FINAL',dict(audit),'triplets',len(t) if len(r) else 0)
