"""
Rasch Evaluator - Yagona class test natijalarini baholash uchun
test_answers va user_test_results jadvallaridan foydalanadi
"""

import psycopg2
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from typing import List, Dict
try:
    from .rasch_model import RaschModel
except ImportError:
    from rasch_model import RaschModel


class RaschEvaluator:
    """
    Test natijalarini Rasch modeli asosida baholash uchun yagona class

    PostgreSQL ma'lumotlar bazasidagi test_answers va user_test_results
    jadvallaridan foydalanadi
    """

    def __init__(self, host="localhost", port=5432, database="rash_test",
                 username="postgres", password="password"):
        """
        RaschEvaluator obyektini yaratish

        Args:
            host: Ma'lumotlar bazasi host
            port: Ma'lumotlar bazasi port
            database: Ma'lumotlar bazasi nomi
            username: Foydalanuvchi nomi
            password: Parol
        """
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.connection = None
        self.rasch_model = RaschModel()

    def connect(self):
        """Ma'lumotlar bazasiga ulanish"""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password
            )
            return True
        except Exception as e:
            print(f"Ulanish xatosi: {e}")
            return False

    def disconnect(self):
        """Ma'lumotlar bazasidan uzilish"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def get_available_tests(self) -> List[Dict]:
        """
        Mavjud testlar ro'yxatini olish

        Returns:
            List[Dict]: Testlar ro'yxati
        """
        if not self.connection:
            if not self.connect():
                return []

        query = """
        SELECT
            ta.test_id,
            COUNT(DISTINCT ta.question_number) as total_questions,
            COUNT(DISTINCT utr.user_id) as participants_count
        FROM test_answers ta
        LEFT JOIN user_test_results utr ON ta.test_id = utr.test_id
        GROUP BY ta.test_id
        HAVING COUNT(DISTINCT utr.user_id) > 0
        ORDER BY participants_count DESC
        """

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            cursor.close()

            # Dict formatiga aylantirish
            results = []
            for row in rows:
                results.append(dict(zip(columns, row)))

            return results
        except Exception as e:
            print(f"Testlarni olishda xatolik: {e}")
            return []

    def _parse_user_answers(self, user_answers_data) -> List[int]:
        """
        Foydalanuvchi javoblarini parse qilish

        Args:
            user_answers_data: JSON ma'lumotlar

        Returns:
            List[int]: To'g'ri/noto'g'ri javoblar (1/0)
        """
        try:
            if isinstance(user_answers_data, str):
                answers_dict = json.loads(user_answers_data)
            else:
                answers_dict = user_answers_data

            # correct_questions arrayini olish
            correct_questions = answers_dict.get('correct_questions', [])
            if not correct_questions:
                return []

            correct_set = set(correct_questions)

            # Raqamli kalitlarni olish
            numeric_keys = [k for k in answers_dict.keys()
                            if str(k).isdigit()]

            if not numeric_keys:
                max_question = (max(correct_questions)
                                if correct_questions else 0)
                numeric_keys = [str(i) for i in range(1, max_question + 1)]

            numeric_keys.sort(key=int)

            # Har bir savol uchun to'g'ri/noto'g'ri
            answers = []
            for key in numeric_keys:
                question_num = int(key)
                if question_num in correct_set:
                    answers.append(1)  # To'g'ri
                else:
                    answers.append(0)  # Noto'g'ri

            return answers

        except Exception as e:
            print(f"Parse qilishda xatolik: {e}")
            return []

    def evaluate_users(self, test_id: str,
                       user_ids: List[int] = None) -> List[Dict]:
        """
        Foydalanuvchilarni Rasch modeli bilan baholash

        Args:
            test_id: Test ID
            user_ids: Foydalanuvchilar ID lari (ixtiyoriy)

        Returns:
            List[Dict]: Baholash natijalari
        """
        if not self.connection:
            if not self.connect():
                return []

        # Foydalanuvchi natijalarini olish
        base_query = """
        SELECT utr.user_id, utr.user_answers,
               tu.username, tu.first_name, tu.last_name
        FROM user_test_results utr
        LEFT JOIN telegram_users tu ON utr.user_id = tu.user_id
        WHERE utr.test_id = %s
        """

        params = [test_id]

        if user_ids:
            placeholders = ','.join(['%s'] * len(user_ids))
            base_query += f" AND utr.user_id IN ({placeholders})"
            params.extend(user_ids)

        base_query += " ORDER BY utr.user_id"

        try:
            cursor = self.connection.cursor()
            cursor.execute(base_query, params)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            cursor.close()

            if not rows:
                return []

            # Ma'lumotlarni tayyorlash
            users_data = []
            for row in rows:
                row_dict = dict(zip(columns, row))
                user_id = row_dict['user_id']

                # Foydalanuvchi ismini aniqlash
                first_name = row_dict.get('first_name')
                last_name = row_dict.get('last_name')
                username = row_dict.get('username')

                if first_name and last_name:
                    user_name = f"{first_name} {last_name}"
                elif username:
                    user_name = username
                else:
                    user_name = f"User_{user_id}"

                # Javoblarni parse qilish
                answers = self._parse_user_answers(row_dict['user_answers'])

                if answers:
                    users_data.append({
                        'id': str(user_id),
                        'name': user_name,
                        'answers': answers
                    })

            # Rasch modeli bilan baholash
            if not users_data:
                return []

            rasch_results = self.rasch_model.process_multiple_students(
                users_data)

            # Natijalarni dict formatiga aylantirish
            results = []
            for result in rasch_results:
                percentage = round(
                    (result.correct_count / result.total_questions) * 100, 2)
                results.append({
                    'user_id': int(result.student_id),
                    'name': result.name,
                    'correct_count': result.correct_count,
                    'total_questions': result.total_questions,
                    'percentage': percentage,
                    'theta': round(result.theta, 6),
                    'z_score': round(result.z_score, 6),
                    'rasch_score': round(result.scaled_score, 2),
                    'grade': result.grade.value
                })

            return results

        except Exception as e:
            print(f"Baholashda xatolik: {e}")
            return []

    def export_to_excel(self, test_id: str, results: List[Dict],
                        filename: str = None) -> str:
        """
        Natijalarni Excel fayliga eksport qilish

        Args:
            test_id: Test ID
            results: Baholash natijalari
            filename: Fayl nomi (ixtiyoriy)

        Returns:
            str: Yaratilgan fayl yo'li
        """
        if not results:
            return ""

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rasch_results_{test_id}_{timestamp}.xlsx"

        os.makedirs('output', exist_ok=True)
        filepath = os.path.join('output', filename)

        # DataFrame yaratish
        df = pd.DataFrame(results)

        # Excel ga yozish
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Rasch_Natijalar', index=False)

        print(f"Natijalar eksport qilindi: {filepath}")
        return filepath

    def get_statistics(self, results: List[Dict]) -> Dict:
        """
        Natijalar statistikasini olish

        Args:
            results: Baholash natijalari

        Returns:
            Dict: Statistika ma'lumotlari
        """
        if not results:
            return {}

        scores = [r['rasch_score'] for r in results]
        grades = [r['grade'] for r in results]

        # Daraja taqsimoti
        grade_counts = {}
        for grade in grades:
            grade_counts[grade] = grade_counts.get(grade, 0) + 1

        grade_distribution = {}
        for grade, count in grade_counts.items():
            percentage = (count / len(results)) * 100
            grade_distribution[grade] = {
                'count': count,
                'percentage': round(percentage, 1)
            }

        return {
            'total_students': len(results),
            'avg_score': round(np.mean(scores), 2),
            'min_score': round(min(scores), 2),
            'max_score': round(max(scores), 2),
            'std_score': round(np.std(scores), 2),
            'grade_distribution': grade_distribution
        }

    def __enter__(self):
        """Context manager uchun"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager uchun"""
        # Parametrlar ishlatilmaydi, lekin context manager protokoli uchun
        del exc_type, exc_val, exc_tb
        self.disconnect()
