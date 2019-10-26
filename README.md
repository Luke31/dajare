# Dajare
Super Dry Dajare generator

## What is Dajare?
Examples:
- Camping is intense, Camping is in tents
- 布団が吹っ飛んだ (ふとんがふっとんだ)

See definition: [Wikipedia Dajare](https://en.wikipedia.org/wiki/Dajare)

## Usage

1. Start using
    ```
    docker-compose up
    ```

2. Then open following URL: `http://localhost:8080/static/index.html`
3. Try using any Kanji sentence like `ひと月居てもいい？`, `あなた毛布取らないで`, `音した？`, `おお味噌か?` or `カナリヤ少ない` 
4. Hit the `Generate Daraje` button

(Swagger available here `http://localhost:8080`)

## Open points
- Currently quite stupid, does merely acquire the most common expected kanjis for the provided kanas.
  What you would expect from an IME. If you put in a common sentences, you will almost always get the 
  same kanjis. Should elminiate same sentences
- Katakana is not converted to Hiragana
- Split before requesting Google API, e.g. tomo, dachi instead of tomodachi

# Credits
- Used [pymlhelloworld](https://github.com/pellmont/pymlhelloworld) by [pellmont](https://github.com/pellmont) as a base for starting project.
- Kana to Kanji conversion using [Google IME](https://www.google.co.jp/ime/cgiapi.html) 
