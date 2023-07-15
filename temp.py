dictionary = {
    '13389': {'review': '13389', 'link': 'https://www.amazon.com/Flash-Furniture-Black-Folding-Table/dp/B00E8SZ4MY/ref=sr_1_11?keywords=table&qid=1688187548&sr=8-11', 'price': '44', 'rating': '4.6'},
    '6168': {'review': '6168', 'link': 'https://www.amazon.com/sspa/click?ie=UTF8&spc=MTo1MjgxODQwNTc5NTk4MTE3OjE2ODgxODc1NDg6c3BfbXRmOjIwMDE3ODIyOTU2NjA5ODo6MDo6&url=%2FFlash-Furniture-Granite-Plastic-Folding%2Fdp%2FB00MUYNLS2%2Fref%3Dsr_1_14_sspa%3Fkeywords%3Dtable%26qid%3D1688187548%26sr%3D8-14-spons%26sp_csd%3Dd2lkZ2V0TmFtZT1zcF9tdGY%26psc%3D1', 'price': '65', 'rating': '4.7'},
    '186': {'review': '186', 'link': 'https://www.amazon.com/Computer-Writing-Storage-Headphone-Bedroom/dp/B0BTD84D35/ref=sr_1_4?keywords=table&qid=1688187548&sr=8-4', 'price': '52', 'rating': '4.3'},
    '16844': {'review': '16844', 'link': 'https://www.amazon.com/Cosco-14678BLK1-Deluxe-Folding-Rectangle/dp/B00DOZTM3O/ref=sr_1_5?keywords=table&qid=1688187548&sr=8-5', 'price': '70', 'rating': '4.7'},
    '15078': {'review': '15078', 'link': 'https://www.amazon.com/Flash-Furniture-Kids-Folding-Table/dp/B00E84CGLA/ref=sr_1_7?keywords=table&qid=1688187548&sr=8-7', 'price': '24', 'rating': '4.6'}
}

sorted_items = sorted(dictionary.items(), reverse=True)  # Sort dictionary items by keys in descending order
result = dict(sorted(dictionary.items(), key=lambda x: int(x[0]), reverse=True)[:2])# Retrieve the first two items with highest keys

print(result)