# AI GTA:

Project = 'Gta'

valid_speakers = ["CJ", "SMOKE", "RYDER"]
replacements = [
    ("CJ", "CJ"),
    ("SMOKE", "SMOKE"),
    ("RYDER", "RYDER"),
]
default_topic_suggest_message = 'Окей, бро! Добавил тему в список'
default_style = 'Агрессивная беседа гангстеров'


mongodb_address = 'mongodb+srv://chubemba:klMBAQo6ZgfcEWqY@aistreams.5lhluvc.mongodb.net/'

# Параметры
CanAddTopic = True
CanAddMashup = False
threshold = 80

TopicDelay = 300
TopicDelayTg = 600
MashupDelay = 60

NeedTopicDelay = True
NeedMashupDelay = True
NeedMashupDelayPerUser = False

MaxLengthTG = 300

TopicPriority = 1
MashapPriority = 1

TopicsChatName = ["💥заказать-тему", "🔥быстрые-темы", "💥┆заказать-тему"]
MashupsChatName = "💥заказать-мэшап"

AdminNames = ['pryanik26', 'meyson420']
AdminTgIds = [1484475666, 709479935, -1002175092872]
SubsLvl1ChatID = -1002246167622
SubChat = [-4263371994]
ChanelToSubscribeID = '@neurogta'

#Donat config
DonatedTopicSumRub = 35
DonatedMashupSumRub = 0
DonatedInteractionOneSumRub = 25
DonatedInteractionTwoSumRub = 0
DonatEnableTopics = True
DonatEnableMashups = False
DonatEnableInteractionOne = True
DonatEnableInteractionTwo = False
