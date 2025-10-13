#!/usr/bin/env python3
import os, sys, csv, json, zipfile, io, datetime as dt, requests
GHTOKEN=os.getenv("GH_TOKEN"); ORG=os.getenv("ORG"); REPO=os.getenv("REPO")
if not (GHTOKEN and ORG and REPO): sys.exit("Defina GH_TOKEN, ORG e REPO")

S=requests.Session(); S.headers.update({"Authorization":f"Bearer {GHTOKEN}","Accept":"application/vnd.github+json"})
API="https://api.github.com"

def list_all(url, params=None):
    out=[]; page=1
    while True:
        p=dict(params or {}); p.update(per_page=100, page=page)
        r=S.get(url, params=p); r.raise_for_status()
        batch=r.json()
        if not batch: break
        out+=batch; page+=1
    return out

def prs_all():
    return list_all(f"{API}/repos/{ORG}/{REPO}/pulls", {"state":"all"})

def runs_for_pr(num):
    runs=list_all(f"{API}/repos/{ORG}/{REPO}/actions/runs", {"event":"pull_request"})
    return [r for r in runs for pr in r.get("pull_requests",[]) if pr.get("number")==num]

def artifacts():
    return list_all(f"{API}/repos/{ORG}/{REPO}/actions/artifacts")

def dl_zip(aid):
    r=S.get(f"{API}/repos/{ORG}/{REPO}/actions/artifacts/{aid}/zip"); r.raise_for_status(); return r.content

def parse_quality(pr_number):
    pref=f"quality-report-pr-{pr_number}"
    for a in artifacts():
        if a.get("name","").startswith(pref) and not a.get("expired"):
            z=zipfile.ZipFile(io.BytesIO(dl_zip(a["id"])))
            eslint_err=None; html_err=None
            for n in z.namelist():
                if n.endswith("eslint.json"):
                    data=json.loads(z.read(n).decode("utf-8") or "[]"); total=0
                    for f in data: total+=len([m for m in f.get("messages",[]) if m.get("severity",2)==2])
                    eslint_err=total
                if n.endswith("htmlvalidate.json"):
                    data=json.loads(z.read(n).decode("utf-8") or "[]"); total=0
                    if isinstance(data, dict) and "results" in data:
                        for res in data["results"]: total+=len(res.get("messages",[]))
                    elif isinstance(data, list):
                        for res in data: total+=len(res.get("messages",[]))
                    html_err=total
            return eslint_err, html_err
    return None, None

def label_week(labels):
    for lb in labels:
        n=(lb["name"] or "").upper().strip()
        if n.startswith("SEM"): return n
    return ""

def label_ia(labels):
    names=[(lb["name"] or "").upper().strip() for lb in labels]
    if "IA:ON" in names: return "ON"
    if "IA:OFF" in names: return "OFF"
    return ""

def changes_requested(num):
    r=S.get(f"{API}/repos/{ORG}/{REPO}/pulls/{num}/reviews"); r.raise_for_status()
    return len([rv for rv in r.json() if (rv.get("state") or "").upper()=="CHANGES_REQUESTED"])

print("pr_number,week,ia,created_at,merged_at,time_to_approve_hours,runs_total,runs_failed,ci_failure_rate,eslint_errors,htmlvalidate_errors,changes_requested")
for pr in prs_all():
    num=pr["number"]; created=pr["created_at"]; merged=pr.get("merged_at") or ""
    week=label_week(pr.get("labels",[])); ia=label_ia(pr.get("labels",[]))
    tta=""
    if merged:
        f=lambda s: dt.datetime.fromisoformat(s.replace("Z","+00:00"))
        tta=round((f(merged)-f(created)).total_seconds()/3600,2)
    runs=runs_for_pr(num); rt=len(runs); rf=len([r for r in runs if r.get("conclusion")=="failure"])
    rate=round((rf/rt)*100,2) if rt else ""
    es, hv = parse_quality(num)
    cr = changes_requested(num)
    print(",".join(map(str,[num,week,ia,created,merged,tta,rt,rf,rate, es if es is not None else "", hv if hv is not None else "", cr])))

