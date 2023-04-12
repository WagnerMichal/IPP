# Implementační dokumentace k 1. úloze do IPP 2022/2023

Jméno a příjmení: Michal Wagner <br>
Login: xwagne12

## Implementace ```parse.php```

Při tvorbě skriptu ```parse.php``` bylo využito vzoru abstraktní továrny a objektově orientovaného programování.

### Zpracovaní argumentů
Třída ```ArgumentParser``` provede kontrolu vstupních argumentů od uživatele metodou ```args_check()```. V případě, že je více jak jeden argument se provede kontrola zda se počet vstupních argumentů rovná dvoum a hodnota 2. argumentu je ```--help```, Pokud ano, tak se zobrazí nápověda a skript se ukončí, jinak se ukončí s návratovým kódem ```10```.

### Zpracování kódu
Třída ```Parser``` zpracovává vstupní kód. Tato třída inicializuje třídu pro generování XML. Zpracování kódu je prováděno metodou ```parse()```. Provede se kontrola zda je na prvním řádku hlavička a případné komentáře a bílé znaky jsou odfiltrovány. Program dále započne smyčku, ve které zpracovává vstupní kód po řádku. Z každého řádku jsou odstraněny bílé znaky a komentáře. V případě, že následně řádek není prázdný, tak se rozdělí podle bílých znaků a provede se zpracovaní instrukce. V případě konce souboru je vytisknuto XML na standardní výstup.

### Zpracování instrukcí
Abstraktní třída ```Instructions``` je základem pro definování ostatních tříd instrukcí podle počtu jejich operandů, které slouží ke zpracování instukcí. Definuje kontrolu zápisu instrukce, reprezentaci XML a kontrolu typů operandů instrukcí. Ověřování operandů instrukcí je prováděno regulárním výrazy.

Zpracování instrukce je provedeno na řádku rozděleného podle bílých znaků. Pomocí kontroly počtu operandů a kódu operace instrukce je vytvořena instance instrukce. Poté se zavolá metoda pro kontrolu instrukce a repreztentaci xml.