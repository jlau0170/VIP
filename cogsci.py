from Generalize import generalize
import operator
import random

class CogSciModule(object):
    def __init__(self, i_how_often = 1):
        self.i_how_often = i_how_often
        self.topics = {
            'location': 0,
            'time': 0,
            'person': 0,
            'nature': 0
        }
        self.hypothesis = ""
        self.locations = open('Resources/cities15000.txt', encoding='utf-8').read()
        self.times = open('Resources/time.txt', encoding='utf-8').read()
        self.persons = open('Resources/clothes.txt', encoding='utf-8').read()
        self.nature = open('Resources/nature.txt', encoding='utf-8').read()
        self.toggle = True
        self.counter = random.randint(0, 100)
        self.question = ''


    def updateCurrentAnnotations(self, ls_new_annotations):
        if (type(ls_new_annotations) is not type([])):
            if (type(ls_new_annotations) is not type('string')):
                raise ValueError('Please enter a list of strings or string')
            else:
                ls_new_annotations = [ls_new_annotations]

        annotations = ls_new_annotations
        for annotation in annotations:
            if (self.hypothesis != annotation):
                self.hypothesis = annotation
                gen_hypo = generalize("Resources/extraneousWords.txt", self.hypothesis)
                # import pdb; pdb.set_trace()
                hypo = gen_hypo.split(',')
                for word in hypo:
                    if word in self.locations:
                        self.topics['location'] += 1
                    elif word in self.times:
                        self.topics['time'] += 1
                    elif word in self.persons:
                        self.topics['person'] += 1
                    elif word in self.nature:
                        self.topics['nature'] += 1
        self.maxTopic = max(self.topics.items(), key=operator.itemgetter(1))[0]
        self.toggle = not self.toggle
        if (self.counter % 2 == 0):
            self.confirmationBias()
        else:
            self.anchoringBias()

        self.counter += 1
        return self.question

    def confirmationBias(self):
        if (self.toggle):
            self.question = "What evidence do you have which supports this " + self.maxTopic
        else:
            self.question = "What evidence do you have which doesn't support this " + self.maxTopic

    def anchoringBias(self):
        alternatives = []
        for topic in self.topics.keys():
            if topic is not self.maxTopic:
                alternatives.append(topic)
        if len(alternatives) == 0:
            self.question = "You have focused on location, person, time, and nature. Do you have other aspects you'd like to focus on?"
        else:
            newFocus = alternatives[random.randrange(len(alternatives))]
            self.question = "You are focusing on " + self.maxTopic + " too much." + " Do you have any hypothesis regarding " + newFocus



if __name__ == "__main__":
    csm = CogSciModule()
    xD = csm.updateCurrentAnnotations(['atlanta', 'day', 'hour', 'minute', 'second', 'time', 'now'])
    print(xD)
