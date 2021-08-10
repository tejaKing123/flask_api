from googleapiclient.discovery import build
import pandas as pd
import demoji
import urllib.request
import urllib
from langdetect import detect
import re   # regular expression
import json
from textblob import TextBlob


key="AIzaSyAIGeU6DMwurpAb9Ndcwyr9TB2rVzzPnbk"

def can_you():
  return "hello"

#* 1st step

# * this method helps us to make a connection between the google apis 

def build_service():
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    return build(YOUTUBE_API_SERVICE_NAME,
                  YOUTUBE_API_VERSION,
                  developerKey=key)


# * this is the video title retriving method which was took from youtube api documentation

def get_vid_title(vidid):
    # VideoID = "LAUa5RDUvO4"
    params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % vidid}
    url = "https://www.youtube.com/oembed"
    query_string = urllib.parse.urlencode(params)
    url = url + "?" + query_string

    with urllib.request.urlopen(url) as response:
        response_text = response.read()
        data = json.loads(response_text.decode())
        # print(data['title'])
        return data['title']



def main_method(videolink):
  #* 2nd step
  # Then we will call this connection method to build connection
  service = build_service()

  # videolink="https://www.youtube.com/watch?v=TXakJYHe9uQ"

  #* 3rd step:
  #  we will pass the video link to this method

  # then we are retriving the video id from the youtube link
  test=(videolink.find("v=")) 

  videoid=videolink[test+2:]

  #  and then we are passing this link to out query_vid_title method which will help in geting our video title

  # query will be our video title

  query = get_vid_title(videoid)

  #* query result will be our video details 
  # this search is just like google search which will get all the relevent data reagrding the video title

  query_results = service.search().list(part='snippet', q=query,
                                        order='relevance',
                                        type='video',
                                        relevanceLanguage='en',
                                        safeSearch='moderate').execute()


  video_id = []
  channel = []
  video_title = []
  video_desc = []
  video_thumb=[]
  video_pubdate=[]

  # this  query_result will be in the form of json
  
  print(query_results['items'])
  # result={'thumbnail': '', 'videoTitle': '', 'MainResult': '', 'description': '','publishTime':'','publishedAt':'','channelTitle':'',}

  for item in query_results['items']:
      video_id.append(item['id']['videoId'])
      channel.append(item['snippet']['channelTitle'])
      video_title.append(item['snippet']['title'])
      video_desc.append(item['snippet']['description'])
      video_pubdate.append(item['snippet']['publishTime'])
      video_thumb.append(item['snippet']['thumbnails']['medium']['url'])

  video_id = video_id[0]
  channel = channel[0]
  video_title = video_title[0]
  video_desc = video_desc[0]
  video_thumb=video_thumb[0]
  video_pubdate=video_pubdate[0]
  print(video_id,channel,video_title,video_desc,video_thumb)
  


  video_id_pop = []
  channel_pop = []
  video_title_pop = []
  video_desc_pop = []
  comments_pop = []
  comment_id_pop = []
  reply_count_pop = []
  like_count_pop = []


  comments_temp = []
  comment_id_temp = []
  reply_count_temp = []
  like_count_temp = []


  # The token that can be used as the value of the pageToken parameter to retrieve the next page in the result set.
  nextPage_token = None

  while 1:
    response = service.commentThreads().list(
                      part = 'snippet',
                      videoId = videoid,
                      maxResults = 100, 
                      order = 'relevance', 
                      textFormat = 'plainText',
                      pageToken = nextPage_token
                      ).execute()


    nextPage_token = response.get('nextPageToken')
    for item in response['items']:
        comments_temp.append(item['snippet']['topLevelComment']['snippet']['textDisplay'])
        comment_id_temp.append(item['snippet']['topLevelComment']['id'])
        reply_count_temp.append(item['snippet']['totalReplyCount'])
        like_count_temp.append(item['snippet']['topLevelComment']['snippet']['likeCount'])
        comments_pop.extend(comments_temp)
        comment_id_pop.extend(comment_id_temp)
        reply_count_pop.extend(reply_count_temp)
        like_count_pop.extend(like_count_temp)
          
        video_id_pop.extend([video_id]*len(comments_temp))
        channel_pop.extend([channel]*len(comments_temp))
        video_title_pop.extend([video_title]*len(comments_temp))
        video_desc_pop.extend([video_desc]*len(comments_temp))

    # this will help us to find wheather there is another page or not
    if nextPage_token is  None:
      break

  # print(comments_pop)

  output_dict = {
          'Channel': channel_pop,
          'Video Title': video_title_pop,
          'Video Description': video_desc_pop,
          'Video ID': video_id_pop,
          'Comment': comments_pop,
          'Comment ID': comment_id_pop,
          'Replies': reply_count_pop,
          'Likes': like_count_pop,
          }

  output_df = pd.DataFrame(output_dict, columns = output_dict.keys())

  duplicates = output_df[output_df.duplicated("Comment ID")]


  unique_df = output_df.drop_duplicates(subset=['Comment'])

  # unique_df.to_csv("extraced_comments.csv",index = False)

  # comments = pd.read_csv('extraced_comments.csv')

  comments=unique_df
  demoji.download_codes()

  #replacing emoji with empty text
  comments['clean_comments'] = comments['Comment'].apply(lambda x: demoji.replace(x,""))

  comments['language'] = 0

  count = 0
  for i in range(0,len(comments)):


    temp = comments['clean_comments'].iloc[i]
    count += 1
    try:
      comments['language'].iloc[i] = detect(temp)
    except:
      comments['language'].iloc[i] = "error"

  comments[comments['language']=='en']['language'].value_counts()

  english_comm = comments[comments['language'] == 'en']

  # english_comm.to_csv("english_comments.csv",index = False)

  # en_comments = pd.read_csv('english_comments.csv',encoding='utf8',error_bad_lines=False)
  en_comments=english_comm
  en_comments.shape

  regex = r"[^0-9A-Za-z'\t]"

  copy = en_comments.copy()

  copy['reg'] = copy['clean_comments'].apply(lambda x:re.findall(regex,x))
  copy['regular_comments'] = copy['clean_comments'].apply(lambda x:re.sub(regex,"  ",x))

  dataset = copy[['Video ID','Comment ID','regular_comments']].copy()


  dataset = dataset.rename(columns = {"regular_comments":"comments"})

  # dataset.to_csv("Dataset.csv",index = False)

  # data = pd.read_csv("Dataset.csv")

  data=dataset

  data['polarity'] = data['comments'].apply(lambda x: TextBlob(x).sentiment.polarity)

  data = data.sample(frac=1).reset_index(drop=True)

  data['pol_cat']  = 0

  data['pol_cat'][data.polarity > 0] = 1
  data['pol_cat'][data.polarity < 0] = -1
  data['pol_cat'][data.polarity == 0] = 0
  data['pol_cat'].value_counts()

  data.to_csv("Dataset1.csv",index = False)

  size=len(data)
  data_nutral=data[data['pol_cat']==0]
  data_pos = data_nutral.reset_index(drop = True)
  data_pos = data[data['pol_cat'] == 1]
  data_pos = data_pos.reset_index(drop = True)
  data_neg = data[data['pol_cat'] == -1]
  data_neg = data_neg.reset_index(drop = True)

  sizepos=len(data_pos)/len(data)
  #          0                   1                          2                             3             4     5            6       7                8  9        10                                              
  return len(data_pos)/len(data),len(data_neg)/len(data),len(data_nutral)/len(data),video_desc,video_title,video_thumb,channel,video_pubdate,data_pos,data_neg,data_nutral

# link=input()
# print(main_method(link))