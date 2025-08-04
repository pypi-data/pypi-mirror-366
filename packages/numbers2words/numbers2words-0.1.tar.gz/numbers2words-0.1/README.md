🧮 numbers2words
Convert numbers into words in:

Tamil

🇮🇳 Indian English format (e.g., lakh, crore)

International English format (e.g., million, billion)

Tamil Format — num2wordsTA
Uses Tamil number system (e.g., கோடி, இலட்சம்)

Supports up to 18 digits before the decimal

Decimal part (if present) is stripped to 2 digits

✅ Example

from numbers2words.numbers2words import num2wordsTA

print(num2wordsTA(12345678))
# ('ஒரு கோடியே இருபத்து மூன்று இலட்சத்து நாற்பத்து ஐந்து ஆயிரத்து அறுநூற்று எழுபத்து எட்டு', '')

print(num2wordsTA(1234567.80))
# ('பன்னிரண்டு இலட்சத்து முப்பத்து நான்கு ஆயிரத்து ஐநூற்று அறுபத்து ஏழு', 'எண்பது')

print(num2wordsTA("12345678"))
print(num2wordsTA("1234567.80"))
🇮🇳 Indian English Format — num2wordsIND
Uses Indian number system (e.g., lakh, crore)

Supports up to 17 digits before the decimal

Decimal part is stripped to 2 digits

✅ Example

from numbers2words.numbers2words import num2wordsIND

print(num2wordsIND("12345678"))
# ('one crore twenty three lakh forty five thousand six hundred and seventy eight', '')

print(num2wordsIND("1234567.80"))
# ('twelve lakh thirty four thousand five hundred and sixty seven', 'eighty')

print(num2wordsIND(12345678))
print(num2wordsIND(1234567.80))
🌍 International Format — num2wordsSI
Uses standard international format (e.g., million, billion)

Supports up to 17 digits before the decimal

Decimal part is stripped to 2 digits

✅ Example

from numbers2words.numbers2words import num2wordsSI

print(num2wordsSI(12345678))
# ('twelve million three hundred and forty five thousand six hundred and seventy eight', '')

print(num2wordsSI(1234567.80))
# ('one million two hundred and thirty four thousand five hundred and sixty seven', 'eighty')

print(num2wordsSI("12345678"))
print(num2wordsSI("1234567.80"))















