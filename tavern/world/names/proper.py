# -*- coding: utf-8 -*-
'''Module handling proper names.'''
from random import randint, choice


class LanguageGenerator(object):
    def __init__(self, start, middle, end, long_words=25):
        self.start = start
        self.middle = middle
        self.end = end
        # Proportion of long words in the langage, in percentage
        self.long_words = long_words

    def generate(self):
        starter = choice(self.start)
        if randint(1, 100) <= self.long_words:
            starter = '%s%s' % (starter, choice(self.middle))
        return '%s%s' % (starter, choice(self.end))

human_start = ['Ab', 'An', 'Ag', 'Ba', 'Be', 'Ca', 'Ce', 'Do', 'Gh', 'Ho',
               'Ir', 'It', 'Ja', 'Ju', 'Kel', 'Lan', 'Lam', 'Las', 'Lat',
               'Mon', 'Mun', 'Met', 'Mit', 'No', 'Na', 'Ni', 'Oc', 'Ol',
               'Om', 'Pa', 'Pha', 'Pe', 'Phe', 'Par', 'Per', 'Pir',
               'Por', 'Sa', 'So', 'Su', 'Ta', 'To', 'Te', 'Um', 'Un', 'Uv',
               'Wa', 'Wo', 'We', 'Wi']
human_middle = ['ânn', 'ack', 'agr', 'all', 'but', 'bun', 'cor', 'com', 'cod',
                'coll', 'de', 'del', 'dal', 'dell', 'dall', 'dern', 'darn',
                'eck', 'emn', 'garn', 'gern', 'gorn', 'harn', 'hun', 'hamn',
                'homn', 'kar', 'mann', 'min', 'menn', 'sek', 'sun', 'tek',
                'tun', 'vir', 'vil', 'val', 'vam', 'van', 'vat', 'xi', 'ya']
human_end = ['ad', 'al', 'ack', 'ber', 'bel', 'bet', 'bid', 'cil', 'cid',
             'cin', 'cinn', 'cils', 'darn', 'dagg', 'damm', 'deth', 'doth',
             'enn', 'emm', 'eth', 'esh', 'ew', 'fil', 'fel', 'fen', 'fan',
             'fon', 'gan', 'gam', 'gatt', 'il', 'it', 'in', 'ibn', 'iban',
             'iran', 'iman', 'itan', 'illen', 'illim', 'illen', 'issan',
             'jun', 'jut', 'jat', 'jet', 'jeck', 'kam', 'kom', 'kem',
             'lam', 'lum', 'len', 'lon', 'lent', 'lens', 'lev', 'lept',
             'mun', 'mot', 'mol', 'nack', 'nock', 'nuck', 'neck',
             'oct', 'opt', 'ont', 'pel', 'pal', 'pat', 'pril', 'pil',
             'son', 'san', 'sot', 'sat', 'selt', 'tan', 'tun', 'tin',
             'torn', 'tarn', 'terk', 'turk', 'talk', 'ter', 'um', 'utt',
             'ull', 'varn', 'venn', 'vane', 'vall', 'vale', 'vis',
             'wat', 'wale', 'wane', 'wenn', 'xor', 'xat', 'yel', 'yen']

human_language = LanguageGenerator(human_start, human_middle, human_end)

elfish_start = ['All', 'Ald', 'Aln' 'Alm', 'Cael', 'Caed', 'Caeil', 'Cill',
                'Coell', 'Daell', 'Dill', 'Doell', 'Daeil', 'Ell', 'Edd',
                'Eld', 'Emii', 'Enii', 'Enei', 'Enae', 'Faen', 'Faei',
                'Faeil', 'Faiel', 'Fill', 'Fall', 'Flael', 'Gaesil', 'Gill',
                'Goell', 'Goiel', 'Galil', 'Hill', 'Haei', 'Henae', 'Henei',
                'Hoel', 'Laell', 'Laeill', 'Leill', 'Lenae', 'Lanae', 'Lerie',
                'Lian', 'Liae', 'Llie', 'Llae', 'Llan', 'Llaiein', 'Lloon',
                'Mael', 'Meil', 'Meoll', 'Meonn', 'Mesil', 'Mesael',
                'Mesia', 'Maesie', 'Nael', 'Neiel', 'Neoll', 'Neomm', 'Nesil',
                'Nesael', 'Nemael', 'Nesia,' 'Naesia', 'Naesi', 'Oel',
                'Oael', 'Ollael', 'Olloei', 'Oli', 'Osei', 'Osai', 'Obae',
                'Oberai', 'Oberil', 'Oberel', 'Obarel', 'Obeia', 'Oblea',
                'Oblia', 'Pae', 'Phae', 'Phai', 'Pheil', 'Phael', 'Peill',
                'Pell', 'Teil', 'Till', 'Taell', 'Tae', 'Taei', 'Tanaei',
                'Tanael', 'Tasia', 'Tasia', 'Tsai', 'Tsei', 'Taleil',
                'Tallei', 'Thalei', 'Thill', 'Thoell', 'Thell', 'Thaeln',
                'Thae']
elfish_middle = ['all', 'aen', 'ell', 'emn', 'ill', 'ien', 'moon', 'maen',
                 'thee', 'thal', 'thia', 'sia', 'sae', 'sail', 'soon']
elfish_end = ['ban', 'bann', 'baenn', 'bainn', 'beiln', 'can', 'cail',
              'caell', 'casai', 'casei', 'casil', 'casael', 'dun', 'din',
              'dan', 'daen', 'dasil', 'dailn', 'dol', 'dil', 'dael',
              'dail', 'ebil', 'edil', 'ethil', 'efil', 'efaeil', 'ethaeil',
              'ebon', 'ebil', 'ebail', 'ethoe', 'ilan', 'ilein', 'ilael',
              'ilati', 'ithoe', 'ilatel', 'mil', 'mel', 'mael', 'moael',
              'mobeil', 'mabeil', 'masil', 'mesil', 'nil', 'nel', 'nael',
              'noael', 'nobeil', 'nabetil', 'nabethil', 'nabil', 'nefil',
              'oath', 'oveil', 'ofeil', 'ofae', 'ofanae', 'ofeinae',
              'olla', 'ollae', 'oeil', 'pasae', 'pathae', 'pallae', 'pellae',
              'paith', 'pethae', 'pelan', 'pelein', 'tasae', 'tathae',
              'talla', 'toel', 'tesil', 'telein', 'tenei', 'tenn', 'toenn']

elfish_language = LanguageGenerator(elfish_start, elfish_middle, elfish_end, 5)

dwarven_start = ['Caan', 'Caar', 'Caad', 'Câha', 'Câhu', 'Cuu', 'Daan',
                 'Daar', 'Daad', 'Dahâ', 'Dûha', 'Dûan', 'Drâha',
                 'Hark', 'Hârn', 'Hâad', 'Hûud', 'Hûan', 'Hûu', 'Kaa',
                 'Kahar', 'Kahân', 'Kabâ', 'Kûha', 'Kâkr', 'Kûkr', 'Kûn',
                 'Kûun', 'Kâra', 'Kûra', 'Shûu', 'Shâa', 'Shâkr', 'Shûkr',
                 'Shuhar', 'Shâhar', 'Xââ', 'Xâhu', 'Xûu', 'Xaan', 'Xur',
                 'Xâr', 'Xâh']
dwarven_middle = ['-câr-', '-kâr', '-dûr-', '-dâr', '-kûa-', '-kadûl-',
                  'haan', 'hakran', 'hâakrun', 'huxân', 'kaxân', 'kuxân',
                  'xââ', 'xûû']
dwarven_end = ['abakad', 'abakud', 'abûx', 'abax', 'aud', 'auuk', 'axur',
               'abash', 'abush', 'abâsh', 'habax', 'habaud', 'habuuk',
               'harkûn', 'harkûx', 'harkuk', 'harkaud', 'haxur', 'haxuuk',
               'kân', 'kabud', 'kabuud', 'kabux', 'kabax', 'kaud', 'kârn',
               'kâshur', 'kâshuk', 'kuusha', 'kaasha', 'kaaxaud', 'kabax',
               'kabûx', 'shâruk', 'shârak', 'shaxa', 'shaud', 'shûuk',
               'shaabuk', 'shaarax', 'shaak', 'xarikan', 'xaraud', 'xaâuk',
               'xahûk', 'xashaa', 'xashaud', 'xashûûk', 'xukaud', 'xâhuk']

dwarven_language = LanguageGenerator(dwarven_start, dwarven_middle, dwarven_end,
                                     50)
