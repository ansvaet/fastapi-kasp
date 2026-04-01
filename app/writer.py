from openpyxl import Workbook
from typing import Dict, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def write_excel(output_path: Path, 
                total_counts: Dict[str, int], 
                line_counts: Dict[str, Dict[int, int]], 
                total_lines: int) -> None:
   
    try:
        wb = Workbook()
        ws = wb.active
        ws.title = "Частотный анализ"
        
        headers = ["Словоформа", "Кол-во во всём документе", "Кол-во в каждой строке"]
        ws.append(headers)

        ws.freeze_panes = 'A2'

        for lemma, total in sorted(total_counts.items(), key=lambda x: x[1], reverse=True):

            per_line = [
                str(line_counts.get(lemma, {}).get(line_idx, 0)) 
                for line_idx in range(total_lines)
            ]
            per_line_str = ",".join(per_line)
            ws.append([lemma, total, per_line_str])
        

        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        wb.save(output_path)
        logger.info(f"Excel file saved: {output_path}")
        
    except Exception as e:
        logger.error(f"Error writing Excel file: {e}")
        raise