from datetime import datetime

def timedelta_pl(end_date):
    now = datetime.now()
      # 2019-08-01T18:15:00.000Z
    end = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S.%fZ")
    time = end - now

    days = time.days
    hours, remainder = divmod(time.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    countdown = []

    days_remainder = None
    if days >= 7:
        weeks, days_remainder = divmod(days, 7)
        days = days_remainder

        if weeks == 1:
            countdown.append("tydzień")
        elif weeks <= 4:
            countdown.append("{} tygodnie".format(weeks))
        else:
            countdown.append("{} tygodni".format(weeks))
    
    if days != 0:
        if days == 1:
            countdown.append("1 dzień")
        else:
            countdown.append("{} dni".format(days))
    
    if len(countdown) == 0:
        if hours == 0:
            pass
        elif hours == 1:
            countdown.append("1 godzinę")
        else:
            countdown.append("{} godzin".format(hours))

    if len(countdown) == 0:
        if minutes != 0:
            countdown.append("{} minut".format(minutes))
        else:
            countdown.append("{} sekund".format(seconds))

    if len(countdown) != 1:
        result = ', '.join(countdown[:-1])
        result += " i " + countdown[-1]

    else:
        result = countdown[0]

    if days < 0:
        result = "<strong>... już mineła</strong>"

    return result