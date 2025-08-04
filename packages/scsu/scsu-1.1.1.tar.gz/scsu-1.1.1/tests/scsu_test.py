import unittest

from src import scsu


class EncodingTest(unittest.TestCase):
    def test_no_change_ascii(self):
        s = "ASCII string."
        self.assertEqual(s, s.encode(scsu.CODEC_NAME).decode(scsu.CODEC_NAME))

    def test_no_change_latin1(self):
        s = "¿Dónde está mi Pokémon, señor?"
        self.assertEqual(s, s.encode(scsu.CODEC_NAME).decode(scsu.CODEC_NAME))

    def test_change_katakana(self):
        s = "In Japanese, Unicode is ユニコード"
        self.assertEqual(s, s.encode(scsu.CODEC_NAME).decode(scsu.CODEC_NAME))

    def test_define_new_window(self):
        s = "In Armenian, Unicode is Յունիկոդը"
        self.assertEqual(s, s.encode(scsu.CODEC_NAME).decode(scsu.CODEC_NAME))

    def test_unicode_ascii(self):
        s = "유니코드에 대해 ?"
        self.assertEqual(s, s.encode(scsu.CODEC_NAME).decode(scsu.CODEC_NAME))

    def test_supplementary_window(self):
        s = "😀😁😂😃😄😅😆😇😈😉😊😋😌😍😎😏😐😑😒😓😔😕😖😗😘😙😚😛😜😝😞😟😠😡😢😣😤😥😦😧😨😩😪😫😬😭😮😯"
        self.assertEqual(s, s.encode(scsu.CODEC_NAME).decode(scsu.CODEC_NAME))

    def test_dynamic_static_window(self):
        s = "ありがとうございました。"
        self.assertEqual(s, s.encode(scsu.CODEC_NAME).decode(scsu.CODEC_NAME))

    def test_all_dynamic_windows(self):
        s = "\r\n".join(["¿Qué es Unicode?",
                         "Što je Unicode?",
                         "Что такое Unicode?",
                         "ما هي الشفرة الموحدة يونِكود ؟",
                         "यूनिकोड क्या है?",
                         "ゆにこーど",
                         "ユニコード",
                         "Ｕｎｉｃｏｄｅ"])
        self.assertEqual(s, s.encode(scsu.CODEC_NAME).decode(scsu.CODEC_NAME))

    def test_all_static_windows(self):
        s = "AÁĀŻA̋⁕₳Å〠"
        self.assertEqual(s, s.encode(scsu.CODEC_NAME).decode(scsu.CODEC_NAME))

    def test_mixture(self):
        s = "犬夜叉が大好きよ。❤️　ワンワン　🐶 Woof woof!"
        self.assertEqual(s, s.encode(scsu.CODEC_NAME).decode(scsu.CODEC_NAME))

    def test_uts6_sample_text(self):
        s = "　♪リンゴ可愛いや可愛いやリンゴ。" \
            "半世紀も前に流行した「リンゴの歌」がぴったりするかもしれない。" \
            "米アップルコンピュータ社のパソコン「マック（マッキントッシュ）」を、こよなく愛する人たちのことだ。" \
            "「アップル信者」なんて言い方まである。"
        b = s.encode(scsu.CODEC_NAME)
        self.assertLessEqual(len(b), 178)
        self.assertEqual(s, b.decode(scsu.CODEC_NAME))


class DecodingTest(unittest.TestCase):
    def test_ascii(self):
        b = b"ASCII string."
        self.assertEqual(b.decode("ASCII"), b.decode(scsu.CODEC_NAME))

    def test_ascii_quote(self):
        b = b"Form feed or clear screen.\x01\x0C"
        s = b.decode(scsu.CODEC_NAME)
        self.assertEqual(s[-1], "\f")
        self.assertNotEqual(s[-2], chr(0x01))

    def test_window_quote(self):
        b = b"A\x03\x94\x06\x82"
        s = b.decode(scsu.CODEC_NAME)
        self.assertEqual(s, "AДあ")

    def test_unicode_quote_basic(self):
        b = b"Dog \x0E\x72\xAC"
        s = b.decode(scsu.CODEC_NAME)
        self.assertEqual(s[-1], "犬")

    def test_unicode_quote_supplementary(self):
        b = b"Dog \x0E\xD8\x3D\x0E\xDC\x36"
        s = b.decode(scsu.CODEC_NAME)
        self.assertEqual(s[-1], "🐶")

    def test_incomplete_unicode_byte_pair(self):
        b = b"Cat \x0F\x73"
        self.assertRaises(UnicodeDecodeError, b.decode, scsu.CODEC_NAME)

    def test_incomplete_unicode_quote(self):
        b = b"Cat \x0E\x73"
        self.assertRaises(UnicodeDecodeError, b.decode, scsu.CODEC_NAME)

    def test_incomplete_unicode_mode_emoji(self):
        b = b"Cat \x0F\xD8\x3D"
        self.assertRaises(UnicodeDecodeError, b.decode, scsu.CODEC_NAME)

    def test_incomplete_unicode_quote_emoji(self):
        b = b"Cat \x0E\xD8\x3D"
        self.assertRaises(UnicodeDecodeError, b.decode, scsu.CODEC_NAME)

    def test_bad_emoji_encoding(self):
        b = b"\x0F\xDE\x3A\xD8\x3D"
        self.assertRaises(UnicodeDecodeError, b.decode, scsu.CODEC_NAME)

    def test_reserved_bytes(self):
        b = b"\x0C"
        self.assertRaises(UnicodeDecodeError, b.decode, scsu.CODEC_NAME)

        b = b"\x0F\xF2"
        self.assertRaises(UnicodeDecodeError, b.decode, scsu.CODEC_NAME)


if __name__ == "__main__":
    unittest.main()
