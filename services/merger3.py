def get_speaker_for_word(
        word_start,
        word_end,
        pyann_seg
):

    midpoint = (
                       word_start + word_end
               ) / 2

    for seg in pyann_seg:

        if (
                seg["start"]
                <= midpoint
                <= seg["end"]
        ):

            return seg["speaker"]

    # nearest fallback
    nearest_seg = min(
        pyann_seg,
        key=lambda seg: min(
            abs(midpoint - seg["start"]),
            abs(midpoint - seg["end"])
        )
    )

    return nearest_seg["speaker"]


def merge_whisper_first(
        whis_words,
        pyann_seg
):

    aligned_words = []

    # assign speaker to words
    for word_info in whis_words:

        speaker = get_speaker_for_word(
            word_info["start"],
            word_info["end"],
            pyann_seg
        )

        aligned_words.append({
            "speaker": speaker,
            "word": word_info["word"],
            "start": word_info["start"],
            "end": word_info["end"]
        })

    if not aligned_words:
        return []

    merged_seg = []

    current_speaker = aligned_words[0]["speaker"]

    current_words = [
        aligned_words[0]["word"]
    ]

    current_start = aligned_words[0]["start"]

    current_end = aligned_words[0]["end"]

    i = 1

    while i < len(aligned_words):

        word_info = aligned_words[i]

        speaker = word_info["speaker"]

        word = word_info["word"]

        start = word_info["start"]

        end = word_info["end"]

        time_gap = start - current_end

        # SAME SPEAKER
        if (
                speaker == current_speaker
                and time_gap < 1.0
        ):

            current_words.append(word)

            current_end = end

            i += 1

            continue

        # POSSIBLE FALSE SPEAKER SWITCH
        # check next few words

        lookahead_count = 0

        j = i

        while (
                j < len(aligned_words)
                and aligned_words[j]["speaker"] == speaker
                and lookahead_count < 3
        ):

            lookahead_count += 1
            j += 1

        # if only tiny switch,
        # ignore it
        if lookahead_count <= 2:

            current_words.append(word)

            current_end = end

            i += 1

            continue

        # REAL speaker change

        merged_seg.append({
            "speaker": current_speaker,
            "start": current_start,
            "end": current_end,
            "text": " ".join(current_words).strip()
        })

        current_speaker = speaker

        current_words = [word]

        current_start = start

        current_end = end

        i += 1

    # append final segment
    merged_seg.append({
        "speaker": current_speaker,
        "start": current_start,
        "end": current_end,
        "text": " ".join(current_words).strip()
    })

    return merged_seg

def combine_same_speaker_segments(
        segments,
        max_gap=2.0
):

    if not segments:
        return []

    combined = []

    current = segments[0]

    for seg in segments[1:]:

        gap = (
                seg["start"]
                - current["end"]
        )

        # merge nearby same-speaker segments
        if (
                seg["speaker"]
                == current["speaker"]
                and gap <= max_gap
        ):

            current["text"] += (
                    " " + seg["text"]
            )

            current["end"] = seg["end"]

        else:

            combined.append(current)

            current = seg

    combined.append(current)

    return combined