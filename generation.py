import os
from time import sleep
import random
import shlex
import subprocess
import soundfile as sf
import pyrubberband as pyrb
from pydub import AudioSegment #mix
import librosa
import mashability as mas

input_path='../../hip-pop2/'
can_path='../../hip-pop2/'
can_output='ps_ts.wav'
can_ps_output='ps.wav'
output_path='./output_audio/'


def generation(matched_wave, pitch, input_chroma, input_tempo, input_phrase):
    print("choose:{}".format(matched_wave))
    ## change dir to output_path in pitchShift()
    pitchShift(matched_wave, pitch, input_phrase)

    print("---Generating time stretching file---")
    timeStretch(input_tempo)

    print("---Generating volume adjust file(nor)---")
    volumeNor(input_phrase)

    print("---Generating mixed file---")
    mixed(input_phrase)

def pitchShift(loop, pitch, input_phrase):
    os.chdir(output_path+input_phrase[:-4])
    y, sr = librosa.load(can_path+loop,sr=44100)
    sf.write(loop, y, samplerate=44100) #original candidate
    # pitch shifting (maybe a little difference after shifting)
    y_shift = pyrb.pitch_shift(y, sr, n_steps=-pitch)
    sf.write(can_ps_output, y_shift, samplerate=44100)
    #y_shift = librosa.effects.pitch_shift(y, sr, n_steps=pitch) #by liborsa

    '''
    # checked by hormonic
    chromagram = librosa.feature.chroma_cqt(y=y_harmonic,sr=sr)
    # We'll use the median value of each feature between beat frames                                   
    beat_chroma = librosa.util.sync(chromagram,
                                beat_frames,
                                aggregate=np.median)
    print('shape of can_chroma:{}'.format(beat_chroma.shape))
    can_chroma24 =np.concatenate((beat_chroma,beat_chroma),axis=0)
    mas.harmonic(input_chroma,can_chroma24)
    '''

def timeStretch(input_tempo):
    y_shift, sr = librosa.load(can_ps_output,sr=44100)
    y_tempo=mas.get_tempo(can_ps_output)
    print("can_tempo:{}".format(y_tempo))
    rate =float(input_tempo)/y_tempo
    print("stretch_rate:{}".format(rate))
    #librosa.effects.time_stretch(y_shift, rate) #by liborsa
    y_stretch_shift=pyrb.time_stretch(y_shift, sr, rate)
    # seg11
    sf.write(can_output, y_stretch_shift, samplerate=44100)    
    #librosa.output.write_wav('candidate.wav',y_stretch_shift, sr=44100) #bit will be 64

def volumeNor(input_phrase):
    FFMPEG_CMD = "ffmpeg-normalize"
    cmd2=FFMPEG_CMD+' -v -f '+input_path+input_phrase+' -o '+input_phrase[:-4]+'_nv.wav'
    subprocess.Popen(shlex.split(cmd2))
    cmd=FFMPEG_CMD+' -v -f '+can_output+' -o '+can_output[:-4]+'_nv.wav'
    subprocess.Popen(shlex.split(cmd))
    

def mixed(input_phrase):
    # wait for cmd ffmpeg
    while True:   
        if os.path.isfile(can_output[:-4]+'_nv.wav') and os.path.isfile(input_phrase[:-4]+'_nv.wav'):
            can_wave=AudioSegment.from_file(can_output[:-4]+'_nv.wav')
            input_wave=AudioSegment.from_file(input_phrase[:-4]+'_nv.wav')
            combined=input_wave.overlay(can_wave) #if can is longer than input, will be cut
            # seg11
            combined.export('combination.wav',format='wav')
            break
        else:
            sleep(random.uniform(0.5, 1.3))

