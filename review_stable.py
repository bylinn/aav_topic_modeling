"""
This script is for converting output of topic stabilizer to format
that is more easily reviewed

USAGE: review_stable.py <stable ids file path> <component topic keys files parent directory>
WRITES: a review file in the same dir as the stable ids file.

"""

import os, sys

try: stable_path = os.path.abspath(sys.argv[1])
except IndexError: raise IOError('Must provide filepath of stable ids.\n'\
'USAGE: review_stable.py <stable ids file path> <component topic keys files parent directory>')
out_path = stable_path[:-7] + 'review.txt'
try: components_dir = os.path.abspath(sys.argv[2])
except IndexError: raise IOError('Must provide path containing topic key files.\n'\
'USAGE: review_stable.py <stable ids file path> <component topic keys files parent directory>')

collected = 0
for f in sorted(next(os.walk(components_dir))[2]):
    if 'topic_keys' in f: 
        if collected == 0:
            a_path = os.path.join(components_dir, f)
        elif collected == 1:
            b_path = os.path.join(components_dir, f)
        elif collected == 2:
            c_path = os.path.join(components_dir, f)
        collected += 1
try: _ = a_path
except NameError: raise IOError('topic_keys-1.txt file not found in {}'.format(components_dir))
try: _ = b_path
except NameError: raise IOError('topic_keys-2.txt file not found in {}'.format(components_dir))
try: _ = c_path
except NameError: raise IOError('topic_keys-3.txt file not found in {}'.format(components_dir))

with open(out_path, 'w') as f_out, open(stable_path, 'r') as f_ids, \
    open(a_path, 'r') as f_a, open(b_path, 'r') as f_b, open(c_path, 'r') as f_c:

    a = {topic.split()[0]:' '.join(topic.split()[1:]) for topic in f_a}
    b = {topic.split()[0]:' '.join(topic.split()[1:]) for topic in f_b}
    c = {topic.split()[0]:' '.join(topic.split()[1:]) for topic in f_c}

    next(f_ids)  # skip header

    # for each stable topic, rearrange correctly
    for topic in f_ids:
        stable_id, a_id, b_id, c_id = topic.split()

        stable_topic = 'Stable-{}'.format(stable_id)
        a_topic = 'A-{}: {}'.format(a_id, a[a_id])
        b_topic = 'B-{}: {}'.format(b_id, b[b_id])
        c_topic = 'C-{}: {}'.format(c_id, c[c_id])

        f_out.write('\r\n'.join([stable_topic, a_topic, b_topic, c_topic, '\r\n\r\n']))