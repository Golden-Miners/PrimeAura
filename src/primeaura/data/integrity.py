from collections import Counter, defaultdict
from datetime import datetime, timedelta

from .models import OHLCVBar

EXPECTED_MINUTES = {"M1":1,"M5":5,"M15":15,"M30":30,"H1":60,"H4":240,"D1":1440}

def _session_contains(ts: datetime, sessions: dict | None) -> bool:
    if not sessions: return False
    seconds=ts.hour*3600+ts.minute*60+ts.second
    weekday=(ts.weekday()+1)%7
    for session in sessions.get(weekday,[]):
        start,end=session["from"],session["to"]
        if start<=end and start<=seconds<=end: return True
        if start>end and (seconds>=start or seconds<=end): return True
    return False

def _gap_is_session_closed(start,end,expected,sessions):
    cursor=start+expected; checked=0
    while cursor<end:
        if _session_contains(cursor,sessions): return False
        cursor+=expected; checked+=1
    return checked>0

def _recurring_gap_keys(ordered,expected):
    gaps=defaultdict(list)
    for a,b in zip(ordered,ordered[1:]):
        if a.timestamp.date()==b.timestamp.date() and b.timestamp-a.timestamp>expected:
            key=(a.timestamp.strftime("%H:%M"),b.timestamp.strftime("%H:%M"))
            gaps[key].append((a.timestamp,b.timestamp))
    return gaps

def validate_bars(bars,sessions=None):
    if not bars: return {"valid":False,"status":"FAIL","bar_count":0,"issues":["no_bars"],"warnings":[]}
    issues=[]; warnings=[]; ordered=sorted(bars,key=lambda b:b.timestamp); timestamps=[b.timestamp for b in ordered]
    duplicates=[ts for ts,count in Counter(timestamps).items() if count>1]
    if duplicates: issues.append(f"duplicate_timestamps:{len(duplicates)}")
    if any(a.timestamp>=b.timestamp for a,b in zip(bars,bars[1:])): issues.append("timestamps_not_strictly_increasing")
    for bar in ordered:
        if bar.timestamp.tzinfo is None or bar.timestamp.utcoffset() is None: issues.append(f"naive_timestamp:{bar.timestamp.isoformat()}")
        if bar.volume is not None and bar.volume<0: issues.append(f"negative_volume:{bar.timestamp.isoformat()}")
        if not (bar.low<=bar.open<=bar.high and bar.low<=bar.close<=bar.high): issues.append(f"invalid_ohlc:{bar.timestamp.isoformat()}")
        if bar.low>bar.high: issues.append(f"low_above_high:{bar.timestamp.isoformat()}")
    timeframe=ordered[0].timeframe; minutes=EXPECTED_MINUTES.get(timeframe)
    if minutes:
        expected=timedelta(minutes=minutes); recurring=_recurring_gap_keys(ordered,expected)
        for a,b in zip(ordered,ordered[1:]):
            delta=b.timestamp-a.timestamp
            if delta<=expected: continue
            if sessions and _gap_is_session_closed(a.timestamp,b.timestamp,expected,sessions):
                warnings.append(f"session_boundary_gap:{a.timestamp.isoformat()}->{b.timestamp.isoformat()}")
            elif a.timestamp.date()!=b.timestamp.date():
                warnings.append(f"cross_day_gap_unverified:{a.timestamp.isoformat()}->{b.timestamp.isoformat()}")
            else:
                key=(a.timestamp.strftime("%H:%M"),b.timestamp.strftime("%H:%M"))
                occurrences=recurring.get(key,[])
                if len(occurrences)>=2:
                    warnings.append(f"recurring_session_gap:{a.timestamp.isoformat()}->{b.timestamp.isoformat()}:{len(occurrences)}_occurrences")
                else:
                    issues.append(f"time_gap:{a.timestamp.isoformat()}->{b.timestamp.isoformat()}")
    return {"valid":not issues,"status":"FAIL" if issues else ("WARNING" if warnings else "PASS"),"bar_count":len(bars),"timeframe":timeframe,"first_timestamp":timestamps[0],"last_timestamp":timestamps[-1],"issues":issues,"warnings":warnings}

def validate_multitimeframe(bars_by_tf,sessions_by_tf=None):
    sessions_by_tf=sessions_by_tf or {}
    reports={tf:validate_bars(bars,sessions_by_tf.get(tf)) for tf,bars in bars_by_tf.items()}
    issues={tf:r["issues"] for tf,r in reports.items() if r["issues"]}
    warnings={tf:r["warnings"] for tf,r in reports.items() if r["warnings"]}
    return {"valid":not issues,"status":"FAIL" if issues else ("WARNING" if warnings else "PASS"),"timeframes":reports,"issues":issues,"warnings":warnings}
