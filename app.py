import sys
from io import BytesIO

import telegram
from flask import Flask, request, send_file

from fsm import TocMachine


API_TOKEN = '501071757:AAHMkTIfwFEJvH0UaRNAmZyQeH813XFqE7s'
WEBHOOK_URL = 'https://ce7dc1d9.ngrok.io/hook'

app = Flask(__name__)
bot = telegram.Bot(token=API_TOKEN)
machine = TocMachine(
    states=[
        'user',
        'state0', #start
        
        'state1', #product
        'state1_2',
        'state1_2_3',
        'state1_3',
        'state1_3_3',
        'state1_4',
        'state1_4_3',

        'state2', #search store

        'state3', #book
        'state3_2',
        'state3_2_3',
        
    ],
    transitions=[
       {
            'trigger': 'advance',
            'source': 'user',
            'dest': 'state0',
            'conditions': 'is_going_to_state0'
        },
        {
            'trigger': 'advance',
            'source': 'state0',
            'dest': 'state1',
            'conditions': 'is_going_to_state1'
        },

        # 1 => 1_2 
        {
            'trigger': 'advance',
            'source': 'state1',
            'dest': 'state1_2',
            'conditions': 'is_going_to_state1_2'
        },
        {
            'trigger': 'advance',
            'source': 'state1_2',
            'dest': 'state1_2_3',
            'conditions': 'is_going_to_state1_2_3'
        },
        

        #1 => 1_3
        {
            'trigger': 'advance',
            'source': 'state1',
            'dest': 'state1_3',
            'conditions': 'is_going_to_state1_3'
        },
        {
            'trigger': 'advance',
            'source': 'state1_3',
            'dest': 'state1_3_3',
            'conditions': 'is_going_to_state1_3_3'
        },

        #1 => 1_4
        {
            'trigger': 'advance',
            'source': 'state1',
            'dest': 'state1_4',
            'conditions': 'is_going_to_state1_4'
        },
        {
            'trigger': 'advance',
            'source': 'state1_4',
            'dest': 'state1_4_3',
            'conditions': 'is_going_to_state1_4_3'
        },
        #back to state1
        {
            'trigger': 'advance',
            'source':[
                'state1_2',
                'state1_3',
                'state1_4',
            ], 
            'dest': 'state1',
            'conditions': 'back_to_state1'
        },

        # state2
        {
            'trigger': 'advance',
            'source': 'state0',
            'dest': 'state2',
            'conditions': 'is_going_to_state2'
        },
        

        # state3
        {
            'trigger': 'advance',
            'source': 'state0',
            'dest': 'state3',
            'conditions': 'is_going_to_state3'
        },
        {
            'trigger': 'advance',
            'source': 'state3',
            'dest': 'state3_2',
            'conditions': 'is_going_to_state3_2'
        },
        {
            'trigger': 'advance',
            'source': 'state3_2',
            'dest': 'state3_2_3',
            'conditions': 'is_going_to_state3_2_3'
        },
        {
            'trigger': 'advance',
            'source': 'state3_2_3',
            'dest': 'state3',
            'conditions': 'back_to_state3'
        },
        {
            'trigger': 'advance',
            'source': 'state3_2_3',
            'dest': 'state0',
            'conditions': 'state3_2_3_back_to_state0'
        },
        {
            'trigger': 'advance',
            'source': [
                'state1',
                'state2',
                'state3',
            ],
            'dest': 'state0',
            'conditions': 'back_to_state0'
        },


        #go back
        {
            'trigger': 'go_back',
            'source': 'state1_2_3',
            'dest': 'state1_2'
        },
        {
            'trigger': 'go_back',
            'source': 'state1_3_3',
            'dest': 'state1_3'
        },
        {
            'trigger': 'go_back',
            'source': 'state1_4_3',
            'dest': 'state1_4'
        },
    ],
    initial='user',
    auto_transitions=False,
    show_conditions=True,
)


def _set_webhook():
    status = bot.set_webhook(WEBHOOK_URL)
    if not status:
        print('Webhook setup failed')
        sys.exit(1)
    else:
        print('Your webhook URL has been set to "{}"'.format(WEBHOOK_URL))


@app.route('/hook', methods=['POST'])
def webhook_handler():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    print (update.message.text)
    machine.advance(update)
    return 'ok'


@app.route('/show-fsm', methods=['GET'])
def show_fsm():
    byte_io = BytesIO()
    machine.graph.draw(byte_io, prog='dot', format='png')
    byte_io.seek(0)
    return send_file(byte_io, attachment_filename='fsm.png', mimetype='image/png')


if __name__ == "__main__":
    _set_webhook()
    app.run()