import random
"""
def passing(each, chord_tone, scale, c, b, a):
    if ( abs(each[b]-each[a])==6 ):
        d=[j for j in [-1,1,-2,2] if (each[a]+j)%12 in scale or (each[a]+j)%12 in chord_tone]
    elif(each[b]==each[a] or abs(each[b]-each[a]) in [1,11]):
        if each[c] > each[b]:
            d=[j for j in [-1,-2] if (each[a]+j)%12 in scale or (each[a]+j)%12 in chord_tone]
        else:
            d=[j for j in [1,2] if (each[a]+j)%12 in scale or (each[a]+j)%12 in chord_tone]
    elif (each[b]<each[a] and each[b]-each[a]<6) or (each[b]>each[a] and each[b]-each[a]>6):
        d=[j for j in [-1,-2] if (each[a]+j)%12 in scale or (each[a]+j)%12 in chord_tone]
    else:
        d=[j for j in [1,2] if (each[a]+j)%12 in scale or (each[a]+j)%12 in chord_tone]

    return d
"""

def passing(bassline, i, b,a,scale):

    if bassline[i][a]==bassline[i][b]:
        ret=random.choice([j+bassline[i][b] for j in [-1,1]] + [j+bassline[i][b] for j in [-2,2] if (j+bassline[i][b])%12 in scale] )
    elif abs(bassline[i][a]-bassline[i][b])<=6:
        ret = random.choice([j%12 for j in range(min(bassline[i][b],bassline[i][a]),max(bassline[i][b],bassline[i][a])+1) if j%12 in scale])
    else:
        ret = random.choice([j%12 for j in range(max(bassline[i][a], bassline[i][b]),min(bassline[i][a], bassline[i][b])+13) if j%12 in scale])

    return ret