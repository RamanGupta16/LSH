import re
import string
from collections import defaultdict
import numpy as np
import json
import mmh3
import random
from sklearn.metrics import mean_squared_error

random.seed(0)

OUTER_SEPARATOR='|'
INNER_SEPARATOR=' '
BANDS=250
ROWS=4
NUM_HASHES=BANDS*ROWS # 1000
SIMILARITY_THRESHOLD = (1.0/BANDS)**(1.0/ROWS) # (1/b)^(1/r)

CORPUS = {}
CORPUS_BAND_BUCKET = defaultdict(lambda: defaultdict(list))

# For RMSE between _LSH_SIMILARITY and JACCARD_SIMILARITY
LIST_LSH_SIMILARITY_SCORE = []
LIST_JACCARD_SIMILARITY_SCORE = []

ampercentRe = re.compile(r'\s(&|&amp;)\s')
stripApostsRe = re.compile(r"([^0-9])[`']s ")
stripApostOnlyRe = re.compile(r"[`']")
backslashWRe = re.compile(r'\sw/\s')
compressSpaceRe = re.compile(r'\s+')

# Hash Functions
''' MurmurHash3 Functions'''
class MurmurHashFunctions(object):
    def __init__(self, numHashes):
        random.seed(0)
        self.num_hashes = numHashes

    def get_hash(self, hash_index, shingle_Id):
        if hash_index >= self.num_hashes or hash_index < 0:
            raise 'Requested number of hash %d is out of range 0 to %d' % (hash_index, self.num_hashes-1)
        shingle = str(shingle_Id)
        return  mmh3.hash(shingle, seed=hash_index, signed=False) # 32bit unsigned hash

HASH_FUNCTIONS = MurmurHashFunctions(NUM_HASHES)

# String Processing
def normalise(s):
	s = stripApostsRe.sub('\\1 ', s)
	s = stripApostOnlyRe.sub('', s)
	s = ampercentRe.sub(' and ', s)
	s = backslashWRe.sub(' with ', s)
	s = s.upper()
	return s

# LSH MinHash Processing
def get_k_shingles_set(sentence, k=2):
        shingles_map = {}
        for i in range(len(sentence)-(k-1)):
            k_shingle = sentence[i:i+k]
            shingle_hash = hash(k_shingle)
            shingles_map[shingle_hash] = k_shingle
        return shingles_map

def create_minhash_signatures(shingles):
	signature = []
	for i in range(0, NUM_HASHES): # Apply each hash function on all shingles
		minHashCode = float('inf') # infinite value

		# Apply i'th hash function to each shingle and find min hash value
		for shingleID in shingles:
			hashCode = HASH_FUNCTIONS.get_hash(i, shingleID)
			minHashCode = min(minHashCode, hashCode)
		signature.append(minHashCode)
	return signature # list of signatures

def convert_into_bands_hash_list(minhash_signature_list, bands=BANDS, rows=ROWS):
	minhash_signature_band_hash_list = []
	for band in range(0, bands):
		start = band*rows
		end = start + rows
		minhash_signature_band = minhash_signature_list[start:end]
		minhash_signature_band_hash = hash(tuple(minhash_signature_band))
		minhash_signature_band_hash_list.append(minhash_signature_band_hash)
	return minhash_signature_band_hash_list

# Corpus Document
def process_corpus_doc(doc):
	Ry = doc['ReleaseYear']
	Type = doc['Type']
	Id = doc['Id']
	Ti = doc['Title']
	if len(Ti) == 1:
		Ti = Ti + ' ' # Ti must have length of minimum 2
	Ti_bigrams_list = [ Ti[i:i+2] for i in range(len(Ti)-1) ]
	Cast_List = doc['Cast'].split(',')
	if len(Cast_List) > 2: # Consider top 2 cast only
		Cast_List = Cast_List[0:2]
	Di_List = doc['Director'].split(',')
	Description = doc['Description']
	Du = doc["Duration"]
	Language = doc['Language']

	feature_list = [INNER_SEPARATOR.join(Ti_bigrams_list)] + [INNER_SEPARATOR.join(Di_List)] + [INNER_SEPARATOR.join(Cast_List)] + [Ry, Du, Language]
	#print (feature_list)

	normalised_data = OUTER_SEPARATOR.join([normalise(x) for x in feature_list])
	shingles = [ y.encode('utf-8') for x in normalised_data.split(OUTER_SEPARATOR) for y in x.split(INNER_SEPARATOR) if len(y) > 0 ]
	#print (shingles)

	minhash_signature = create_minhash_signatures(shingles)
	#print ('len of minhash_signature %d' % len(minhash_signature))
	minhash_signature_band_hash = convert_into_bands_hash_list(minhash_signature)
	#print('len of minhash_signature_band_hash %d' % len(minhash_signature_band_hash))

	# Store in database
	CORPUS[Id] = {'minhash_signature':minhash_signature, 'normalised_data':normalised_data, 'shingles':shingles, 'Title':doc['Title']}
	for band, band_hash in enumerate(minhash_signature_band_hash):
		CORPUS_BAND_BUCKET[band][band_hash].append(Id)

# Process Corpus database from file corpus.txt
def process_corpus(corpus_file='corpus.txt'):
	stats = {'total_count': 0, 'successfully_processed_count': 0}
	print(f"Reading corpus data file {corpus_file}")
	with open(corpus_file, 'r') as corpus:
		for line in corpus:
			stats['total_count'] += 1
			line = json.loads(line.strip())
			try:
				process_corpus_doc(line)
				stats['successfully_processed_count'] += 1
			except Exception as e:
				print(f"Exception:{e} During processing of corpus entry {line}")
	return stats

# Process User Document
def process_user_input(doc):
	Ry = doc.get('ReleaseYear', '')
	Type = doc.get('Type', '')
	Du = doc.get("Duration", '')
	Id = doc['Id']
	Ti = doc.get('Title')
	Ti_bigrams_list = []
	if Ti and len(Ti) == 1:
		Ti = Ti + ' ' # Ti must have length of minimum 2
	Ti_bigrams_list = [ Ti[i:i+2] for i in range(len(Ti)-1) ]
	
	Cast_List = []
	if doc.get('Cast'):
		Cast_List = doc['Cast'].split(',')
	if len(Cast_List) > 2: # Consider top 2 cast only
		Cast_List = Cast_List[0:2]

	Di_List = []
	if doc.get('Director'):
		Di_List = doc['Director'].split(',')
	
	Language = doc.get('Language') or "English"

	feature_list = [INNER_SEPARATOR.join(Ti_bigrams_list)] + [INNER_SEPARATOR.join(Di_List)] + [INNER_SEPARATOR.join(Cast_List)] + [Ry, Du, Language]
	#print (feature_list)

	normalised_data = OUTER_SEPARATOR.join([normalise(x) for x in feature_list])
	shingles = [ y.encode('utf-8') for x in normalised_data.split(OUTER_SEPARATOR) for y in x.split(INNER_SEPARATOR) if len(y) > 0 ]
	#print (shingles)

	minhash_signature = create_minhash_signatures(shingles)
	#print ('len of minhash_signature %d' % len(minhash_signature))
	minhash_signature_band_hash = convert_into_bands_hash_list(minhash_signature)
	#print('len of minhash_signature_band_hash %d' % len(minhash_signature_band_hash))

	userDoc = {'minhash_signature':minhash_signature, 'minhash_signature_band_hash' : minhash_signature_band_hash, 'normalised_data':normalised_data, 'shingles':shingles, 'Id' : Id, 'Title':doc['Title']}
	return userDoc

# Read User Document to match from file user_input.txt
def read_and_match_user_inputs():
	stats = {'request_count': 0, 'total_matched_count': 0, 'total_unmatched_count': 0, 'total_unmatched_lower_threshold':0}
	results = {}
	with open('user_input.txt', 'r') as user_inputs:
		for line in user_inputs:
			line = line.strip()
			if line and not line.startswith('#'):
				stats['request_count'] += 1
				user_input_doc = json.loads(line)
				user_doc = process_user_input(user_input_doc)
				result = match_and_rank(user_doc, stats)
				if result:
					match, score = result
					matched_corpus_id = match['Id']
					matched_corpus_title = CORPUS[matched_corpus_id]['Title']
					user_doc_title = user_doc['Title']
					results[user_doc['Id']] = (user_doc_title, matched_corpus_id, matched_corpus_title, score)
	return stats, results

# Main matching step
def match_and_rank(userDoc, stats):
	candidate_list = set()
	for band, band_hash in enumerate(userDoc['minhash_signature_band_hash']):
		band_bucket = CORPUS_BAND_BUCKET[band]
		if band_bucket.get(band_hash):
			for matched_id in CORPUS_BAND_BUCKET[band][band_hash]:
				candidate_list.add(matched_id)
	#print('candidate_list for %s is %s' % (userDoc['Id'], candidate_list))

	results=[]
	for candidate in candidate_list:
		user_minhash_signature = np.array(userDoc['minhash_signature'])
		cand_minhash_signature = np.array(CORPUS[candidate]['minhash_signature'])
		assert(user_minhash_signature.size == cand_minhash_signature.size)

		# LSH Similarity = Number of MinHash Signatures matches / Size of MinHash Signatures
		lsh_similarity = len([x for x in (user_minhash_signature == cand_minhash_signature).tolist() if x is True])/float(cand_minhash_signature.size)

		# Jaccard Similarity = |A ⋂ B| / | A ∪ B| It is also known as Intersection over Union (IOU). 
		user_jaccard_set = set([y for x in userDoc['normalised_data'].split(OUTER_SEPARATOR) for y in x.split(INNER_SEPARATOR) if len(x) > 0])
		corpus_jaccard_set = set([y for x in CORPUS[candidate]['normalised_data'].split(OUTER_SEPARATOR) for y in x.split(INNER_SEPARATOR) if len(x) > 0])
		jaccard_similarity = len(user_jaccard_set.intersection(corpus_jaccard_set))/float(len(user_jaccard_set.union(corpus_jaccard_set))) # intersection / union

		#print('lsh_similarity:%f		jaccard_similarity:%f' % (lsh_similarity, jaccard_similarity))
		results.append({'Id':candidate, 'LSH_Similarity_Estimate':lsh_similarity, 'Actual_Jaccard_Similarity':jaccard_similarity})
		LIST_LSH_SIMILARITY_SCORE.append(lsh_similarity)
		LIST_JACCARD_SIMILARITY_SCORE.append(jaccard_similarity)

	final_result = None

	# Sort Results with highest LSH Similarity scored item as first
	results.sort(key = lambda similarity: similarity['LSH_Similarity_Estimate'], reverse=True)
	if results:
		score = results[0]['LSH_Similarity_Estimate']
		if score >= SIMILARITY_THRESHOLD:
			print('MATCH FOUND 	:: For userDoc %s Higest matched corpus documet is %s with matching score:%f' % (userDoc['Id'], results[0]['Id'], score))
			stats['total_matched_count'] += 1
			final_result = results[0], score
		else:
			print('NO MATCH FOUND 	:: For userDoc %s Higest matched corpus documet is %s with matching score:%f less than SIMILARITY_THRESHOLD:%f' % (userDoc['Id'], results[0]['Id'], score, SIMILARITY_THRESHOLD))
			stats['total_unmatched_lower_threshold'] += 1
	else:
		print('NO MATCH FOUND 	:: No Corpus document matched')
		stats['total_unmatched_count'] += 1

	return final_result

def print_stats():
	mse = mean_squared_error(LIST_JACCARD_SIMILARITY_SCORE, LIST_LSH_SIMILARITY_SCORE)
	rmse = mean_squared_error(LIST_JACCARD_SIMILARITY_SCORE, LIST_LSH_SIMILARITY_SCORE, squared=False)
	print("Difference between JACCARD_SIMILARITY_SCORE and LSH_SIMILARITY_SCORE 	mean_squared_error:%f	root_mean_squared_error:%f" % (mse, rmse))


if __name__ == "__main__":
	print('BANDS:%d		ROWS:%d		NUM_HASHES:%d	SIMILARITY_THRESHOLD:%f' % (BANDS, ROWS, NUM_HASHES, SIMILARITY_THRESHOLD))
	print("Processing Corpus Documents...")
	corpus_stats = process_corpus()
	print(f"Corpus Processing Stats {corpus_stats}")
	print("Matching User Documents")
	user_matches_stats, results = read_and_match_user_inputs()
	print(f"User Input Match Stats {user_matches_stats}")
	print_stats()
