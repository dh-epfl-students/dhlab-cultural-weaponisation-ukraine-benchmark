def timelines_to_dataframe(timelines):
    """
    Convert the timelines dict into a pandas DataFrame with:
    article | start | end | status | diff (days)
    Ensures all datetimes are UTC-aware to avoid subtraction errors.
    """
    rows = []

    for article, intervals in timelines.items():
        for interval in intervals:
            start = interval["start"]
            end = interval["end"]
            status = interval["status"]

            # Normalize timezone to UTC
            if start is not None:
                if start.tzinfo is None:
                    start = start.replace(tzinfo=timezone.utc)
                else:
                    start = start.astimezone(timezone.utc)

            if end is not None:
                if end.tzinfo is None:
                    end = end.replace(tzinfo=timezone.utc)
                else:
                    end = end.astimezone(timezone.utc)

            # Compute difference in days
            diff_days = (end - start).days if start and end else None

            rows.append({
                "article": article,
                "start": start,
                "end": end,
                "status": status,
                "diff": diff_days
            })

    return pd.DataFrame(rows)