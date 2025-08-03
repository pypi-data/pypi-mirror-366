import sys

if sys.platform == 'linux':
    from SCbtr.pulseaudio import *

    # also load main classes if building documentation:
    if 'sphinx' in sys.modules:
        from SCbtr.pulseaudio import _Speaker, _Microphone, _Player, _Recorder

elif sys.platform == 'darwin':
    from SCbtr.coreaudio import *
elif sys.platform == 'win32':
    from SCbtr.mediafoundation import *
else:
    raise NotImplementedError('SoundCard does not support {} yet'.format(sys.platform))
