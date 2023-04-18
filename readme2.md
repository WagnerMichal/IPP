# Implementační dokumentace k 2. úloze do IPP 2022/2023
Jméno a příjmení: Michal Wagner
Login: xwagne12

## `interpret.py`
Při tvorbě `interpret.py` bylo využito principů objektově orientovaného programování. Skript je rozdělen na několik logických částí, které se nacházi ve složce `libs_interpret`.

### Zpracování agrumentů
Zpracování argumentů probíhá ve třídě `XMLCheck` v metodě `arguments_parse()` s pomocí třídy `ArgumentParser` z knihovny `argparse`.

### Načítání a zpracování XML
Načítání a kontrola XML reprezentace kódu IPPCode23 se provádí v zbylých metodách třídy `XMLCheck`. Na zpracování XML se využívá knihovna `xml.etree.ElementTree`. Třídá provádí kontroly struktury XML a seřadí ve správném pořadí instrukce pomocí atributu order. Kontroluje se zda je správný počet argumentů pomocí slovníku který obsahuje `opcodes` a jejich očekávaný počet argumentů. Následně inicializuje objekty tříd instrukcí a uloží je do výsledného pole `instructions_list`.

### Instrukce
Pro jednotlivé operace instrukcí je vytvořen slovník mapující jejich instance. Každá instrukce je potomek třídy `Instruction` a zásobníkové instrukce jsou potomky nezásobníkových verzí. V této třídě se navíc nachází metoda pro získání symbolů z rámce a ze zásobníku.

V souboru `argument.py` jsou vytvořeny funkce pro sémantickou kontrolu operandů instrukcí. Tyto funkce například kontrolují operace mezi nepovolenými datovými typy. Typy operandů zde mají vytvořeny třídy pro jejich uložení a větší přehlednost.

### Interpretace instrukcí
Interpretace instrukcí je provedena ve třídě `Core`, která spouští jednotlivé instrukce z pole ve správném pořadí. Třída se navíc stará o rámce a obsahuje další metody pro práci s instrukcemi. Mezi tyto metody patří uložení symbolu na zásobník, ověření existence proměnné v rámci, získání, nastavení a definování proměnné, ověření existence návěští a získání symbolu.

## Rozšíření
Díky dobrému původnímu návrhu byla implementace rozšíření jednoduchou záležitostí.
### STACK
Instrukce rozšíření stack jsou potomky nezásobníkových verzí instrukcí. Jsou pro ně navíc vytvořeny metody pro uložení symbolu na zásobník a získání symbolu ze zásobníku.
### FLOAT
Rozšíření FLOAT je implementované přidáním nového podporovaného datového typu a přidání sémantické kontroly pro datový typ `float`. Pro převádění jsou využity funkce `float.fromhex()` a `float.hex()`.

## UML diagram
Kvůli velkému počtu tříd v mé implementaci může být UML diagram nečitelný, proto jsem přidal fotku do složky UML-diagram pro lepší přehlednost.
![UML-diagram](/UML-diagram/classes.png)