import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import pandas as pd, numpy as np

plt.rcParams.update({'font.family':'serif','font.serif':['Liberation Serif','TeX Gyre Termes','Nimbus Roman','DejaVu Serif'],'font.size':10,'axes.edgecolor':'#1F4E79','axes.linewidth':0.8,'figure.dpi':300,'savefig.dpi':300,'savefig.bbox':'tight'})
BLUE='#1F4E79'; LBLUE='#4472C4'; GRAY='#8A8A8A'; RED='#9E2A2B'; GREEN='#2E6E3A'
FIG='/downloads/exp41-package/figures/'

# ---------- F1 pipeline diagram ----------
fig,ax=plt.subplots(figsize=(7.2,4.6)); ax.set_xlim(0,10); ax.set_ylim(0,10); ax.axis('off')
def box(x,y,w,h,text,fc='#EAF1F8',ec=BLUE,fs=8.2,tc='black'):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.09',fc=fc,ec=ec,lw=1.2))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=fs,color=tc)
def arr(x1,y1,x2,y2,c=BLUE):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=13,color=c,lw=1.3))
box(0.3,7.9,2.6,1.5,'DrugComb v1.4\nZenodo 18449193\n3 files, MD5 verified')
box(3.7,7.9,2.6,1.5,'Four-study cohort\n7,442,556 rows\n406,749 blocks')
box(7.1,7.9,2.6,1.5,'Unit conversion\nconc to uM\n(block-level)')
arr(2.9,8.65,3.7,8.65); arr(6.3,8.65,7.1,8.65)
box(7.1,5.5,2.6,1.5,'Missing-dose and\nsame-drug exclusion\n(7 same-drug blocks)')
arr(8.4,7.9,8.4,7.0)
box(3.7,5.5,2.6,1.5,'Hill monotherapy fits\nsynergy==1.0.0\nE0 = 1.0, E=(100-I)/100')
arr(8.4,5.5,7.6,5.5); 
box(0.3,5.5,2.6,1.5,'ZIP per block\nZIP v1.0.0, no clip,\nno winsorization')
arr(3.7,6.25,2.9,6.25)
box(0.3,3.0,4.4,1.6,'LOCKED WHOLE-BLOCK RANGE GATE (A-2):\nany E outside [0,1] excludes the whole block\n406,650 of 406,749 blocks excluded',fc='#F5E9E9',ec=RED,fs=8.4)
arr(1.6,5.5,1.6,4.6)
box(0.3,0.6,2.6,1.5,'Retained: 91 blocks\n(all Mathews)\n19 triplets (remnant)')
arr(1.6,3.0,1.6,2.1)
box(5.4,0.6,4.3,1.5,'ERM / DANN training and locked gates\nNOT REACHED - no viable source cohort,\nno ALMANAC target (models_trained = 0)',fc='#EFEFEF',ec=GRAY,fs=8.4)
arr(4.7,2.9,6.2,2.1)
ax.text(5.0,9.8,'F1. Locked DOC-1-044 pipeline with preregistration checkpoints',ha='center',fontsize=9.5,color=BLUE,weight='bold')
for x,t in [(1.6,'L0'),(5.0,'A-1'),(8.4,'A-2')]:
    ax.text(x,9.55,t,ha='center',fontsize=7.5,color=BLUE)
ax.plot([1.6],[9.45],marker='v',color=BLUE,ms=5); ax.plot([5.0],[9.45],marker='v',color=BLUE,ms=5); ax.plot([8.4],[9.45],marker='v',color=BLUE,ms=5)
plt.savefig(FIG+'F1-pipeline.png'); plt.close()

# ---------- F2 cohort attrition ----------
stages=['Selected\n(4 studies)','Range-excluded\nE outside [0,1]','Same-drug\nexcluded','Hill-fit\nfailure','Included\nblocks']
vals=[406749,406650,7,1,91]
fig,ax=plt.subplots(figsize=(6.6,3.4))
cols=[LBLUE,RED,GRAY,GRAY,GREEN]
b=ax.bar(range(5),vals,color=cols,edgecolor=BLUE,linewidth=0.8,width=0.62)
ax.set_yscale('log'); ax.set_ylim(0.5,1.2e6)
for i,v in enumerate(vals): ax.text(i,v*1.35,f'{v:,}',ha='center',fontsize=9,color='black')
ax.set_xticks(range(5)); ax.set_xticklabels(stages,fontsize=8)
ax.set_ylabel('Blocks (log scale)')
ax.set_title('F2. Cohort attrition under the locked A-2 preprocessing rules',color=BLUE,fontsize=10,weight='bold')
ax.spines[['top','right']].set_visible(False)
ax.text(0.99,0.03,'Range exclusions by study: ALMANAC 311,604; O\'Neil 92,208; FORCINA 1,818; Mathews 1,020',transform=ax.transAxes,ha='right',fontsize=7.2,color=GRAY)
plt.savefig(FIG+'F2-attrition.png'); plt.close()

# ---------- F3 remnant ZIP distribution ----------
bz=pd.read_csv('/downloads/exp41/outputs/block_zip.csv')
fig,ax=plt.subplots(figsize=(6.4,3.2))
ax.hist(bz['zip_native'],bins=18,color=LBLUE,edgecolor=BLUE,linewidth=0.7)
ax.axvline(bz['zip_native'].mean(),color=RED,ls='--',lw=1.2,label=f"mean = {bz['zip_native'].mean():.2f}")
ax.set_xlabel('Per-block ZIP (native DrugComb percentage points)')
ax.set_ylabel('Blocks')
ax.legend(fontsize=8,frameon=False)
ax.set_title('F3. ZIP distribution of the 91 retained blocks (preprocessing remnant, not a scientific subgroup)',color=BLUE,fontsize=9.5,weight='bold')
ax.spines[['top','right']].set_visible(False)
plt.savefig(FIG+'F3-remnant-zip.png'); plt.close()

# ---------- F4 gate panel ----------
gates=['DANN ALMANAC Spearman\n(threshold >= 0.30)','DANN minus ERM Spearman\n(threshold >= 0.05)','Paired bootstrap 95% CI\nlower bound (> 0)','DANN MAE / ERM MAE\n(<= 1.05)']
fig,ax=plt.subplots(figsize=(6.6,3.0))
y=np.arange(4)[::-1]
ax.barh(y,[1,1,1,1],color='#EFEFEF',edgecolor=GRAY,hatch='//',height=0.55)
for yi in y: ax.text(0.5,yi,'NOT EVALUABLE',ha='center',va='center',fontsize=10,color=GRAY,weight='bold')
ax.set_yticks(y); ax.set_yticklabels(gates,fontsize=8.5)
ax.set_xticks([]); ax.set_xlim(0,1)
ax.set_title('F4. Locked gate outcome panel - no model trained, no metric computable',color=BLUE,fontsize=10,weight='bold')
ax.spines[['top','right','bottom']].set_visible(False)
plt.savefig(FIG+'F4-gates.png'); plt.close()

# ---------- F5 exclusion diagnostics ----------
ba=pd.read_csv('/downloads/exp41/outputs/block_audit.csv')
fig,(a1,a2)=plt.subplots(1,2,figsize=(7.2,3.1))
exc=ba[ba.status=='excluded']
reasons=exc.reason.value_counts()
labels=['E outside [0,1]\n(whole-block)','Same-drug','Hill-fit failure']
vals=[reasons.get('effect_outside_0_1',0),reasons.get('same_drug',0),reasons.get('Residuals are not finite in the initial point.',0)]
a1.bar(range(3),vals,color=[RED,GRAY,GRAY],edgecolor=BLUE,linewidth=0.8,width=0.55)
a1.set_yscale('log'); a1.set_ylim(0.5,2e6)
for i,v in enumerate(vals): a1.text(i,v*1.4,f'{v:,}',ha='center',fontsize=8.5)
a1.set_xticks(range(3)); a1.set_xticklabels(labels,fontsize=8); a1.set_ylabel('Blocks (log scale)')
a1.set_title('(a) Exclusion reasons',color=BLUE,fontsize=9.5)
studies=['ALMANAC',"O'Neil",'FORCINA','Mathews']
sel=[ba[ba.study==s].shape[0] for s in studies]
inc=[ba[(ba.study==s)&(ba.status=='included')].shape[0] for s in studies]
x=np.arange(4); w=0.38
a2.bar(x-w/2,sel,w,color=LBLUE,edgecolor=BLUE,label='selected')
a2.bar(x+w/2,[max(v,0.6) for v in inc],w,color=GREEN,edgecolor=BLUE,label='included')
a2.set_yscale('log'); a2.set_ylim(0.5,2e6)
for i,v in enumerate(sel): a2.text(i-w/2,v*1.3,f'{v:,}',ha='center',fontsize=7.4)
for i,v in enumerate(inc): a2.text(i+w/2,max(v,0.6)*1.5,f'{v:,}',ha='center',fontsize=7.4)
a2.set_xticks(x); a2.set_xticklabels(studies,fontsize=8); a2.legend(fontsize=7.5,frameon=False)
a2.set_title('(b) Selected vs included by study',color=BLUE,fontsize=9.5)
for a in (a1,a2): a.spines[['top','right']].set_visible(False)
fig.suptitle('F5. Exclusion diagnostics across 406,749 blocks',color=BLUE,fontsize=10,weight='bold',y=1.02)
plt.savefig(FIG+'F5-exclusions.png'); plt.close()

# ---------- F8 tool worked example ----------
fig,ax=plt.subplots(figsize=(7.2,3.4)); ax.set_xlim(0,10); ax.set_ylim(0,10); ax.axis('off')
def tbox(x,y,w,h,text,fc='#EAF1F8',ec=BLUE,fs=8.2):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.09',fc=fc,ec=ec,lw=1.2))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=fs)
tbox(0.2,5.6,2.7,2.6,'INPUT\ndrugcomb_data_v1.4.csv\n(2.0 GB, streamed in chunks,\nconstant memory)')
tbox(3.5,5.6,3.0,2.6,'LOCKED A-2 AUDITOR\npreprocess_zip.py\nunit conversion, block build,\nHill fits, ZIP, range gate')
tbox(7.1,6.9,2.7,1.6,'block_audit.csv\n406,749 rows,\nper-block disposition')
tbox(7.1,4.9,2.7,1.6,'metrics.json verdict\nINVALID_NOT_EVALUABLE\nmodels_trained = 0')
ax.add_patch(FancyArrowPatch((2.9,6.9),(3.5,6.9),arrowstyle='-|>',mutation_scale=13,color=BLUE,lw=1.3))
ax.add_patch(FancyArrowPatch((6.5,7.4),(7.1,7.7),arrowstyle='-|>',mutation_scale=13,color=BLUE,lw=1.3))
ax.add_patch(FancyArrowPatch((6.5,6.4),(7.1,5.7),arrowstyle='-|>',mutation_scale=13,color=BLUE,lw=1.3))
tbox(0.2,1.0,9.6,2.6,'WORKED EXAMPLE (this experiment): 7,442,556 rows / 406,749 blocks streamed in ~14 min on a ~2 GB-RAM-constrained worker\nOutput: 406,650 range exclusions, 7 same-drug, 1 Hill-fit failure, 91 included blocks, 19 triplets\nMachine-readable verdict for the ledger; identical code reruns any future DOC against the same locked rules',fc='#F5F5EF',ec=GREEN,fs=8.2)
ax.text(5.0,9.3,'F8. The shipped tool: streaming locked-rule ZIP preprocessor and cohort auditor',ha='center',fontsize=9.5,color=BLUE,weight='bold')
plt.savefig(FIG+'F8-tool.png'); plt.close()
print('figures done'); import os; [print(f, os.path.getsize(FIG+f)) for f in sorted(os.listdir(FIG))]
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'serif','font.serif':['Liberation Serif','DejaVu Serif'],'font.size':10,'axes.edgecolor':'#1F4E79','axes.linewidth':0.8,'figure.dpi':300,'savefig.dpi':300,'savefig.bbox':'tight'})
BLUE='#1F4E79'; LBLUE='#4472C4'; GRAY='#8A8A8A'; RED='#9E2A2B'; GREEN='#2E6E3A'
stages=['Selected\n(4 studies)','Range-excluded\nE outside [0,1]','Same-drug\nexcluded','Hill-fit\nfailure','Included\nblocks']
vals=[406749,406650,7,1,91]
fig,ax=plt.subplots(figsize=(6.6,3.5))
cols=[LBLUE,RED,GRAY,GRAY,GREEN]
ax.bar(range(5),vals,color=cols,edgecolor=BLUE,linewidth=0.8,width=0.62)
ax.set_yscale('log'); ax.set_ylim(0.5,3e6)
for i,v in enumerate(vals): ax.text(i,v*1.35,f'{v:,}',ha='center',fontsize=9)
ax.set_xticks(range(5)); ax.set_xticklabels(stages,fontsize=8)
ax.set_ylabel('Blocks (log scale)')
ax.set_title('F2. Cohort attrition under the locked A-2 preprocessing rules',color=BLUE,fontsize=10,weight='bold')
ax.spines[['top','right']].set_visible(False)
ax.text(0.5,0.55,"Range exclusions by study: ALMANAC 311,604; O'Neil 92,208;\nFORCINA 1,818; Mathews 1,020",transform=ax.transAxes,ha='center',fontsize=7.6,color='#333333',bbox=dict(boxstyle='round,pad=0.35',fc='white',ec='#BBBBBB',lw=0.6))
plt.savefig('/downloads/exp41-package/figures/F2-attrition.png'); plt.close()
print('ok')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
plt.rcParams.update({'font.family':'serif','font.serif':['Liberation Serif','DejaVu Serif'],'figure.dpi':300,'savefig.dpi':300,'savefig.bbox':'tight'})
BLUE='#1F4E79'; GREEN='#2E6E3A'
fig,ax=plt.subplots(figsize=(7.4,3.6)); ax.set_xlim(0,10); ax.set_ylim(0,10); ax.axis('off')
def tbox(x,y,w,h,text,fc='#EAF1F8',ec=BLUE,fs=8.2):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.09',fc=fc,ec=ec,lw=1.2))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=fs)
tbox(0.2,5.9,2.7,2.6,'INPUT\ndrugcomb_data_v1.4.csv\n(2.0 GB, streamed in chunks,\nconstant memory)')
tbox(3.5,5.9,3.0,2.6,'LOCKED A-2 AUDITOR\npreprocess_zip.py\nunit conversion, block build,\nHill fits, ZIP, range gate')
tbox(7.1,7.2,2.7,1.6,'block_audit.csv\n406,749 rows,\nper-block disposition')
tbox(7.1,5.2,2.7,1.6,'metrics.json verdict\nINVALID_NOT_EVALUABLE\nmodels_trained = 0')
ax.add_patch(FancyArrowPatch((2.9,7.2),(3.5,7.2),arrowstyle='-|>',mutation_scale=13,color=BLUE,lw=1.3))
ax.add_patch(FancyArrowPatch((6.5,7.7),(7.1,8.0),arrowstyle='-|>',mutation_scale=13,color=BLUE,lw=1.3))
ax.add_patch(FancyArrowPatch((6.5,6.7),(7.1,6.0),arrowstyle='-|>',mutation_scale=13,color=BLUE,lw=1.3))
tbox(0.2,0.8,9.6,3.2,'WORKED EXAMPLE (this experiment):\n7,442,556 rows / 406,749 blocks streamed in ~14 min on a ~2 GB-RAM-constrained worker.\nOutput: 406,650 range exclusions, 7 same-drug, 1 Hill-fit failure, 91 included blocks, 19 triplets.\nMachine-readable verdict for the ledger; identical code reruns any future DOC against the same locked rules.',fc='#F5F5EF',ec=GREEN,fs=8.0)
ax.text(5.0,9.5,'F8. The shipped tool: streaming locked-rule ZIP preprocessor and cohort auditor',ha='center',fontsize=9.5,color=BLUE,weight='bold')
plt.savefig('/downloads/exp41-package/figures/F8-tool.png'); plt.close()
print('ok')
