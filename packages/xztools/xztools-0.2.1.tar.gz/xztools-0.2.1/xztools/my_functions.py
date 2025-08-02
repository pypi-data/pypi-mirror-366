def random_compliment():
    compliments = ["You're awesome!", "You light up the room!", "You're a coding star!"]
    import random
    return random.choice(compliments)

def time_remaining():
    """
    Calculate and display how many days are left for:
    - Weekend (end of Sunday)
    - End of current month
    - End of current year
    """
    from datetime import datetime, timedelta
    import calendar
    
    today = datetime.now()
    
    # Calculate days until end of weekend (Sunday)
    days_until_sunday = (6 - today.weekday()) % 7
    if days_until_sunday == 0:
        days_until_sunday = 7  # If today is Sunday, count to next Sunday
    
    # Calculate days until end of month
    last_day_of_month = calendar.monthrange(today.year, today.month)[1]
    days_until_month_end = last_day_of_month - today.day
    
    # Calculate days until end of year
    end_of_year = datetime(today.year, 12, 31)
    days_until_year_end = (end_of_year - today).days
    
    # Create a colorful and informative output
    result = f"""
⏰ TIME REMAINING REPORT ⏰
{'='*40}

📅 Today: {today.strftime('%A, %B %d, %Y')}
{'='*40}

🎉 Weekend Countdown: {days_until_sunday} day{'s' if days_until_sunday != 1 else ''} until Sunday
📅 Month Countdown: {days_until_month_end} day{'s' if days_until_month_end != 1 else ''} until end of {today.strftime('%B')}
🎊 Year Countdown: {days_until_year_end} day{'s' if days_until_year_end != 1 else ''} until New Year!

{'='*40}
"""
    
    return result