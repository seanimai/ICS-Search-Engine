from simhash import Simhash

# set to hold fingerprints of downloaded web pages
fingerprints = set()

# function to find the similarity between values v1, v2.
# f is the dimension of the fingerprint. Higher the return value,
# the less similar are the values v1 and v2
def distance(v1, v2, f):
    x = (v1 ^ v2) & ((1 << f) - 1)
    ans = 0
    while x:
        ans += 1
        x &= x - 1
    return ans

# function that calculates simhash fingerprint from token_frequencies of a web page
# and compares against each value in fingerprints set to see if there exists a crawled page
# which is a near duplicate of current page.
def isNearDuplicate(token_frequencies):
    #
    currFingerprint = Simhash(token_frequencies, 64).value
    for fingerprint in fingerprints:
        if distance(currFingerprint, fingerprint, 64) <= 64*0.05/100.0:
            fingerprints.add(currFingerprint)

            return True

    fingerprints.add(currFingerprint)
    return False

