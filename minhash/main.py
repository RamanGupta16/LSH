import os
from scrape_wikipedia_movies import scrape_wikipedia_Lists_of_films, CORPUS_WIKIPEDIA 
from lsh_minhash_document_matching import process_corpus, read_and_match_user_inputs, print_stats
from lsh_minhash_document_matching import BANDS, ROWS, NUM_HASHES, SIMILARITY_THRESHOLD

USER_DEFONED_CORPUS = 'corpus.txt'

if __name__ == "__main__":
	print("CREATE CORPUS :: Create/Read Corpus")
	# Scrape Wikipedia to create corpus of movie data
	if not os.path.exists(CORPUS_WIKIPEDIA):
		print(f"Scrape Wikipedia Highest-grossing films of each year to create corpus of movie data into file {CORPUS_WIKIPEDIA}")
		scrape_wikipedia_Lists_of_films()
	else:
		print(f"Reading existing corpus of movie data from file {CORPUS_WIKIPEDIA}")
	
	print("========================================================================================================================")

	# Process the Corpus data using LSH MinHash
	print("INDEX CORPUS :: LSH Processing All Corpus Documents...")
	print('BANDS:%d		ROWS:%d		NUM_HASHES:%d	SIMILARITY_THRESHOLD:%f' % (BANDS, ROWS, NUM_HASHES, SIMILARITY_THRESHOLD))

	print("Processing Wikipedia Corpus Documents...")
	corpus_stats = process_corpus(CORPUS_WIKIPEDIA)
	print(f"Wikipedia Corpus {corpus_stats}")

	print("Processing User defined Corpus Documents...")
	corpus_stats = process_corpus(USER_DEFONED_CORPUS)
	print(f"User defined Corpus {corpus_stats}")

	print("========================================================================================================================")

	# Matching User Documents
	print("MATCH :: Matchinging User Inputs using LSH MinHash...")
	user_matches_stats, results = read_and_match_user_inputs()
	print(f"User Input Match Stats {user_matches_stats}")

	print("========================================================================================================================")

	print("RESULTS :: Final Matches Found")
	for user_doc_id, result in results.items():
		user_doc_title, matched_corpus_id, matched_corpus_title, score = result
		print(f"Matched user input {user_doc_id}({user_doc_title}) with {matched_corpus_id}({matched_corpus_title}) with score {score}")

	# Print basic LSH Stats
	print("========================================================================================================================")
	print_stats()
