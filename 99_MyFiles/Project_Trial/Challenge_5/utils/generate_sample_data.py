import os, json, random, logging
from datetime import datetime, timedelta
import pandas as pd
import nltk
logger = logging.getLogger(__name__)


def _ensure_vader():
    try:
        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        SentimentIntensityAnalyzer()
        return True
    except LookupError:
        try:
            nltk.download('vader_lexicon', quiet=True)
            return True
        except Exception as exc:
            logger.warning('Could not download VADER: %s', exc)
            return False


_VAC_POS = [
    'This robot vacuum has completely changed my life. Floors are spotless every morning.',
    'Incredible suction power - picks up dog hair better than my old Roomba.',
    'Battery lasts over 90 minutes. Covers my whole first floor no problem.',
    'The self-empty base is a game changer. I only empty the bin once a week.',
    'Navigation is surprisingly smart. Learned my floor plan after two runs.',
    'Runs so quietly I forgot it was on. Cat does not notice it.',
    'Replaced my Dyson - suction is just as good at half the price.',
    'DuoClean head is brilliant - works on carpet and hardwood seamlessly.',
    'Anti-hair-wrap tech actually works. Lifesaver for those with long hair.',
    'So lightweight. My elderly mom uses it without any strain.',
    'Scheduling via the app is flawless. Set it and forget it.',
    'HEPA filter makes a real difference for my allergies.',
    'Saved money vs Dyson. Cannot tell the performance difference.',
]

_VAC_NEG = [
    'Robot gets stuck on area rug every time. Useless for homes with rugs.',
    'Battery died after 8 months. Customer service was unhelpful.',
    'App connectivity is terrible. Drops Wi-Fi constantly.',
    'So loud my neighbor came to check if something was wrong.',
    'Maps corrupted after firmware update. Now wanders randomly.',
    'Self-empty bin fills up after 3 cleans. Much smaller than advertised.',
    'Brush roll tangled with carpet fibers after two weeks.',
    'Old iRobot navigates better than this new Shark. Disappointed.',
    'Charging dock is flimsy and robot constantly fails to dock.',
    'Side brushes broke after a month. Replacement parts overpriced.',
    'Stick vacuum motor started grinding after 4 months.',
    'Tried 3 times to contact support. Never got a real answer.',
]

_VAC_NEU = [
    'Fine product. Nothing extraordinary but nothing terrible.',
    'Decent for the price. Some features work, others underwhelm.',
    'Suction is good but dustbin is too small.',
    'Works as expected. Nothing wows me vs competitors.',
    'Solid for everyday cleaning but struggles with deep carpet.',
    'Good for bare floors. Carpet performance average at best.',
]

_KIT_POS = [
    'DualZone air fryer is a revelation. Two baskets at different temps.',
    'Ninja air fryer makes crispiest fries at home. Rivals fast food.',
    'Coffee is smooth and rich. Have not visited Starbucks since getting this.',
    'Blender demolishes frozen fruit. No chunks, silky smooth every time.',
    'Family uses air fryer daily. Chicken wings are a weekly tradition.',
    'Replaced my KitchenAid with Ninja blender. Better value, same power.',
    'Full meal in under 15 minutes with the Speedi. Amazing for busy nights.',
    'Hot and iced coffee modes both excellent. Carafe keeps coffee hot.',
    'Air fryer reheats pizza better than oven. Crispy crust, no sogginess.',
    'All removable parts are dishwasher safe. Very easy to clean.',
    'Smoothie consistency perfect every time. No seeds, no chunks.',
    'Programmable settings make morning coffee completely hands-free.',
    'Ninja handles ice so much better than my old KitchenAid.',
]

_KIT_NEG = [
    'Air fryer fan is deafeningly loud. We have to shout over it.',
    'Plastic handle cracked after 6 months. Poor build quality.',
    'Coffee maker leaves grounds in the cup. Frustrating design flaw.',
    'App features useless - Wi-Fi drops every other day.',
    'Blender lid does not seal. Smoothie all over my ceiling.',
    'Air fryer basket coating started peeling after 3 months.',
    'Buttons stopped responding after a year.',
    'Carafe gasket leaked from day one. Support took 6 weeks.',
    'Ninja blender is loud enough to wake a sleeping baby.',
    'Returned it after heating element died within 90 days.',
    'Too many parts to wash. Took the joy out of cooking.',
]

_KIT_NEU = [
    'Does the job. Not as revolutionary as marketing suggests.',
    'Coffee is good, not great. Still prefer French press on weekends.',
    'Works fine for basic air frying. Not a game changer at this price.',
    'Powerful blender but noisier than expected.',
    'Solid appliance. Six months in and nothing has broken.',
    'Average performance. Competitors offer similar results at lower price.',
]

_HAIR_POS = [
    'HyperAIR dries my thick hair in half the time of my old dryer.',
    'Zero frizz. Been fighting frizz my whole life and this finally solved it.',
    'FlexStyle replaced my straightener, curler, AND dryer. Impressive.',
    'Gentler on my hair than anything used before. Color-treated hair loves it.',
    'Ionic technology is real - hair feels soft and smooth every time.',
    'Much quieter than my Dyson Supersonic. Same results for less money.',
    'Hair has never looked this good. Worth every penny.',
]

_HAIR_NEG = [
    'Broke after 4 months of daily use. Not acceptable at this price.',
    'Cord is annoyingly short. Have to stand right next to outlet.',
    'Much louder than product videos suggest.',
    'Attachments pop off mid-use. Locking mechanism feels cheap.',
    'Does not live up to the Dyson hype it competes with.',
    'Overheated twice and shut off. Makes me nervous to use it.',
]

_HAIR_NEU = [
    'Good dryer, not exceptional. Gets the job done.',
    'Works fine. About the same as my old dryer but with more attachments.',
    'Decent for the price. Not sure I would buy at full retail.',
]

_EXTRAS = [
    ' Would definitely recommend to a friend.',
    ' Been using it for three months now.',
    ' My whole family agrees.',
    ' Big improvement over my previous model.',
    ' Bought it as a gift - recipient loves it.',
    ' Saw it on TikTok and decided to try.',
    ' Found it on sale which made decision easier.',
    ' Read multiple Reddit threads before purchasing.',
    '',
    '',
    '',
]

_ADJ = [
    'tiny',
    'fluffy',
    'lazy',
    'electric',
    'hungry',
    'sleepy',
    'epic',
    'random',
    'cosmic',
    'crispy',
    'silent',
    'golden',
]

_NOUN = [
    'panda',
    'robot',
    'vacuum',
    'chef',
    'ninja',
    'shark',
    'blender',
    'fryer',
    'bean',
    'carpet',
    'gadget',
    'couch',
]

_AFN = [
    'James',
    'Sarah',
    'Michael',
    'Jennifer',
    'David',
    'Lisa',
    'Robert',
    'Emily',
    'Chris',
    'Amanda',
    'Brian',
    'Megan',
    'Kevin',
    'Rachel',
    'Tyler',
    'Melissa',
    'Daniel',
    'Karen',
    'Mark',
    'Nicole',
    'Steven',
    'Jessica',
    'Paul',
    'Ashley',
]

_AFL = [
    'T.',
    'M.',
    'R.',
    'B.',
    'L.',
    'K.',
    'W.',
    'H.',
    'S.',
    'G.',
    'P.',
    'D.',
]

_TTH = [
    'homechef',
    'cleanfreak',
    'kitchenqueen',
    'vacuumlife',
    'cookingwith',
    'techtested',
    'dailyreview',
    'lifeupgrade',
    'gadgetguru',
    'realreviews',
    'busymom',
    'coffeeaddict',
]

_TTS = [
    '2024',
    'official',
    '_real',
    'xo',
    '99',
    '2k',
    'vibes',
    'irl',
]

_TKW = {
    'Suction Power': ['suction', 'picks up', 'strong', 'powerful', 'cleaning power'],
    'Battery Life': ['battery', 'charge', 'runtime', 'dies', 'lasts'],
    'Noise Level': ['loud', 'quiet', 'noise', 'silent', 'noisy', 'sound'],
    'App Experience': ['app', 'wifi', 'connect', 'phone', 'schedule', 'smart', 'alexa'],
    'Build Quality': ['broke', 'break', 'quality', 'cheap', 'flimsy', 'durable', 'sturdy'],
    'Ease of Use': ['easy', 'simple', 'intuitive', 'setup', 'complicated', 'confusing'],
    'Value for Money': ['price', 'worth', 'value', 'expensive', 'cost', 'affordable'],
    'Cooking Quality': ['crispy', 'cook', 'taste', 'food', 'meal', 'fries', 'delicious'],
    'Pet Hair': ['hair', 'frizz', 'smooth', 'style', 'pet', 'fur', 'shedding'],
    'Customer Service': ['support', 'service', 'return', 'warranty', 'replacement'],
    'Design': ['design', 'look', 'sleek', 'compact', 'attachment', 'aesthetic', 'lightweight'],
    'Maintenance': ['filter', 'maintenance', 'wash', 'replace', 'clog'],
    'Capacity': ['capacity', 'size', 'fit', 'small', 'large', 'family'],
}

TEMPLATES = {
    'robot_vacuum': (_VAC_POS, _VAC_NEG, _VAC_NEU),
    'stick_vacuum': (_VAC_POS, _VAC_NEG, _VAC_NEU),
    'hair_dryer': (_HAIR_POS, _HAIR_NEG, _HAIR_NEU),
    'air_fryer': (_KIT_POS, _KIT_NEG, _KIT_NEU),
    'blender': (_KIT_POS, _KIT_NEG, _KIT_NEU),
    'coffee_maker': (_KIT_POS, _KIT_NEG, _KIT_NEU),
}

PLT_WEIGHTS = {'amazon': [0.60,0.25,0.15], 'reddit': [0.40,0.35,0.25], 'tiktok': [0.65,0.15,0.20]}

def _rn(): return 'u/{}_{}{}'.format(random.choice(_ADJ), random.choice(_NOUN), random.randint(10,9999))
def _an(): return '{} {}'.format(random.choice(_AFN), random.choice(_AFL))
def _tn(): return '@{}{}'.format(random.choice(_TTH), random.choice(_TTS))
_AG = {'amazon': _an, 'reddit': _rn, 'tiktok': _tn}

def _topics(text):
    t = text.lower()
    return [k for k, ws in _TKW.items() if any(w in t for w in ws)][:5]

def _eng(plt, sent):
    if plt == 'amazon': return random.randint(0,50)+(random.randint(10,80) if sent=='negative' else 0)
    if plt == 'reddit': return random.randint(1,1200)
    return random.randint(10,50000)

def _rat(plt, sent):
    if plt != 'amazon': return 0.0
    if sent == 'positive': return random.choice([4.0,5.0,5.0,5.0])
    if sent == 'negative': return random.choice([1.0,1.0,2.0])
    return 3.0

def _date(end, months=6):
    wt = random.betavariate(2.5, 1.2)
    d = int((1 - wt) * months * 30)
    return end - timedelta(days=d, hours=random.randint(0,23))


def generate_sample_data():
    from config import DATA_DIR, PRODUCT_NAMES, BRAND_CATEGORY_MAP, SENTIMENT_THRESHOLDS
    _ensure_vader()
    try:
        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        sia = SentimentIntensityAnalyzer(); use_vader = True
    except Exception:
        sia = None; use_vader = False
    end = datetime.now(); records = []; rid = 1
    plts = ['amazon', 'amazon', 'amazon', 'reddit', 'reddit', 'tiktok']
    pairs = [(b,c) for b,cats in BRAND_CATEGORY_MAP.items() for c in cats]
    per_pair = 2000 // len(pairs)
    for brand, cat in pairs:
        products = PRODUCT_NAMES.get(cat, [brand.title() + ' Product'])
        pt, nt, ut = TEMPLATES.get(cat, ([],[],[]))
        for _ in range(per_pair):
            plt = random.choice(plts)
            bkt = random.choices(['positive','negative','neutral'], weights=PLT_WEIGHTS[plt])[0]
            if bkt == 'positive' and pt: base = random.choice(pt)
            elif bkt == 'negative' and nt: base = random.choice(nt)
            elif ut: base = random.choice(ut)
            else: base = 'This product is okay.'
            text = base + random.choice(_EXTRAS)
            if use_vader and sia: score = round(sia.polarity_scores(text)['compound'], 4)
            elif bkt == 'positive': score = round(random.uniform(0.25,0.95), 4)
            elif bkt == 'negative': score = round(random.uniform(-0.95,-0.25), 4)
            else: score = round(random.uniform(-0.15,0.15), 4)
            if score > SENTIMENT_THRESHOLDS['positive']: lbl = 'positive'
            elif score < SENTIMENT_THRESHOLDS['negative']: lbl = 'negative'
            else: lbl = 'neutral'
            records.append({
                'id': 'SN-{:05d}'.format(rid),
                'platform': plt,
                'product_category': cat,
                'product_name': random.choice(products),
                'brand': brand,
                'text': text,
                'rating': _rat(plt, bkt),
                'date': _date(end).strftime('%Y-%m-%d %H:%M:%S'),
                'sentiment_score': score,
                'sentiment_label': lbl,
                'topics': json.dumps(_topics(text)),
                'engagement_score': _eng(plt, bkt),
                'author': _AG[plt](),
            })
            rid += 1
    df = pd.DataFrame(records)
    os.makedirs(DATA_DIR, exist_ok=True)
    out = os.path.join(DATA_DIR, 'reviews.csv')
    df.to_csv(out, index=False)
    logger.info('Sample data saved: %d rows -> %s', len(df), out)
    return df
