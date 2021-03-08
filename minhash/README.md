# MinHash
One of the methods of LSH is **MinHash** or the min-wise independent permutations. MinHash quickly *estimates* Jaccard Similarity of two documents and thus finds degree of
“similarity” of 2 documents. This degree of similarity can be used to rank nearest neighbours or match a document against a corpus of documents. For the problem of
finding similar documents from a corpus, matching a given document, the search space and the number of comparisons needed is drsatically reduced. Only the items which hash to the same
bucket need to be compared, instead of comapring every item from corpus. 

**Jaccard Similarity Index**  
Jaccard Similarity Index defines the degree of “similarity” of 2 sets. The Jaccard Similarity of two sets is defined as the ratio of the number of elements of their intersection and the number of elements of their union. Thus for 2 sets A and B the Jaccard Similarity Index is defined as 

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

## LSH MinHash Example  
### Problem:
A user provided sparse entertainment (movie/episodes) metadata JSON document consisting of fields like Title, Language, Genre, Cast, Director, Release Year, Duration, Production House, Description, Summary etc. 

This user JSON document is matched against a much larger corpus of proprietary enriched JSON documents. The corpus documents have more and enriched fields, has complete and correct data, provides summary, trailer & poster links etc.

*The task is to match a user document against the corpus and returning the most matching document from the corpus back to the user.*

### Solution:
MinHash LSH algorithm was used to match and then rank the matched corpus documents.  
This is not simply a Title database search because it handles inconsistent or wrong user input data, missing fields (like missing Title) in user input, handling user spelling mistakes, scoring of matched results etc. 

MinHash LSH algorithm helps
- Reduce document search space
- Transforms from string matching to machine word sized integers matching, which is much faster. 

As the size and number of documents grows the improvements in speed is more pronounced.

## Detailed MinHash LSH Algorithm 
### Process the Corpus Documents as per MinHash LSH Algorithm:  For all corpus documents  
1. **Normalize the document**: Clean all the value strings by removing punctuation marks, converting into upper case.
2. **Title Bigrams**: To tolerate the user mistakes in Titles, divide the Titles into bigrams. Example “Titanic”: ['Ti', 'it', 'ta', 'an', 'ni', 'ic']
3. **Convert document into set of shingles**: Concatenate all the document value strings (including Title bigrams) in a single string. This string is then converted into set of *k-shingles*. A *shingle* is a substring of length k. The shingle can be in terms of characters or words of the document. In our case we choose shingles of one complete word. Example:
- “King of England” converted into 5-characters shingles: ['King ', 'ing o', 'ng of', 'g of ', ' of E', 'of En', 'f Eng', ' Engl', 'Engla', 'nglan', 'gland’]. Note that whitespace is also treated as a character.
- “King of England” converted into shingles of 1 complete word: [‘King’, ‘of’, ‘England’]. Words are separated by whitespace. *This is our choice for generating shingles*.
4. **Construct MinHash Signatures from shingles set**:
- Choose appropriate number of hash functions to use. More the hash functions better the Jaccard Similarity estimate. From experience I have chosen 1000 hash functions. 
- In practice each hash function is same hash function but with a different seed value. Example with seed value from 0-to-999 on a Murmur3 hash function we can get 1000 different hash functions.
- The hash functions take a shingle and return their hashed integer value.
- Apply each hash function on each shingle and select the minimum hash value in every iteration. Collect this minimum hash value from every iteration in a MinHash Signatures list. Thus, the normalised JSON document is converted into MinHash Signatures list whose count same as number of hash functions.
5. **Convert MinHash Signatures List into Bands-Hash List**: 
- The comparison of MinHash Signatures list between given user document and every corpus document will take a very long time. 
- An effective way to reduce search space is by dividing MinHash Signatures list into ‘b’ bands consisting of ‘r’ hashes each and bucketize them using same hash function. Then hash value of each of the ‘r’ hashes is collected into a Bands-Hash List which will be of size ‘b’. From experience I have found r=4 and b=250 to be reasonable.
6. **Create Corpus Documents Database**: Store the Bands-Hash List and MinHash Signatures for each corpus document in a database along with Id of the corpus document.

### Follow same process as above for input user JSON document
1. Normalize the document.
2. Convert document into set of shingles of 1 complete word.
3. Construct MinHash Signatures of shingles set.
4. Convert MinHash Signatures into Bands-Hash List.

## Main Matching Step
1. Select all corpus documents from database where *band* and *hash* matches that of the given user document Bands-Hash List. This is the major reduction in search space. Instead of finding Jaccard Similarity for all documents in entire corpus space, narrow it down to just this Candidate List of corpus documents.
2. Compare each corpus documents from this Candidate List with the user document:
- Find how many corresponding MinHash Signatures matches between current corpus document and user document.
- *Document Similarity = Number of MinHash Signatures matches / Size of MinHash Signatures*
- Document Similarity ratio is the *estimate* of the Jaccard Similarity and thus “overall similarity” of 2 documents. This ratio also helps to rank the matches.
- Highest Similarity documents is the most matching document and returned to user as enriched document corresponding to user document.


## Code
```
1. LSH MinHash Python3 Code : lsh_minhash_document_matching.py
2. Python modules required : numpy, mmh3 (MurMurHash3), sklearn
3. Corpus documents database : corpus.txt
4. User Inputs : user_inputs.txt
```

### Processing of Corpus Documents: Sample processing of corpus document Id2 (Titanic 1997)
1.	Normalize, Bigrams and convert into one word shingles => ['Ti', 'it', 'ta', 'an', 'ni', 'ic', 'James', 'Cameron', 'Leonardo', 'DiCaprio', 'Kate', 'Winslet', '1997', '195', 'English']
2.	MinHash Signatures List of length 1000 => [51698105, 71268306093….]
3.	Bands-Hash List of length 250 (b=250, r=4, b*r=1000) => [679105346, 307527197…]

### Processing of User Document: Sample processing of Req1
1.	Normalize, Bigrams and convert into shingles => ['Ti', 'it', 'ta', 'an', 'ni', 'ic', 'Cameron']
2.	MinHash Signatures List of length 1000 => [51698105, 71268306093….]
3.	Bands-Hash List of length 250 (b=250, r=4, b*r=1000) => [679105346, 307527197…]

*Note*: Hash Values can be differrent in real execution

### Main User Document Matching Step
1.	Candidate List: Select all corpus documents from database where band and hash matches that of the user document Bands-Hash List.
- For user document Req1 the corpud documents candidate list is : [Id1(Titanic 1953), Id2(Titanic 1997)]

2.	From this Candidate List:
- LSH Similarity (Jaccard Similarity estimated from MinHash Signatures List) of candidates => [0.421, 0.521]
- Actual Jaccard Similarity of candidates => [0.411765, 0.500]
- Highest Similarity score is of corpus document Id2(Titanic 1997), and thus it is the most matching corpus document for user input Req1.

### Similarity Threshold 
Similarity Threshold (ratio) is the minimum LSH Similarity or Jaccard Similarity threshold below which a pair of documents will not be considered matched. Example if 2 docuemnts have LSH Similarity or Jaccard Similarity = 0.05 then it is too low a matching score value to deduce that documents are similar. 
```
Similarity Threshold = (1.0/BANDS)**(1.0/ROWS) # (1/b)^(1/r)
```
Bands = b = 250  
Rows = r = 4
Similarity Threshold = 0.25
