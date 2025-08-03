import os
import sys
import logging
import re
from concurrent.futures import ThreadPoolExecutor
import xml.etree.ElementTree as ET
from tqdm import tqdm
from collections import defaultdict
from typing import Dict, List, Optional, DefaultDict

# Настройка логгирования
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

class Config:
    """Конфигурация анализатора"""
    EXCLUDE_DIRS = {'.git', 'venv', '__pycache__', 'include'}
    SUPPORTED_EXTENSIONS = {'.c', '.h'}
    METRICS = [
        'comment_percentage',
        'max_block_depth',
        'pointer_operations',
        'preprocessor_directives'
    ]
    THRESHOLDS = {
        'comment_percentage': 20,
        'max_block_depth': 5,
        'pointer_operations': 20,
        'preprocessor_directives': 15
    }

class FileAnalyzer:
    """Анализатор отдельных файлов"""
    @staticmethod
    def _remove_string_literals(content: str) -> str:
        """Удаляет строковые литералы для упрощения анализа"""
        return re.sub(r'"[^"]*"', '', content)

    @staticmethod
    def _count_comments(content: str) -> int:
        """Подсчёт количества строк с комментариями"""
        lines = content.split('\n')
        comment_lines = 0
        in_block_comment = False
        
        for line in lines:
            line = line.strip()
            if in_block_comment:
                comment_lines += 1
                if '*/' in line:
                    in_block_comment = False
                continue
            if line.startswith('/*'):
                comment_lines += 1
                in_block_comment = True
                if '*/' in line:
                    in_block_comment = False
            elif line.startswith('//'):
                comment_lines += 1
                
        return comment_lines

    @staticmethod
    def _calculate_block_depth(content: str) -> int:
        """Вычисление максимальной глубины вложенности"""
        max_depth = 0
        current_depth = 0
        
        for char in content:
            if char == '{':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == '}':
                current_depth -= 1
                
        return max_depth

    @classmethod
    def analyze(cls, file_path: str) -> Optional[Dict[str, float]]:
        """Анализ файла и возврат метрик"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            content_no_strings = cls._remove_string_literals(content)
            total_lines = len(content.split('\n'))
            comment_lines = cls._count_comments(content)
            
            return {
                'file_name': os.path.basename(file_path),
                'file_path': os.path.relpath(file_path),
                'comment_percentage': (comment_lines / total_lines * 100) if total_lines else 0,
                'max_block_depth': cls._calculate_block_depth(content_no_strings),
                'pointer_operations': content_no_strings.count('*') + content_no_strings.count('&'),
                'preprocessor_directives': len([l for l in content.split('\n') if l.strip().startswith('#')]),
            }
        except Exception as e:
            logger.warning(f"Ошибка анализа {file_path}: {str(e)}")
            return None

class MetricsAggregator:
    """Агрегация метрик по всем файлам"""
    def __init__(self):
        self.file_metrics: List[Dict[str, float]] = []
        self.total_metrics: DefaultDict[str, float] = defaultdict(float)
        self.counts: DefaultDict[str, int] = defaultdict(int)

    def add_file_metrics(self, metrics: Dict[str, float]) -> None:
        """Добавление метрик файла"""
        self.file_metrics.append(metrics)
        for key in Config.METRICS:
            if key in metrics:
                self.total_metrics[key] += metrics[key]
                self.counts[key] += 1

    def get_averages(self) -> Dict[str, float]:
        """Расчёт средних значений"""
        return {
            metric: self.total_metrics[metric] / self.counts[metric]
            for metric in Config.METRICS
            if self.counts[metric] > 0
        }

class ReportGenerator:
    """Генерация отчётов"""
    @staticmethod
    def generate_xml(metrics: List[Dict[str, float]], output_path: str) -> None:
        """Генерация XML отчёта"""
        root = ET.Element('sourcemonitor_metrics')
        for file_metrics in metrics:
            file_node = ET.SubElement(root, 'file', 
                                   name=file_metrics['file_name'],
                                   path=file_metrics['file_path'])
            for metric in Config.METRICS:
                ET.SubElement(file_node, metric).text = str(file_metrics.get(metric, 0))
        
        tree = ET.ElementTree(root)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        logger.info(f"XML-отчёт сохранён в {output_path}")



class SourceMonitorMetrics:
    """Основной класс анализатора"""
    def __init__(self, path: str):
        self.path = os.path.abspath(path)
        self.output_xml = os.path.join(os.path.dirname(self.path), 'sourcemonitor_metrics.xml')
        self.aggregator = MetricsAggregator()

    def _collect_files(self) -> List[str]:
        """Сбор файлов для анализа"""
        c_files = []
        for root, dirs, files in os.walk(self.path):
            dirs[:] = [d for d in dirs if d not in Config.EXCLUDE_DIRS]
            c_files.extend(
                os.path.join(root, f) 
                for f in files 
                if os.path.splitext(f)[1] in Config.SUPPORTED_EXTENSIONS
            )
        return c_files

    def get_metrics(self) -> List[Dict[str, float]]:
        """Возвращает собранные метрики для интеграции"""
        return self.aggregator.file_metrics

    def analyze_directory(self) -> None:
        """Анализ директории"""
        if not os.path.exists(self.path):
            logger.error(f"Ошибка: путь '{self.path}' не существует!")
            sys.exit(1)

        files = self._collect_files()
        logger.info(f"Найдено {len(files)} файлов для анализа...")
        
        with ThreadPoolExecutor() as executor:
            results = list(tqdm(
                executor.map(FileAnalyzer.analyze, files),
                total=len(files),
                desc="Анализ файлов"
            ))
        
        for metrics in filter(None, results):
            self.aggregator.add_file_metrics(metrics)

        ReportGenerator.generate_xml(
            self.aggregator.file_metrics, 
            self.output_xml
        )

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(1)

    analyzer = SourceMonitorMetrics(sys.argv[1])
    analyzer.analyze_directory()