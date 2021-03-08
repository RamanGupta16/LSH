# MinHash
One of the methods of LSH is **MinHash** or the min-wise independent permutations. MinHash quickly *estimates* Jaccard Similarity of two documents and thus finds degree of
“similarity” of 2 documents. This degree of similarity can be used to rank nearest neighbours or match a document against a corpus of documents. For the problem of
finding similar documents from a corpus, matching a given document, the search space and the number of comparisons needed is drsatically reduced. Only the items which hash to the same
bucket need to be compared, instead of comapring every item from corpus. 

**Jaccard Similarity Index** defines the degree of “similarity” of 2 sets. The Jaccard Similarity of two sets is defined as the ratio of the number of elements of their intersection and the number of elements of their union. Thus for 2 sets A and B the Jaccard Similarity Index is defined as 

J = |A ⋂ B| / | A ∪ B|  It is also known as Intersection over Union (IoU). 

Here the similarity focus is on lexical similarity instead of semantics similarity i.e. character-level or word-level similarity, not “similar meaning” similarity. A very trivial example 

A = King of England  
B = King of Poland  
C = Queen and King  

Jaccard Similarity of A & B = 2/4 = 0.5  
Jaccard Similarity of A & C = 1/5 = 0.2  
Jaccard Similarity of B & C = 1/5 = 0.2  

Pair (A, B) are more similar that other pairs, since J is highest for this apir.

The primary use case of Jaccard Similarity or MinHash is to find textually similar documents in a large corpus. Example detecting plagiarism, mirrored webpages etc. 
