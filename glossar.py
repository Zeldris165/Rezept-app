"""
glossar.py
==========
Statische Daten für das Kochlexikon: Begriff, Kategorie, Erklärung und
Pfad zur passenden Illustration. Bewusst als einfache Liste gehalten,
lässt sich aber jederzeit in eine eigene DB-Tabelle umziehen, falls
später z.B. eigene Begriffe hinzugefügt werden sollen.
"""

BEGRIFFE = [
    {
        "name": "Blanchieren",
        "kategorie": "Feuchte Garmethoden",
        "bild": "assets/flaticon/blanchieren.png",
        "erklaerung": (
            "Lebensmittel (meist Gemüse) werden kurz in kochendes Wasser gegeben "
            "und danach sofort in Eiswasser abgeschreckt. Das stoppt den Garprozess "
            "abrupt, erhält die knackige Textur und eine kräftige Farbe. Wird oft "
            "vor dem Einfrieren von Gemüse oder zum Lösen von Tomatenhaut genutzt."
        ),
    },
    {
        "name": "Dünsten",
        "kategorie": "Feuchte Garmethoden",
        "bild": "assets/flaticon/duensten2.png",
        "erklaerung": (
            "Garen in wenig Flüssigkeit (Wasser, Brühe oder im eigenen Saft) bei "
            "geringer Hitze, meist zugedeckt. Schonender als Kochen, das Gargut "
            "bleibt zart und die Aromen gehen kaum verloren."
        ),
    },
    {
        "name": "Dämpfen",
        "kategorie": "Feuchte Garmethoden",
        "bild": "assets/flaticon/daempfen.png",
        "erklaerung": (
            "Garen im Wasserdampf, ohne dass das Lebensmittel direkten Kontakt zum "
            "kochenden Wasser hat (z. B. im Dampfeinsatz oder Bambuskorb). Besonders "
            "schonend für Vitamine und Textur, typisch für Gemüse, Fisch oder Knödel."
        ),
    },
    {
        "name": "Kochen",
        "kategorie": "Feuchte Garmethoden",
        "bild": "assets/flaticon/kochen.png",
        "erklaerung": (
            "Garen in sprudelnd kochender Flüssigkeit bei ca. 100°C. Die stärkste "
            "Form der feuchten Hitze, geeignet für Nudeln, Kartoffeln oder Eier."
        ),
    },
    {
        "name": "Sieden (Köcheln)",
        "kategorie": "Feuchte Garmethoden",
        "bild": "assets/flaticon/simmern.png",
        "erklaerung": (
            "Sanftes Garen knapp unter dem Siedepunkt, bei dem nur vereinzelt kleine "
            "Bläschen aufsteigen. Wird oft für Saucen, Suppen oder Schmorgerichte "
            "verwendet, damit nichts anbrennt und Aromen sich langsam entfalten."
        ),
    },
    {
        "name": "Pochieren",
        "kategorie": "Feuchte Garmethoden",
        "bild": "assets/flaticon/pochieren.png",
        "erklaerung": (
            "Sehr sanftes Garen in nicht kochender, nur leicht simmernder Flüssigkeit "
            "(deutlich unter 100°C). Klassisch für pochierte Eier, aber auch für "
            "empfindlichen Fisch oder Obst."
        ),
    },
    {
        "name": "Braten",
        "kategorie": "Trockene/heiße Garmethoden",
        "bild": "assets/flaticon/braten.png",
        "erklaerung": (
            "Garen in wenig Fett bei hoher Hitze in Pfanne oder Ofen. Durch die "
            "Bräunung entstehen die typischen Röstaromen (Maillard-Reaktion). "
            "Geeignet für Fleisch, Fisch und viele Gemüsesorten."
        ),
    },
    {
        "name": "Wokken (Stir-Frying)",
        "kategorie": "Trockene/heiße Garmethoden",
        "bild": "assets/flaticon/wokken2.png",
        "erklaerung": (
            "Sehr schnelles Braten kleingeschnittener Zutaten bei extrem hoher Hitze "
            "im Wok, unter ständigem Wenden und Rühren. Gemüse bleibt dadurch knackig, "
            "typisch für die asiatische Küche. Wichtig: Zutaten vorher bereitlegen "
            "(Mise en Place), da alles sehr schnell geht."
        ),
    },
    {
        "name": "Grillen",
        "kategorie": "Trockene/heiße Garmethoden",
        "bild": "assets/flaticon/grillen.png",
        "erklaerung": (
            "Garen über direkter, trockener Hitzequelle (Rost, offene Flamme oder "
            "Grillplatte), meist ohne zusätzliches Fett. Erzeugt die charakteristischen "
            "Grillstreifen und ein rauchiges Aroma."
        ),
    },
    {
        "name": "Frittieren",
        "kategorie": "Trockene/heiße Garmethoden",
        "bild": "assets/flaticon/frittieren.png",
        "erklaerung": (
            "Garen vollständig eingetaucht in heißes Fett oder Öl (meist 160–180°C). "
            "Erzeugt eine knusprige Außenhülle bei saftigem Inneren, typisch für "
            "Pommes, Backfisch oder Krapfen."
        ),
    },
    {
        "name": "Gratinieren",
        "kategorie": "Trockene/heiße Garmethoden",
        "bild": "assets/flaticon/ueberbacken.png",
        "erklaerung": (
            "Ein fertiges oder vorgegartes Gericht wird im Ofen unter Ober- oder "
            "Grillhitze überbacken, oft mit Käse, Sauce oder Semmelbröseln, bis eine "
            "goldbraune, leicht krosse Kruste entsteht."
        ),
    },
    {
        "name": "Karamellisieren",
        "kategorie": "Trockene/heiße Garmethoden",
        "bild": "assets/flaticon/karamellisieren.png",
        "erklaerung": (
            "Zucker (oder der natürliche Zucker in Gemüse wie Zwiebeln) wird durch "
            "Hitze so lange erwärmt oder angebraten, bis er bräunt und ein "
            "nussig-süßes Röstaroma entwickelt."
        ),
    },
    {
        "name": "Anschwitzen (glasig dünsten)",
        "kategorie": "Trockene/heiße Garmethoden",
        "bild": "assets/flaticon/anbraten.png",
        "erklaerung": (
            "Zwiebeln, Knoblauch oder anderes Gemüse werden in wenig Fett bei "
            "milder Hitze gedünstet, bis sie weich und glasig, aber nicht braun "
            "werden. Oft der erste Schritt vieler Pfannengerichte und Saucen."
        ),
    },
    {
        "name": "Ablöschen",
        "kategorie": "Sauce & Technik",
        "bild": "assets/flaticon/abloeschen2.png",
        "erklaerung": (
            "Nach dem scharfen Anbraten wird der Bratensatz am Topf- oder "
            "Pfannenboden mit einer Flüssigkeit (Wein, Brühe, Wasser) gelöst. Das "
            "bringt konzentrierten Geschmack in die Sauce, statt ihn wegzuwerfen."
        ),
    },
    {
        "name": "Reduzieren",
        "kategorie": "Sauce & Technik",
        "bild": "assets/flaticon/reduzieren.png",
        "erklaerung": (
            "Eine Flüssigkeit (Sauce, Brühe, Wein) wird offen bei mittlerer bis "
            "hoher Hitze eingekocht, sodass Wasser verdunstet. Dadurch wird sie "
            "sämiger und der Geschmack konzentrierter."
        ),
    },
    {
        "name": "Abschmecken",
        "kategorie": "Sauce & Technik",
        "bild": "assets/flaticon/abschmecken2.png",
        "erklaerung": (
            "Ein Gericht wird kurz vor dem Servieren probiert und bei Bedarf mit "
            "Salz, Pfeffer, Säure oder Kräutern final nachgewürzt, um den Geschmack "
            "auszubalancieren."
        ),
    },
    {
        "name": "Marinieren",
        "kategorie": "Vorbereitung",
        "bild": "assets/flaticon/marinieren.png",
        "erklaerung": (
            "Fleisch, Fisch oder Gemüse wird vor dem Garen für einige Zeit in einer "
            "Würzflüssigkeit (Öl, Säure, Kräuter, Gewürze) eingelegt. Das verleiht "
            "Aroma und kann bei Fleisch zusätzlich zart machen."
        ),
    },
    {
        "name": "Panieren",
        "kategorie": "Vorbereitung",
        "bild": "assets/flaticon/panieren2.png",
        "erklaerung": (
            "Das Gargut wird nacheinander in Mehl, verquirltem Ei und "
            "Semmelbröseln gewendet, bevor es gebraten oder frittiert wird. Ergibt "
            "eine knusprige Hülle, die das Innere saftig hält - klassisch beim "
            "Schnitzel."
        ),
    },
    {
        "name": "Pürieren",
        "kategorie": "Vorbereitung",
        "bild": "assets/flaticon/puerieren2.png",
        "erklaerung": (
            "Gegartes oder rohes Gargut wird mit Stabmixer, Standmixer oder "
            "Kartoffelstampfer zu einer glatten, cremigen Masse verarbeitet - etwa "
            "für Suppen, Saucen oder Pürees."
        ),
    },
    {
        "name": "Backen",
        "kategorie": "Trockene/heiße Garmethoden",
        "bild": "assets/flaticon/backen.png",
        "erklaerung": (
            "Garen durch trockene, umgebende Hitze im Ofen, meist bei Temperaturen "
            "zwischen 150 und 220°C. Typisch für Brot, Kuchen, Aufläufe und "
            "Gebäck, bei denen die Hitze von allen Seiten gleichmäßig wirkt."
        ),
    },
    {
        "name": "Rösten",
        "kategorie": "Trockene/heiße Garmethoden",
        "bild": "assets/flaticon/roesten.png",
        "erklaerung": (
            "Kurzes, intensives Garen bei sehr hoher, trockener Hitze - etwa im "
            "Ofen oder in der Pfanne ohne oder mit sehr wenig Fett. Erzeugt "
            "kräftige Röstaromen, typisch für Nüsse, Gewürze oder Ofengemüse."
        ),
    },
    {
        "name": "Sautieren",
        "kategorie": "Trockene/heiße Garmethoden",
        "bild": "assets/flaticon/sautieren.png",
        "erklaerung": (
            "Sehr schnelles Braten kleiner Stücke in wenig heißem Fett unter "
            "ständigem Schwenken der Pfanne, ohne Wenden mit dem Kochlöffel. Der "
            "Name kommt vom französischen 'sauter' (springen) - typisch für "
            "Gemüse oder kleine Fleischstücke."
        ),
    },
    {
        "name": "Trockenrösten",
        "kategorie": "Trockene/heiße Garmethoden",
        "bild": "assets/flaticon/trockenroesten.png",
        "erklaerung": (
            "Rösten ganz ohne Fett in einer heißen Pfanne, meist für Gewürze, "
            "Nüsse oder Samen. Die trockene Hitze setzt ätherische Öle frei und "
            "intensiviert das Aroma deutlich, muss aber genau beobachtet werden, "
            "damit nichts verbrennt."
        ),
    },
    {
        "name": "Sous-vide",
        "kategorie": "Feuchte Garmethoden",
        "bild": "assets/flaticon/sous_vide.png",
        "erklaerung": (
            "Vakuumierte Lebensmittel werden über einen längeren Zeitraum bei "
            "sehr genau kontrollierter, niedriger Temperatur (meist 55-65°C) im "
            "Wasserbad gegart. Ergibt besonders gleichmäßig gegartes, saftiges "
            "Fleisch oder Fisch, erfordert aber spezielles Equipment."
        ),
    },
    {
        "name": "Räuchern",
        "kategorie": "Trockene/heiße Garmethoden",
        "bild": "assets/flaticon/raeuchern.png",
        "erklaerung": (
            "Lebensmittel werden Rauch von glimmendem Holz ausgesetzt, entweder "
            "heiß (gleichzeitiges Garen und Aromatisieren) oder kalt (reine "
            "Aromatisierung ohne Garen). Verleiht den typischen rauchigen "
            "Geschmack, klassisch bei Fisch, Fleisch und Käse."
        ),
    },
    {
        "name": "Ruhen lassen",
        "kategorie": "Sauce & Technik",
        "bild": "assets/flaticon/ruhen_lassen.png",
        "erklaerung": (
            "Gebratenes oder gebackenes Fleisch wird nach dem Garen einige Minuten "
            "abgedeckt beiseitegestellt, bevor es angeschnitten wird. Der "
            "Fleischsaft verteilt sich dadurch gleichmäßiger, statt beim "
            "Anschneiden sofort auszulaufen."
        ),
    },
    {
        "name": "Schneiden",
        "kategorie": "Vorbereitung",
        "bild": "assets/flaticon/schneiden.png",
        "erklaerung": (
            "Zerteilen von Zutaten mit dem Messer in Scheiben, Streifen oder "
            "andere Formen. Die Schnittform beeinflusst nicht nur die Optik, "
            "sondern auch die Garzeit und wie Aromen freigesetzt werden."
        ),
    },
    {
        "name": "Würfeln",
        "kategorie": "Vorbereitung",
        "bild": "assets/flaticon/wuerfeln.png",
        "erklaerung": (
            "Zutaten werden in gleichmäßige, würfelförmige Stücke geschnitten. "
            "Gleich große Würfel sorgen dafür, dass alle Stücke in etwa gleich "
            "schnell garen."
        ),
    },
    {
        "name": "Hacken",
        "kategorie": "Vorbereitung",
        "bild": "assets/flaticon/hacken.png",
        "erklaerung": (
            "Zutaten wie Kräuter, Nüsse oder Knoblauch werden mit dem Messer in "
            "sehr kleine, unregelmäßige Stücke zerkleinert. Feiner als Würfeln, "
            "meist für Zutaten, die sich gleichmäßig in einem Gericht verteilen "
            "sollen."
        ),
    },
    {
        "name": "Verquirlen",
        "kategorie": "Sauce & Technik",
        "bild": "assets/flaticon/verquirlen.png",
        "erklaerung": (
            "Zutaten wie Eier werden mit einem Schneebesen oder einer Gabel "
            "kräftig verrührt, bis eine gleichmäßige Masse entsteht, oft auch mit "
            "Luft angereichert. Grundtechnik für Rührei, Pfannkuchenteig oder "
            "Marinaden."
        ),
    },
    {
        "name": "Vermengen",
        "kategorie": "Sauce & Technik",
        "bild": "assets/flaticon/vermengen.png",
        "erklaerung": (
            "Mehrere Zutaten werden vorsichtig miteinander vermischt, meist mit "
            "einem Löffel oder Spatel, ohne dabei viel Luft einzuarbeiten. "
            "Sanfter als Verquirlen, häufig bei Teigen oder Salaten verwendet."
        ),
    },
    {
        "name": "Abseihen",
        "kategorie": "Sauce & Technik",
        "bild": "assets/flaticon/abseihen.png",
        "erklaerung": (
            "Flüssigkeit wird durch ein Sieb gegossen, um feste Bestandteile "
            "abzutrennen - etwa Nudelwasser vom Nudeln, oder eine Brühe von "
            "Gemüseresten und Gewürzen."
        ),
    },
    {
        "name": "Emulgieren",
        "kategorie": "Sauce & Technik",
        "bild": "assets/flaticon/emulgieren.png",
        "erklaerung": (
            "Zwei eigentlich nicht mischbare Flüssigkeiten wie Öl und Essig "
            "werden durch kräftiges Rühren oder Mixen zu einer stabilen, "
            "cremigen Mischung verbunden, oft mit Hilfe eines Bindemittels wie "
            "Senf oder Eigelb - die Grundlage für Mayonnaise oder Vinaigrette."
        ),
    },
]

KATEGORIEN = [
    "Feuchte Garmethoden",
    "Trockene/heiße Garmethoden",
    "Sauce & Technik",
    "Vorbereitung",
]
