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
									"description": ("snippet", descriptions)}

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
		"descriptions": descriptions
	}

	next_page_token = search_response.get("nextPageToken")

	return youtube_dict, next_page_token


if __name__ == "__main__":
	# setting up dataframe of results
	if not path.exists(f'cat_test_results_trial.csv'):
		final_results = pd.DataFrame()
	else:
		final_results = pd.read_csv(f'cat_test_results_trial.csv')  # continue with existing for nth crawl

	# setting up token for next page, string for query, and list to store all valid results
	search_next_page = None
	search_queries = ["funny cats", "cat compilation"]
	results_to_add = []
	
	# logging variables
	duplicate_data = 0
	valid_data = 0
	
	# sorry for the nested for loops but ok this goes through the search queries and adjusts for potential quota limit
	try:
		for search_query in search_queries:
			for i in range(1, 20):  # just change this value for how many pages to run
				next_page_results, search_next_page = youtube_search(
					q=search_query,
					token=search_next_page,
					max_results=50,
				)
				
				next_page_df = pd.DataFrame.from_dict(next_page_results)
				next_page_df['search_query'] = search_query  # adding search query column value
		
				# iterate over table with itertuples (good performance)
				for result in next_page_df.itertuples():
					try:
						if result[6] not in final_results['videoId'].values:  # result[6] is videoId column value
							valid_data += 1
							results_to_add.append(result)
							print(f"LOGGING: {result[6]} has been added.")
							continue
						duplicate_data += 1
						print(f"WARNING: {result[6]} already exists.")
					except KeyError:
						valid_data += 1
						results_to_add.append(result)
						print(f"LOGGING: {result[6]} has been added.")
				
				final_results = final_results.append(results_to_add, ignore_index=True)
		
				print()
				print(f"Ran {i} times for search query '{search_query}', page {search_next_page}.")
				print(f"Valid data found: {valid_data}")
				print(f"Duplicate data found: {duplicate_data}")
				print()
	
	# don't exit when http error just save final results
	except HttpError:
		print('WARNING: You have exceeded your daily quota.')

	# saving output
	final_results.to_csv("cat_test_results_trial.csv", index=False)
	# print(final_results.head())
