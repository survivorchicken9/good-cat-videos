def predict(video_input: str):
    # convert to lowercase and create list
    video_input_processed = video_input.lower().split()

    # manually adding top words from CountVectorizer
    good_words = [
        "2020",
        "39",
        "animals",
        "baby",
        "baby cats",
        "best",
        "best funny",
        "cat",
        "cat compilation",
        "cat videos",
        "cat videos compilation",
        "cats",
        "cats cute",
        "cats cute funny",
        "cats dogs",
        "compilation",
        "cute",
        "cute funny",
        "cute funny cat",
        "dogs",
        "funny",
        "funny cat",
        "funny cat videos",
        "funny cats",
        "funny cats dogs",
        "laugh",
        "try",
        "video",
        "videos",
        "videos compilation",
    ]

    # heuristic: video is good if >= 50% of title is made of top words
    video_input_good_words_count = len(
        [word for word in video_input_processed if word in good_words]
    )
    video_input_count = len(video_input_processed)
    if video_input_good_words_count / video_input_count >= 0.4:
        return True
    return False
