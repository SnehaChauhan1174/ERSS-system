def merge_whisper_first(whis_seg,pyann_seg):
    # both are list
    merged_seg=[]

    for seg in whis_seg:
        best_overlap=-1
        best_speaker=None
        best_dist=float("inf")
        nearest_speaker=None
        for p_seg in pyann_seg:
            if p_seg["start"]>seg["end"]:
                break

            overlap=min(seg["end"],p_seg["end"])-max(p_seg["start"],seg["start"])
            if overlap>best_overlap:
                best_overlap=overlap
                best_speaker=p_seg["speaker"]
            distance=min(
                abs(seg["start"]-p_seg["end"]),
                abs(seg["end"]-p_seg["start"])
            )
            if distance<best_dist:
                best_dist=distance
                nearest_speaker=p_seg["speaker"]

        # use overlap speaker if found, else nearest speaker
        final_speaker = best_speaker if best_overlap > 0 else nearest_speaker
        merged_seg.append({
            "start":seg["start"],
            "end":seg["end"],
            "speaker":final_speaker if final_speaker else "UNKNOWN",
            "text":seg["text"]
        })
    return merged_seg


