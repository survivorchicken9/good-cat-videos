from os import path, getenv
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd


load_dotenv()  # loading env variables for access
DEVELOPER_KEY = getenv("DEVELOPER-KEY")
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

#Data columns to be collected from Youtube
column_names = ["videoId","tags","channelId","channelTitle",\
		"categoryId","title","viewCount","likeCount", \
		"dislikeCount","commentCount","favoriteCount", \
		"thumbnails","descriptions","category","searchQuery",\
		"uploadDate","videoLen", "videoQual"]

def youtube_search(
	q: str = None,  # query as string
	max_results: int = 5,
	order="relevance",
	token=None,
	location=None,
	location_radius=None,
	publishedBefore=None,
	publishedAfter=None,
):
	# instantiate discovery object from googleapiclient
	youtube = build(
		YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY
	)

	# get raw search: list result
	search_response = (
		youtube.search()
		.list(
			q=q,
			type="video",
			pageToken=token,
			order=order,
			part="id, snippet",  # which type of data to get
			maxResults=max_results,
			location=location,
			locationRadius=location_radius,
			publishedBefore=publishedBefore,
			publishedAfter=publishedAfter,
		)
		.execute()
	)

	# set up lists to store metadata
	compiled_data = {key:[] for key in column_names}
	# fill lists with metadata from search items in the raw search: list
	for search_result in search_response.get("items", []):
		# making sure it's a video first
		if search_result["id"]["kind"] == "youtube#video":
			compiled_data['videoId'].append(search_result["id"]["videoId"])
			# compiled_data['searchQuery'].append(f'/"{str(q)}"/ ')
			compiled_data['searchQuery'].append((str(q)))
			video_metadata_response = (
						youtube.videos()
						.list(part="statistics,snippet,contentDetails", \
							 id=search_result["id"]["videoId"])
						.execute()
			)
			video_metadata_items = {("title","snippet"): "title",
									("channelId","snippet"): "channelId",
									("channelTitle", "snippet"): "channelTitle",
									("categoryId", "snippet"): "categoryId",
									("viewCount", "statistics"): "viewCount",
									("likeCount", "statistics"): "likeCount",
									("dislikeCount", "statistics"): "dislikeCount",
									("commentCount", "statistics"): "commentCount",
									("favoriteCount", "statistics"): "favoriteCount",
									("category", "snippet"): "category",
									("tags", "snippet"): "tags",
									# ("videos", "snippet"): "videos",
									("thumbnails", "snippet"): "thumbnails",
									("description", "snippet"): "descriptions",
									("publishedAt", "snippet"): "uploadDate",
									("duration", "contentDetails"): "videoLen",
									("definition", "contentDetails"): "videoQual"}

			# adding all metadata results to metadata lists if they are there
			for item, target in video_metadata_items.items():
				try:
					response_type = str(item[1])
					compiled_data[target].append(
						video_metadata_response["items"][0][response_type][item[0]]
					)
				except KeyError:
					compiled_data[target].append("N/A")

	next_page_token = search_response.get("nextPageToken")

	return compiled_data, next_page_token

def combine_queries(querySeries):
	queries = ",".join(set(querySeries.tolist()[0].split(sep=",")))
	return queries

def remove_redundancy(prev_list=[],added_list=[]):
	combined_list = pd.concat([prev_list,added_list])
	main_list = combined_list.groupby("videoId") \
		[[key for key in column_names if key != "searchQuery"]] \
		.head(1)
	query_list = combined_list.groupby(["videoId"]) \
		["searchQuery"].apply(lambda ser: combine_queries(ser))
	main_list = main_list.join(query_list,on='videoId')

	return main_list

if __name__ == "__main__":
	# setting up dataframe of results
	# Default csv save name, check environment for alternative save names
	# Then checks directory for the csv file
	try:
		SAVEFILE_NAME = getenv("SAVEFILE-NAME")
	except:
		SAVEFILE_NAME = f'cat_test_results.csv'
	if not path.exists(SAVEFILE_NAME):
		final_results = pd.DataFrame(columns=column_names)
	else:
		final_results = pd.read_csv(SAVEFILE_NAME)  # continue with existing for nth crawl
		final_results = remove_redundancy(pd.DataFrame(columns=column_names),final_results)

	# setting up token for search start position, string for query, and list to store all valid results
	start_token = getenv("NEXT-PAGE-TOKEN")
	search_queries = ["funny cats", "cat compilation"]
	
	# sorry for the nested for loops but ok this goes through the search queries and adjusts for potential quota limit
	try:
		for count, search_query in enumerate(search_queries):
			search_next_page = start_token
			for i in range(1):  # just change this value for how many pages to run
				#YT Search
				next_page_results, search_next_page = youtube_search(
					q=search_query,
					token=search_next_page,
					max_results=50,
					order='relevance',		#relevance, rating, viewCount, date, title, videoCount
					publishedBefore='2018-12-31T23:59:59Z',		#RFC3339 Date format
					publishedAfter='2016-01-01T00:00:01Z',
				)
				
				#Processing Search data
				next_page_df = pd.DataFrame.from_dict(next_page_results).set_index("videoId").reset_index()
				
				# add to existing data
				final_results = remove_redundancy(final_results,next_page_df)
			print(f'Token for next search {search_query} : {search_next_page}')
	
	# don't exit when http error just save final results
	except HttpError:
		print('WARNING: You have exceeded your daily quota.')
	# saving output, overwrite previous csv
	final_results.to_csv(SAVEFILE_NAME,index=False,mode='w')
