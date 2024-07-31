from datetime import datetime, timedelta, time

class Timeslot:
    def __init__(self, id, day_of_week, start_time, end_time):
        self.id = id
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time

    def __str__(self):
        return (
            f"Timeslot("
            f"id={self.id}, "
            f"day_of_week={self.day_of_week}, "
            f"start_time={self.start_time}, "
            f"end_time={self.end_time})"
        )

def generate_timeslots(start_date, end_date, interval_minutes):
    timeslot_list = []
    current_id = 1

    while start_date <= end_date:
        for hour in range(7, 15):
            for minute in range(0, 60, interval_minutes):
                start_time = datetime.combine(start_date, time(hour, minute))
                end_time = start_time + timedelta(minutes=interval_minutes)
                timeslot_list.append(Timeslot(current_id, start_date.strftime("%Y-%m-%d"), start_time.time(), end_time.time()))
                current_id += 1
        start_date += timedelta(days=1)

    return timeslot_list

# Przykładowe użycie
start_date = datetime(2024, 7, 1)
end_date = datetime(2024, 7, 3)
timeslots = generate_timeslots(start_date, end_date, 10)

for timeslot in timeslots:
    print(timeslot)
