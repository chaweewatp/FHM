from tqdm import tqdm
from time import sleep

pbar1 = tqdm(["a", "b", "c", "d"])
pbar2 = tqdm(['1','2','3','4'])
for char in pbar1:
    sleep(0.25)
    pbar1.set_description("Processing %s" % char)
    for char2 in pbar2:
        sleep(0.25)
        pbar2.set_description("Processing %s" % char)
