# Locality Sensitive Hashing (LSH)
[LSH](https://en.wikipedia.org/wiki/Locality-sensitive_hashing) is technique used to cluster together similar items in a common bucket. LSH is used for Nearest Neighbour search for finding similar documents in a large corpus of documents. Instead of using the brute force approach of comparing all pairs of items, LSH instead hashes them into buckets, such that similar items are more likely to hash into the same buckets. 

LSH differs from a cryptographic hash, because aim here is to maximise collisions to bucketize the similar documents. 

# LSH Techniques
- [MinHash](https://github.com/RamanGupta16/LSH/tree/main/minhash) :: One of the methods of LSH is MinHash or the min-wise independent permutations. MinHash quickly estimates *Jaccard Similarity* of two documents and thus finds degree of “similarity” of 2 documents. This degree of similarity can be used to rank nearest neighbours or match a document against a corpus of documents. MinHash is described in detail along with code in [MinHash](https://github.com/RamanGupta16/LSH/tree/main/minhash)

![LSH MinHash Image](https://github.com/RamanGupta16/LSH/blob/main/docs/LSH_MinHash_Process.jpg)

