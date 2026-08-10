"""
Excel Parser Utility
Handles Excel file parsing and data extraction for both Vocational and General subjects
"""

import os
import pandas as pd

def parse_excel_file(file_path):
    """
    Parse Excel file dynamically and extract student data cleanly.
    Supports Theory+Practical subjects and prevents Grade calculation bugs.
    """
    try:
        # pandas দিয়ে সহজে পুরো এক্সেল শিট পড়া
        df = pd.read_excel(file_path)
        
        # কলামের নামের আসেপাশে ফালতু স্পেস থাকলে তা মুছে ফেলা
        df.columns = df.columns.str.strip()

        # কলাম ভ্যালিডেশন
        cols_lower = [str(c).lower() for c in df.columns]
        if 'roll' not in cols_lower and 'রোল' not in cols_lower:
            return None, "Invalid Excel format. Must contain 'Roll' column."

        # রোল এবং নাম কলাম খুঁজে বের করা
        roll_col = next((c for c in df.columns if str(c).lower() in ['roll', 'রোল']), None)
        name_col = next((c for c in df.columns if str(c).lower() in ['name', 'নাম']), None)

        students = []
        skip_cols = {roll_col, name_col, 'Total_Marks', 'Status', 'GPA'}

        for _, row in df.iterrows():
            if pd.isna(row[roll_col]):
                continue

            subjects = []
            processed_subjects = set()

            for col in df.columns:
                if col in skip_cols or col is None:
                    continue

                # ১. ভোকেশনাল / প্র্যাকটিক্যাল ওয়ালা সাবজেক্ট (যেমন: IT3_Theory, IT3_Practical, IT3_Grade)
                if '_Theory' in col or '_Practical' in col or '_Grade' in col:
                    base_sub = col.split('_')[0]
                    if base_sub not in processed_subjects:
                        processed_subjects.add(base_sub)
                        
                        theory = row.get(f"{base_sub}_Theory")
                        practical = row.get(f"{base_sub}_Practical")
                        grade = row.get(f"{base_sub}_Grade", "-")

                        # মার্কস সাজানো
                        if pd.notna(theory) and pd.notna(practical):
                            marks_str = f"T: {int(theory)}, P: {int(practical)}"
                        elif pd.notna(theory):
                            marks_str = str(int(theory))
                        elif pd.notna(practical):
                            marks_str = f"P: {int(practical)}"
                        else:
                            marks_str = "-"

                        subjects.append({
                            "name": base_sub,
                            "marks": marks_str,
                            "grade": str(grade) if pd.notna(grade) and str(grade) != 'nan' else "-"
                        })

                # ২. সাধারণ বিষয় (যেমন: Bangla, Math বা Bangla_Marks)
                else:
                    base_sub = col.replace('_Marks', '')
                    if base_sub not in processed_subjects:
                        processed_subjects.add(base_sub)
                        
                        grade = row.get(f"{base_sub}_Grade", row.get(f"{col}_Grade", "-"))
                        marks_val = row.get(col, "-")

                        if pd.notna(marks_val) and isinstance(marks_val, (int, float)):
                            marks_str = str(int(marks_val))
                        elif pd.notna(marks_val):
                            marks_str = str(marks_val)
                        else:
                            marks_str = "-"

                        subjects.append({
                            "name": base_sub,
                            "marks": marks_str,
                            "grade": str(grade) if pd.notna(grade) and str(grade) != 'nan' else "-"
                        })

            # রো লেভেল মেটাডাটা
            roll_val = str(int(row[roll_col])) if pd.notna(row[roll_col]) else ""
            name_val = str(row[name_col]).strip() if name_col and pd.notna(row[name_col]) else ""
            total_marks = str(int(row['Total_Marks'])) if 'Total_Marks' in row and pd.notna(row['Total_Marks']) else "-"
            status_val = str(row.get('Status', 'Pass')) if pd.notna(row.get('Status')) else "Pass"
            gpa_val = str(row['GPA']) if 'GPA' in row and pd.notna(row['GPA']) else "0.00"

            student_data = {
                "roll": roll_val,
                "name": name_val,
                "total_marks": total_marks,
                "status": status_val,
                "gpa": gpa_val,
                "subjects": subjects
            }
            students.append(student_data)

        return students, "Success"

    except Exception as e:
        return None, f"Error parsing Excel: {str(e)}"


def validate_file(file_path):
    """Validate if file is valid Excel"""
    if not os.path.exists(file_path):
        return False, "File not found"

    if not file_path.endswith(('.xlsx', '.xls')):
        return False, "Invalid file format. Use .xlsx or .xls"

    return True, "Valid"