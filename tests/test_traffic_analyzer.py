from pathlib import Path
import json
from src.ai_test_lab.traffic.analyzer import plot_csv, correlate_with_logs

def test_plot_csv_and_correlate(tmp_path):
    # create fake csv
    csv = tmp_path / 'traffic.csv'
    csv.write_text('time,size,dst\n1000,500,1.1.1.1\n1000.5,200,1.1.1.1\n1002,150,1.1.1.1\n')
    png = tmp_path / 'plot.png'
    out = plot_csv(str(csv), out_png=str(png))
    assert Path(out).exists()

    # create fake logs json
    logs = tmp_path / 'logs.json'
    logs.write_text(json.dumps([{"created_at": 1000, "prompt":"hello"}, {"created_at":1002, "prompt":"secret ssn 123-45-6789"}]))
    out2 = tmp_path / 'corr.png'
    res = correlate_with_logs(str(csv), logs_path=str(logs), out_png=str(out2))
    assert Path(res).exists()
