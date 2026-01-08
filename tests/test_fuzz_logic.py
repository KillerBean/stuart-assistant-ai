from thefuzz import process, fuzz

def test_fuzzy_wake_word_matching():
    keyword = "stuart"
    
    # Case 1: Perfect match
    text1 = "stuart que horas são"
    words1 = text1.split()
    match1 = process.extractOne(keyword, words1, scorer=fuzz.ratio)
    assert match1[0] == "stuart"
    assert match1[1] == 100
    
    # Case 2: Typo "stewart"
    text2 = "stewart ligar luz"
    words2 = text2.split()
    match2 = process.extractOne(keyword, words2, scorer=fuzz.ratio)
    # Ratio between stuart and stewart is usually high
    assert match2[0] == "stewart"
    assert match2[1] > 70 
    
    # Case 3: Typo "start"
    text3 = "start ver tempo"
    words3 = text3.split()
    match3 = process.extractOne(keyword, words3, scorer=fuzz.ratio)
    assert match3[0] == "start"
    assert match3[1] > 70 # Tunable
    
    # Case 4: No match
    text4 = "hoje o dia está bonito"
    words4 = text4.split()
    match4 = process.extractOne(keyword, words4, scorer=fuzz.ratio)
    # Should be low confidence
    assert match4[1] < 60
