"""
Rasch Evaluator Test Cases
RaschEvaluator klassi uchun test holatlar
"""

import unittest
import sys
import os
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

# src papkasini path ga qo'shish
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from rasch_evaluator import RaschEvaluator
from rasch_model import RaschModel, GradeLevel


class TestRaschEvaluatorImports(unittest.TestCase):
    """Import funksiyalarini test qilish"""
    
    def test_relative_import(self):
        """Relative import ishlashini test qilish"""
        try:
            from src.rasch_evaluator import RaschEvaluator
            self.assertTrue(True, "Relative import muvaffaqiyatli")
        except ImportError as e:
            self.fail(f"Relative import xatosi: {e}")
    
    def test_direct_import(self):
        """Direct import ishlashini test qilish"""
        try:
            # src papkasidan to'g'ridan-to'g'ri import
            import rasch_evaluator
            self.assertTrue(hasattr(rasch_evaluator, 'RaschEvaluator'))
        except ImportError as e:
            self.fail(f"Direct import xatosi: {e}")
    
    def test_rasch_model_import_in_evaluator(self):
        """RaschEvaluator ichida RaschModel import qilish"""
        evaluator = RaschEvaluator()
        self.assertIsInstance(evaluator.rasch_model, RaschModel)


class TestRaschEvaluatorDatabase(unittest.TestCase):
    """Ma'lumotlar bazasi bilan ishlashni test qilish"""
    
    def setUp(self):
        """Test uchun kerakli ma'lumotlarni tayyorlash"""
        self.evaluator = RaschEvaluator()
    
    def test_connection_parameters(self):
        """Ulanish parametrlarini test qilish"""
        self.assertEqual(self.evaluator.host, "localhost")
        self.assertEqual(self.evaluator.port, 5432)
        self.assertEqual(self.evaluator.database, "rash_test")
        self.assertEqual(self.evaluator.username, "postgres")
        self.assertEqual(self.evaluator.password, "password")
    
    @patch('psycopg2.connect')
    def test_connect_success(self, mock_connect):
        """Muvaffaqiyatli ulanishni test qilish"""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        result = self.evaluator.connect()
        
        self.assertTrue(result)
        self.assertEqual(self.evaluator.connection, mock_connection)
        mock_connect.assert_called_once_with(
            host="localhost",
            port=5432,
            database="rash_test",
            user="postgres",
            password="password"
        )
    
    @patch('psycopg2.connect')
    def test_connect_failure(self, mock_connect):
        """Ulanish xatosini test qilish"""
        mock_connect.side_effect = Exception("Connection failed")
        
        result = self.evaluator.connect()
        
        self.assertFalse(result)
        self.assertIsNone(self.evaluator.connection)


class TestRaschEvaluatorTestIdFiltering(unittest.TestCase):
    """Test ID bo'yicha filtrlashni test qilish"""
    
    def setUp(self):
        """Test uchun kerakli ma'lumotlarni tayyorlash"""
        self.evaluator = RaschEvaluator()
        self.evaluator.connection = Mock()
    
    def test_evaluate_users_with_test_id(self):
        """Test ID bilan foydalanuvchilarni baholash"""
        # Mock cursor va natijalar
        mock_cursor = Mock()
        mock_cursor.description = [
            ('user_id',), ('user_answers',), ('username',), 
            ('first_name',), ('last_name',)
        ]
        mock_cursor.fetchall.return_value = [
            (1, '{"correct_questions": [1, 2], "1": "A", "2": "B", "3": "C"}', 
             'user1', 'John', 'Doe'),
            (2, '{"correct_questions": [1, 3], "1": "A", "2": "C", "3": "A"}', 
             'user2', 'Jane', 'Smith')
        ]
        
        self.evaluator.connection.cursor.return_value = mock_cursor
        
        # Test ID bilan baholash
        test_id = "test_123"
        results = self.evaluator.evaluate_users(test_id)
        
        # SQL query test_id bilan chaqirilganini tekshirish
        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args
        query = call_args[0][0]
        params = call_args[0][1]
        
        self.assertIn("WHERE utr.test_id = %s", query)
        self.assertEqual(params[0], test_id)
    
    def test_evaluate_users_with_user_ids_filter(self):
        """Test ID va user IDs bilan filtrlash"""
        mock_cursor = Mock()
        mock_cursor.description = [
            ('user_id',), ('user_answers',), ('username',), 
            ('first_name',), ('last_name',)
        ]
        mock_cursor.fetchall.return_value = []
        
        self.evaluator.connection.cursor.return_value = mock_cursor
        
        test_id = "test_123"
        user_ids = [1, 2, 3]
        
        self.evaluator.evaluate_users(test_id, user_ids)
        
        # SQL query test_id va user_ids bilan chaqirilganini tekshirish
        call_args = mock_cursor.execute.call_args
        query = call_args[0][0]
        params = call_args[0][1]
        
        self.assertIn("WHERE utr.test_id = %s", query)
        self.assertIn("AND utr.user_id IN", query)
        self.assertEqual(params[0], test_id)
        self.assertEqual(params[1:], user_ids)


class TestRaschEvaluatorExcelSorting(unittest.TestCase):
    """Excel eksport va tartibga solishni test qilish"""
    
    def setUp(self):
        """Test uchun kerakli ma'lumotlarni tayyorlash"""
        self.evaluator = RaschEvaluator()
        
        # Test natijalari (tartibsiz)
        self.test_results = [
            {
                'user_id': 1, 'name': 'User1', 'correct_count': 30,
                'total_questions': 50, 'percentage': 60.0,
                'theta': 0.5, 'z_score': 0.5, 'rasch_score': 55.0, 'grade': 'B'
            },
            {
                'user_id': 2, 'name': 'User2', 'correct_count': 45,
                'total_questions': 50, 'percentage': 90.0,
                'theta': 2.0, 'z_score': 2.0, 'rasch_score': 70.0, 'grade': 'A+'
            },
            {
                'user_id': 3, 'name': 'User3', 'correct_count': 35,
                'total_questions': 50, 'percentage': 70.0,
                'theta': 1.0, 'z_score': 1.0, 'rasch_score': 60.0, 'grade': 'B+'
            },
            {
                'user_id': 4, 'name': 'User4', 'correct_count': 40,
                'total_questions': 50, 'percentage': 80.0,
                'theta': 1.5, 'z_score': 1.5, 'rasch_score': 65.0, 'grade': 'A'
            },
            {
                'user_id': 5, 'name': 'User5', 'correct_count': 20,
                'total_questions': 50, 'percentage': 40.0,
                'theta': -0.5, 'z_score': -0.5, 'rasch_score': 45.0, 'grade': 'NC'
            }
        ]
    
    def test_excel_export_sorting(self):
        """Excel eksport qilishda tartibga solish"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Temporary fayl yaratish
            filename = "test_results.xlsx"
            
            # output papkasini vaqtincha o'zgartirish
            original_makedirs = os.makedirs
            original_join = os.path.join
            
            def mock_makedirs(path, exist_ok=False):
                return True
            
            def mock_join(*args):
                if args[0] == 'output':
                    return os.path.join(temp_dir, args[1])
                return original_join(*args)
            
            with patch('os.makedirs', mock_makedirs), \
                 patch('os.path.join', mock_join):
                
                filepath = self.evaluator.export_to_excel(
                    "test_123", self.test_results, filename
                )
                
                # Fayl yaratilganini tekshirish
                expected_path = os.path.join(temp_dir, filename)
                self.assertTrue(os.path.exists(expected_path))
                
                # Excel faylni o'qish va tartibni tekshirish
                df = pd.read_excel(expected_path)
                
                # Birinchi qator eng yuqori ball bo'lishi kerak
                self.assertEqual(df.iloc[0]['grade'], 'A+')
                self.assertEqual(df.iloc[0]['rasch_score'], 70.0)
                
                # Oxirgi qator eng past ball bo'lishi kerak
                self.assertEqual(df.iloc[-1]['grade'], 'NC')
                self.assertEqual(df.iloc[-1]['rasch_score'], 45.0)
                
                # Tartib to'g'riligini tekshirish
                scores = df['rasch_score'].tolist()
                self.assertEqual(scores, sorted(scores, reverse=True))
    
    def test_grade_order_priority(self):
        """Daraja tartibining ustuvorligini test qilish"""
        # Bir xil ballga ega, lekin turli darajali natijalar
        same_score_results = [
            {
                'user_id': 1, 'name': 'User1', 'rasch_score': 60.0, 'grade': 'B+'
            },
            {
                'user_id': 2, 'name': 'User2', 'rasch_score': 60.0, 'grade': 'A'
            }
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = "test_grade_order.xlsx"
            
            with patch('os.makedirs'), \
                 patch('os.path.join', return_value=os.path.join(temp_dir, filename)):
                
                self.evaluator.export_to_excel(
                    "test_123", same_score_results, filename
                )
                
                df = pd.read_excel(os.path.join(temp_dir, filename))
                
                # A daraja B+ dan yuqorida bo'lishi kerak
                self.assertEqual(df.iloc[0]['grade'], 'A')
                self.assertEqual(df.iloc[1]['grade'], 'B+')


if __name__ == '__main__':
    # Test ishga tushirish
    unittest.main(verbosity=2)
