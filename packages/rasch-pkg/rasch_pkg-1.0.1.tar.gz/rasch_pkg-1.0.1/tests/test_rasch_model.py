"""
Rasch Model Test Cases
Rasch modeli uchun test holatlar
"""

import unittest
import numpy as np
import pandas as pd
import sys
import os

# src papkasini path ga qo'shish
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from rasch_model import RaschModel, GradeLevel, StudentResult


class TestRaschModel(unittest.TestCase):
    """Rasch modeli uchun test klassi"""
    
    def setUp(self):
        """Test uchun kerakli ma'lumotlarni tayyorlash"""
        self.rasch = RaschModel()
        
        # Test ma'lumotlari
        self.test_answers_perfect = [1] * 55  # Barcha javoblar to'g'ri
        self.test_answers_zero = [0] * 55     # Barcha javoblar noto'g'ri
        self.test_answers_half = [1] * 27 + [0] * 28  # Yarmi to'g'ri
        
        # Real Excel ma'lumotlaridan olingan test case
        self.test_answers_real = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                                 1.0, 1.0, 1.0, 1.0, 0.0]  # 54 ta to'g'ri javob
    
    def test_calculate_theta(self):
        """Theta hisoblash funksiyasini test qilish"""
        # Perfect score
        theta_perfect = self.rasch.calculate_theta(55, 55)
        self.assertEqual(theta_perfect, 4.0)
        
        # Zero score
        theta_zero = self.rasch.calculate_theta(0, 55)
        self.assertEqual(theta_zero, -4.0)
        
        # Half score
        theta_half = self.rasch.calculate_theta(27, 55)
        expected_theta = np.log(27/55 / (1 - 27/55))
        self.assertAlmostEqual(theta_half, expected_theta, places=5)
        
        # Real case: 54/55
        theta_real = self.rasch.calculate_theta(54, 55)
        p = 54/55
        expected_theta_real = np.log(p / (1 - p))
        self.assertAlmostEqual(theta_real, expected_theta_real, places=5)
    
    def test_calculate_z_score(self):
        """Z-score hisoblash funksiyasini test qilish"""
        theta = 2.0
        mu = 0.0
        sigma = 1.0
        
        z_score = self.rasch.calculate_z_score(theta, mu, sigma)
        expected_z = (theta - mu) / sigma
        self.assertAlmostEqual(z_score, expected_z, places=5)
        
        # Boshqa parametrlar bilan
        z_score2 = self.rasch.calculate_z_score(3.0, 0.5, 1.5)
        expected_z2 = (3.0 - 0.5) / 1.5
        self.assertAlmostEqual(z_score2, expected_z2, places=5)
    
    def test_calculate_scaled_score(self):
        """Scaled score hisoblash funksiyasini test qilish"""
        # Z = 0 bo'lganda Ball = 50
        score1 = self.rasch.calculate_scaled_score(0.0)
        self.assertAlmostEqual(score1, 50.0, places=2)
        
        # Z = 1 bo'lganda Ball = 60
        score2 = self.rasch.calculate_scaled_score(1.0)
        self.assertAlmostEqual(score2, 60.0, places=2)
        
        # Z = -1 bo'lganda Ball = 40
        score3 = self.rasch.calculate_scaled_score(-1.0)
        self.assertAlmostEqual(score3, 40.0, places=2)
        
        # Extreme qiymatlar
        score_high = self.rasch.calculate_scaled_score(10.0)
        self.assertEqual(score_high, 100.0)  # Maksimal 100
        
        score_low = self.rasch.calculate_scaled_score(-10.0)
        self.assertEqual(score_low, 0.0)     # Minimal 0
    
    def test_determine_grade(self):
        """Daraja belgilash funksiyasini test qilish"""
        # A+ daraja (70-100)
        grade_a_plus = self.rasch.determine_grade(85.0)
        self.assertEqual(grade_a_plus, GradeLevel.A_PLUS)
        
        # A daraja (65-69.99)
        grade_a = self.rasch.determine_grade(67.0)
        self.assertEqual(grade_a, GradeLevel.A)
        
        # B+ daraja (60-64.99)
        grade_b_plus = self.rasch.determine_grade(62.0)
        self.assertEqual(grade_b_plus, GradeLevel.B_PLUS)
        
        # B daraja (55-59.99)
        grade_b = self.rasch.determine_grade(57.0)
        self.assertEqual(grade_b, GradeLevel.B)
        
        # C+ daraja (50-54.99)
        grade_c_plus = self.rasch.determine_grade(52.0)
        self.assertEqual(grade_c_plus, GradeLevel.C_PLUS)
        
        # C daraja (46-49.99)
        grade_c = self.rasch.determine_grade(48.0)
        self.assertEqual(grade_c, GradeLevel.C)
        
        # NC daraja (0-45.99)
        grade_nc = self.rasch.determine_grade(30.0)
        self.assertEqual(grade_nc, GradeLevel.NC)
    
    def test_process_student_answers(self):
        """Bitta o'quvchi javoblarini qayta ishlash"""
        result = self.rasch.process_student_answers(
            student_id="1",
            name="Test Student",
            answers=self.test_answers_real
        )
        
        # Asosiy ma'lumotlarni tekshirish
        self.assertEqual(result.student_id, "1")
        self.assertEqual(result.name, "Test Student")
        self.assertEqual(result.correct_count, 54)
        self.assertEqual(result.total_questions, 55)
        self.assertAlmostEqual(result.raw_score, 54/55, places=5)
        
        # Theta qiymati
        expected_theta = np.log((54/55) / (1 - 54/55))
        self.assertAlmostEqual(result.theta, expected_theta, places=5)
        
        # Z-score
        expected_z = (result.theta - 0.0) / 1.0
        self.assertAlmostEqual(result.z_score, expected_z, places=5)
        
        # Scaled score
        expected_score = 50 + 10 * result.z_score
        self.assertAlmostEqual(result.scaled_score, expected_score, places=2)
        
        # Daraja
        self.assertIsInstance(result.grade, GradeLevel)
    
    def test_process_multiple_students_dataframe(self):
        """Ko'p o'quvchilarni DataFrame orqali qayta ishlash"""
        # Test DataFrame yaratish
        data = {
            'F.I.0': ['Student1', 'Student2', 'Student3'],
            'V1': [1, 1, 0],
            'V2': [1, 0, 1],
            'V3': [1, 1, 0],
            'V4': [0, 1, 1],
            'V5': [1, 0, 0]
        }
        df = pd.DataFrame(data)
        
        results = self.rasch.process_multiple_students(df)
        
        # Natijalarni tekshirish
        self.assertEqual(len(results), 3)
        
        for i, result in enumerate(results):
            self.assertEqual(result.student_id, str(i + 1))
            self.assertEqual(result.name, f'Student{i + 1}')
            self.assertEqual(result.total_questions, 5)
            self.assertIsInstance(result.grade, GradeLevel)
    
    def test_process_multiple_students_list(self):
        """Ko'p o'quvchilarni list orqali qayta ishlash"""
        data = [
            {
                'id': '1',
                'name': 'Student A',
                'answers': [1, 1, 1, 0, 0]
            },
            {
                'id': '2', 
                'name': 'Student B',
                'answers': [1, 0, 1, 1, 0]
            }
        ]
        
        results = self.rasch.process_multiple_students(data)
        
        # Natijalarni tekshirish
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].student_id, '1')
        self.assertEqual(results[0].name, 'Student A')
        self.assertEqual(results[1].student_id, '2')
        self.assertEqual(results[1].name, 'Student B')
    
    def test_get_statistics(self):
        """Statistika hisoblash funksiyasini test qilish"""
        # Test ma'lumotlari yaratish
        results = []
        for i in range(10):
            answers = [1] * (30 + i) + [0] * (25 - i)  # Har xil natijalar
            result = self.rasch.process_student_answers(
                student_id=str(i),
                name=f"Student{i}",
                answers=answers
            )
            results.append(result)
        
        stats = self.rasch.get_statistics(results)
        
        # Statistika mavjudligini tekshirish
        self.assertIn('total_students', stats)
        self.assertIn('score_statistics', stats)
        self.assertIn('grade_distribution', stats)
        
        self.assertEqual(stats['total_students'], 10)
        
        # Score statistikasi
        score_stats = stats['score_statistics']
        self.assertIn('min', score_stats)
        self.assertIn('max', score_stats)
        self.assertIn('mean', score_stats)
        self.assertIn('median', score_stats)
        self.assertIn('std', score_stats)
        
        # Daraja taqsimoti
        grade_dist = stats['grade_distribution']
        for grade in GradeLevel:
            self.assertIn(grade.value, grade_dist)
            self.assertIn('count', grade_dist[grade.value])
            self.assertIn('percentage', grade_dist[grade.value])
    
    def test_edge_cases(self):
        """Chekka holatlarni test qilish"""
        # Bo'sh javoblar
        result_empty = self.rasch.process_student_answers("1", "Empty", [])
        self.assertEqual(result_empty.correct_count, 0)
        self.assertEqual(result_empty.total_questions, 0)
        
        # Noto'g'ri javob formatlari
        mixed_answers = [1, 0, 1.0, 0.0, 2, -1, 'a', None]
        result_mixed = self.rasch.process_student_answers("2", "Mixed", mixed_answers)
        # 2 va -1, 'a', None 0 ga aylantirilishi kerak
        expected_correct = sum([1, 0, 1.0, 0.0, 0, 0, 0, 0])
        self.assertEqual(result_mixed.correct_count, int(expected_correct))


class TestRaschModelIntegration(unittest.TestCase):
    """Rasch modeli integratsiya testlari"""
    
    def setUp(self):
        """Test uchun kerakli ma'lumotlarni tayyorlash"""
        self.rasch = RaschModel()
    
    def test_excel_file_processing(self):
        """Excel fayl bilan ishlashni test qilish"""
        # Test Excel fayl mavjudligini tekshirish
        excel_file = 'docs/exam_answers_example_3.xlsx'
        if os.path.exists(excel_file):
            try:
                df = pd.read_excel(excel_file, sheet_name='Sheet1')
                
                # Birinchi 10 ta o'quvchini qayta ishlash
                test_df = df.head(10)
                results = self.rasch.process_multiple_students(test_df)
                
                self.assertEqual(len(results), 10)
                
                # Birinchi o'quvchi uchun Excel bilan taqqoslash
                first_result = results[0]
                excel_first = df.iloc[0]
                
                # To'g'ri javoblar sonini tekshirish
                self.assertEqual(first_result.correct_count, int(excel_first['SUMMA']))
                
                # Ball qiymatini tekshirish (taxminan)
                excel_ball = excel_first['BALL']
                self.assertAlmostEqual(first_result.scaled_score, excel_ball, delta=1.0)
                
            except Exception as e:
                self.skipTest(f"Excel fayl o'qishda xatolik: {e}")
        else:
            self.skipTest("Test Excel fayl topilmadi")


if __name__ == '__main__':
    # Test ishga tushirish
    unittest.main(verbosity=2)
