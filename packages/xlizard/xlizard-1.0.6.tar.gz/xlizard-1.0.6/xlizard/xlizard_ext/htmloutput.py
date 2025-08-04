from __future__ import print_function
import sys
import os
import datetime
from combined_metrics import CombinedMetrics
from sourcemonitor_metrics import SourceMonitorMetrics, Config
from sourcemonitor_metrics import FileAnalyzer, Config

def html_output(result, options, *_):
    try:
        from jinja2 import Template
    except ImportError:
        sys.stderr.write(
                "HTML Output depends on jinja2. `pip install jinja2` first")
        sys.exit(2)

    # Get SourceMonitor metrics
    try:
        sm = SourceMonitorMetrics(options.paths[0] if options.paths else '.')
        sm.analyze_directory()
        
        # Create metrics dictionary with normalized paths
        sm_metrics = {}
        for m in sm.get_metrics():
            original_path = m['file_path']
            normalized_path = os.path.normpath(original_path)
            basename = os.path.basename(normalized_path)
            
            sm_metrics[normalized_path] = m
            sm_metrics[basename] = m
            sm_metrics[f"./{normalized_path}"] = m
            sm_metrics[normalized_path.replace('\\', '/')] = m
            
    except Exception as e:
        sys.stderr.write(f"Warning: SourceMonitor metrics not available ({str(e)})\n")
        sm_metrics = {}

    file_list = []
    for source_file in result:
        if source_file and not source_file.filename.endswith('.h'):
            file_key = os.path.normpath(source_file.filename)
            file_metrics = sm_metrics.get(file_key) or sm_metrics.get(os.path.basename(file_key))

            combined = CombinedMetrics(
                source_file,
                file_metrics
            )
            
            dirname = combined.dirname
            source_file_dict = {
                "filename": combined.filename,
                "basename": combined.basename,
                "dirname": dirname,
                "comment_percentage": file_metrics.get('comment_percentage', 0) if file_metrics else 0,
                "max_block_depth": file_metrics.get('max_block_depth', 0) if file_metrics else 0,
                "pointer_operations": file_metrics.get('pointer_operations', 0) if file_metrics else 0,
                "preprocessor_directives": file_metrics.get('preprocessor_directives', 0) if file_metrics else 0,
                "sourcemonitor": file_metrics
            }
            
            func_list = []
            max_complexity = 0
            for source_function in combined.functions:
                if source_function:
                    func_dict = _create_dict(source_function, source_file.filename)  # Передаём путь к файлу
                    if not hasattr(source_function, 'token_count'):
                        func_dict['token_count'] = 0
                    func_list.append(func_dict)
                    # Calculate max complexity for the file
                    if func_dict['cyclomatic_complexity'] > max_complexity:
                        max_complexity = func_dict['cyclomatic_complexity']
            
            source_file_dict["functions"] = func_list
            source_file_dict["max_complexity"] = max_complexity
            source_file_dict["avg_complexity"] = sum(
                func['cyclomatic_complexity'] for func in func_list
            ) / len(func_list) if func_list else 0
            file_list.append(source_file_dict)
    
    # Group files by directories
    dir_groups = {}
    for file in file_list:
        dirname = file['dirname']
        if dirname not in dir_groups:
            dir_groups[dirname] = []
        dir_groups[dirname].append(file)
    
    # Calculate metrics for dashboard
    complexity_data = []
    comment_data = []
    depth_data = []
    pointer_data = []
    directives_data = []
    
    for file in file_list:
        if file['functions']:
            complexity_data.extend([f['cyclomatic_complexity'] for f in file['functions']])
            comment_data.append(file['comment_percentage'])
            depth_data.append(file['max_block_depth'])
            pointer_data.append(file['pointer_operations'])
            directives_data.append(file['preprocessor_directives'])
    
    # Prepare comment distribution data
    comment_ranges = {
        '0-10': sum(1 for p in comment_data if p <= 10),
        '10-20': sum(1 for p in comment_data if 10 < p <= 20),
        '20-30': sum(1 for p in comment_data if 20 < p <= 30),
        '30-40': sum(1 for p in comment_data if 30 < p <= 40),
        '40-50': sum(1 for p in comment_data if 40 < p <= 50),
        '50+': sum(1 for p in comment_data if p > 50)
    }
    
    # Prepare depth vs pointers data
    depth_pointers_data = [
        {'x': f['pointer_operations'], 'y': f['max_block_depth'], 'file': f['basename']} 
        for f in file_list
    ]
    
    # Prepare complexity vs nloc data
    complexity_nloc_data = []
    top_complex_functions = []
    
    for file in file_list:
        for func in file['functions']:
            complexity_nloc_data.append({
                'x': func['nloc'],
                'y': func['cyclomatic_complexity'],
                'function': func['name'],
                'file': file['basename']
            })
            
            top_complex_functions.append({
                'name': func['name'],
                'complexity': func['cyclomatic_complexity'],
                'nloc': func['nloc'],
                'file': file['basename'],
                'filepath': file['filename']
            })
    
    # Get top 5 most complex functions
    top_complex_functions.sort(key=lambda x: -x['complexity'])
    top_complex_functions = top_complex_functions[:5]
    
    # Get files with min/max comments
    files_sorted_by_comments = sorted(file_list, key=lambda x: x['comment_percentage'])
    min_comments_files = files_sorted_by_comments[:5]
    max_comments_files = files_sorted_by_comments[-5:]
    max_comments_files.reverse()
    
    # Calculate code/comment/empty ratio
    total_lines = 0
    total_comments = 0
    total_empty = 0
    
    for file in file_list:
        if file.get('sourcemonitor'):
            total_lines += file['sourcemonitor'].get('lines_of_code', 0)
            total_comments += file['sourcemonitor'].get('comment_lines', 0)
            total_empty += file['sourcemonitor'].get('blank_lines', 0)
    
    code_ratio = {
        'code': total_lines,
        'comments': total_comments,
        'empty': total_empty
    }
    
    # Calculate directory complexity stats
    dir_complexity_stats = []
    for dirname, files in dir_groups.items():
        avg_complexity = sum(f['avg_complexity'] for f in files) / len(files) if files else 0
        dir_complexity_stats.append({
            'name': dirname,
            'avg_complexity': avg_complexity,
            'file_count': len(files)
        })
    
    # Sort directories by complexity
    dir_complexity_stats.sort(key=lambda x: -x['avg_complexity'])
    
    # Prepare dashboard data
    dashboard_data = {
        'complexity_distribution': {
            'low': sum(1 for c in complexity_data if c <= options.thresholds['cyclomatic_complexity'] * 0.5),
            'medium': sum(1 for c in complexity_data if options.thresholds['cyclomatic_complexity'] * 0.5 < c <= options.thresholds['cyclomatic_complexity']),
            'high': sum(1 for c in complexity_data if c > options.thresholds['cyclomatic_complexity'])
        },
        'avg_metrics': {
            'complexity': sum(complexity_data)/len(complexity_data) if complexity_data else 0,
            'comments': sum(comment_data)/len(comment_data) if comment_data else 0,
            'depth': sum(depth_data)/len(depth_data) if depth_data else 0,
            'pointers': sum(pointer_data)/len(pointer_data) if pointer_data else 0,
            'directives': sum(directives_data)/len(directives_data) if directives_data else 0
        },
        'comment_ranges': comment_ranges,
        'depth_pointers_data': depth_pointers_data,
        'complexity_nloc_data': complexity_nloc_data,
        'thresholds': options.thresholds
    }
    
    # Calculate metrics for files view
    total_complexity = 0
    total_functions = 0
    problem_files = 0
    total_comments = 0
    total_depth = 0
    total_pointers = 0
    total_directives = 0
    
    directory_stats = []
    
    for dirname, files in dir_groups.items():
        dir_complexity = 0
        dir_max_complexity = 0
        dir_functions = 0
        dir_problem_functions = 0
        dir_comments = 0
        dir_depth = 0
        dir_pointers = 0
        dir_directives = 0
        
        for file in files:
            file['problem_functions'] = sum(
                1 for func in file['functions'] 
                if func['cyclomatic_complexity'] > options.thresholds['cyclomatic_complexity']
            )
            file['max_complexity'] = max(
                (func['cyclomatic_complexity'] for func in file['functions']),
                default=0
            )
            file['avg_complexity'] = sum(
                func['cyclomatic_complexity'] for func in file['functions']
            ) / len(file['functions']) if file['functions'] else 0
            
            dir_complexity += file['avg_complexity']
            dir_max_complexity = max(dir_max_complexity, file['max_complexity'])
            dir_functions += len(file['functions'])
            dir_problem_functions += file['problem_functions']
            dir_comments += file['comment_percentage']
            dir_depth += file['max_block_depth']
            dir_pointers += file['pointer_operations']
            dir_directives += file['preprocessor_directives']
            
            total_complexity += file['avg_complexity']
            total_functions += len(file['functions'])
            total_comments += file['comment_percentage']
            total_depth += file['max_block_depth']
            total_pointers += file['pointer_operations']
            total_directives += file['preprocessor_directives']
            
            if file['max_complexity'] > options.thresholds['cyclomatic_complexity']:
                problem_files += 1
        
        directory_stats.append({
            'name': dirname,
            'max_complexity': dir_max_complexity,
            'avg_complexity': dir_complexity / len(files) if files else 0,
            'total_functions': dir_functions,
            'problem_functions': dir_problem_functions,
            'file_count': len(files),
            'avg_comments': dir_comments / len(files) if files else 0,
            'avg_depth': dir_depth / len(files) if files else 0,
            'avg_pointers': dir_pointers / len(files) if files else 0,
            'avg_directives': dir_directives / len(files) if files else 0
        })
    
    avg_complexity = total_complexity / len(file_list) if file_list else 0
    avg_comments = total_comments / len(file_list) if file_list else 0
    avg_depth = total_depth / len(file_list) if file_list else 0
    avg_pointers = total_pointers / len(file_list) if file_list else 0
    avg_directives = total_directives / len(file_list) if file_list else 0
    
    # Combine thresholds
    full_thresholds = {
        'cyclomatic_complexity': options.thresholds.get('cyclomatic_complexity', 15),
        'nloc': options.thresholds.get('nloc', 100),
        'comment_percentage': options.thresholds.get('comment_percentage', Config.THRESHOLDS['comment_percentage']),
        'max_block_depth': options.thresholds.get('max_block_depth', Config.THRESHOLDS['max_block_depth']),
        'pointer_operations': options.thresholds.get('pointer_operations', Config.THRESHOLDS['pointer_operations']),
        'preprocessor_directives': options.thresholds.get('preprocessor_directives', Config.THRESHOLDS['preprocessor_directives']),
        'function_count': 20,
        'token_count': 50
    }
    
    output = Template(TEMPLATE).render(
            title='xlizard + SourceMonitor code report',
            date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            thresholds=full_thresholds, 
            dir_groups=dir_groups,
            total_files=len(file_list),
            problem_files=problem_files,
            avg_complexity=round(avg_complexity, 2),
            avg_comments=round(avg_comments, 2),
            avg_depth=round(avg_depth, 2),
            avg_pointers=round(avg_pointers, 2),
            avg_directives=round(avg_directives, 2),
            total_functions=total_functions,
            directory_stats=sorted(directory_stats, key=lambda x: -x['max_complexity']),
            dashboard_data=dashboard_data,
            top_complex_functions=top_complex_functions,
            min_comments_files=min_comments_files,
            max_comments_files=max_comments_files,
            code_ratio=code_ratio,
            dir_complexity_stats=dir_complexity_stats)
    print(output)
    return 0

def _get_function_code(file_path, start_line, end_line):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return ''.join(lines[start_line-1:end_line])
    except Exception:
        return ""
    
def _create_dict(source_function, file_path):
    func_dict = source_function.__dict__
    # Получаем код функции
    func_code = _get_function_code(file_path, source_function.start_line, source_function.end_line)
    
    if func_code:
        # Удаляем параметр is_function, так как метод его не принимает
        func_dict['max_depth'] = FileAnalyzer._calculate_block_depth(func_code)
    else:
        func_dict['max_depth'] = 0
    return func_dict

TEMPLATE = '''<!DOCTYPE HTML PUBLIC
"-//W3C//DTD HTML 4.01 Transitional//EN"
"http://www.w3.org/TR/html4/loose.dtd">
<html>
 <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ title }}</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');
        
        :root {
            --primary: #2563eb;
            --primary-light: #3b82f6;
            --secondary: #10b981;
            --error: #ef4444;
            --dark: #1e293b;
            --darker: #0f172a;
            --light: #f8fafc;
            --gray: #94a3b8;
            --border: #e2e8f0;
            --transition-time: 0.5s;
        }
        
        [data-theme="dark"] {
            --primary: #3b82f6;
            --primary-light: #60a5fa;
            --secondary: #10b981;
            --error: #ef4444;
            --dark: #e2e8f0;
            --darker: #f8fafc;
            --light: #1e293b;
            --gray: #64748b;
            --border: #334155;
        }
        
        body {
            font-family: 'IBM Plex Sans', sans-serif;
            background-color: var(--light);
            color: var(--dark);
            margin: 0;
            padding: 0;
            line-height: 1.6;
            transition: background-color var(--transition-time) ease, 
                        color var(--transition-time) ease;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            transition: all var(--transition-time) ease;
        }
        
        .report-header {
            text-align: center;
            margin-bottom: 2.5rem;
            position: relative;
        }
        
        .report-title {
            font-size: 2rem;
            font-weight: 600;
            color: var(--darker);
            margin-bottom: 0.5rem;
        }
        
        .report-meta {
            display: flex;
            justify-content: center;
            margin-bottom: 1.5rem;
            color: var(--gray);
            font-size: 0.9rem;
            gap: 1rem;
            flex-wrap: wrap;
        }
        
        .theme-toggle-container {
            position: absolute;
            top: 0;
            right: 0;
        }
        
        .theme-toggle {
            background: var(--primary);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }
        
        .theme-toggle:hover {
            background: var(--primary-light);
            transform: scale(1.05);
        }
        
        .search-container {
            position: relative;
            max-width: 100%;
            width: 800px;
            margin: 0 auto 1.5rem;
            padding: 0 15px;
            box-sizing: border-box;
        }
        
        .search-box {
            width: 100%;
            padding: 0.75rem 2.5rem 0.75rem 1rem;
            border: 1px solid var(--border);
            border-radius: 25px;
            font-family: inherit;
            background-color: var(--light);
            color: var(--dark);
            transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            box-sizing: border-box;
        }
        
        .search-box:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2);
            transform: scale(1.02);
        }
        
        .search-box::placeholder {
            color: var(--gray);
            opacity: 1;
        }
        
        .search-icon {
            position: absolute;
            right: 25px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--gray);
            transition: all 0.3s ease;
            pointer-events: none;
        }
        
        .search-box:focus + .search-icon {
            color: var(--primary);
            transform: translateY(-50%) scale(1.1);
        }
        
        .clear-search {
            position: absolute;
            right: 25px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--gray);
            cursor: pointer;
            display: none;
        }
        
        .clear-search:hover {
            color: var(--error);
        }
        
        .tab-nav {
            display: flex;
            border-bottom: 1px solid var(--border);
            margin-bottom: 1.5rem;
            position: relative;
            overflow-x: auto;
            white-space: nowrap;
            -ms-overflow-style: none;
            scrollbar-width: none;
        }
        
        .tab-nav::-webkit-scrollbar {
            display: none;
        }
        
        .tab-button {
            padding: 0.75rem 1.5rem;
            cursor: pointer;
            position: relative;
            font-weight: 500;
            color: var(--gray);
            transition: all 0.3s ease;
            border: none;
            background: none;
        }
        
        .tab-button.active {
            color: var(--primary);
        }
        
        .tab-indicator {
            position: absolute;
            bottom: -1px;
            left: 0;
            height: 3px;
            background-color: var(--primary);
            border-radius: 3px 3px 0 0;
            transition: all 0.3s ease;
        }
        
        .tab-content {
            display: none;
            animation: fadeIn 0.5s ease;
        }
        
        .tab-content.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .directory-group {
            margin-bottom: 2rem;
            animation: fadeIn 0.5s ease;
        }
        
        .directory-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--border);
        }
        
        .card {
            background: var(--light);
            border-radius: 8px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            margin-bottom: 1.5rem;
            overflow: hidden;
            border: 1px solid var(--border);
            transition: all 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        
        .file-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 1.5rem;
            background-color: var(--light);
            border-bottom: 1px solid var(--border);
            font-weight: 500;
            color: var(--darker);
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .file-header:hover {
            background-color: rgba(59, 130, 246, 0.05);
        }
        
        .file-title {
            display: flex;
            align-items: center;
            min-width: 0;
            overflow: hidden;
        }
        
        .file-icon {
            flex-shrink: 0;
            width: 24px;
            height: 24px;
            margin-right: 0.75rem;
            background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%232563eb"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6z"/></svg>') no-repeat center;
            transition: all 0.3s ease;
        }
        
        .file-metrics {
            display: flex;
            gap: 0.5rem;
            flex-shrink: 0;
            margin-left: 1rem;
            flex-wrap: wrap;
        }
        
        .metric-badge {
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            background: var(--light);
            border: 1px solid var(--border);
            transition: all 0.3s ease;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }
        
        .metric-badge.safe {
            background: #dcfce7;
            color: #166534;
            border-color: #22c55e;
        }
        
        .metric-badge.warning {
            background: #fef3c7;
            color: #92400e;
            border-color: #f59e0b;
        }
        
        .metric-badge.danger {
            background: #fee2e2;
            color: #991b1b;
            border-color: #ef4444;
        }
        
        .tooltip-icon {
            cursor: pointer;
            width: 16px;
            height: 16px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            background-color: var(--gray);
            color: white;
            font-size: 0.7rem;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .tooltip-icon:hover {
            background-color: var(--primary);
        }
        
        .custom-tooltip {
            position: absolute;
            z-index: 100;
            background: var(--darker);
            color: var(--light);
            padding: 0.75rem 1rem;
            border-radius: 6px;
            font-size: 0.85rem;
            max-width: 300px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            opacity: 0;
            transform: translateY(10px);
            transition: all 0.3s ease;
            pointer-events: none;
        }
        
        .custom-tooltip.visible {
            opacity: 1;
            transform: translateY(0);
        }
        
        .file-content {
            display: none;
            padding: 1rem;
            overflow: hidden;
            transition: all 0.3s ease, max-height 0.3s ease;
            max-height: 0;
        }
        
        .file-content.expanded {
            display: block;
            max-height: 5000px;
            animation: fadeIn 0.3s ease;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th {
            text-align: left;
            padding: 1rem 1.5rem;
            font-weight: 500;
            color: var(--gray);
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            background-color: var(--light);
            border-bottom: 1px solid var(--border);
            position: sticky;
            top: 0;
        }
        
        td {
            padding: 1rem 1.5rem;
            border-bottom: 1px solid var(--border);
            transition: all 0.3s ease;
        }
        
        .threshold-label {
            display: block;
            font-size: 0.75rem;
            color: var(--gray);
            margin-top: 0.25rem;
            font-weight: normal;
        }
        
        tr:hover td {
            background-color: rgba(59, 130, 246, 0.05);
        }
        
        tr:last-child td {
            border-bottom: none;
        }
        
        .function-name {
            font-family: 'IBM Plex Mono', monospace;
            color: var(--darker);
            font-size: 0.95rem;
            word-break: break-word;
        }
        
        .greater-value {
            color: var(--error);
            font-weight: 500;
        }
        
        .lesser-value {
            color: var(--secondary);
        }
        
        .highlight {
            background-color: rgba(255, 255, 0, 0.3);
            padding: 0 2px;
            border-radius: 2px;
        }
        
        .footer {
            text-align: center;
            margin-top: 3rem;
            color: var(--gray);
            font-size: 0.85rem;
        }
        
        .footer a {
            color: var(--primary);
            text-decoration: none;
        }
        
        .badge {
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.75rem;
            background-color: var(--primary-light);
            color: white;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        
        .metrics-overview {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .metric-overview-card {
            background: var(--light);
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border: 1px solid var(--border);
            transition: all 0.3s ease;
            text-align: center;
        }
        
        .metric-overview-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        
        .metric-overview-value {
            font-size: 1.8rem;
            font-weight: 600;
            margin: 0.5rem 0;
            color: var(--darker);
        }
        
        .metric-overview-label {
            font-size: 0.9rem;
            color: var(--gray);
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .chart-container {
            background: var(--light);
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border: 1px solid var(--border);
            transition: all 0.3s ease;
        }
        
        .chart-container:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        
        .chart-title {
            font-size: 1.1rem;
            font-weight: 500;
            margin-bottom: 1rem;
            color: var(--darker);
        }
        
        .chart-wrapper {
            position: relative;
            height: 300px;
            width: 100%;
        }
        
        .advanced-metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .stats-table {
            width: 100%;
            margin-bottom: 1.5rem;
        }
        
        .stats-table th {
            text-align: left;
            padding: 0.75rem;
            background-color: rgba(59, 130, 246, 0.1);
        }
        
        .stats-table td {
            padding: 0.75rem;
            border-bottom: 1px solid var(--border);
        }
        
        .stats-table tr:last-child td {
            border-bottom: none;
        }
        
        .heatmap-container {
            width: 100%;
            height: 400px;
        }
        
        .hotspot-badge {
            background-color: #fee2e2;
            color: #991b1b;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            display: inline-block;
            margin-right: 0.5rem;
            margin-bottom: 0.5rem;
        }
        
        .hotspot-container {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 1.5rem;
        }
        
        html {
            scrollbar-gutter: stable;
        }
        
        @media (max-width: 1440px) {
            .container {
                padding: 1.5rem;
            }
            
            .report-title {
                font-size: 1.75rem;
            }
        }
        
        @media (max-width: 1280px) {
            .container {
                padding: 1.25rem;
            }
            
            .report-title {
                font-size: 1.5rem;
            }
            
            .file-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 0.5rem;
            }
            
            .file-metrics {
                margin-left: 0;
                width: 100%;
                justify-content: flex-start;
            }
        }
        
        @media (max-width: 1024px) {
            .container {
                padding: 1rem;
            }
            
            .report-title {
                font-size: 1.4rem;
            }
            
            .tab-nav {
                font-size: 0.9rem;
            }
            
            .tab-button {
                padding: 0.5rem 1rem;
            }
            
            th, td {
                padding: 0.75rem 1rem;
            }
        }
        
        @media (max-width: 900px) {
            .directory-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 0.5rem;
            }
            
            .dashboard-grid, .advanced-metrics-grid {
                grid-template-columns: 1fr;
            }
        }
        
        @media (max-width: 800px) {
            .report-title {
                font-size: 1.3rem;
                margin-top: 1.5rem;
            }
            
            .theme-toggle-container {
                position: static;
                margin-bottom: 1rem;
            }
            
            .theme-toggle {
                width: 100%;
                justify-content: center;
            }
            
            .function-name {
                font-size: 0.85rem;
            }
            
            th, td {
                padding: 0.5rem 0.75rem;
                font-size: 0.8rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="report-header">
            <div class="theme-toggle-container">
                <button class="theme-toggle" id="themeToggle">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
                    </svg>
                    Theme
                </button>
            </div>
            <h1 class="report-title">{{ title }}</h1>
        </div>
        
        <div class="report-meta">
            <div>Generated on: {{ date }}</div>
            <div class="badge">Total files: {{ total_files }}</div>
        </div>
        
        <div class="search-container">
            <input type="text" class="search-box" placeholder="Search files..." id="searchInput">
            <div class="search-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="11" cy="11" r="8"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
            </div>
            <div class="clear-search" id="clearSearch">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </div>
        </div>
        
        <div class="tab-nav">
            <button class="tab-button active" data-tab="dashboardTab">Dashboard</button>
            <button class="tab-button" data-tab="filesTab">Files</button>
            <button class="tab-button" data-tab="advancedTab">Advanced Metrics</button>
            <div class="tab-indicator"></div>
        </div>
        
        <!-- Dashboard Tab -->
        <div class="tab-content active" id="dashboardTab">
            <div class="metrics-overview">
                <div class="metric-overview-card">
                    <div class="metric-overview-label">Total Files</div>
                    <div class="metric-overview-value">{{ total_files }}</div>
                </div>
                <div class="metric-overview-card">
                    <div class="metric-overview-label">Problem Files</div>
                    <div class="metric-overview-value">{{ problem_files }}</div>
                </div>
                <div class="metric-overview-card">
                    <div class="metric-overview-label">Avg Complexity</div>
                    <div class="metric-overview-value">{{ avg_complexity|round(1) }}</div>
                </div>
                <div class="metric-overview-card">
                    <div class="metric-overview-label">Avg Comments</div>
                    <div class="metric-overview-value">{{ avg_comments|round(1) }}%</div>
                </div>
            </div>
            
            <div class="dashboard-grid">
                <div class="chart-container">
                    <div class="chart-title">Complexity Distribution</div>
                    <div class="chart-wrapper">
                        <canvas id="complexityChart"></canvas>
                    </div>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Metrics Comparison</div>
                    <div class="chart-wrapper">
                        <canvas id="metricsChart"></canvas>
                    </div>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Comments Distribution</div>
                    <div class="chart-wrapper">
                        <canvas id="commentsChart"></canvas>
                    </div>
                </div>
                <div class="chart-container">
                    <div class="chart-title">Depth vs Pointers</div>
                    <div class="chart-wrapper">
                        <canvas id="depthPointersChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Files Tab -->
        <div class="tab-content" id="filesTab">
            {% for dirname, files in dir_groups.items() %}
            <div class="directory-group" id="dir-{{ dirname }}">
                <div class="directory-header">
                    <h3>{{ dirname }}</h3>
                    <div>{{ files|length }} files</div>
                </div>
                
                {% for file in files %}
                <div class="card">
                    <div class="file-header" onclick="toggleFile(this)">
                        <div class="file-title">
                            <div class="file-icon"></div>
                            <div>{{ file.basename }}</div>
                        </div>
                        <div class="file-metrics">
                            <div class="metric-badge {% if file.max_complexity <= thresholds['cyclomatic_complexity']*0.5 %}safe{% elif file.max_complexity <= thresholds['cyclomatic_complexity'] %}warning{% else %}danger{% endif %}">
                                Max CC: {{ file.max_complexity }}
                                <div class="tooltip-icon" data-tooltip="Thresholds: ≤{{ (thresholds['cyclomatic_complexity']*0.5)|round }} (safe), ≤{{ thresholds['cyclomatic_complexity'] }} (warning), >{{ thresholds['cyclomatic_complexity'] }} (danger)">?</div>
                            </div>
                            <div class="metric-badge {% if file.functions|length <= thresholds['function_count']*0.5 %}safe{% elif file.functions|length <= thresholds['function_count'] %}warning{% else %}danger{% endif %}">
                                Funcs: {{ file.functions|length }}
                                <div class="tooltip-icon" data-tooltip="Thresholds: ≤{{ (thresholds['function_count']*0.5)|round }} (safe), ≤{{ thresholds['function_count'] }} (warning), >{{ thresholds['function_count'] }} (danger)">?</div>
                            </div>
                            <div class="metric-badge {% if file.comment_percentage >= thresholds['comment_percentage']*1.2 %}safe{% elif file.comment_percentage >= thresholds['comment_percentage']*0.8 %}warning{% else %}danger{% endif %}">
                                Comments: {{ file.comment_percentage|round(1) }}%
                                <div class="tooltip-icon" data-tooltip="Thresholds: ≥{{ (thresholds['comment_percentage']*1.2)|round }}% (safe), ≥{{ (thresholds['comment_percentage']*0.8)|round }}% (warning), <{{ (thresholds['comment_percentage']*0.8)|round }}% (danger)">?</div>
                            </div>
                            <div class="metric-badge {% if file.max_block_depth <= thresholds['max_block_depth']*0.7 %}safe{% elif file.max_block_depth <= thresholds['max_block_depth'] %}warning{% else %}danger{% endif %}">
                                Depth: {{ file.max_block_depth }}
                                <div class="tooltip-icon" data-tooltip="Thresholds: ≤{{ (thresholds['max_block_depth']*0.7)|round }} (safe), ≤{{ thresholds['max_block_depth'] }} (warning), >{{ thresholds['max_block_depth'] }} (danger)">?</div>
                            </div>
                            <div class="metric-badge {% if file.pointer_operations <= thresholds['pointer_operations']*0.5 %}safe{% elif file.pointer_operations <= thresholds['pointer_operations'] %}warning{% else %}danger{% endif %}">
                                Ptr Ops: {{ file.pointer_operations }}
                                <div class="tooltip-icon" data-tooltip="Thresholds: ≤{{ (thresholds['pointer_operations']*0.5)|round }} (safe), ≤{{ thresholds['pointer_operations'] }} (warning), >{{ thresholds['pointer_operations'] }} (danger)">?</div>
                            </div>
                            <div class="metric-badge {% if file.preprocessor_directives <= thresholds['preprocessor_directives']*0.5 %}safe{% elif file.preprocessor_directives <= thresholds['preprocessor_directives'] %}warning{% else %}danger{% endif %}">
                                PP Directives: {{ file.preprocessor_directives }}
                                <div class="tooltip-icon" data-tooltip="Thresholds: ≤{{ (thresholds['preprocessor_directives']*0.5)|round }} (safe), ≤{{ thresholds['preprocessor_directives'] }} (warning), >{{ thresholds['preprocessor_directives'] }} (danger)">?</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="file-content">
            {% if file.functions|length > 0 %}
            <table>
                <thead>
                    <tr>
                        <th>Function</th>
                        <th>
                            CCN <div class="tooltip-icon" data-tooltip="Cyclomatic Complexity Number">?</div>
                            <span class="threshold-label">Threshold: {{ thresholds['cyclomatic_complexity'] }}</span>
                        </th>
                        <th>
                            LOC <div class="tooltip-icon" data-tooltip="Lines of Code">?</div>
                            <span class="threshold-label">Threshold: {{ thresholds['nloc'] }}</span>
                        </th>
                        <th>
                            Tokens <div class="tooltip-icon" data-tooltip="Number of tokens in function">?</div>
                            <span class="threshold-label">Threshold: {{ thresholds['token_count'] }}</span>
                        </th>
                        <th>
                            Depth <div class="tooltip-icon" data-tooltip="Maximum nesting depth">?</div>
                            <span class="threshold-label">Threshold: {{ thresholds['max_block_depth'] }}</span>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {% for func in file.functions %}
                        <tr>
                            <td class="function-name">{{ func.name }}</td>
                            
                            <td class="{% if func.cyclomatic_complexity > thresholds['cyclomatic_complexity'] %}greater-value{% else %}lesser-value{% endif %}">
                                {{ func.cyclomatic_complexity }}
                            </td>
                            
                            <td class="{% if func.nloc > thresholds['nloc'] %}greater-value{% else %}lesser-value{% endif %}">
                                {{ func.nloc }}
                            </td>
                            
                            <td class="{% if func.token_count > thresholds['token_count'] %}greater-value{% else %}lesser-value{% endif %}">
                                {{ func.token_count }}
                            </td>
                            
                            <td class="{% if func.max_depth > thresholds['max_block_depth'] %}greater-value{% else %}lesser-value{% endif %}">
                                {{ func.max_depth }}
                            </td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <div class="no-functions">
                No functions found in this file
            </div>
            {% endif %}
        </div>
                </div>
                {% endfor %}
            </div>
            {% endfor %}
        </div>
        
        <!-- Advanced Metrics Tab -->
        <div class="tab-content" id="advancedTab">
            <div class="advanced-metrics-grid">
                <div class="chart-container">
                    <div class="chart-title">Complexity vs Lines of Code</div>
                    <div class="chart-wrapper">
                        <canvas id="complexityNlocChart"></canvas>
                    </div>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">Code Composition</div>
                    <div class="chart-wrapper">
                        <canvas id="codeCompositionChart"></canvas>
                    </div>
                </div>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">Directory Complexity Heatmap</div>
                <div class="heatmap-container" id="heatmapChart"></div>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">Top 5 Most Complex Functions</div>
                <table class="stats-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Function</th>
                            <th>File</th>
                            <th>Complexity</th>
                            <th>Lines</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for func in top_complex_functions %}
                        <tr>
                            <td>{{ loop.index }}</td>
                            <td>{{ func.name }}</td>
                            <td>{{ func.file }}</td>
                            <td class="greater-value">{{ func.complexity }}</td>
                            <td>{{ func.nloc }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">Files with Lowest Comments</div>
                <table class="stats-table">
                    <thead>
                        <tr>
                            <th>File</th>
                            <th>Comment %</th>
                            <th>Complexity</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for file in min_comments_files %}
                        <tr>
                            <td>{{ file.basename }}</td>
                            <td class="greater-value">{{ file.comment_percentage|round(1) }}%</td>
                            <td>{{ file.max_complexity }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">Files with Highest Comments</div>
                <table class="stats-table">
                    <thead>
                        <tr>
                            <th>File</th>
                            <th>Comment %</th>
                            <th>Complexity</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for file in max_comments_files %}
                        <tr>
                            <td>{{ file.basename }}</td>
                            <td class="lesser-value">{{ file.comment_percentage|round(1) }}%</td>
                            <td>{{ file.max_complexity }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">Average Complexity by Directory</div>
                <table class="stats-table">
                    <thead>
                        <tr>
                            <th>Directory</th>
                            <th>Avg Complexity</th>
                            <th>Files</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for dir in dir_complexity_stats %}
                        <tr>
                            <td>{{ dir.name }}</td>
                            <td class="{% if dir.avg_complexity > thresholds['cyclomatic_complexity'] %}greater-value{% else %}lesser-value{% endif %}">
                                {{ dir.avg_complexity|round(1) }}
                            </td>
                            <td>{{ dir.file_count }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">Code Hotspots (High Complexity + Low Comments)</div>
                <div class="hotspot-container">
                    {% for file in file_list %}
                        {% if file.max_complexity > thresholds['cyclomatic_complexity'] and file.comment_percentage < thresholds['comment_percentage']*0.5 %}
                        <div class="hotspot-badge">
                            {{ file.basename }} (CC: {{ file.max_complexity }}, Comments: {{ file.comment_percentage|round(1) }}%)
                        </div>
                        {% endif %}
                    {% endfor %}
                </div>
            </div>
        </div>
        
        <div class="footer">
            Generated by <a href="http://www.xlizard.ws/" target="_blank">xlizard</a> with SourceMonitor metrics
        </div>
    </div>

    <script>
        // Инициализация при загрузке страницы
        document.addEventListener('DOMContentLoaded', function() {
            // Плавное переключение темы
            document.getElementById('themeToggle').addEventListener('click', function() {
                const isDark = document.body.getAttribute('data-theme') === 'dark';
                
                document.body.style.transition = 'background-color var(--transition-time) ease, color var(--transition-time) ease';
                document.querySelector('.container').style.transition = 'all var(--transition-time) ease';
                
                document.body.setAttribute('data-theme', isDark ? 'light' : 'dark');
                localStorage.setItem('theme', isDark ? 'light' : 'dark');
                
                setTimeout(() => {
                    document.body.style.transition = '';
                    document.querySelector('.container').style.transition = '';
                }, 500);
                
                updateChartsTheme();
            });
            
            // Проверка сохраненной темы
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.body.setAttribute('data-theme', savedTheme);
            
            // Инициализация tooltip
            const tooltip = document.createElement('div');
            tooltip.className = 'custom-tooltip';
            document.body.appendChild(tooltip);
            
            document.querySelectorAll('.tooltip-icon').forEach(icon => {
                icon.addEventListener('click', function(e) {
                    e.stopPropagation();
                    const text = this.getAttribute('data-tooltip');
                    const rect = this.getBoundingClientRect();
                    
                    tooltip.textContent = text;
                    tooltip.style.left = `${rect.left + window.scrollX}px`;
                    tooltip.style.top = `${rect.top + window.scrollY - tooltip.offsetHeight - 10}px`;
                    tooltip.classList.add('visible');
                });
            });
            
            document.addEventListener('click', function() {
                tooltip.classList.remove('visible');
            });
            
            // Инициализация вкладок
            const tabButtons = document.querySelectorAll('.tab-button');
            const tabContents = document.querySelectorAll('.tab-content');
            const tabIndicator = document.querySelector('.tab-indicator');
            
            tabButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const tabId = this.dataset.tab;
                    
                    tabButtons.forEach(btn => btn.classList.remove('active'));
                    this.classList.add('active');
                    
                    tabIndicator.style.width = `${this.offsetWidth}px`;
                    tabIndicator.style.left = `${this.offsetLeft}px`;
                    
                    tabContents.forEach(content => content.classList.remove('active'));
                    document.getElementById(tabId).classList.add('active');
                    
                    if (tabId === 'dashboardTab' && !window.chartsInitialized) {
                        initDashboardCharts();
                        window.chartsInitialized = true;
                    } else if (tabId === 'advancedTab' && !window.advancedChartsInitialized) {
                        initAdvancedCharts();
                        window.advancedChartsInitialized = true;
                    }
                });
            });
            
            if (tabButtons.length > 0) {
                const activeTab = document.querySelector('.tab-button.active');
                tabIndicator.style.width = `${activeTab.offsetWidth}px`;
                tabIndicator.style.left = `${activeTab.offsetLeft}px`;
            }
            
            if (document.querySelector('.tab-button.active').dataset.tab === 'dashboardTab') {
                initDashboardCharts();
                window.chartsInitialized = true;
            }
            
            // Очистка поиска
            document.getElementById('clearSearch').addEventListener('click', function() {
                document.getElementById('searchInput').value = '';
                this.style.display = 'none';
                document.querySelectorAll('.card').forEach(card => {
                    card.style.display = '';
                    card.querySelectorAll('.highlight').forEach(el => {
                        el.outerHTML = el.innerHTML;
                    });
                });
            });
        });
        
        // Плавное переключение файлов с прокруткой
        function toggleFile(header) {
            const content = header.nextElementSibling;
            const isExpanding = !content.classList.contains('expanded');
            const card = header.closest('.card');
            
            if (isExpanding) {
                const scrollPosition = window.scrollY;
                const cardPosition = card.getBoundingClientRect().top + window.scrollY;
                
                content.style.display = 'block';
                const contentHeight = content.scrollHeight;
                content.style.maxHeight = '0';
                
                content.classList.add('expanded');
                content.style.maxHeight = `${contentHeight}px`;
                
                setTimeout(() => {
                    const newCardPosition = card.getBoundingClientRect().top + window.scrollY;
                    const positionDiff = newCardPosition - cardPosition;
                    
                    window.scrollTo({
                        top: scrollPosition + positionDiff,
                        behavior: 'smooth'
                    });
                }, 10);
            } else {
                const scrollPosition = window.scrollY;
                const cardPosition = card.getBoundingClientRect().top + window.scrollY;
                
                content.style.maxHeight = '0';
                
                setTimeout(() => {
                    content.classList.remove('expanded');
                    
                    const newCardPosition = card.getBoundingClientRect().top + window.scrollY;
                    const positionDiff = newCardPosition - cardPosition;
                    
                    window.scrollTo({
                        top: scrollPosition + positionDiff,
                        behavior: 'smooth'
                    });
                }, 300);
            }
        }
        
        // Улучшенный поиск с учетом функций
        document.getElementById('searchInput').addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const clearBtn = document.getElementById('clearSearch');
            clearBtn.style.display = searchTerm ? 'block' : 'none';
            
            if (!searchTerm) {
                document.querySelectorAll('.card').forEach(card => {
                    card.style.display = '';
                    card.querySelectorAll('.highlight').forEach(el => {
                        el.outerHTML = el.innerHTML;
                    });
                });
                return;
            }
            
            document.querySelectorAll('.card').forEach(card => {
                const filename = card.querySelector('.file-title div:nth-child(2)').textContent.toLowerCase();
                const functions = card.querySelectorAll('.function-name');
                let hasMatch = filename.includes(searchTerm);
                
                // Сброс предыдущего выделения
                card.querySelectorAll('.highlight').forEach(el => {
                    el.outerHTML = el.innerHTML;
                });
                
                // Поиск в имени файла
                if (searchTerm && filename.includes(searchTerm)) {
                    const highlighted = filename.replace(
                        new RegExp(searchTerm, 'gi'), 
                        match => `<span class="highlight">${match}</span>`
                    );
                    card.querySelector('.file-title div:nth-child(2)').innerHTML = highlighted;
                    hasMatch = true;
                }
                
                // Поиск в функциях
                functions.forEach(func => {
                    const funcName = func.textContent.toLowerCase();
                    if (funcName.includes(searchTerm)) {
                        const highlighted = func.textContent.replace(
                            new RegExp(searchTerm, 'gi'), 
                            match => `<span class="highlight">${match}</span>`
                        );
                        func.innerHTML = highlighted;
                        hasMatch = true;
                    }
                });
                
                card.style.display = hasMatch ? '' : 'none';
                
                // Автоматическое раскрытие при совпадении
                if (hasMatch && !card.querySelector('.file-content').classList.contains('expanded')) {
                    toggleFile(card.querySelector('.file-header'));
                }
            });
        });
        
        // Инициализация графиков dashboard
        function initDashboardCharts() {
            const dashboardData = {{ dashboard_data|tojson }};
            const isDark = document.body.getAttribute('data-theme') === 'dark';
            const textColor = isDark ? '#e2e8f0' : '#1e293b';
            const gridColor = isDark ? 'rgba(100, 116, 139, 0.2)' : 'rgba(148, 163, 184, 0.2)';
            const fontFamily = "'IBM Plex Sans', sans-serif";
            
            // Общие настройки для графиков
            const commonOptions = {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: textColor,
                            font: {
                                family: fontFamily
                            }
                        }
                    },
                    tooltip: {
                        bodyFont: {
                            family: fontFamily
                        }
                    }
                }
            };
            
            // Complexity Distribution Chart
            const complexityCtx = document.getElementById('complexityChart').getContext('2d');
            const complexityChart = new Chart(complexityCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Low Complexity', 'Medium Complexity', 'High Complexity'],
                    datasets: [{
                        data: [
                            dashboardData.complexity_distribution.low,
                            dashboardData.complexity_distribution.medium,
                            dashboardData.complexity_distribution.high
                        ],
                        backgroundColor: [
                            '#10b981',
                            '#f59e0b',
                            '#ef4444'
                        ],
                        borderColor: isDark ? '#334155' : '#ffffff',
                        borderWidth: 1
                    }]
                },
                options: {
                    ...commonOptions,
                    plugins: {
                        ...commonOptions.plugins,
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: textColor,
                                font: {
                                    family: fontFamily
                                }
                            }
                        }
                    },
                    cutout: '70%',
                    animation: {
                        animateScale: true,
                        animateRotate: true
                    }
                }
            });
            
            // Metrics Comparison Chart
            const metricsCtx = document.getElementById('metricsChart').getContext('2d');
            const metricsChart = new Chart(metricsCtx, {
                type: 'bar',
                data: {
                    labels: ['Complexity', 'Comments', 'Depth', 'Pointers', 'Directives'],
                    datasets: [{
                        label: 'Average Value',
                        data: [
                            dashboardData.avg_metrics.complexity,
                            dashboardData.avg_metrics.comments,
                            dashboardData.avg_metrics.depth,
                            dashboardData.avg_metrics.pointers,
                            dashboardData.avg_metrics.directives
                        ],
                        backgroundColor: '#3b82f6',
                        borderColor: '#2563eb',
                        borderWidth: 1
                    }, {
                        label: 'Threshold',
                        data: [
                            dashboardData.thresholds.cyclomatic_complexity,
                            dashboardData.thresholds.comment_percentage,
                            dashboardData.thresholds.max_block_depth,
                            dashboardData.thresholds.pointer_operations,
                            dashboardData.thresholds.preprocessor_directives
                        ],
                        backgroundColor: '#94a3b8',
                        borderColor: '#64748b',
                        borderWidth: 1
                    }]
                },
                options: {
                    ...commonOptions,
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: gridColor
                            },
                            ticks: {
                                color: textColor,
                                font: {
                                    family: fontFamily
                                }
                            }
                        },
                        x: {
                            grid: {
                                color: gridColor
                            },
                            ticks: {
                                color: textColor,
                                font: {
                                    family: fontFamily
                                }
                            }
                        }
                    }
                }
            });
            
            // Comments Distribution Chart
            const commentsCtx = document.getElementById('commentsChart').getContext('2d');
            const commentsChart = new Chart(commentsCtx, {
                type: 'polarArea',
                data: {
                    labels: Object.keys(dashboardData.comment_ranges).map(k => k.replace('-', '-') + '%'),
                    datasets: [{
                        data: Object.values(dashboardData.comment_ranges),
                        backgroundColor: [
                            'rgba(59, 130, 246, 0.7)',
                            'rgba(16, 185, 129, 0.7)',
                            'rgba(245, 158, 11, 0.7)',
                            'rgba(139, 92, 246, 0.7)',
                            'rgba(236, 72, 153, 0.7)',
                            'rgba(239, 68, 68, 0.7)'
                        ],
                        borderColor: isDark ? '#334155' : '#ffffff',
                        borderWidth: 1
                    }]
                },
                options: {
                    ...commonOptions,
                    plugins: {
                        ...commonOptions.plugins,
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: textColor,
                                font: {
                                    family: fontFamily
                                }
                            }
                        }
                    },
                    scales: {
                        r: {
                            grid: {
                                color: gridColor
                            },
                            angleLines: {
                                color: gridColor
                            },
                            pointLabels: {
                                color: textColor,
                                font: {
                                    family: fontFamily
                                }
                            },
                            ticks: {
                                display: false,
                                backdropColor: 'transparent'
                            }
                        }
                    },
                    animation: {
                        animateScale: true,
                        animateRotate: true
                    }
                }
            });
            
            // Depth vs Pointers Chart
            const depthPointersCtx = document.getElementById('depthPointersChart').getContext('2d');
            const depthPointersChart = new Chart(depthPointersCtx, {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: 'Files',
                        data: dashboardData.depth_pointers_data,
                        backgroundColor: '#3b82f6',
                        borderColor: '#2563eb',
                        borderWidth: 1,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }]
                },
                options: {
                    ...commonOptions,
                    scales: {
                        y: {
                            title: {
                                display: true,
                                text: 'Block Depth',
                                color: textColor,
                                font: {
                                    family: fontFamily
                                }
                            },
                            grid: {
                                color: gridColor
                            },
                            ticks: {
                                color: textColor,
                                font: {
                                    family: fontFamily
                                }
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Pointer Operations',
                                color: textColor,
                                font: {
                                    family: fontFamily
                                }
                            },
                            grid: {
                                color: gridColor
                            },
                            ticks: {
                                color: textColor,
                                font: {
                                    family: fontFamily
                                }
                            }
                        }
                    },
                    plugins: {
                        ...commonOptions.plugins,
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `File: ${context.raw.file}`;
                                },
                                afterLabel: function(context) {
                                    return `Depth: ${context.raw.y}\nPointers: ${context.raw.x}`;
                                }
                            }
                        }
                    }
                }
            });
            
            window.charts = {
                complexity: complexityChart,
                metrics: metricsChart,
                comments: commentsChart,
                depthPointers: depthPointersChart
            };
        }
        
        // Инициализация графиков advanced metrics
        function initAdvancedCharts() {
            const dashboardData = {{ dashboard_data|tojson }};
            const isDark = document.body.getAttribute('data-theme') === 'dark';
            const textColor = isDark ? '#e2e8f0' : '#1e293b';
            const gridColor = isDark ? 'rgba(100, 116, 139, 0.2)' : 'rgba(148, 163, 184, 0.2)';
            const fontFamily = "'IBM Plex Sans', sans-serif";
            
            // Complexity vs NLOC Chart
            const complexityNlocCtx = document.getElementById('complexityNlocChart').getContext('2d');
            const complexityNlocChart = new Chart(complexityNlocCtx, {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: 'Functions',
                        data: dashboardData.complexity_nloc_data,
                        backgroundColor: '#3b82f6',
                        borderColor: '#2563eb',
                        borderWidth: 1,
                        pointRadius: 5,
                        pointHoverRadius: 7
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            title: {
                                display: true,
                                text: 'Cyclomatic Complexity',
                                color: textColor,
                                font: {
                                    family: fontFamily
                                }
                            },
                            grid: {
                                color: gridColor
                            },
                            ticks: {
                                color: textColor,
                                font: {
                                    family: fontFamily
                                }
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Lines of Code',
                                color: textColor,
                                font: {
                                    family: fontFamily
                                }
                            },
                            grid: {
                                color: gridColor
                            },
                            ticks: {
                                color: textColor,
                                font: {
                                    family: fontFamily
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `Function: ${context.raw.function}`;
                                },
                                afterLabel: function(context) {
                                    return `File: ${context.raw.file}\nLines: ${context.raw.x}\nComplexity: ${context.raw.y}`;
                                }
                            }
                        }
                    }
                }
            });
            
            // Code Composition Chart
            const codeCompositionCtx = document.getElementById('codeCompositionChart').getContext('2d');
            const codeCompositionChart = new Chart(codeCompositionCtx, {
                type: 'pie',
                data: {
                    labels: ['Code', 'Comments', 'Empty'],
                    datasets: [{
                        data: [{{ code_ratio.code }}, {{ code_ratio.comments }}, {{ code_ratio.empty }}],
                        backgroundColor: [
                            '#3b82f6',
                            '#10b981',
                            '#94a3b8'
                        ],
                        borderColor: isDark ? '#334155' : '#ffffff',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: textColor,
                                font: {
                                    family: fontFamily
                                }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.raw || 0;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = Math.round((value / total) * 100);
                                    return `${label}: ${value} (${percentage}%)`;
                                }
                            }
                        }
                    },
                    animation: {
                        animateScale: true,
                        animateRotate: true
                    }
                }
            });
            
            // Heatmap Chart
            const heatmapChart = echarts.init(document.getElementById('heatmapChart'));
            
            const dirData = {{ dir_complexity_stats|tojson }};
            const heatmapData = dirData.map(dir => ({
                name: dir.name,
                value: dir.avg_complexity,
                itemStyle: {
                    color: getHeatmapColor(dir.avg_complexity, {{ thresholds['cyclomatic_complexity'] }})
                }
            }));
            
            const heatmapOption = {
                tooltip: {
                    trigger: 'item',
                    formatter: function(params) {
                        return `<strong>${params.name}</strong><br/>
                                Avg Complexity: ${params.value.toFixed(1)}<br/>
                                Files: ${params.data.file_count || 0}`;
                    }
                },
                series: [{
                    name: 'Directory Complexity',
                    type: 'treemap',
                    visibleMin: 1,
                    data: heatmapData,
                    breadcrumb: {
                        show: false
                    },
                    label: {
                        show: true,
                        formatter: '{b}'
                    },
                    upperLabel: {
                        show: true,
                        height: 30
                    },
                    itemStyle: {
                        borderColor: isDark ? '#334155' : '#f8fafc'
                    },
                    levels: [
                        {
                            itemStyle: {
                                borderWidth: 0,
                                gapWidth: 1
                            }
                        },
                        {
                            itemStyle: {
                                borderWidth: 1,
                                gapWidth: 1
                            }
                        }
                    ]
                }]
            };
            
            heatmapChart.setOption(heatmapOption);
            
            function getHeatmapColor(value, threshold) {
                if (value <= threshold * 0.5) {
                    return '#10b981'; // green
                } else if (value <= threshold) {
                    return '#f59e0b'; // yellow
                } else {
                    return '#ef4444'; // red
                }
            }
            
            window.advancedCharts = {
                complexityNloc: complexityNlocChart,
                codeComposition: codeCompositionChart,
                heatmap: heatmapChart
            };
        }
        
        function updateChartsTheme() {
            if (window.charts) {
                const isDark = document.body.getAttribute('data-theme') === 'dark';
                const textColor = isDark ? '#e2e8f0' : '#1e293b';
                const gridColor = isDark ? 'rgba(100, 116, 139, 0.2)' : 'rgba(148, 163, 184, 0.2)';
                
                Object.values(window.charts).forEach(chart => {
                    if (chart.options.scales) {
                        if (chart.options.scales.x) {
                            chart.options.scales.x.ticks.color = textColor;
                            if (chart.options.scales.x.title) {
                                chart.options.scales.x.title.color = textColor;
                            }
                        }
                        if (chart.options.scales.y) {
                            chart.options.scales.y.ticks.color = textColor;
                            if (chart.options.scales.y.title) {
                                chart.options.scales.y.title.color = textColor;
                            }
                        }
                        if (chart.options.scales.r) {
                            chart.options.scales.r.pointLabels.color = textColor;
                        }
                    }
                    
                    if (chart.options.plugins?.legend?.labels) {
                        chart.options.plugins.legend.labels.color = textColor;
                    }
                    
                    chart.update();
                });
            }
            
            if (window.advancedCharts?.heatmap) {
                const isDark = document.body.getAttribute('data-theme') === 'dark';
                window.advancedCharts.heatmap.setOption({
                    itemStyle: {
                        borderColor: isDark ? '#334155' : '#f8fafc'
                    }
                });
            }
        }
    </script>
</body>
</html>'''