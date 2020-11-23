from os import path, getenv
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd


load_dotenv()  # loading env variables for access
DEVELOPER_KEY = getenv("DEVELOPER-KEY")
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def youtube_search(
	q: str = None,  # query as string
	max_results: int = 5,
	order="relevance",
	token=None,
	location=None,
	location_radius=None,
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
		)
		.execute()
	)

	# set up lists to store metadata
	title = []
	channelId = []
	channelTitle = []
	categoryId = []
	videoId = []
	viewCount = []
	likeCount = []
	dislikeCount = []
	commentCount = []
	favoriteCount = []
	category = []
	tags = []
	videos = []
	thumbnails = []
	descriptions = []
	dates = []

	# fill lists with metadata from search items in the raw search: list
	for search_result in search_response.get("items", []):
		# making sure it's a video first
		if search_result["id"]["kind"] == "youtube#video":
			title.append(search_result["snippet"]["title"])
			videoId.append(search_result["id"]["videoId"])

			video_metadata_response = (
						youtube.videos()
						.list(part="statistics, snippet", id=search_result["id"]["videoId"])
						.execute()
			)

			video_metadata_items = {"channelId": ("snippet", channelId),
									"channelTitle": ("snippet", channelTitle),
									"categoryId": ("snippet", categoryId),
									"viewCount": ("statistics", viewCount),
									"likeCount": ("statistics", likeCount),
									"dislikeCount": ("statistics", dislikeCount),
									"commentCount": ("statistics", commentCount),
									"favoriteCount": ("statistics", favoriteCount),
									"category": ("snippet", category),
									"tags": ("snippet", tags),
									"videos": ("snippet", videos),
									"thumbnails": ("snippet", thumbnails),
									"description": ("snippet", descriptions),
									"publishedAt": {"snippet", dates}}

			# adding all metadata results to metadata lists if they are there
			for item in video_metadata_items:
				try:
					response_type = str(video_metadata_items[item][0])
					video_metadata_items[item][1].append(
						video_metadata_response["items"][0][response_type][item]
					)
				except KeyError:
					video_metadata_items[item][1].append("N/A")

	youtube_dict = {
		"tags": tags,
		"channelId": channelId,
		"channelTitle": channelTitle,
		"categoryId": categoryId,
		"title": title,
		"videoId": videoId,
		"viewCount": viewCount,
		"likeCount": likeCount,
		"dislikeCount": dislikeCount,
		"commentCount": commentCount,
		"favoriteCount": favoriteCount,
		"thumbnails": thumbnails,
		"descriptions": descriptions,
		"dates": dates
	}

	next_page_token = search_response.get("nextPageToken")

	return youtube_dict, next_page_token

def remove_redundancy(prev_list=[],added_list=[]):
	new_list = []
	for vid in added_list:
		# print(vid)
		if vid[0] not in prev_list['videoId'].values:
			new_list.append(vid)
	if new_list == []: return None
	return pd.DataFrame(new_list).set_index("videoId").reset_index()

if __name__ == "__main__":
	# setting up dataframe of results
	column_names = ['videoId','tags','channelId','channelTitle','categoryId',\
			'title','viewCount','likeCount', \
			'dislikeCount','commentCount','favoriteCount', \
			'thumbnails','descriptions','search_query','dates']
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
		final_results = remove_redundancy(pd.DataFrame(columns=column_names),final_results.itertuples(index=False))

	# setting up token for search start position, string for query, and list to store all valid results
	search_next_page = getenv("NEXT-PAGE-TOKEN")
	search_queries = ["funny cats", "cat compilation"]
	
	# sorry for the nested for loops but ok this goes through the search queries and adjusts for potential quota limit
	try:
		for search_query in search_queries:
			for i in range(3):  # just change this value for how many pages to run
				#YT Search
				next_page_results, search_next_page = youtube_search(
					q=search_query,
					token=search_next_page,
					max_results=50,
				)
				
				#Processing Search data
				next_page_df = pd.DataFrame.from_dict(next_page_results). \
					set_index("videoId").reset_index()
				next_page_df['search_query'] = search_query  # adding search query column value

				# add to existing data
				results_to_add = remove_redundancy(final_results,next_page_df.itertuples(index=False))
				final_results = final_results.append(results_to_add,ignore_index=True)
	
	# don't exit when http error just save final results
	except HttpError:
		print('WARNING: You have exceeded your daily quota.')
	# saving output, overwrite previous csv
	final_results.to_csv(SAVEFILE_NAME,index=False,mode='w')
	print('Token for next search:',search_next_page)
