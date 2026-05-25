import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from calculator import calc

def test_calc_bju_to_calories():
    """Тест 1: Расчёт калорий по БЖУ (24/3.6/0 → 128.4 ккал на 100г)"""
    result = calc(protein=24, fat=3.6, carbs=0, weight=100)
    expected = 128.4
    assert abs(result["calories"] - expected) < 0.1, f"Ошибка: {result['calories']} != {expected}"
    print("✓ Тест 1 пройден: БЖУ 24/3.6/0 → 128.4 ккал")

def test_calc_zero_bju():
    """Тест 2: Нулевые БЖУ → 0 калорий"""
    result = calc(protein=0, fat=0, carbs=0, weight=100)
    expected = 0
    assert result["calories"] == expected, f"Ошибка: {result['calories']} != {expected}"
    print("✓ Тест 2 пройден: Нулевые БЖУ → 0 ккал")

def test_calc_weight_150():
    """Тест 3: Пересчёт на 150 грамм (курица 24/3.6/0 → 192.6 ккал)"""
    result = calc(protein=24, fat=3.6, carbs=0, weight=150)
    expected = 192.6
    assert abs(result["calories"] - expected) < 0.1, f"Ошибка: {result['calories']} != {expected}"
    assert abs(result["protein"] - 36.0) < 0.1, f"Ошибка: белки {result['protein']} != 36.0"
    assert abs(result["fat"] - 5.4) < 0.1, f"Ошибка: жиры {result['fat']} != 5.4"
    print("✓ Тест 3 пройден: 150г курицы → 192.6 ккал, 36г белка, 5.4г жира")

def test_calc_weight_zero():
    """Тест 4: Вес 0 → все значения 0"""
    result = calc(protein=24, fat=3.6, carbs=0, weight=0)
    assert result["calories"] == 0, f"Ошибка: калории {result['calories']} != 0"
    assert result["protein"] == 0, f"Ошибка: белки {result['protein']} != 0"
    assert result["fat"] == 0, f"Ошибка: жиры {result['fat']} != 0"
    print("✓ Тест 4 пройден: Вес 0 → всё 0")

def test_calc_weight_negative():
    """Тест 5: Отрицательный вес → отрицательные значения"""
    result = calc(protein=24, fat=3.6, carbs=0, weight=-50)
    expected = -64.2
    assert abs(result["calories"] - expected) < 0.1, f"Ошибка: {result['calories']} != {expected}"
    print("✓ Тест 5 пройден: Отрицательный вес даёт отрицательные калории")

def test_calc_from_product_db():
    """Тест 6: Расчёт из продукта базы данных (яблоко 52 ккал, 150г → 78 ккал)"""
    product = {"calories": 52, "protein": 0.3, "fat": 0.2, "carbs": 14}
    result = calc(from_product=product, weight=150)
    expected_calories = 78.0
    assert abs(result["calories"] - expected_calories) < 0.1, f"Ошибка: {result['calories']} != {expected_calories}"
    print("✓ Тест 6 пройден: Яблоко 150г → 78 ккал")

def test_calc_negative_bju():
    """Тест 7: Отрицательные БЖУ → отрицательные калории"""
    result = calc(protein=-10, fat=0, carbs=0, weight=100)
    expected = -40
    assert result["calories"] == expected, f"Ошибка: {result['calories']} != {expected}"
    print("✓ Тест 7 пройден: Отрицательные БЖУ → -40 ккал")

def test_calc_manual_product():
    """Тест 8: Полный расчёт ручного продукта (20/10/30 на 200г)"""
    result = calc(protein=20, fat=10, carbs=30, weight=200)
    expected_calories = 580
    expected_protein = 40
    expected_fat = 20
    expected_carbs = 60
    assert abs(result["calories"] - expected_calories) < 0.1, f"Ошибка: калории {result['calories']} != {expected_calories}"
    assert abs(result["protein"] - expected_protein) < 0.1, f"Ошибка: белки {result['protein']} != {expected_protein}"
    assert abs(result["fat"] - expected_fat) < 0.1, f"Ошибка: жиры {result['fat']} != {expected_fat}"
    assert abs(result["carbs"] - expected_carbs) < 0.1, f"Ошибка: углеводы {result['carbs']} != {expected_carbs}"
    print("✓ Тест 8 пройден: БЖУ 20/10/30 на 200г → 580 ккал")

def test_calc_large_weight():
    """Тест 9: Большой вес (15000г = 15кг)"""
    result = calc(protein=24, fat=3.6, carbs=0, weight=15000)
    expected = 19260
    assert abs(result["calories"] - expected) < 1, f"Ошибка: {result['calories']} != {expected}"
    print("✓ Тест 9 пройден: 15кг курицы → 19260 ккал")

def test_calc_decimal_weight():
    """Тест 10: Дробный вес (150.5 грамм)"""
    result = calc(protein=24, fat=3.6, carbs=0, weight=150.5)
    ratio = 150.5 / 100
    expected = round(128.4 * ratio, 1)
    assert abs(result["calories"] - expected) < 0.1, f"Ошибка: {result['calories']} != {expected}"
    print("✓ Тест 10 пройден: Дробный вес 150.5г корректно обрабатывается")

if __name__ == "__main__":
    tests = [
        test_calc_bju_to_calories,
        test_calc_zero_bju,
        test_calc_weight_150,
        test_calc_weight_zero,
        test_calc_weight_negative,
        test_calc_from_product_db,
        test_calc_negative_bju,
        test_calc_manual_product,
        test_calc_large_weight,
        test_calc_decimal_weight,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"{test.__name__} провален: {e}")
            failed += 1
        except Exception as e:
            print(f"{test.__name__} ошибка: {e}")
            failed += 1
    
    print(f"\nИтог: {passed} пройдено, {failed} провалено из {len(tests)} тестов")
