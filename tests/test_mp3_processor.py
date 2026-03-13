import os
import sys
import unittest
import shutil
from unittest.mock import patch, MagicMock, mock_open
import builtins

# Импортируем тестируемый модуль
import mp3_processor as proc

class DummyEasyID3(dict):
    def __init__(self, path):
        # имитируем поведение EasyID3: наполним тестовыми тегами
        super().__init__({
            'title': ['Test Title'],
            'artist': ['© ÀÐÄÈÑ / Art Dictation Studio\x99, 2008']
        })
        self._path = path
    def save(self, path=None):
        # имитируем сохранение: создаём пустой файл чтобы тесты могли проверить наличие
        target = path or self._path
        with open(target, 'wb') as f:
            f.write(b'')  # пустой файл

class TestMp3Processor(unittest.TestCase):
    def setUp(self):
        self.test_dir = 'tests/data'
        os.makedirs(self.test_dir, exist_ok=True)
        self.dummy_mp3 = os.path.join(self.test_dir, 'test.mp3')
        # создаём "оригинальный" mp3-файл
        with open(self.dummy_mp3, 'wb') as f:
            f.write(b'ID3')  # минимальное содержание

    def tearDown(self):
        # Рекурсивно удаляем всю тестовую папку
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)


    @patch('mp3_processor.EasyID3', side_effect=DummyEasyID3)
    @patch('mp3_processor.shutil.copy')
    def test_parse_and_fix_tags_with_backup(self, mock_copy, mock_easy):
        # Тестируем parse_and_fix_tags: backup=True, dry_run=False
        res = proc.parse_and_fix_tags(self.dummy_mp3, decode_fn=proc.decode_, create_backup=True, dry_run=False)

        # Проверки результата структуры
        self.assertIsNone(res['error'])
        self.assertEqual(res['path'], self.dummy_mp3)
        self.assertIn('title', res['was'])
        self.assertIn('title', res['now'])
        self.assertTrue(res['backup_path'].endswith('-fix.mp3'))
        # shutil.copy должен быть вызван (не dry-run)
        mock_copy.assert_called_once_with(self.dummy_mp3, res['backup_path'])
        # backup файл должен существовать because DummyEasyID3.save created it
        self.assertTrue(os.path.exists(res['backup_path']))

    @patch('mp3_processor.EasyID3', side_effect=DummyEasyID3)
    @patch('mp3_processor.shutil.copy')
    def test_parse_and_fix_tags_dry_run(self, mock_copy, mock_easy):
        # backup=True, dry_run=True => shutil.copy не вызывается, файлов нет
        res = proc.parse_and_fix_tags(self.dummy_mp3, decode_fn=proc.decode_, create_backup=True, dry_run=True)
        self.assertIsNone(res['error'])
        mock_copy.assert_not_called()
        # файл не создан в dry-run
        self.assertFalse(os.path.exists(res['backup_path']))

    @patch('mp3_processor.EasyID3', side_effect=DummyEasyID3)
    def test_parse_and_fix_tags_no_backup(self, mock_easy):
        # backup=False => файл перезаписывается на месте
        res = proc.parse_and_fix_tags(self.dummy_mp3, decode_fn=proc.decode_, create_backup=False, dry_run=False)
        self.assertIsNone(res['error'])
        self.assertIsNone(res['backup_path'])
        self.assertEqual(res['updated_path'], self.dummy_mp3)
        # исходный файл перезаписан (DummyEasyID3.save создаёт его снова)
        self.assertTrue(os.path.exists(self.dummy_mp3))

    @patch('mp3_processor.EasyID3', side_effect=Exception("bad file"))
    def test_parse_and_fix_tags_error(self, mock_easy):
        # Если EasyID3 бросает исключение, результат должен содержать error
        res = proc.parse_and_fix_tags(self.dummy_mp3, decode_fn=proc.decode_, create_backup=True, dry_run=True)
        self.assertIsNotNone(res['error'])
        self.assertIn('bad file', res['error'])

    def test_decode_function(self):
        test_string = "© ÀÐÄÈÑ / Art Dictation Studio\x99, 2008"
        decoded_string = proc.decode_(test_string)
        self.assertEqual(decoded_string, "© АРДИС / Art Dictation Studio™, 2008")

    @patch('mp3_processor.EasyID3', side_effect=DummyEasyID3)
    @patch('mp3_processor.shutil.copy')
    def test_main_invocation_backup_and_recursive(self, mock_copy, mock_easy):
        # Создаём поддиректорию и файл для проверки рекурсивного прохода
        subdir = os.path.join(self.test_dir, 'sub')
        os.makedirs(subdir, exist_ok=True)
        subfile = os.path.join(subdir, 'subtest.mp3')
        with open(subfile, 'wb') as f:
            f.write(b'ID3')

        # Вызов main с --recursive и backup=yes
        test_argv = ['mp3_processor.py', self.test_dir, '--recursive', '--backup', 'yes']
        with patch.object(sys, 'argv', test_argv):
            proc.main()

        # ожидается, что shutil.copy вызывался как минимум для пары файлов
        self.assertTrue(mock_copy.called)

    @patch('mp3_processor.EasyID3', side_effect=DummyEasyID3)
    @patch('mp3_processor.shutil.copy')
    def test_main_invocation_dry_run_no_files_created(self, mock_copy, mock_easy):
        # Вызов main с --dry-run --backup yes -> не должно создавать файлов
        test_argv = ['mp3_processor.py', self.test_dir, '--dry-run', '--backup', 'yes']
        with patch.object(sys, 'argv', test_argv):
            proc.main()
        mock_copy.assert_not_called()
        # Убедимся, что backup-файлов нет
        self.assertNotIn('test-fix.mp3', os.listdir(self.test_dir))

if __name__ == '__main__':
    unittest.main()
