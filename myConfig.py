
# AI GTA:
Project = 'Gta'

valid_speakers = ["CJ", "SMOKE"]
replacements = [
    ("CJ", "CJ"),
    ("SMOKE", "SMOKE"),
]
default_topic_suggest_message = 'Окей, бро! Добавил тему в список'
default_style = ''


mongodb_address = 'mongodb+srv://chubemba:klMBAQo6ZgfcEWqY@aistreams.5lhluvc.mongodb.net/'

# Параметры
TopicDelay = 300
TopicDelayTg = 300
MashupDelay = 60

CanAddTopic = True
CanAddMashup = False

NeedTopicDelay = False
NeedMashupDelay = True
NeedMashupDelayPerUser = False

TopicPriority = 1
MashapPriority = 1

TopicsChatName = ["💥заказать-тему", "🔥быстрые-темы", "💥┆заказать-тему"]
MashupsChatName = "💥заказать-мэшап"

AdminNames = ['pryanik26', 'meyson420']
AdminTgIds = [1484475666, 709479935, -1002175092872]

#Queue config
QueueGeneratedText = "Темы готовы:"
QueueSuggestedText = "Темы в очереди:"

#Donat config
DonatedTopicSumRub = 25
DonatedMashupSumRub = 0
DonatedInteractionOneSumRub = 0
DonatedInteractionTwoSumRub = 0
DonatEnableTopics = True
DonatEnableMashups = False
DonatEnableInteractionOne = False
DonatEnableInteractionTwo = False
