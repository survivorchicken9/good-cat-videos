from os import path, getenv
from dotenv import load_dotenv
from googleapiclient.discovery import build
import pandas as pd


load_dotenv()  # loading env variables for access
DEVELOPER_KEY = getenv("DEVELOPER-KEY")
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def youtube_search(
	q: str,
	max_results: int = 50,
	order="relevance",
	token=None,
	location=None,
	location_radius=None,
):
	# instantiate discovery object from googleapiclient
	# print(DEVELOPER_KEY)
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
			part="id,snippet",  # Part signifies the different types of data you want
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
									"videos": ("snippet", videos)}

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
	}

	next_page_token = search_response.get("nextPageToken")

	return youtube_dict, next_page_token


if __name__ == "__main__":
	# setting up dataframe of results
	if not path.exists(f'cat_test_results.csv'):
		final_results = pd.DataFrame(columns=['tags','channelId','channelTitle' \
				,'Title','videoId','viewCount','likeCount','dislikeCount' \
				,'commentCount','favoriteCount'])  # initialize empty df for first time crawl
	else:
		final_results = pd.read_csv(f'cat_test_results.csv')  # continue with existing for nth crawl
		# print(final_results.head())

	search_next_page = None
	for i in range(1, 7):  # just change this value for how many pages to run
		next_page_results, search_next_page = youtube_search("cat videos", token=search_next_page)
		next_page_df = pd.DataFrame.from_dict(next_page_results)
		results_to_add = []

		# iterate over table with itertuples (good performance)
		for result in next_page_df.itertuples():
			try:
				if result[6] not in final_results['videoId'].values:
					results_to_add.append(result)
					# print(f"LOGGING: {result[6]} has been added.")
					continue
				# print(f"WARNING: {result[6]} already exists.")
			except KeyError:
				results_to_add.append(result)

		final_results = final_results.append(results_to_add, ignore_index=True)

		# print()
		# print(f"Ran {i} times, page {search_next_page}.")

	# saving output
	final_results.to_csv("cat_test_results.csv",index=False)
	# print(final_results.head())
