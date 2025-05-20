import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from src.DB import PipelineGrade, init_db
from src.config import LATEX_DIR
import os
import re
import asyncio
from collections import defaultdict
from itertools import groupby


async def main():
    await init_db()
    grades = await PipelineGrade.find().to_list()

    grouped_pipelines = {}
    for grade in grades:
        if grade.pipeline_type not in grouped_pipelines:
            grouped_pipelines[grade.pipeline_type] = []
        grouped_pipelines[grade.pipeline_type].append(grade)

    def convert_step(step):
        if "PinExtractor" in step:
            step = re.sub(r"PinExtractor\s*\((.*?)\)", r"\1", step)
            step = step.replace("Qwen/", "")
            step = re.sub(r"google/gemma-3-(\w+)-it", r"Gemma-3-\1", step)
            step = re.sub(r"microsoft/Phi-4-multimodal-instruct", r"Phi-4-multimodal", step)
        elif "PyTesseract" in step:
            return "PyTesseract"
        elif "PDFPlumberPagewise" in step:
            return "PDFPlumber"
        elif "Google Gemini" in step:
            return "Gemini-2.0-flash"
        elif "OpenAI" in step:
            return re.sub(r"OpenAI \((.*?)\)", lambda m: m.group(1).split("-")[0].upper() + "-" + "-".join(m.group(1).split("-")[1:]), step)
        return step

    def generate_latex_table(grades):
        latex = [
            r"\resizebox{\textwidth}{!}{",
            r"\begin{tabular}{llcccc}",
            r"\toprule",
            r"\multicolumn{2}{l}{\underline{\textbf{Pipeline}}} & \multicolumn{4}{c}{\textbf{\underline{Metrics}}} \\",
            r"\textbf{Text-Extraction} & \textbf{Pin-Extraction} & \textbf{Accuracy (\%)} & \textbf{Recall (\%)} & \textbf{Precision (\%)} & \textbf{F1 Score (\%)} \\",
        ]

        best_accuracy = max(grades, key=lambda g: g.accuracy).accuracy
        best_recall = max(grades, key=lambda g: g.recall).recall
        best_precision = max(grades, key=lambda g: g.precision).precision
        best_f1 = max(grades, key=lambda g: g.f1_score).f1_score

        def format_metric(value, best_value):
            return f"\\textbf{{{value:.2f}}}" if value == best_value else f"{value:.2f}"

        key_map = {
            "text": "Text-based pipelines",
            "proprietary": "Property-based pipelines",
            "vision": "Vision-based pipelines",
        }

        for key, value in grouped_pipelines.items():
            latex.append(r"\midrule")
            latex.append("\\multicolumn{6}{l}{\\underline{\\textbf{" + key_map.get(key, key) + "}}}\\\\")

            if key == "text" or key == "vision":
                method_groups = defaultdict(list)
                for grade in value:
                    extraction_steps = [step for step in grade.display_steps if step not in ["TextRAG", "LLMGrader (gpt-4o-mini)"]]
                    if len(extraction_steps) >= 2:
                        text_method = convert_step(extraction_steps[0])
                        pin_method = convert_step(extraction_steps[1])
                        method_groups[text_method].append((pin_method, grade))

                first_group = True
                for text_method, items in sorted(method_groups.items()):
                    if not first_group:
                        latex.append(r"\hdashline")
                    first_group = False

                    items.sort(key=lambda x: x[0])
                    row_count = len(items)
                    for i, (pin_method, grade) in enumerate(items):
                        acc = format_metric(grade.accuracy, best_accuracy)
                        rec = format_metric(grade.recall, best_recall)
                        prec = format_metric(grade.precision, best_precision)
                        f1 = format_metric(grade.f1_score, best_f1)

                        text_col = f"\\multirow{{{row_count}}}{{*}}{{{text_method}}}" if i == 0 else ""
                        row = f"{text_col} & {pin_method} & {acc} & {rec} & {prec} & {f1} \\\\"
                        latex.append(row)
            else:
                sorted_grades = sorted(value, key=lambda grade: "& ".join(convert_step(step) for step in grade.display_steps 
                                                                        if step not in ["TextRAG", "LLMGrader (gpt-4o-mini)"]))
                for grade in sorted_grades:
                    display_step = convert_step([step for step in grade.display_steps 
                                            if step not in ["TextRAG", "LLMGrader (gpt-4o-mini)"]][0])
                    
                    acc = format_metric(grade.accuracy, best_accuracy)
                    rec = format_metric(grade.recall, best_recall)
                    prec = format_metric(grade.precision, best_precision)
                    f1 = format_metric(grade.f1_score, best_f1)

                    row = f"\\multicolumn{{2}}{{l}}{{{display_step}}} & {acc} & {rec} & {prec} & {f1} \\\\"
                    latex.append(row)

        latex.extend([
            r"\bottomrule",
            r"\end{tabular}}",
        ])

        return "\n".join(latex)

    output = generate_latex_table(grades)
    print(output)

    os.makedirs(os.path.join(LATEX_DIR, "tables"), exist_ok=True)
    with open(os.path.join(LATEX_DIR, "tables", "gradings.tex"), "w") as f:
        f.write(output)

if __name__ == "__main__":
    asyncio.run(main())