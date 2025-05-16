class Calculation:
    def __init__(self):
        self.calculationLine = ""

    def SetCalculationLine(self, value):
        self.calculationLine = value

    def SetLastSymbolCalculationLine(self, symbol):
        self.calculationLine += symbol

    def GetCalculationLine(self):
        return self.calculationLine

    def GetLastSymbol(self):
        return self.calculationLine[-1] if self.calculationLine else ""

    def DeleteLastSymbol(self):
        self.calculationLine = self.calculationLine[:-1]

calculation = Calculation()
calculation.SetCalculationLine("999")
print("Значение свойства:", calculation.GetCalculationLine())

calculation.SetLastSymbolCalculationLine("$")
print("Прибавить символ '$':", calculation.GetCalculationLine())

print("Полученный последний символ:", calculation.GetLastSymbol())

calculation.DeleteLastSymbol()
print("Удаление последнего символа:", calculation.GetCalculationLine())