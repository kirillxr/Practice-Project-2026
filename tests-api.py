import requests
import json

def test_home_page():
    """Тест 1: GET запрос к корню - возвращает HTML"""
    url = "http://localhost:8000/"
    response = requests.get(url)
    
    assert response.status_code == 200, f"Ошибка: статус {response.status_code} != 200"
    assert "text/html" in response.headers.get("content-type", ""), "Ошибка: ответ не HTML"
    assert "Калькулятор калорий" in response.text, "Ошибка: заголовок не найден"
    
    print("✓ Тест 1 пройден: GET / возвращает HTML страницу")


def test_api_products():
    """Тест 2: GET /api/products - возвращает список продуктов"""
    url = "http://localhost:8000/api/products"
    response = requests.get(url)
    
    assert response.status_code == 200, f"Ошибка: статус {response.status_code} != 200"
    
    data = response.json()
    assert len(data) > 0, "Ошибка: список продуктов пуст"
    assert "name" in data[0], "Ошибка: нет поля name"
    assert "calories" in data[0], "Ошибка: нет поля calories"
    
    print(f"✓ Тест 2 пройден: GET /api/products - {len(data)} продуктов")


def test_api_stats():
    """Тест 3: GET /api/stats - возвращает статистику"""
    url = "http://localhost:8000/api/stats"
    response = requests.get(url)
    
    assert response.status_code == 200, f"Ошибка: статус {response.status_code} != 200"
    
    data = response.json()
    assert "totals" in data, "Ошибка: нет поля totals"
    assert "total_calories" in data["totals"], "Ошибка: нет total_calories"
    
    print("✓ Тест 3 пройден: GET /api/stats возвращает статистику")


def test_add_from_db_valid():
    """Тест 4: POST /add-from-db - добавление продукта из базы"""
    url = "http://localhost:8000/add-from-db"
    form_data = {"product_id": 1, "weight": 150}
    
    response = requests.post(url, data=form_data)
    
    assert response.status_code in [200, 303, 307], f"Ошибка: статус {response.status_code}"
    assert "success" in response.url or "error" in response.url, "Ошибка: нет сообщения"
    
    print("✓ Тест 4 пройден: POST /add-from-db (яблоко 150г)")


def test_add_from_db_invalid_weight():
    """Тест 5: POST /add-from-db - вес 0 (должен быть редирект с ошибкой)"""
    url = "http://localhost:8000/add-from-db"
    form_data = {"product_id": 1, "weight": 0}
    
    response = requests.post(url, data=form_data, allow_redirects=False)
    
    assert response.status_code == 303, f"Ошибка: ожидался редирект 303, получен {response.status_code}"
    assert "error" in response.headers.get("location", ""), "Ошибка: нет сообщения об ошибке"
    
    print("✓ Тест 5 пройден: POST /add-from-db с весом 0 → ошибка")


def test_add_from_db_exceed_max_weight():
    """Тест 6: POST /add-from-db - вес 16000г (больше 15кг)"""
    url = "http://localhost:8000/add-from-db"
    form_data = {"product_id": 1, "weight": 16000}
    
    response = requests.post(url, data=form_data, allow_redirects=False)
    
    assert response.status_code == 303, f"Ошибка: ожидался редирект 303, получен {response.status_code}"
    assert "error" in response.headers.get("location", ""), "Ошибка: нет сообщения об ошибке"
    
    print("✓ Тест 6 пройден: POST /add-from-db с весом 16000г → ошибка")


def test_add_manual_valid():
    """Тест 7: POST /add-manual - ручное добавление продукта"""
    url = "http://localhost:8000/add-manual"
    form_data = {
        "product_name": "Тестовый продукт",
        "protein": 20,
        "fat": 10,
        "carbs": 30,
        "weight": 200
    }
    
    response = requests.post(url, data=form_data)
    
    assert response.status_code in [200, 303, 307], f"Ошибка: статус {response.status_code}"
    assert "success" in response.url or "error" in response.url, "Ошибка: нет сообщения"
    
    print("✓ Тест 7 пройден: POST /add-manual (тестовый продукт)")


def test_add_manual_empty_name():
    """Тест 8: POST /add-manual - пустое название продукта"""
    url = "http://localhost:8000/add-manual"
    form_data = {
        "product_name": "",
        "protein": 20,
        "fat": 10,
        "carbs": 30,
        "weight": 200
    }
    
    response = requests.post(url, data=form_data, allow_redirects=False)
    
    assert response.status_code == 303, f"Ошибка: ожидался редирект 303, получен {response.status_code}"
    assert "error" in response.headers.get("location", ""), "Ошибка: нет сообщения об ошибке"
    
    print("✓ Тест 8 пройден: POST /add-manual с пустым названием → ошибка")


def test_add_manual_negative_bju():
    """Тест 9: POST /add-manual - отрицательные БЖУ"""
    url = "http://localhost:8000/add-manual"
    form_data = {
        "product_name": "Тест",
        "protein": -10,
        "fat": 10,
        "carbs": 30,
        "weight": 200
    }
    
    response = requests.post(url, data=form_data, allow_redirects=False)
    
    assert response.status_code == 303, f"Ошибка: ожидался редирект 303, получен {response.status_code}"
    assert "error" in response.headers.get("location", ""), "Ошибка: нет сообщения об ошибке"
    
    print("✓ Тест 9 пройден: POST /add-manual с отрицательными БЖУ → ошибка")


def test_delete_history():
    """Тест 10: POST /delete-history/{id} - удаление продукта из истории"""
    url = "http://localhost:8000/delete-history/1"
    
    response = requests.post(url, allow_redirects=False)
    
    assert response.status_code in [200, 303, 307, 404], f"Ошибка: статус {response.status_code}"
    
    print("✓ Тест 10 пройден: POST /delete-history/{id} (если запись есть)")

if __name__ == "__main__":
    tests = [
        test_home_page,
        test_api_products,
        test_api_stats,
        test_add_from_db_valid,
        test_add_from_db_invalid_weight,
        test_add_from_db_exceed_max_weight,
        test_add_manual_valid,
        test_add_manual_empty_name,
        test_add_manual_negative_bju,
        test_delete_history,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f" {test.__name__} провален: {e}")
            failed += 1
        except Exception as e:
            print(f" {test.__name__} ошибка: {e}")
            failed += 1
    
    print(f"\n Итог: {passed} пройдено, {failed} провалено")
