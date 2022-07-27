from config import SENDER_EMAIL, EMAIL_PASSWORD, EMAIL_LIST, CHOICE_SORT
import requests
from jinja2 import Environment, FileSystemLoader, select_autoescape
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def get_binance(**kwargs):
    url = "https://api1.binance.com/api/v3/ticker/24hr"

    params = {**kwargs}
    try:
        data = requests.get(url, params).json()
        return data
    except:
        print('Ошибка в получении данных!')


def recurs_find_key(key, obj):
    if obj == None:
        return None
    else:
        if key in obj:
            return obj[key]
        if type(obj) == dict or type(obj) == list:
            for k, v in obj.items():
                if type(v) == dict:
                    result = recurs_find_key(key, v)
                    return result
                elif type(v) == list:
                    for el in range(len(v)):
                        result = recurs_find_key(key, v[el-1])
                        return result


def get_top_data(json):
    top_data = []

    for cripta in json:
        cripta_dict = {}
        symbol = recurs_find_key('symbol', cripta)
        cripta_dict['symbol'] = symbol

        priceChange = recurs_find_key('priceChange', cripta)
        cripta_dict['priceChange'] = priceChange

        priceChangePercent = recurs_find_key('priceChangePercent', cripta)
        cripta_dict['priceChangePercent'] = priceChangePercent

        quoteVolume = recurs_find_key('quoteVolume', cripta)
        cripta_dict['quoteVolume'] = quoteVolume

        count = recurs_find_key('count', cripta)
        cripta_dict['count'] = count

        top_data.append(cripta_dict)
        top_data.sort(key=lambda i: float(i[CHOICE_SORT]), reverse=True)

    return top_data[:10]


def create_message(top_data):

    env = Environment(
        loader = FileSystemLoader('templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('table.html')
    message = template.render(items=top_data)

    return message

message = create_message(get_top_data(get_binance()))


def send_email_with_binance(message, EMAIL_LIST):

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Binance"
    msg['From'] = SENDER_EMAIL
    msg['To'] = ', '.join(EMAIL_LIST)

    part1 = MIMEText(message, 'html')
    msg.attach(part1)

    with smtplib.SMTP_SSL('smtp.yandex.ru', 465) as smtp:

        smtp.login(SENDER_EMAIL, EMAIL_PASSWORD)
        smtp.send_message(msg)

send_email_with_binance(message, EMAIL_LIST)
