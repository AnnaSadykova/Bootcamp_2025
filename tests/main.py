import pytest
import os

if __name__ == "__main__":
    # Получаем абсолютный путь к директории с тестами
    tests_dir = os.path.join(os.path.dirname(__file__), "api")
    
    pytest.main([
        tests_dir,
        # "-v",
        # "--cov=api",
        # "--cov-report=html:cov_html"
    ])
    
    # Открытие отчета в браузере (только для Windows)
    # if os.name == 'nt':
    #     os.system("start cov_html/index.html")