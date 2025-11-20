import csv
import time
from scapy.all import sniff
from collections import defaultdict
import matplotlib.pyplot as plt
import argparse
from pathlib import Path
import json

try:
    # for clustering prompts
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    _SKLEARN_AVAILABLE = True
except Exception:
    _SKLEARN_AVAILABLE = False

records = []

def packet_callback(pkt):
    try:
        ts = float(pkt.time)
        size = len(pkt)
        dst = pkt['IP'].dst if pkt.haslayer('IP') else ''
        records.append({'time': ts, 'size': size, 'dst': dst})
    except Exception:
        pass

def run_capture(duration: int, host: str = None, out_csv: str = 'artifacts/traffic.csv'):
    filt = 'tcp'
    if host:
        filt += f' and host {host}'
    print(f"Starting capture for {duration}s with filter '{filt}'")
    sniff(timeout=duration, prn=packet_callback, filter=filt)
    # write csv
    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['time','size','dst'])
        w.writeheader()
        for r in records:
            w.writerow(r)
    print(f"Saved {len(records)} records to {out_csv}")
    return out_csv

def plot_csv(csv_path: str, out_png: str = 'artifacts/traffic_plot.png'):
    import pandas as pd
    df = pd.read_csv(csv_path)
    df['rel_time'] = df['time'] - df['time'].min()
    # aggregate by 0.1s buckets
    df['bucket'] = (df['rel_time'] / 0.1).astype(int)
    agg = df.groupby('bucket').size()
    plt.figure(figsize=(10,4))
    plt.plot(agg.index * 0.1, agg.values)
    plt.xlabel('seconds')
    plt.ylabel('packets')
    plt.title('Packet rate over time')
    Path(out_png).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png)
    print(f"Wrote plot to {out_png}")
    return out_png

def cluster_prompts(logs, k=3):
    texts = [ (l.get('prompt','') + ' ' + (l.get('response') or '')) for l in logs ]
    if not _SKLEARN_AVAILABLE or len(texts) < 2:
        # fallback: put all into single cluster
        return [0]*len(texts)
    vec = TfidfVectorizer(max_features=500)
    X = vec.fit_transform(texts)
    model = KMeans(n_clusters=min(k, max(1, len(texts))))
    labels = model.fit_predict(X)
    return labels

def correlate_with_logs(csv_path: str, logs_path: str = None, sqlite_db: str = None, out_png: str = 'artifacts/traffic_correlation.png'):
    """Correlate packet captures with logs. Provide either `logs_path` (JSON) or `sqlite_db` to read Storage.
    Creates a scatter plot of log time vs total bytes in the next `window_s` seconds, colored by cluster.
    """
    import pandas as pd
    # load packets
    df = pd.read_csv(csv_path)
    df['time'] = df['time'].astype(float)
    # load logs
    if logs_path:
        logs = json.loads(Path(logs_path).read_text())
        # if wrapped (like runner output), try to find logs key
        if isinstance(logs, dict) and 'logs' in logs:
            logs = logs['logs']
    elif sqlite_db:
        # lazy import Storage to read logs
        from ..storage import Storage
        s = Storage(sqlite_db)
        logs = s.query_logs(10000)
    else:
        raise ValueError('Provide logs_path or sqlite_db')

    # ensure logs have created_at
    times = [float(l.get('created_at', time.time())) for l in logs]
    # cluster prompts
    labels = cluster_prompts(logs, k=4)

    window_s = 2.0
    # for each log, compute packet bytes in [t, t+window_s]
    pkt_times = df['time'].values
    pkt_sizes = df['size'].values
    results = []
    for idx, t in enumerate(times):
        mask = (pkt_times >= t) & (pkt_times <= t + window_s)
        total_bytes = pkt_sizes[mask].sum() if mask.any() else 0
        results.append({'time': t, 'total_bytes': int(total_bytes), 'cluster': int(labels[idx]) if idx < len(labels) else 0})

    rdf = pd.DataFrame(results)
    if rdf.empty:
        print('No correlation results')
        return None

    # normalize times to relative
    rdf['rel_time'] = rdf['time'] - rdf['time'].min()
    plt.figure(figsize=(10,4))
    # scatter by cluster
    for cl in sorted(rdf['cluster'].unique()):
        sub = rdf[rdf['cluster'] == cl]
        plt.scatter(sub['rel_time'], sub['total_bytes'], label=f'cluster {cl}', alpha=0.7)
    plt.xlabel('seconds (relative)')
    plt.ylabel('bytes in next 2s')
    plt.legend()
    plt.title('Packet bytes following prompts, colored by prompt cluster')
    Path(out_png).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png)
    print(f'Wrote correlation plot to {out_png}')
    return out_png


def main():
    parser = argparse.ArgumentParser(description='Side-channel traffic analyzer')
    parser.add_argument('--capture', action='store_true', help='Capture packets for duration')
    parser.add_argument('--duration', '-d', type=int, default=20)
    parser.add_argument('--host', help='Host to filter')
    parser.add_argument('--csv', help='Use existing csv instead of capture')
    parser.add_argument('--logs', help='Path to logs JSON file to correlate')
    parser.add_argument('--sqlite', help='Path to sqlite DB to read logs')
    parser.add_argument('--out', default='artifacts/traffic_plot.png')
    args = parser.parse_args()
    csvp = args.csv
    if args.capture:
        csvp = run_capture(args.duration, host=args.host, out_csv='artifacts/traffic.csv')
        plot_csv(csvp, out_png=args.out)
    if args.logs or args.sqlite:
        correlate_with_logs(csvp or 'artifacts/traffic.csv', logs_path=args.logs, sqlite_db=args.sqlite, out_png='artifacts/traffic_correlation.png')


if __name__ == '__main__':
    main()
