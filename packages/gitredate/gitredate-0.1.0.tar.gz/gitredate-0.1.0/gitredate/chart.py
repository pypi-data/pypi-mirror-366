from datetime import datetime, time, timedelta

from bokeh.models import BoxAnnotation, Range1d
from bokeh.plotting import figure, show


def chart(
    redates: dict[str, tuple[datetime, datetime]],
    old_min_date: datetime,
    old_max_date: datetime,
    new_min_date: datetime,
    new_max_date: datetime,
    work_days: list[int],
    work_hour_start: time,
    work_hour_end: time,
):
    p = figure(
        x_axis_type="datetime",
        sizing_mode="stretch_width",
        height=320,
        tools="pan,wheel_zoom,box_zoom,crosshair,reset",
    )
    p.y_range = Range1d(0, 3)

    min_date = min(old_min_date, new_min_date)
    max_date = max(old_max_date, new_max_date)

    work_days = work_days
    work_hour_start = work_hour_start
    work_hour_end = work_hour_end

    # Old dates
    x = [c[0] for c in redates.values()]
    y = [1 for _ in redates.values()]
    p.scatter(x, y, size=5, color="#F00")

    # New dates
    x = [c[1] for c in redates.values()]
    y = [2 for _ in redates.values()]
    p.scatter(x, y, size=5, color="#000")

    # Annotations
    day = min_date - timedelta(days=1)
    while day <= max_date:
        this_day = day.date()
        next_day = day.date() + timedelta(days=1)
        this_day_is_worked = this_day.weekday() in work_days
        next_day_is_worked = next_day.weekday() in work_days
        if not this_day_is_worked:
            p.add_layout(
                BoxAnnotation(
                    left=datetime.combine(this_day, time.min),
                    right=datetime.combine(next_day, time.min),
                    fill_alpha=0.1,
                    fill_color="#f40",
                )
            )

        p.add_layout(
            BoxAnnotation(
                left=datetime.combine(
                    this_day,
                    work_hour_end if this_day_is_worked else time.max,
                ),
                right=datetime.combine(
                    next_day,
                    work_hour_start if next_day_is_worked else time.min,
                ),
                fill_alpha=0.1,
                fill_color="#f00",
            )
        )
        day += timedelta(days=1)

    # Show chart
    show(p)
