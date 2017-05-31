import threading
import datetime
import shortuuid
import subprocess
import os
import re


def _similarity_test_sim_approach(path1, path2, lang1='text', lang2='text'):
    LANG_C_GROUP = ['c', 'cpp']
    LANG_JAVA_GROUP = ['java']
    if lang1 in LANG_C_GROUP and lang2 in LANG_C_GROUP:
        report = subprocess.check_output(['/usr/bin/sim_c', '-p', path1, path2], timeout=5).decode().strip()
    elif lang1 in LANG_JAVA_GROUP and lang2 in LANG_JAVA_GROUP:
        report = subprocess.check_output(['/usr/bin/sim_java', '-p', path1, path2], timeout=5).decode().strip()
    else:
        report = subprocess.check_output(['/usr/bin/sim_text', '-p', path1, path2], timeout=5).decode().strip()
    raw_data = list(map(int, re.findall(r'consists for (\d+) %', report)))
    if not raw_data:
        return 0
    return sum(raw_data) / len(raw_data)


def similarity_test(code1, code2, lang1, lang2, approach='sim'):
    path1 = os.path.join('/tmp', shortuuid.ShortUUID().random(32))
    path2 = os.path.join('/tmp', shortuuid.ShortUUID().random(32))
    res = ''
    try:
        with open(path1, 'w') as f, open(path2, 'w') as g:
            f.write(code1)
            g.write(code2)
        if approach == 'sim':
            similarity = _similarity_test_sim_approach(path1, path2, lang1, lang2)
            if similarity > 40:
                res = 'similarity confidence %.6f' % similarity
    except Exception as e:
        res = 'error encountered %s' % repr(e)

    if os.path.exists(path1):
        os.remove(path1)
    if os.path.exists(path2):
        os.remove(path2)
    return res


class SimilarityTestThread(threading.Thread):

    def __init__(self, contest, output):
        super().__init__()
        self.submissions = contest.submission_set.all()
        self.output = output

    def run(self):
        with open(self.output, 'w', buffering=1) as output:
            print('Similarity test begins at %s' % str(datetime.datetime.now()), file=output)
            print('==========================\n', file=output)

            print('=== Total submissions: %d ===\n' % len(self.submissions), file=output)

            for idx1, sub1 in enumerate(self.submissions):
                for idx2, sub2 in enumerate(self.submissions):
                    if idx1 >= idx2:
                        continue
                    if sub1.author == sub2.author:
                        continue
                    if sub1.problem != sub2.problem:
                        continue
                    result = similarity_test(sub1.code, sub2.code, sub1.lang, sub2.lang)
                    if result:
                        print('%d %d at Problem %d: %s' % (sub1.id, sub2.id, sub1.problem_id, result), file=output)
                if idx1 % 100 == 0:
                    print('\n=== Mark point %d at %s ===\n' % (idx1, str(datetime.datetime.now())), file=output)

            print('\n==========================', file=output)
            print('Similarity test ends at %s' % str(datetime.datetime.now()), file=output)
