#from configparser import MAX_INTERPOLATION_DEPTH
import re
import random
import math
import sub
import time

import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage
import music21
from midi2audio import FluidSynth




chord_num={'C':0, 'D':2, 'E':4, 'F':5, 'G':7, 'A':9, 'B':11}
tension={'7':10, 'M7':11, '6':9, '2': 2, '4': 5, '9': 2}

def txt_to_mid(fname, output):
    key, bpm, length, chord=make_chord(fname)
    chord_tone=make_chord_tone(chord)
    scale=make_scale(key)
    bassline=make_bassline(chord_tone,chord,scale)
    mid,mid_b=make_track(key, bpm, bassline, chord_tone,length)

    mid.save(output+".mid")
    show_sheet(mid,chord)
    mid_b.save(output+"_b.mid")

    




def make_chord(fname):
    f=open(fname,'r')
    data=f.readlines()
    key=re.split('[key: \n]',data[0])
    key=[i for i in key if i]

    bpm=re.split('[bpm: \n]',data[1])
    bpm=[i for i in bpm if i]

    chord=data[2].split('|')
    chord=[i for i in chord if i]
    length=len(chord)
    newchord=[]
    for i in chord:
        if not '*' in i:
            count=0
            idx=[]
            for j in range(len(i)):
                if i[j] in chord_num.keys():
                    count+=1
                    idx.append(j)
            if count==1:
                newchord.append(i+'***')
            elif count==2:
                newchord.append(i[:idx[1]]+'*')
                newchord.append(i[idx[1]:]+'*')
            elif count==4:
                for j in i:
                    newchord.append(j)
            


        else:
            prev=0
            for j in range(1,len(i)):
                if i[j] in chord_num.keys():
                    newchord.append(i[prev:j])
                    prev=j
            newchord.append(i[prev:])

    chords=[] #[コードシンボル, 拍数]の二次元配列
    for i in newchord:
        cs=i.split('*')[0]
        num=len(i.split('*'))
        chords.append([cs,num])
    """
    for i in range(len(chords)-1):
        if i<len(chords):
            if chords[i][0]==chords[i+1][0] and chords[i][1]+chords[i+1][1]<=8:
                chords[i][1]+=chords[i+1][1]
                chords.pop(i+1)
    """


    f.close()

    return key[0], int(bpm[0]), length, chords


def make_chord_tone(data):
    length=[i[1] for i in data]
    data=[i[0] for i in data]

    chordtone=[]
    for chord in data:
        root=chord_num[chord[0]]
        if len(chord)>1 and chord[1]=='-':
            root-=1
        elif len(chord)>1 and chord[1]=='#':
            root+=1

        tone=[root,root+4,root+7]

        if('dim' in chord):
            tone[1]-=1
            tone[2]-=1
        elif('aug' in chord):
            tone[1]+=1
            tone[2]+=1
        elif('m' in chord):
            tone[1]-=1
        elif('sus' in chord):
            tone.pop(1)

        
        for i in reversed(chord):
            if i.isdecimal():
                tone.append(root+tension[i])
                if('M' in chord and i=='7'):
                    tone[-1]+=1
            #else:
                #break
        
        tone=[i%12 for i in tone]
        chordtone.append(tone)

    ret=list(zip(chordtone,length))
    return ret

def make_scale(key):
    root=chord_num[key[0]]
    if key[-1]!='m':
        scale=[root,root+2,root+4,root+5,root+7,root+9,root+11]
    else:
        scale=[root,root+2,root+3,root+5,root+7,root+8,root+10]
    
    scale=[i%12 for i in scale]

    return scale 

def make_bassline(chord_tone, chord, scale):

    length=[i[1] for i in chord_tone]
    chord_tone_=[]
    for i in range(len(chord_tone)):#7th以外のコードトーンは無視
        if(chord[i][0][-1]=='7'):
            chord_tone_.append(chord_tone[i][0][:4])
        else:
            chord_tone_.append(chord_tone[i][0][:3])

    for i in range(len(chord_tone_)):
        if i<len(chord_tone_):
            if i<len(chord_tone_)-1 and chord_tone_[i]==chord_tone_[i+1] and length[i]+length[i+1]<=8:
                length[i]=[length[i],length[i+1]]
                chord_tone_.pop(i+1)
                length.pop(i+1)
            else:
                length[i]=[length[i]]
                   
    bassline=[]
    diff=[-1,-1,-1,1,1,1,-2,-2,2,2]
    pattern=[0,1,1,2,2]
    chord_tone=[]
    for i in range(len(chord_tone_)):
        for j in range(len(length[i])):#頭だけ決定し、横並びに(以降lengthはlen(bassline[i])で代用)
            bassline.append([chord_tone_[i][0] for k in range(length[i][j])])
            if j!=0:
                bassline[-1][0]=random.choice(chord_tone_[i])
            chord_tone.append(chord_tone_[i])
            
    for i in range(len(bassline)-1):#お尻だけ決定
        if len(bassline[i])>1:
            d=diff[:6]+[j for j in diff[6:] if (bassline[i+1][0]+j)%12 in scale+chord_tone[i]] 
            bassline[i][-1]=(bassline[i+1][0]+random.choice(d))%12

    for i in range(len(bassline)):
        if len(bassline[i])==4 and i<len(bassline)-1:
            p=random.choice(pattern)
            if p==0:
                bassline[i][1]=random.choice(chord_tone[i])
                if bassline[i][1]==bassline[i][0]:
                    bassline[i][1]=random.choice(chord_tone[i])
                    
                bassline[i][2]=random.choice(chord_tone[i])
                if bassline[i][2]==bassline[i][1] or bassline[i][2]==bassline[i][3]:
                    bassline[i][2]=random.choice(chord_tone[i])
            elif p==1:
                bassline[i][1]=random.choice(chord_tone[i])
                if bassline[i][1]==bassline[i][0]:
                    bassline[i][1]=random.choice(chord_tone[i])

                if (bassline[i][3]-bassline[i+1][0])%12==11:
                    bassline[i][2]=random.choice([bassline[i+1][0]+7,bassline[i+1][0]-2])%12
                elif (bassline[i][3]-bassline[i+1][0])%12==1:
                    bassline[i][2]=random.choice([bassline[i+1][0]+2])%12

                else:
                    bassline[i][2]=sub.passing(bassline,i,1,3,scale)
                    if bassline[i][2]==bassline[i][1] or bassline[i][2]==bassline[i][3]:
                        bassline[i][2]=sub.passing(bassline,i,1,3,scale)
                
            else:
                bassline[i][2]=random.choice(chord_tone[i])
                if bassline[i][2]==bassline[i][1] or bassline[i][2]==bassline[i][3]:
                    bassline[i][2]=random.choice(chord_tone[i])

                bassline[i][1]=sub.passing(bassline,i,0,2,scale)
                if bassline[i][1]==bassline[i][0] or bassline[i][1]==bassline[i][2]:
                     bassline[i][1]=sub.passing(bassline,i,0,2,scale)
                
        elif len(bassline[i])==3:
            p=random.choice(pattern[:2])
            if p==0:
                bassline[i][1]=random.choice(chord_tone[i])
            else:
                bassline[i][1]=sub.passing(bassline,i,0,2,scale)


        elif len(bassline[i])==4 and i==len(bassline)-1:
            bassline[i][1]=random.choice(chord_tone[i])
            bassline[i][2]=random.choice(chord_tone[i])


    bassline_=[]
    for i in bassline:
        for j in i:
            bassline_.append(j)

    bassline=bassline_.copy()


    #オクターブ調節

    MAX_NOTE=16
    MIN_NOTE=-8
    updown=[-1,-1,-1,0,0,0,1,1,1]
    for i in range(len(bassline)-1):
        if (bassline_[i] > bassline[i+1] and (bassline_[i]-bassline_[i+1])%12 in [1,2]) or (bassline_[i] < bassline_[i+1] and (bassline_[i]-bassline_[i+1])%12 in [10,11]):
            bassline[i+1]=bassline_[i+1]+(bassline[i]-bassline_[i])
        elif bassline_[i] < bassline[i+1] and (bassline_[i]-bassline_[i+1])%12 in [1,2]:
            bassline[i+1]=bassline_[i+1]+(bassline[i]-bassline_[i])-12
        elif bassline_[i] > bassline_[i+1] and (bassline_[i]-bassline_[i+1])%12 in [10,11]:
            bassline[i+1]=bassline_[i+1]+(bassline[i]-bassline_[i])+12

        elif (bassline_[i] > bassline_[i+1] and (bassline_[i]-bassline[i+1])%12 < 6):
            bassline[i+1]=bassline_[i+1]+(bassline[i]-bassline_[i])+12*random.choice(updown[3:7])
        elif (bassline_[i] > bassline_[i+1] and (bassline_[i]-bassline[i+1])%12 > 6):
            bassline[i+1]=bassline_[i+1]+(bassline[i]-bassline_[i])+12*random.choice(updown[5:])
        elif (bassline_[i] > bassline_[i+1] and (bassline_[i]-bassline[i+1])%12 == 6):
            bassline[i+1]=bassline_[i+1]+(bassline[i]-bassline_[i])+12*random.choice(updown[3:])

        elif (bassline_[i] < bassline_[i+1] and (bassline_[i]-bassline[i+1])%12 < 6):
            bassline[i+1]=bassline_[i+1]+(bassline[i]-bassline_[i])+12*random.choice(updown[2:6])
        elif (bassline_[i] < bassline_[i+1] and (bassline_[i]-bassline[i+1])%12 > 6):
            bassline[i+1]=bassline_[i+1]+(bassline[i]-bassline_[i])+12*random.choice(updown[:4]) 
        elif (bassline_[i] < bassline_[i+1] and (bassline_[i]-bassline[i+1])%12 == 6):
            bassline[i+1]=bassline_[i+1]+(bassline[i]-bassline_[i])+12*random.choice(updown[:6])

        elif bassline_[i] == bassline_[i+1]:
            bassline[i+1]=bassline_[i+1]+(bassline[i]-bassline_[i])+12*random.choice(updown[2:7]) 
        ###この時点で差が12より大きくなることはない

        if bassline[i+1]>MAX_NOTE: 
            bassline[i+1]-=12
            if (i+1)%2==0:
                bassline[i]-=12
        if bassline[i+1]<MIN_NOTE: 
            bassline[i+1]+=12
            if (i+1)%2==0:
                bassline[i]+=12

        #おまじない(多分なくても平気)
        if bassline[i]-bassline[i+1]>12:
            bassline[i+1]+=12
        if bassline[i+1]-bassline[i]>12:
            bassline[i+1]-=12
    
    #print(bassline)

    return bassline


    

def make_track(key, tmp, bassline, chord_tone, length):
    
    mid = MidiFile()
    """
    ベースの部分
    """
    basstrack = MidiTrack()
    basstrack.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(tmp)))
    basstrack.append(MetaMessage('key_signature', key=key))
    basstrack.append(Message('program_change',channel=1, program=32))

    for i in bassline:
        basstrack.append(Message('note_on', channel=1, note=i+36, velocity=127, time=1))
        basstrack.append(Message('note_off', channel=1, note=i+36,time = 479))

    """
    伴奏の部分(おまけ)
    """

    
    guitartrack=MidiTrack()
    guitartrack.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(tmp)))
    guitartrack.append(MetaMessage('key_signature', key=key))
    guitartrack.append(Message('program_change', channel=0, program=4))
    """
    timediff=[[1,960,320,160],[320,1599,1,479]]


    for i in range(len(chord_tone)):
        for j in range(len(timediff[i%2])):
            if j%2==0:
                for k in range(len(chord_tone[i])):
                    if k==0:
                        guitartrack.append(Message('note_on', channel=0, note=60+chord_tone[i][k],velocity=20, time=timediff[i%2][j]))
                    else:
                        guitartrack.append(Message('note_on',channel=0, note=60+chord_tone[i][k],velocity=20, time=0))
            else:
                for k in range(len(chord_tone[i])):
                    if k==0:
                        guitartrack.append(Message('note_off', channel=0, note=60+chord_tone[i][k],time=timediff[i%2][j]))
                    else:
                        guitartrack.append(Message('note_off', channel=0, note=60+chord_tone[i][k],time=0))
    """

    for i in chord_tone:
        for k in range(i[1]//2):
            for j in range(len(i[0])):
                if j==0:
                    guitartrack.append(Message('note_on', channel=0, note=60+i[0][j], velocity=80, time=0))
                else:
                    guitartrack.append(Message('note_on', channel=0, note=60+i[0][j], velocity=80, time=0))
            for j in range(len(i[0])):
                if j==0:
                    guitartrack.append(Message('note_off', channel=0, note=60+i[0][j], time=2*480-160))
                else:
                    guitartrack.append(Message('note_off', channel=0, note=60+i[0][j], time=0))
            guitartrack.append(Message('note_on', channel=0, note=60, velocity=0, time=0))
            guitartrack.append(Message('note_off', channel=0, note=60, time=160))
            
        for k in range(i[1]%2):
            for j in range(len(i[0])):
                if j==0:
                    guitartrack.append(Message('note_on', channel=0, note=60+i[0][j], velocity=80, time=0))
                else:
                    guitartrack.append(Message('note_on', channel=0, note=60+i[0][j], velocity=80, time=0))
            for j in range(len(i[0])):
                if j==0:
                    guitartrack.append(Message('note_off', channel=0, note=60+i[0][j], time=1*480-160))
                else:
                    guitartrack.append(Message('note_off', channel=0, note=60+i[0][j], time=0))

            guitartrack.append(Message('note_on', channel=0, note=60, velocity=0, time=0))
            guitartrack.append(Message('note_off', channel=0, note=60, time=160))
    """
    ドラムの部分
    """
    drumtrack=MidiTrack()
    drumtrack.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(tmp)))
    drumtrack.append(MetaMessage('key_signature', key=key))
    drumtrack.append(Message('program_change', channel=9))

    timediff=[[0,800,160,800],[0,800,160,480,320],[0,800,160,800],[0,800,160,320,160,320]]
    for i in range(length):
        for j in timediff[i%4]:
            drumtrack.append(Message('note_on', channel=9, note=40, velocity=80,time=j))
        drumtrack.append(Message('note_on', channel=9, note=40, velocity=0, time=160))


    

    mid.tracks.append(guitartrack)
    mid.tracks.append(basstrack)
    mid.tracks.append(drumtrack)

    mid_b = MidiFile()
    mid_b.tracks.append(basstrack)

    return mid, mid_b


def num_to_note(num):
    chord={0:'C', 1: 'C#', 2: 'D', 3: 'E-', 4: 'E', 5: 'F', 6: 'F#', 7: 'G', 8: 'A-', 9: 'A', 10: 'B-', 11: 'B'}
    tone=chord[num%12]
    oct=num//12-1
    return tone+str(oct)

def show_sheet(mid, chord):
    key = mid.tracks[0][1].key
    bassline = [num_to_note(i.note) for i in mid.tracks[1] if i.type=='note_on']#  伴奏あり

    sheet=music21.stream
    melody = sheet.Stream()


    prev=0
    for i in chord:
        cs=music21.harmony.ChordSymbol(i[0])
        cs.duration.quarterLength=0
        melody.append(cs)
        for j in range(i[1]):
            melody.append(music21.note.Note(bassline[prev+j]))
        prev+=i[1]

    
    if(key[-1]=='m'):
        melody.keySignature=music21.key.Key(key[:-1],'minor')
    else:
        melody.keySignature=music21.key.Key(key)
    

    conv_musicxml = music21.converter.subConverters.ConverterMusicXML()
    conv_musicxml.write(melody, 'musicxml', fp='output/tmp.png', subformats=['png'])


    #.mp3作ってページで再生できるようにしたかったがなぜか無音になる
    # サウンドフォントを指定する
    fs = FluidSynth(sound_font='font.sf2')
    #fs = FluidSynth()
    # 入力するmidiファイルとアウトプットファイル
    fs.midi_to_audio('output/tmp.mid', 'output/tmp.mp3') # またはoutput.wav