# Locality Sensitive Hashing (LSH)
[LSH](https://en.wikipedia.org/wiki/Locality-sensitive_hashing) is technique used to cluster together similar items in a common bucket. LSH is used for Nearest Neighbour search for finding similar documents in a large corpus of documents. Instead of using the brute force approach of comparing all pairs of items, LSH instead hashes them into buckets, such that similar items are more likely to hash into the same buckets. 

LSH differs from a cryptographic hash, because aim here is to maximise collisions to bucketize the similar documents. 
