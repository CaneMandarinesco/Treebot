import telegram as tg
import telegram.ext as tge
from telegram.ext.filters import Filters as tgFilters
import logging
import data
import json

TOKEN='FATTI I CAZZI TUOI'
updater: tge.Updater = None
dispatcher: tge.Dispatcher = None

start_text = '''🌲*Cosa puo' fare questo bot?*🌲
Questo bot puo tenere traccia dei tuoi *alberi* su *Treedom*!

Riguardo a un albero posso farti sapere:
💬 `Nome`
💬 `Nome Scientifico`
💬 `Nome Assegnato`
👤 `Proprietario`
🌳 `Foresta`
📍 `Posizione`

*Per aggiungere una albero basta mandarmi suo codice!*
*Per chiedermi informazioni su un'albero usa il comando /tree*'''

def start_callback(update: tg.Update, context: tge.CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=start_text,
        parse_mode='markdown'
    )

tree_text = '''*%s* | *%s*
💬 Nome Assegnato: `%s`
📍 Posizione: `%s`'''

def tree_callback(update: tg.Update, context: tge.CallbackContext):
    inline_keyboard_ls = []
    usersd = []

    with open('users.json') as f:
        usersd = json.load(f)
    
    for t in usersd[str(update.effective_chat.id)]:
        tdata = data.get_tree_name(t)
        inline_keyboard_ls.append([tg.InlineKeyboardButton(
            text= tdata['name'] + ('' if tdata['assignedName'] == None else ' | ' + tdata['assignedName']),
            callback_data=data.create_query_data('show_tree', t)
        )])
    
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Scegli un albero!',
        reply_markup=tg.InlineKeyboardMarkup(inline_keyboard_ls)
    )

def query_callback(update: tg.Update, context: tge.CallbackContext):
    qdata = json.loads(update.callback_query.data)

    if qdata['op'] == 'show_tree':
        tdata = data.get_tree_data(qdata['treeId'])

        inline_keyboard_ls = []
        inline_keyboard_ls.append([tg.InlineKeyboardButton(
            text='📱 Pagina web 📱',
            url='https://www.treedom.net/it/user/%s/trees/%s' % (tdata['owner']['slug'], tdata['treeId'])
        )])
        inline_keyboard_ls.append([tg.InlineKeyboardButton(
            text='🌳 Foresta 🌳',
            url='https://www.treedom.net/it/user/%s/event/%s' % (tdata['owner']['slug'], tdata['forest']['slug'])
        )])
        inline_keyboard_ls.append([tg.InlineKeyboardButton(
            text='📩 NOTIFICHE 📩',
            callback_data=data.create_query_data('enable_notifications', tdata['treeId'])
        )])

        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=tdata['image'],
            caption=tree_text % (tdata['name'], tdata['scientificName'], tdata['assignedName'],
                tdata['location']),
            parse_mode='markdown',
            reply_markup=tg.InlineKeyboardMarkup(inline_keyboard_ls)
        )

    elif qdata['op'] == 'enable_notifications':
        pass

def link_callback(update: tg.Update, context: tge.CallbackContext):
    # https://www.treedom.net/it/user/3-m/trees/E8K-8M8?filter=all
    # https://www.treedom.net/it/user/3-m/event/fratta-del-musicale-liceo/trees/E8K-8M8
    link = update.effective_message.text
    if link.endswith('all'):
        print(link[len(link)-18:7])

def add_handlers(dispatcher: tg.ext.Dispatcher):
    start_handler = tge.CommandHandler('start', start_callback)
    dispatcher.add_handler(start_handler)

    tree_handler = tge.CommandHandler('tree', tree_callback)
    dispatcher.add_handler(tree_handler)

    callback_handler = tge.CallbackQueryHandler(query_callback)
    dispatcher.add_handler(callback_handler)

    link_handler = tge.MessageHandler(
        filters=[tgFilters.text], 
        callback=link_callback
    )
    dispatcher.add_handler(link_handler)

def run():
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s - %(levelname)s]: %(message)s')

    updater = tg.ext.Updater(TOKEN)
    dispatcher = updater.dispatcher

    add_handlers(dispatcher)

    updater.start_polling()
