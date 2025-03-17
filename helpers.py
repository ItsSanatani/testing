def extract_username(link):
    """
    Extract username from t.me link or @username format
    """
    if "t.me/" in link:
        username = link.split("t.me/")[-1].strip("/")
        return username
    elif link.startswith("@"):
        return link.strip("@")
    else:
        return link
