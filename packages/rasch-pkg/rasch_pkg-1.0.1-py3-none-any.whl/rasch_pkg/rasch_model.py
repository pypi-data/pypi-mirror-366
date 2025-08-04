"""
Rasch Model Implementation for Student Assessment
Rasch modeli asosida o'quvchilarni baholash tizimi
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Union
import logging
from dataclasses import dataclass
from enum import Enum


class GradeLevel(Enum):
    """Daraja darajalarini belgilash"""
    NC = "NC"  # Not Classified
    C = "C"
    C_PLUS = "C+"
    B = "B"
    B_PLUS = "B+"
    A = "A"
    A_PLUS = "A+"


@dataclass
class StudentResult:
    """O'quvchi natijasi uchun ma'lumotlar strukturasi"""
    student_id: str
    name: str
    answers: List[Union[int, float]]
    correct_count: int
    total_questions: int
    raw_score: float
    theta: float  # Skill level (ϴ)
    mu: float  # μ
    sigma: float  # σ
    z_score: float
    scaled_score: float  # Ball (0-100)
    grade: GradeLevel


class RaschModel:
    """
    Rasch modeli asosida o'quvchilarni baholash tizimi

    Bu class quyidagi funksiyalarni bajaradi:
    1. O'quvchi javoblarini tahlil qilish
    2. Rasch modeli asosida skill level (theta) hisoblash
    3. Z-score va scaled score hisoblash
    4. Daraja (grade) belgilash
    """

    def __init__(self,
                 grade_thresholds: Optional[Dict[str, Tuple[float, float]]] = None,  # noqa: E501
                 max_iterations: int = 100,
                 convergence_threshold: float = 1e-6):
        """
        Rasch modeli obyektini yaratish

        Args:
            grade_thresholds: Daraja chegaralari {grade: (min_score, max_score)}  # noqa: E501
            max_iterations: Maksimal iteratsiya soni
            convergence_threshold: Konvergensiya chegarasi
        """
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold

        # Default daraja chegaralari (Excel fayldan olingan)
        if grade_thresholds is None:
            self.grade_thresholds = {
                GradeLevel.NC.value: (0.0, 45.99),
                GradeLevel.C.value: (46.0, 49.99),
                GradeLevel.C_PLUS.value: (50.0, 54.99),
                GradeLevel.B.value: (55.0, 59.99),
                GradeLevel.B_PLUS.value: (60.0, 64.99),
                GradeLevel.A.value: (65.0, 69.99),
                GradeLevel.A_PLUS.value: (70.0, 100.0)
            }
        else:
            self.grade_thresholds = grade_thresholds

        # Model parametrlari
        self.item_difficulties = None
        self.person_abilities = None
        self.mu = 0.0  # O'rtacha
        self.sigma = 1.0  # Standart og'ish

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def calculate_theta(self, correct_answers: int,
                        total_questions: int) -> float:
        """
        O'quvchining skill level (theta) ni hisoblash

        Args:
            correct_answers: To'g'ri javoblar soni
            total_questions: Jami savollar soni

        Returns:
            theta: Skill level
        """
        if correct_answers == 0:
            return -4.0  # Minimal theta qiymati
        elif correct_answers == total_questions:
            return 4.0   # Maksimal theta qiymati

        # Logit transformatsiya
        p = correct_answers / total_questions
        # Extreme qiymatlarni cheklash
        p = max(0.001, min(0.999, p))

        # Logit formula: ln(p/(1-p))
        theta = np.log(p / (1 - p))

        return theta

    def calculate_z_score(self, theta: float, mu: float,
                          sigma: float) -> float:
        """
        Z-score hisoblash

        Args:
            theta: Skill level
            mu: O'rtacha
            sigma: Standart og'ish

        Returns:
            z_score: Standartlashtirilgan ball
        """
        return (theta - mu) / sigma

    def calculate_scaled_score(self, z_score: float) -> float:
        """
        Scaled score (0-100 oralig'ida ball) hisoblash

        Args:
            z_score: Z-score qiymati

        Returns:
            scaled_score: 0-100 oralig'idagi ball
        """
        # Formula: Ball = 50 + 10 * Z
        scaled_score = 50 + 10 * z_score

        # 0-100 oralig'ida cheklash
        return max(0.0, min(100.0, scaled_score))

    def determine_grade(self, scaled_score: float) -> GradeLevel:
        """
        Ball asosida daraja belgilash

        Args:
            scaled_score: 0-100 oralig'idagi ball

        Returns:
            grade: Daraja
        """
        for grade, (min_score, max_score) in self.grade_thresholds.items():
            if min_score <= scaled_score <= max_score:
                return GradeLevel(grade)

        # Default NC daraja
        return GradeLevel.NC

    def process_student_answers(self,
                                student_id: str,
                                name: str,
                                answers: List[Union[int, float]]) -> StudentResult:  # noqa: E501
        """
        Bitta o'quvchining javoblarini qayta ishlash

        Args:
            student_id: O'quvchi ID
            name: O'quvchi ismi
            answers: Javoblar ro'yxati (1 - to'g'ri, 0 - noto'g'ri)

        Returns:
            StudentResult: O'quvchi natijasi
        """
        # Javoblarni tekshirish
        answers = [float(ans) if ans in [0, 1, 0.0, 1.0] else 0.0
                   for ans in answers]

        correct_count = int(sum(answers))
        total_questions = len(answers)
        if total_questions > 0:
            raw_score = correct_count / total_questions
        else:
            raw_score = 0.0

        # Theta hisoblash
        theta = self.calculate_theta(correct_count, total_questions)

        # Z-score hisoblash
        z_score = self.calculate_z_score(theta, self.mu, self.sigma)

        # Scaled score hisoblash
        scaled_score = self.calculate_scaled_score(z_score)

        # Daraja belgilash
        grade = self.determine_grade(scaled_score)
        return StudentResult(
            student_id=student_id,
            name=name,
            answers=answers,
            correct_count=correct_count,
            total_questions=total_questions,
            raw_score=raw_score,
            theta=theta,
            mu=self.mu,
            sigma=self.sigma,
            z_score=z_score,
            scaled_score=scaled_score,
            grade=grade
        )

    def process_multiple_students(self,
                                  data: Union[pd.DataFrame, List[Dict]]) -> List[StudentResult]:  # noqa: E501
        """
        Ko'p o'quvchilarning javoblarini qayta ishlash

        Args:
            data: O'quvchilar ma'lumotlari (DataFrame yoki dict ro'yxati)

        Returns:
            List[StudentResult]: Barcha o'quvchilar natijalari
        """
        results = []
        if isinstance(data, pd.DataFrame):
            # DataFrame dan ma'lumotlarni olish
            for idx, row in data.iterrows():
                student_id = str(idx + 1)
                name = row.get('F.I.0', row.get('name', f'Student_{idx+1}'))

                # Savol ustunlarini topish (V1, V2, ...)
                question_cols = [col for col in data.columns
                                 if col.startswith('V') and col[1:].isdigit()]

                if not question_cols:
                    # Agar V ustunlari bo'lmasa, raqamli ustunlarni qidirish
                    question_cols = [col for col in data.columns
                                     if isinstance(col, (int, str)) and
                                     str(col).isdigit()]

                answers = row[question_cols].tolist() if question_cols else []

                if answers:
                    result = self.process_student_answers(student_id, name,
                                                          answers)
                    results.append(result)

        elif isinstance(data, list):
            # List dan ma'lumotlarni olish
            for idx, student_data in enumerate(data):
                student_id = student_data.get('id', str(idx + 1))
                name = student_data.get('name', f'Student_{idx+1}')
                answers = student_data.get('answers', [])

                if answers:
                    result = self.process_student_answers(student_id, name,
                                                          answers)
                    results.append(result)

        return results

    def get_statistics(self, results: List[StudentResult]) -> Dict:
        """
        Natijalar statistikasini hisoblash

        Args:
            results: O'quvchilar natijalari

        Returns:
            Dict: Statistik ma'lumotlar
        """
        if not results:
            return {}

        scores = [r.scaled_score for r in results]
        grades = [r.grade.value for r in results]

        # Daraja taqsimoti
        grade_distribution = {}
        for grade in GradeLevel:
            count = grades.count(grade.value)
            percentage = (count / len(grades)) * 100 if grades else 0
            grade_distribution[grade.value] = {
                'count': count,
                'percentage': round(percentage, 2)
            }

        return {
            'total_students': len(results),
            'score_statistics': {
                'min': round(min(scores), 2) if scores else 0,
                'max': round(max(scores), 2) if scores else 0,
                'mean': round(np.mean(scores), 2) if scores else 0,
                'median': round(np.median(scores), 2) if scores else 0,
                'std': round(np.std(scores), 2) if scores else 0
            },
            'grade_distribution': grade_distribution
        }

    def export_results(self,
                       results: List[StudentResult],
                       filename: str = 'rasch_results.xlsx') -> None:
        """
        Natijalarni Excel fayliga eksport qilish

        Args:
            results: O'quvchilar natijalari
            filename: Fayl nomi
        """
        if not results:
            self.logger.warning("Eksport qilish uchun natijalar mavjud emas")
            return

        # DataFrame yaratish
        data = []
        for result in results:
            data.append({
                'ID': result.student_id,
                'F.I.Sh': result.name,
                'To\'g\'ri_javoblar': result.correct_count,
                'Jami_savollar': result.total_questions,
                'Foiz': round(result.raw_score * 100, 2),
                'Theta': round(result.theta, 6),
                'Z_score': round(result.z_score, 6),
                'Ball': round(result.scaled_score, 2),
                'Daraja': result.grade.value
            })

        df = pd.DataFrame(data)

        # Excel fayliga yozish
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Natijalar', index=False)

            # Statistika sheetini qo'shish
            stats = self.get_statistics(results)
            stats_df = pd.DataFrame([stats['score_statistics']])
            stats_df.to_excel(writer, sheet_name='Statistika', index=False)

        self.logger.info(f"Natijalar {filename} fayliga eksport qilindi")

    def compare_with_excel(self,
                           results: List[StudentResult],
                           excel_file: str,
                           sheet_name: str = 'Sheet1') -> Dict:
        """
        Bizning natijalarni Excel fayl bilan taqqoslash

        Args:
            results: Bizning hisoblagan natijalar
            excel_file: Excel fayl yo'li
            sheet_name: Sheet nomi

        Returns:
            Dict: Taqqoslash natijalari
        """
        try:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)

            comparison_data = []
            for i, result in enumerate(results):
                if i < len(df):
                    excel_row = df.iloc[i]
                    excel_ball = excel_row.get('BALL', 0)
                    excel_grade = excel_row.get("Da'reje",
                                                excel_row.get('Daraja', 'NC'))

                    comparison_data.append({
                        'student_name': result.name,
                        'our_score': result.scaled_score,
                        'excel_score': excel_ball,
                        'score_difference': abs(result.scaled_score -
                                                excel_ball),
                        'our_grade': result.grade.value,
                        'excel_grade': excel_grade,
                        'grade_match': result.grade.value == excel_grade
                    })

            # Statistika hisoblash
            score_differences = [item['score_difference']
                                 for item in comparison_data]
            grade_matches = [item['grade_match'] for item in comparison_data]

            return {
                'total_compared': len(comparison_data),
                'average_score_difference': (np.mean(score_differences)
                                             if score_differences else 0),
                'max_score_difference': (max(score_differences)
                                         if score_differences else 0),
                'grade_accuracy': (sum(grade_matches) / len(grade_matches) * 100  # noqa: E501
                                   if grade_matches else 0),
                'detailed_comparison': comparison_data
            }

        except Exception as e:
            self.logger.error(f"Excel bilan taqqoslashda xatolik: {e}")
            return {}

    def generate_report(self,
                        results: List[StudentResult],
                        filename: str = 'rasch_report.txt') -> None:
        """
        Batafsil hisobot yaratish

        Args:
            results: O'quvchilar natijalari
            filename: Hisobot fayl nomi
        """
        if not results:
            self.logger.warning("Hisobot uchun natijalar mavjud emas")
            return

        stats = self.get_statistics(results)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("RASCH MODELI ASOSIDA BAHOLASH HISOBOTI\n")
            f.write("=" * 50 + "\n\n")

            # Umumiy ma'lumotlar
            f.write(f"Jami o'quvchilar soni: {stats['total_students']}\n")
            timestamp = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"Baholash sanasi: {timestamp}\n\n")

            # Ball statistikasi
            f.write("BALL STATISTIKASI\n")
            f.write("-" * 20 + "\n")
            score_stats = stats['score_statistics']
            f.write(f"O'rtacha ball: {score_stats['mean']}\n")
            f.write(f"Eng yuqori ball: {score_stats['max']}\n")
            f.write(f"Eng past ball: {score_stats['min']}\n")
            f.write(f"Mediana: {score_stats['median']}\n")
            f.write(f"Standart og'ish: {score_stats['std']}\n\n")

            # Daraja taqsimoti
            f.write("DARAJA TAQSIMOTI\n")
            f.write("-" * 20 + "\n")
            for grade, info in stats['grade_distribution'].items():
                count = info['count']
                percentage = info['percentage']
                f.write(f"{grade}: {count} ta ({percentage}%)\n")
            f.write("\n")

            # Eng yaxshi o'quvchilar
            f.write("ENG YAXSHI 10 TA O'QUVCHI\n")
            f.write("-" * 30 + "\n")
            sorted_results = sorted(results, key=lambda x: x.scaled_score,
                                    reverse=True)
            for i, result in enumerate(sorted_results[:10], 1):
                line = f"{i:2d}. {result.name:<20} {result.scaled_score:6.2f}"
                line += f" ({result.grade.value})\n"
                f.write(line)
            f.write("\n")

            # Eng past natijali o'quvchilar
            f.write("ENG PAST NATIJALI 10 TA O'QUVCHI\n")
            f.write("-" * 35 + "\n")
            for i, result in enumerate(sorted_results[-10:], 1):
                line = f"{i:2d}. {result.name:<20} {result.scaled_score:6.2f}"
                line += f" ({result.grade.value})\n"
                f.write(line)
            f.write("\n")

            # Batafsil natijalar
            f.write("BATAFSIL NATIJALAR\n")
            f.write("-" * 20 + "\n")
            header = "{:<3} {:<20} {:<8} {:<6} {:<8} {:<6} {:<6}".format(
                '№', 'F.I.Sh', 'Togri', 'Foiz', 'Theta', 'Ball', 'Daraja'
            )
            f.write(header + "\\n")
            f.write("-" * 70 + "\n")

            for i, result in enumerate(sorted_results, 1):
                line = f"{i:<3} {result.name:<20} {result.correct_count:<8} "
                line += f"{result.raw_score*100:<6.1f} {result.theta:<8.3f} "
                line += f"{result.scaled_score:<6.1f} "
                line += f"{result.grade.value:<6}\n"
                f.write(line)

        self.logger.info(f"Hisobot {filename} fayliga saqlandi")

    def set_custom_parameters(self, mu: float = None,
                              sigma: float = None) -> None:
        """
        Model parametrlarini o'rnatish

        Args:
            mu: O'rtacha qiymat
            sigma: Standart og'ish
        """
        if mu is not None:
            self.mu = mu
            self.logger.info(f"μ (mu) qiymati {mu} ga o'rnatildi")

        if sigma is not None:
            self.sigma = sigma
            self.logger.info(f"σ (sigma) qiymati {sigma} ga o'rnatildi")

    def validate_answers(self,
                         answers: List[Union[int, float]]) -> Tuple[bool, str]:
        """
        Javoblar formatini tekshirish

        Args:
            answers: Javoblar ro'yxati

        Returns:
            Tuple[bool, str]: (valid, error_message)
        """
        if not answers:
            return False, "Javoblar ro'yxati bo'sh"

        if len(answers) == 0:
            return False, "Kamida bitta javob bo'lishi kerak"

        invalid_answers = []
        for i, ans in enumerate(answers):
            if ans not in [0, 1, 0.0, 1.0]:
                invalid_answers.append(f"Pozitsiya {i+1}: {ans}")

        if invalid_answers:
            error_msg = "Noto'g'ri javob formatlari: "
            error_msg += ', '.join(invalid_answers[:5])
            return False, error_msg

        return True, "Javoblar formati to'g'ri"
