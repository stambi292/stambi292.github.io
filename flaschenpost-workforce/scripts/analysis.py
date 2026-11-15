"""Workforce analytics prototype: attrition KPIs and a retention-risk model on IBM's public HR sample (fictional, 1,470 employees)."""
import pandas as pd, numpy as np, json, pathlib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score
root=pathlib.Path(__file__).resolve().parents[1]
df=pd.read_csv(root/'data/ibm_hr_attrition.csv',encoding='utf-8-sig')
df['left']=(df.Attrition=='Yes').astype(int)
def seg(col,order=None,labels=None):
    g=df.groupby(col,observed=True).left.agg(['mean','count'])
    if order is not None: g=g.reindex(order)
    return [{'k':(labels or {}).get(k,str(k)),'rate':round(float(r['mean'])*100,1),'n':int(r['count'])} for k,r in g.iterrows()]
df['Tenure']=pd.cut(df.YearsAtCompany,[-1,0,2,5,10,40],labels=['Under 1 year','1–2 years','3–5 years','6–10 years','Over 10 years'])
df['Income']=pd.qcut(df.MonthlyIncome,4,labels=['Lowest quarter','2nd quarter','3rd quarter','Highest quarter'])
df['Distance']=pd.cut(df.DistanceFromHome,[0,5,10,20,30],labels=['Up to 5','6–10','11–20','21–29'])
df['Travel']=df.BusinessTravel.map({'Non-Travel':'None','Travel_Rarely':'Rarely','Travel_Frequently':'Often'})
segs={'overtime':seg('OverTime',['No','Yes'],{'No':'No overtime','Yes':'Overtime'}),
 'tenure':seg('Tenure'),'income':seg('Income'),'level':seg('JobLevel',[1,2,3,4,5],{1:'Level 1 (entry)',2:'Level 2',3:'Level 3',4:'Level 4',5:'Level 5'}),
 'wlb':seg('WorkLifeBalance',[1,2,3,4],{1:'1 Bad',2:'2 Good',3:'3 Better',4:'4 Best'}),
 'distance':seg('Distance'),'travel':seg('Travel',['None','Rarely','Often']),
 'role':sorted(seg('JobRole'),key=lambda d:-d['rate'])}
num=['DistanceFromHome','MonthlyIncome','YearsAtCompany','YearsInCurrentRole','YearsSinceLastPromotion','TotalWorkingYears','NumCompaniesWorked','JobLevel','JobSatisfaction','EnvironmentSatisfaction','WorkLifeBalance','JobInvolvement','StockOptionLevel','TrainingTimesLastYear','PercentSalaryHike']
cat=['OverTime','BusinessTravel','Department','JobRole']  # age, gender and marital status left out on purpose
pre=ColumnTransformer([('n',StandardScaler(),num),('c',OneHotEncoder(handle_unknown='ignore'),cat)])
model=make_pipeline(pre,LogisticRegression(max_iter=2000,C=0.5))
cv=StratifiedKFold(5,shuffle=True,random_state=7)
p=cross_val_predict(model,df[num+cat],df.left,cv=cv,method='predict_proba')[:,1]
auc=roc_auc_score(df.left,p)
df['p']=p; df['dec']=pd.qcut(df.p.rank(method='first'),10,labels=False)
dec=df.groupby('dec').left.agg(['mean','sum','count']).iloc[::-1]
deciles=[{'d':int(10-i),'rate':round(float(r['mean'])*100,1),'leavers':int(r['sum']),'n':int(r['count'])} for i,(k,r) in enumerate(dec.iterrows())]
top=df[df.dec>=8]; capture=top.left.sum()/df.left.sum()
model.fit(df[num+cat],df.left)
names=num+list(model[0].named_transformers_['c'].get_feature_names_out(cat))
coef=pd.Series(model[-1].coef_[0],index=names)
drivers=[{'f':k,'c':round(float(v),2)} for k,v in coef.sort_values(key=abs,ascending=False).head(10).items()]
emp=[{'ot':r.OverTime=='Yes','ten':int(r.YearsAtCompany),'inc':int(r.MonthlyIncome),'lvl':int(r.JobLevel),'role':r.JobRole,'left':int(r.left),'p':round(float(r.p),3)} for r in df.itertuples()]
out={'n':len(df),'leavers':int(df.left.sum()),'rate':round(df.left.mean()*100,1),'auc':round(auc,3),'top20_capture':round(capture*100,1),
 'top20_rate':round(top.left.mean()*100,1),'median_income':int(df.MonthlyIncome.median()),'segs':segs,'deciles':deciles,'drivers':drivers,'emp':emp,
 'checks':{'rows':len(df),'unique_ids':bool(df.EmployeeNumber.is_unique),'missing':int(df.isna().sum().sum()),'std_hours':sorted(map(int,df.StandardHours.unique()))}}
(root/'data/workforce.json').write_text(json.dumps(out,ensure_ascii=False))
print({k:v for k,v in out.items() if k not in('emp','segs','deciles')}); print(deciles[:3])
