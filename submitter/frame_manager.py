"""
Frame range manager
"""

def framerange_to_frames(input_str):
    """
    Convert a pattern framerange string into a list of frames
    ex : "1-3,5" >> [{start: 1, end: 3, step: 1}, {start: 5, end: 5, step: 1}]

    :param str input_str: the pattern framerange string
    :rtype: list[{start: 0, end: 0, step: 0}]
    """
    framelist = list()
    splits = input_str.split(',')
    for split in splits:
        step = 1
        if '-' in split:
            frame_object = {
                "start": int(split.split('-')[0]),
                "end": int(split.split('-')[1])}
        else:
            frame_object = {
                "start": int(split.split('x')[0]),
                "end": int(split.split('x')[0])}
        if 'x' in split:
            step = int(split.split('x')[-1])
        frame_object["step"] = int(step)
        framelist.append(frame_object)

    return framelist


def frames_to_framerange(frames):
    """
    Convert a list of frame numbers into an optimized deadline framerange string
    ex : [1,2,3,5] >> "1-3,5"

    :param frames: list of frames
    :type frames: list[int]
    :rtype: str
    """
    frames = sorted(list(set(frames)))
    result = list()

    start = None
    prev = None
    for f in frames:
        if start is None:
            start = f
        if prev is not None:
            if f == prev + 1:
                pass
            if f > prev + 1:
                if start == prev:
                    id_range = str(start)
                else:
                    id_range = '{}-{}'.format(start, prev)
                result.append(id_range)
                start = f
        prev = f

    # add the last one
    if start == prev:
        id_range = str(start)
    else:
        id_range = '{}-{}'.format(start, prev)
    result.append(id_range)

    return ','.join(result)
