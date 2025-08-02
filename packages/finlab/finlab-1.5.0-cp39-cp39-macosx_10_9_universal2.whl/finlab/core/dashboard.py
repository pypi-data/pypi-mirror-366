import numpy as np
import random
import string
import html
import json

def default_serialize(obj):
    if isinstance(obj, np.int64):
        return int(obj)
    raise TypeError(
        f"Object of type '{obj.__class__.__name__}' is not JSON serializable")

def read_resource_file(package, resource):
    try:
        # For Python 3.9 and later
        from importlib.resources import files
        resource_path = files(package) / resource
        with open(resource_path, encoding='utf-8') as file:
            return file.read()
    except ImportError:
        try:
            # For Python 3.7 and 3.8
            from importlib.resources import path
            with path(package, resource) as resource_path:
                with open(resource_path, encoding='utf-8') as file:
                    return file.read()
        except ImportError:
            # Fallback for older Python versions without importlib.resources
            import pkg_resources
            resource_path = pkg_resources.resource_filename(package, resource)
            with open(resource_path, encoding='utf-8') as file:
                return file.read()
    raise ImportError("No compatible importlib.resources implementation found.")


def generate_html(report, with_iframe=False):
    """
    Display a report in an interactive dashboard.
    
    Args:
        report: The Report object containing backtest results
    
    Returns:
        None
    """
    j = report.to_json()
    j['trades'] = json.loads(report.trades.tail(500).to_json(orient='records'))
    json_str = json.dumps(j, default=default_serialize)
    position_str = json.dumps(report.position_info2(), default=default_serialize)

    style_str = read_resource_file('finlab.core', 'style.css')
    ctxt = read_resource_file('finlab.core', 'everything.js')

    # Process JavaScript
    lines = ctxt.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('export'):
            break
    ctxt = '\n'.join(lines[:i])

    http_txt = """<!DOCTYPE html>
<html lang="en" class="bg-base-200">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Component Example</title>
</head>
<body class="bg-base-200">
    <script>const reportJson = """+json_str+"""</script>
    <script>const positionJson = """+position_str+"""</script>
    <script type="module">
        """+ctxt+"""
        console.log('create report')
        console.log('reportPosition', positionJson)
        const report = new Report(reportJson.timestamps, reportJson.strategy, reportJson.benchmark, reportJson.trades, reportJson.metrics)
        console.log('create report finish', report)
        report.metrics.backtest.startDate = new Date(report.metrics.backtest.startDate)
        report.metrics.backtest.endDate = new Date(report.metrics.backtest.endDate)
        report.metrics.backtest.updateDate = new Date(report.metrics.backtest.updateDate)
        report.metrics.backtest.nextTradingDate = new Date(report.metrics.backtest.nextTradingDate)
        report.metrics.backtest.livePerformanceStart = new Date(report.metrics.backtest.livePerformanceStart)


            function convertTrade(trade) {
                return Object.fromEntries(
                    Object.entries(trade).map(([key, val]) => {
                    let newkey = key;
                    let newval = val;

            switch (key) {
                case 'bmfe':
                break;
                case 'entry_date':
                newkey = 'entry';
                newval = val ? new Date(val) : null;
                break;
                case 'entry_index':
                newkey = 'entryIndex';
                break;
                case 'entry_sig_date':
                newkey = 'entrySig';
                newval = val ? new Date(val) : null;
                break;
                case 'exit_date':
                newkey = 'exit';
                newval = val ? new Date(val) : null;
                break;
                case 'exit_index':
                newkey = 'exitIndex';
                break;
                case 'exit_sig_date':
                newkey = 'exitSig';
                newval = val ? new Date(val) : null;
                break;
                case 'gmfe':
                case 'mae':
                case 'mdd':
                case 'pdays':
                case 'period':
                case 'position':
                case 'return':
                break;
                case 'stock_id':
                newkey = 'stockId';
                break;
                case 'trade_price@entry_date':
                newkey = 'entryPrice';
                break;
                case 'trade_price@exit_date':
                newkey = 'exitPrice';
                break;
            }
            return [newkey, newval];
            })
        );

        }

        let theme = 'dark'

        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            console.log('User prefers dark theme');
        } else {
            console.log('User prefers light theme or has no preference');
            theme = 'dark' // default to dark
        }
        theme = localStorage.getItem('theme') || theme

        document.documentElement.setAttribute('data-theme', theme);
        report.trades = report.trades.map(convertTrade)

        console.log(report)

        const div = document.getElementById('panel')

        const analytic = document.querySelector('strategy-analytic');
        analytic.report = report;
        analytic.reportPosition = positionJson;
        analytic.browser = true;
        analytic.theme = theme;
        analytic.lang = 'zh-tw';
        analytic.webcomponent = true;

        function updateIconColor() {
            const theme = analytic.theme
            const textColor = theme === 'light' ? 'black' : 'white';
            const elements = document.querySelectorAll('.fill-current');
            elements.forEach(element => {
                element.style.color = textColor
            });
            
        }

        updateIconColor()
    </script>
<div id="panel" style="z-index: 2;position:relative;max-width:960px;margin: 0 auto;padding: 32px;padding-top:0;border-radius: 16px">
    <strategy-analytic></strategy-analytic>
</div>
</body>

<style>"""+style_str+"""
</style>
</html>"""

    if not with_iframe:
        return http_txt

    iframe_id = 'iframe_' + ''.join(random.choice(string.ascii_letters) for _ in range(10))
    iframe_code = """
        <iframe id=\""""+iframe_id+"""\" srcdoc=\""""+html.escape(http_txt)+"""\" style="height: 600px;width: 100%;max-width:800px; border: none;border-radius:20px"></iframe>
        <script>
            // set iframe_id into local storage
            localStorage.setItem('iframe_id', 'IFRAME');
            localStorage.setItem('tab', 'reset');
            window.addEventListener('message', function (event) {
                const data = event.data;

                // not message event
                if (!data.frameHeight || !data.tab) {
                    return;
                }

                // not change tab
                const prevTab = localStorage.getItem('tab');

                if (prevTab === data.tab) {
                    return;
                }

                const iframe_id = localStorage.getItem('iframe_id');
                const iframe = document.querySelector('#'+iframe_id);

                iframe.style.height = (data.frameHeight + 1) + 'px';
                iframe.setAttribute('scrolling', 'no');

                localStorage.setItem('tab', data.tab);
            });
        </script>
    """.replace('IFRAME', iframe_id)

    return iframe_code

