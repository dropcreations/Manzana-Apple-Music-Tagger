import subprocess

def muxhls(input, output):
    try:
        retCode = subprocess.Popen(
            [
                'MP4Box',
                '-itags', 'tool=',
                '-add', input,
                '-new', output
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT
        ).wait()
    except Exception:
        retCode = 1
        
    return retCode