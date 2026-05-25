def calc(protein=0, fat=0, carbs=0, weight=100, from_product=None):
    if from_product:
        protein = from_product.get("protein", 0)
        fat = from_product.get("fat", 0)
        carbs = from_product.get("carbs", 0)
        calories = from_product.get("calories", 0)
    else:
        calories = protein * 4 + fat * 9 + carbs * 4
    
    ratio = weight / 100
    return {
        "calories": round(calories * ratio, 1),
        "protein": round(protein * ratio, 1),
        "fat": round(fat * ratio, 1),
        "carbs": round(carbs * ratio, 1)
    }