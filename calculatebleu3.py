#!/usr/bin/python
import codecs
import fnmatch
import sys
import pickle
import time
import os

import math

WEIGHT = 0.25

P = {}
BP = 0

start_time = time.time()

# droplist = [".",",","(",")",":",";","?","-"]
droplist = []

basepathCandidate = str(sys.argv[1])
basepathReference = str(sys.argv[2])

print(basepathReference)

candidatePathIsDir = os.path.isfile(basepathCandidate)
referencePathIsDir = os.path.isdir(basepathReference)

def get_candidate_clip(line):
    out = {}
    test = []
    for item in line:
        temp = " ".join(item)
        test.append(temp)
    for items in test:
        if items in out:
            out[items] = out[items] + 1
        else:
            out[items] = 1
    return out

def getCandidateNgrams(line, n_value):
    n_grams = {}
    line = line[:-1]
    candidate_line_as_list = line.split()
    # candidate_line_as_list = to_lower(candidate_line_as_list)
    candidate_line_as_grams = [candidate_line_as_list[i:i+n_value] for i in range(len(candidate_line_as_list)-n_value+1)]
    # print(candidate_line_as_grams)
    candidate_line_clip = get_candidate_clip(candidate_line_as_grams)
    # print(candidate_line_clip)
    return candidate_line_clip

def filter_line(line):
    line = line.split()
    out = []
    for i in line:
        out.append(i)
    output = " ".join(out)
    return output


def additemtooutput(item, output):
    for key, value in item.items():
        if key in output:
            if value > output[key]:
                output[key] = value
        else:
            output[key] = value
    return output

def getReferenceClipCount(linenumber, NGRAMS):
    output = {}
    referenceCountList = []
    referenceLengths = []
    if (referencePathIsDir):
        for root, dir, filenames in os.walk(basepathReference):
            for filename in fnmatch.filter(filenames, "*.txt"):
                filename = os.path.join(root, filename)
                with codecs.open(filename, 'r', encoding='utf8') as f:
                    # print("DIR", filename)
                    for i,line in enumerate(f):
                        if i == linenumber:
                            line = filter_line(line)
                            referenceNgrams = getCandidateNgrams(line, NGRAMS)
                            referenceLengths.append(len(line.split()))
                referenceCountList.append(referenceNgrams)
        for item in referenceCountList:
            output = additemtooutput(item, output)
        # print(output, referenceLengths)
        return (output, referenceLengths)
    else:
        with codecs.open(basepathReference, 'r', encoding='utf8') as f:
            # print("TXT")

            for i, line in enumerate(f):
                if i == linenumber:
                    line = filter_line(line)
                    referenceLengths.append(len(line.split()))
                    referenceNgrams = getCandidateNgrams(line, NGRAMS)
            output = referenceNgrams
        # print(output, referenceLengths)

        return (output, referenceLengths)

def clip_the_candidate_ngrams(candidateNgrams, referenceClipCount):
    output = candidateNgrams
    for key, value in candidateNgrams.items():
        if key in referenceClipCount:
            if value < referenceClipCount[key]:
                continue
            else:
                output[key] = referenceClipCount[key]
        else:
            output[key] = 0
    return output

def getCandidateNgramCount(candidateNgrams):
    out = 0
    for key, value in candidateNgrams.items():
        out = out + value
    return out

def getRValue(clength, refe):
    lit=[]
    for i in refe:
        lit.append(abs(i-clength))
    if not lit:
        return 0
    else:
        index = lit.index(min(lit))
    return refe[index]

def getCandidatePrec(candidateNgrams):
    out = 0
    for key, val in candidateNgrams.items():
        out = out + val
    return out

def getSumOfP(p):
    out = 0
    for key, val in p.items():
        out = out + WEIGHT*math.log(val)
    return out

for NGRAMS in [1,2,3,4]:
    with codecs.open(basepathCandidate, 'r', encoding='utf8') as f:
        numerator = 0
        denominator = 0
        c_value = 0
        r_value = 0
        for i, line in enumerate(f):
            line = filter_line(line)
            # print(line)
            candidateLength = len(line.split())
            c_value = c_value + candidateLength
            candidateNgrams = getCandidateNgrams(line, NGRAMS)
            # print(candidateNgrams)
            denominator = denominator + getCandidateNgramCount(candidateNgrams)
            # print(getCandidatePrec(candidateNgrams))
            # print(candidateNgrams)
            referenceClipCount, referenceLengthList = getReferenceClipCount(i, NGRAMS)
            candidateNgrams = clip_the_candidate_ngrams(candidateNgrams, referenceClipCount)
            # print(getCandidateNgramCount(candidateNgrams))
            r_value = r_value + getRValue(candidateLength, referenceLengthList)
            # print(candidateLength, getRValue(candidateLength, referenceLengthList))
            numerator = numerator + getCandidatePrec(candidateNgrams)

        P[NGRAMS] = numerator/denominator
        # print(r_value, c_value)
        # print("-------------")
        if c_value > r_value:
            BP = 1
        else:
            BP = math.exp(1-(r_value/float(c_value)))

print("weighted logs: "+ str(getSumOfP(P)))
print("BP " , BP)
print("P ", P )
OUT = BP * math.exp(getSumOfP(P))
# OUT=0

print(OUT)

fo = open("bleu_out.txt", 'w')
fo.write(str(OUT))

fo.close()

