import pandas as pd, numpy as np, json, os, warnings, csv
from synergy.combination import ZIP
from synergy.single import Hill
from collections import Counter
P='raw/drugcomb_data_v1.4.csv'; OUT='outputs'; os.makedirs(OUT,exist_ok=True)
MAP={'almanac':'ALMANAC','oneil':"O'Neil",'mathews':'Mathews','forcina':'FORCINA'}
cols=['block_id','conc_r','conc_c','inhibition','drug_row_cid','drug_col_cid','cellosaurus_accession','study_name','conc_r_unit','conc_c_unit']
audit=Counter(); seen=set(); last_id=None; carry=None
bout=open(f'{OUT}/block_zip.csv','w',newline=''); bw=csv.DictWriter(bout,fieldnames=['block_id','study','drug_a_cid','drug_b_cid','cell_id','zip_native','n_combo']); bw.writeheader()
aout=open(f'{OUT}/block_audit.csv','w',newline=''); aw=csv.DictWriter(aout,fieldnames=['block_id','study','n_rows','status','reason','n_combo','zip_native']); aw.writeheader()
def process(g):
 bid=g.block_id.iloc[0]; study=g.study.iloc[0]; rec={'block_id':str(bid),'study':study,'n_rows':len(g),'status':'excluded','reason':'','n_combo':'','zip_native':''}; audit['blocks_selected']+=1; audit['rows_selected']+=len(g)
 try:
  if bid in seen: raise ValueError('noncontiguous_duplicate_block')
  seen.add(bid)
  if g.study.nunique()!=1: raise ValueError('multi_study')
  if not ((g.conc_r_unit=='uM').all() and (g.conc_c_unit=='uM').all()): raise ValueError('unit_missing_unparseable')
  num=g[['conc_r','conc_c','inhibition']].apply(pd.to_numeric,errors='coerce'); combo=(num.conc_r>0)&(num.conc_c>0)
  if num.loc[combo,'inhibition'].isna().any(): raise ValueError('missing_combo_inhibition')
  E=(100-num.inhibition)/100
  if (~np.isfinite(E)).any(): raise ValueError('nonfinite_effect')
  if ((E<0)|(E>1)).any(): raise ValueError('effect_outside_0_1')
  m1=(num.conc_r>0)&(num.conc_c==0); m2=(num.conc_c>0)&(num.conc_r==0)
  if m1.sum()<4 or m2.sum()<4: raise ValueError('insufficient_monotherapy_points')
  h1=Hill(E0=1.0); h1.fit(num.loc[m1,'conc_r'].to_numpy(float),E[m1].to_numpy(float),use_jacobian=True)
  h2=Hill(E0=1.0); h2.fit(num.loc[m2,'conc_c'].to_numpy(float),E[m2].to_numpy(float),use_jacobian=True)
  if not (h1.is_specified and h2.is_specified): raise ValueError('hill_fit_failed')
  d1=num.loc[combo,'conc_r'].to_numpy(float); d2=num.loc[combo,'conc_c'].to_numpy(float); ec=E[combo].to_numpy(float)
  if not len(ec): raise ValueError('no_combo_points')
  delta=ZIP(use_jacobian=True,drug1_model=h1,drug2_model=h2).fit(d1,d2,ec,use_jacobian=True); finite=np.isfinite(delta)
  if not finite.any(): raise ValueError('no_finite_zip')
  z=float(np.mean(100*delta[finite])); dr=g.drug_row_cid.dropna().astype(str).unique(); dc=g.drug_col_cid.dropna().astype(str).unique(); cl=g.cellosaurus_accession.dropna().astype(str).unique()
  if len(dr)!=1 or len(dc)!=1 or len(cl)!=1: raise ValueError('ambiguous_identifiers')
  if dr[0]==dc[0]: raise ValueError('same_drug')
  a,b=sorted([dr[0],dc[0]]); bw.writerow({'block_id':bid,'study':study,'drug_a_cid':a,'drug_b_cid':b,'cell_id':cl[0],'zip_native':z,'n_combo':int(combo.sum())}); rec.update(status='included',n_combo=int(combo.sum()),zip_native=z); audit['included_blocks']+=1
 except Exception as e: rec['reason']=str(e); audit['excluded_'+str(e)]+=1
 aw.writerow(rec)
for ci,c in enumerate(pd.read_csv(P,usecols=cols,chunksize=200000,low_memory=False)):
 key=c.study_name.astype('string').str.strip().str.casefold(); c=c[key.isin(MAP)].copy(); c['study']=key[key.isin(MAP)].map(MAP)
 if carry is not None and len(carry): c=pd.concat([carry,c],ignore_index=True)
 if not len(c): continue
 lid=c.block_id.iloc[-1]; complete=c[c.block_id!=lid]; carry=c[c.block_id==lid].copy()
 for _,g in complete.groupby('block_id',sort=False): process(g)
 if ci%10==0: print('chunk',ci,'blocks',audit['blocks_selected'],'included',audit['included_blocks'],flush=True)
if carry is not None and len(carry): process(carry)
bout.close(); aout.close()
r=pd.read_csv(f'{OUT}/block_zip.csv'); t=r.groupby(['study','drug_a_cid','drug_b_cid','cell_id'],as_index=False).agg(zip=('zip_native','mean'),n_blocks=('block_id','nunique')); t.to_csv(f'{OUT}/triplets.csv',index=False)
json.dump(dict(audit),open(f'{OUT}/preprocess-audit.json','w'),indent=2); print('FINAL',dict(audit),'triplets',len(t),flush=True)
